from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from ..database import get_db
from ..models.sprint import Sprint
from ..models.issue import Issue, AuditLog
from ..models.project import Project
from ..schemas import SprintCreate
from ..services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/v1/sprints", tags=["Agile Sprint Planning & Backlog"])

# 1. List Sprints
@router.get("/")
def get_sprints(project_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Sprint)
    if project_id:
        query = query.filter(Sprint.project_id == project_id)
    sprints = query.order_by(Sprint.start_date.desc()).all()
    results = []
    for s in sprints:
        total_items = len(s.issues)
        closed_items = sum(1 for i in s.issues if i.dev_stage in ["CLOSED", "RESOLVED"])
        progress = round((closed_items / total_items * 100), 1) if total_items > 0 else 0
        
        # Calculate actual velocity (completed issues count / story points)
        actual_velocity = closed_items
        
        results.append({
            "id": s.id,
            "sprint_name": s.sprint_name,
            "goal": s.goal or "Feature release & defect resolution",
            "start_date": str(s.start_date),
            "end_date": str(s.end_date),
            "planned_velocity": s.planned_velocity,
            "actual_velocity": actual_velocity,
            "status": s.status,
            "total_items": total_items,
            "closed_items": closed_items,
            "progress_percent": progress,
            "project_name": s.project.project_name if s.project else "General"
        })
    return results

# 2. Create Sprint
@router.post("/")
def create_sprint(data: SprintCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        project = db.query(Project).first()
        proj_id = project.id if project else 1
    else:
        proj_id = project.id

    sprint = Sprint(
        project_id=proj_id,
        sprint_name=data.sprint_name,
        goal=data.goal,
        start_date=data.start_date,
        end_date=data.end_date,
        planned_velocity=data.planned_velocity or 30,
        status="ACTIVE"
    )
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return {
        "message": "Sprint created successfully",
        "sprint_id": sprint.id,
        "sprint_name": sprint.sprint_name,
        "status": sprint.status
    }

# 3. Add Issue from Backlog to Sprint
@router.post("/{sprint_id}/add-issue/{issue_id}")
def add_issue_to_sprint(sprint_id: int, issue_id: int, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    prev_sprint_name = issue.sprint.sprint_name if issue.sprint else "Backlog"
    issue.sprint_id = sprint.id
    
    # Audit log
    WorkflowService.log_action(
        db, issue.id, 1, "SPRINT_ASSIGNMENT", prev_sprint_name, sprint.sprint_name,
        f"Moved from {prev_sprint_name} into {sprint.sprint_name}"
    )
    db.commit()
    return {
        "message": f"Issue {issue.issue_key} successfully added to {sprint.sprint_name}",
        "issue_id": issue.id,
        "sprint_id": sprint.id,
        "sprint_name": sprint.sprint_name
    }

# 4. Complete Sprint and Calculate Velocity
@router.post("/{sprint_id}/complete")
def complete_sprint(sprint_id: int, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    sprint.status = "COMPLETED"
    resolved_count = sum(1 for i in sprint.issues if i.dev_stage in ["CLOSED", "RESOLVED"])
    
    db.commit()
    return {
        "message": f"Sprint {sprint.sprint_name} marked as COMPLETED",
        "sprint_id": sprint.id,
        "status": "COMPLETED",
        "final_velocity": resolved_count,
        "total_issues": len(sprint.issues),
        "resolved_issues": resolved_count
    }

# 5. Get Product Backlog (Unassigned Bugs)
@router.get("/backlog")
def get_backlog_issues(db: Session = Depends(get_db)):
    backlog = db.query(Issue).filter(
        (Issue.sprint_id == None) | (Issue.dev_stage.in_(["REPORTED", "TRIAGED"]))
    ).order_by(Issue.created_at.desc()).all()

    return [{
        "id": i.id,
        "issue_key": i.issue_key,
        "title": i.title,
        "severity": i.severity,
        "priority": i.priority,
        "priority_score": i.priority_score or 6.0,
        "dev_stage": i.dev_stage,
        "assignee": i.assignee.full_name if i.assignee else "Unassigned",
        "sprint_name": i.sprint.sprint_name if i.sprint else "Backlog",
        "created_at": i.created_at.strftime("%Y-%m-%d %H:%M")
    } for i in backlog]

# 6. Sprint Board Column Data
@router.get("/{sprint_id}/board")
def get_sprint_board(sprint_id: int, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    issues = db.query(Issue).filter(Issue.sprint_id == sprint_id).all()
    columns = {
        "REPORTED": [],
        "TRIAGED": [],
        "IN_PROGRESS": [],
        "QA_VERIFICATION": [],
        "RESOLVED": [],
        "CLOSED": []
    }
    for issue in issues:
        stage = (issue.dev_stage or "REPORTED").upper()
        if stage == "ASSIGNED":
            stage = "TRIAGED"
        elif stage == "CODE_REVIEW":
            stage = "IN_PROGRESS"
        elif stage == "QA_TESTING":
            stage = "QA_VERIFICATION"
            
        if stage in columns:
            columns[stage].append({
                "id": issue.id,
                "key": issue.issue_key,
                "title": issue.title,
                "severity": issue.severity,
                "priority": issue.priority,
                "priority_score": issue.priority_score or 6.0,
                "assignee": issue.assignee.full_name if issue.assignee else "Unassigned",
                "estimated_effort": issue.estimated_effort
            })

    return {
        "sprint_id": sprint.id,
        "sprint_name": sprint.sprint_name,
        "goal": sprint.goal,
        "columns": columns
    }
