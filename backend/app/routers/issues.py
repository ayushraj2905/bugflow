import csv
import io
import re
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models.issue import Issue, Comment, Attachment, AuditLog, IssueAssignment, ReporterIssueTracking
from ..models.project import Project, BugCategory
from ..models.user import User
from ..schemas import IssueCreate, IssueUpdate, CommentCreate, TransitionRequest, DuplicateCheckRequest
from ..services.auth_service import get_current_user
from ..services.triage_engine import TriageEngine
from ..services.duplicate_detector import DuplicateDetector
from ..services.workflow_service import WorkflowService

router = APIRouter(tags=["Issue Management & Triage"])

class TriageRecommendationRequest(BaseModel):
    title: str
    description: str
    severity: Optional[str] = None
    category: Optional[str] = None

def generate_next_issue_key(db: Session, project: Project) -> str:
    key_prefix = project.key if (project and project.key) else "BUG"
    existing_keys = db.query(Issue.issue_key).all()
    max_num = 0
    for (k,) in existing_keys:
        if k:
            nums = re.findall(r'\d+', k)
            if nums:
                max_num = max(max_num, int(nums[-1]))
    next_num = max_num + 1
    return f"{key_prefix}-{next_num:03d}"

# 1. Triage Recommendation API
@router.post("/api/v1/issues/triage-recommendation")
@router.post("/api/v1/bugs/triage-recommendation")
def get_triage_recommendation(req: TriageRecommendationRequest, db: Session = Depends(get_db)):
    triage_info = TriageEngine.analyze_issue(
        title=req.title,
        description=req.description,
        severity_override=req.severity,
        category_override=req.category
    )

    devs = db.query(User).filter(User.role.in_(["DEVELOPER", "ADMIN", "PROJECT_MANAGER"])).all()
    dev_recommendations = TriageEngine.recommend_developers(
        issue_text=f"{req.title} {req.description}",
        category_name=triage_info["predicted_category"],
        available_devs=devs,
        db=db
    )

    return {
        "title": req.title,
        "predicted_severity": triage_info["predicted_severity"],
        "predicted_category": triage_info["predicted_category"],
        "priority_score": triage_info["priority_score"],
        "priority_label": triage_info["predicted_priority"],
        "priority_calculation": triage_info["priority_calculation"],
        "estimated_effort_hours": triage_info["estimated_effort"],
        "recommended_developers": dev_recommendations[:3]
    }

# 2. Get Issues List with Database Pagination (skip & limit for 50,000+ scale)
@router.get("/api/v1/bugs/")
@router.get("/api/v1/issues/")
def get_issues(
    project_id: int = None,
    stage: str = None,
    severity: str = None,
    priority: str = None,
    assignee_id: int = None,
    search: str = None,
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Limit records per page"),
    db: Session = Depends(get_db)
):
    query = db.query(Issue)
    if project_id:
        query = query.filter(Issue.project_id == project_id)
    if stage:
        query = query.filter(Issue.dev_stage == stage.upper())
    if severity:
        query = query.filter(Issue.severity == severity.upper())
    if priority:
        query = query.filter(Issue.priority == priority.upper())
    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)
    if search:
        query = query.filter(or_(
            Issue.title.ilike(f"%{search}%"),
            Issue.description.ilike(f"%{search}%"),
            Issue.issue_key.ilike(f"%{search}%")
        ))

    total_count = query.count()
    issues = query.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for issue in issues:
        results.append({
            "id": issue.id,
            "issue_key": issue.issue_key,
            "title": issue.title,
            "description": issue.description,
            "dev_stage": issue.dev_stage,
            "severity": issue.severity,
            "priority": issue.priority,
            "priority_score": issue.priority_score or 6.0,
            "affected_module": issue.affected_module,
            "environment_info": issue.environment_info,
            "project_name": issue.project.project_name if issue.project else "N/A",
            "category_name": issue.category.category_name if issue.category else "General",
            "assignee": issue.assignee.full_name if issue.assignee else "Unassigned",
            "reporter": issue.reporter.full_name if issue.reporter else "Anonymous",
            "created_at": issue.created_at.strftime("%Y-%m-%d %H:%M") if issue.created_at else "",
            "estimated_effort": issue.estimated_effort
        })
    return results

# 3. Create Issue
@router.post("/api/v1/bugs/")
@router.post("/api/v1/issues/")
def create_issue(data: IssueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id if current_user else 1
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        project = db.query(Project).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    issue_key = generate_next_issue_key(db, project)

    category = None
    if data.category_id:
        category = db.query(BugCategory).filter(BugCategory.id == data.category_id).first()
    category_name = category.category_name if category else "API & Integrations"

    triage_info = TriageEngine.analyze_issue(
        title=data.title,
        description=data.description,
        reproduction_steps=data.reproduction_steps or "",
        severity_override=data.severity,
        category_override=category_name
    )

    final_severity = data.severity if (data.severity and data.severity in TriageEngine.SEVERITY_WEIGHTS) else triage_info["predicted_severity"]
    p_calc = TriageEngine.calculate_priority_score(final_severity, category_name)
    final_priority = p_calc["priority_label"]
    final_priority_score = p_calc["priority_score"]

    new_issue = Issue(
        issue_key=issue_key,
        project_id=project.id,
        category_id=data.category_id,
        title=data.title,
        description=data.description,
        reproduction_steps=data.reproduction_steps,
        affected_module=data.affected_module or "Backend API",
        environment_info=data.environment_info or "Production",
        severity=final_severity,
        priority=final_priority,
        priority_score=final_priority_score,
        dev_stage="REPORTED",
        reporter_id=user_id,
        assignee_id=data.assignee_id,
        sprint_id=data.sprint_id,
        estimated_effort=data.estimated_effort or triage_info["estimated_effort"]
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    # Audit log
    author_name = current_user.full_name if current_user else "System"
    WorkflowService.log_action(
        db, new_issue.id, user_id, "ISSUE_CREATED", None, "REPORTED",
        f"Issue {new_issue.issue_key} created with Severity {new_issue.severity} and Priority {new_issue.priority} (Score: {new_issue.priority_score})"
    )

    tracking = ReporterIssueTracking(
        reporter_id=user_id,
        bug_id=new_issue.id,
        related_case=f"Ticket-{new_issue.issue_key}",
        progress=0
    )
    db.add(tracking)

    if data.assignee_id:
        assignment = IssueAssignment(
            bug_id=new_issue.id,
            dev_id=data.assignee_id,
            title=new_issue.title,
            estimated_effort=new_issue.estimated_effort,
            priority=new_issue.priority
        )
        db.add(assignment)
        new_issue.dev_stage = "ASSIGNED"

    db.commit()
    return {
        "message": "Issue created successfully",
        "issue_id": new_issue.id,
        "issue_key": new_issue.issue_key,
        "priority": new_issue.priority,
        "priority_score": new_issue.priority_score
    }

# 4. Get Issue Detail
@router.get("/api/v1/bugs/{issue_id}")
@router.get("/api/v1/issues/{issue_id}")
def get_issue_detail(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    comments = db.query(Comment).filter(Comment.bug_id == issue.id).order_by(Comment.created_at.asc()).all()
    attachments = db.query(Attachment).filter(Attachment.bug_id == issue.id).order_by(Attachment.uploaded_at.desc()).all()
    audit_trail = db.query(AuditLog).filter(AuditLog.bug_id == issue.id).order_by(AuditLog.timestamp.desc()).all()

    devs = db.query(User).filter(User.role.in_(["DEVELOPER", "ADMIN", "PROJECT_MANAGER"])).all()
    category_name = issue.category.category_name if issue.category else "General"
    dev_recommendations = TriageEngine.recommend_developers(
        issue_text=f"{issue.title} {issue.description} {issue.affected_module}",
        category_name=category_name,
        available_devs=devs,
        db=db
    )

    p_calc = TriageEngine.calculate_priority_score(issue.severity, category_name)

    return {
        "id": issue.id,
        "issue_key": issue.issue_key,
        "title": issue.title,
        "description": issue.description,
        "reproduction_steps": issue.reproduction_steps,
        "affected_module": issue.affected_module,
        "environment_info": issue.environment_info,
        "severity": issue.severity,
        "priority": issue.priority,
        "priority_score": issue.priority_score or p_calc["priority_score"],
        "priority_calculation": p_calc,
        "dev_stage": issue.dev_stage,
        "estimated_effort": issue.estimated_effort,
        "actual_effort": issue.actual_effort,
        "resolution_summary": issue.resolution_summary,
        "created_at": issue.created_at.strftime("%Y-%m-%d %H:%M:%S") if issue.created_at else "",
        "project": {"id": issue.project.id, "name": issue.project.project_name, "key": issue.project.key} if issue.project else None,
        "category": {"id": issue.category.id, "name": issue.category.category_name} if issue.category else None,
        "reporter": {"id": issue.reporter.id, "name": issue.reporter.full_name, "email": issue.reporter.email} if issue.reporter else None,
        "assignee": {"id": issue.assignee.id, "name": issue.assignee.full_name, "skills": issue.assignee.core_skills} if issue.assignee else None,
        "sprint": {"id": issue.sprint.id, "name": issue.sprint.sprint_name} if issue.sprint else None,
        "comments": [{
            "id": c.id,
            "user_name": c.author.full_name if c.author else "Unknown",
            "content": c.content,
            "code_reference": c.code_reference,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else ""
        } for c in comments],
        "attachments": [{
            "id": a.id,
            "filename": a.filename,
            "file_url": a.file_path,
            "file_type": a.file_type,
            "file_size": a.file_size,
            "uploaded_by": a.uploader.full_name if a.uploader else "User",
            "uploaded_at": a.uploaded_at.strftime("%Y-%m-%d %H:%M") if a.uploaded_at else ""
        } for a in attachments],
        "audit_logs": [{
            "action": a.action,
            "previous_state": a.previous_state,
            "new_state": a.new_state,
            "details": a.details,
            "user_name": a.user.full_name if a.user else "System",
            "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if a.timestamp else ""
        } for a in audit_trail],
        "developer_recommendations": dev_recommendations[:3]
    }

# 5. Transition Stage
@router.post("/api/v1/bugs/{issue_id}/transition")
@router.post("/api/v1/issues/{issue_id}/transition")
def transition_issue(issue_id: int, req: TransitionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id if current_user else 1
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    updated = WorkflowService.transition_stage(db, issue, req.target_stage, user_id, req.note or "")
    return {"message": f"Issue transitioned to {updated.dev_stage}", "dev_stage": updated.dev_stage}

# 6. Assign Developer
@router.post("/api/v1/bugs/{issue_id}/assign")
@router.post("/api/v1/issues/{issue_id}/assign")
def assign_developer(issue_id: int, dev_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id if current_user else 1
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    dev = db.query(User).filter(User.id == dev_id).first()
    if not issue or not dev:
        raise HTTPException(status_code=404, detail="Issue or Developer not found")

    prev_assignee = issue.assignee.full_name if issue.assignee else "Unassigned"
    issue.assignee_id = dev.id
    if issue.dev_stage == "REPORTED":
        issue.dev_stage = "ASSIGNED"

    assignment = IssueAssignment(
        bug_id=issue.id,
        dev_id=dev.id,
        title=issue.title,
        estimated_effort=issue.estimated_effort,
        priority=issue.priority
    )
    db.add(assignment)

    WorkflowService.log_action(
        db, issue.id, user_id, "REASSIGNMENT", prev_assignee, dev.full_name,
        f"Assigned to {dev.full_name} ({dev.team})"
    )
    db.commit()
    return {"message": f"Assigned to {dev.full_name}", "assignee": dev.full_name}

# 7. Check Duplicate
@router.post("/api/v1/bugs/check-duplicate")
@router.post("/api/v1/issues/check-duplicate")
def check_duplicate(req: DuplicateCheckRequest, db: Session = Depends(get_db)):
    all_issues = db.query(Issue).all()
    duplicates = DuplicateDetector.find_potential_duplicates(req.title, req.description, all_issues)
    return {"duplicates_found": len(duplicates), "candidates": duplicates}

# 8. AI Triage Preview
@router.post("/api/v1/bugs/ai-triage-preview")
@router.post("/api/v1/issues/ai-triage-preview")
def triage_preview(req: DuplicateCheckRequest, db: Session = Depends(get_db)):
    analysis = TriageEngine.analyze_issue(req.title, req.description)
    devs = db.query(User).filter(User.role.in_(["DEVELOPER", "ADMIN", "PROJECT_MANAGER"])).all()
    recommendations = TriageEngine.recommend_developers(f"{req.title} {req.description}", analysis["predicted_category"], devs, db=db)
    return {
        "analysis": analysis,
        "recommended_developers": recommendations[:3]
    }
