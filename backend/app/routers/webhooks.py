import re
import uuid
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models.issue import Issue, AuditLog
from ..models.project import Project
from ..services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/v1/webhooks", tags=["CI/CD & Git Webhooks"])

class GitCommitPayload(BaseModel):
    message: str
    commit_id: Optional[str] = None
    author: Optional[str] = "GitHub Action / Developer"
    branch: Optional[str] = "main"

# 1. Git Commit Webhook Route (Part 1 Requirement)
@router.post("/git")
@router.post("/github")
async def process_git_webhook(req: Request, db: Session = Depends(get_db)):
    body = await req.json()
    
    # Handle direct message or GitHub push payload structure
    commit_messages = []
    commit_id = "commit-" + uuid.uuid4().hex[:7]
    author = "Git Webhook Bot"

    if "message" in body:
        commit_messages.append(body["message"])
        commit_id = body.get("commit_id") or commit_id
        author = body.get("author") or author
    elif "commits" in body and isinstance(body["commits"], list):
        for c in body["commits"]:
            if "message" in c:
                commit_messages.append(c["message"])
            if "id" in c:
                commit_id = c["id"][:8]
            if "author" in c and "name" in c["author"]:
                author = c["author"]["name"]
    else:
        # Fallback string representation
        commit_messages.append(str(body))

    updated_issues = []

    # Regex search: "fixes #2", "closes #5", "resolves #8", "fixes #BF-001", "fixes 2"
    pattern = r'(?:fix|fixes|close|closes|resolve|resolves)\s+#?([A-Za-z0-9_-]+)'

    for msg in commit_messages:
        matches = re.findall(pattern, msg, re.IGNORECASE)
        for target_key in matches:
            issue = None
            # Check if target is a numeric ID (e.g. "2")
            if target_key.isdigit():
                issue = db.query(Issue).filter(Issue.id == int(target_key)).first()
            
            # If not found or alphanumeric, check by issue_key (e.g. "BF-002", "B-002", "BF-004")
            if not issue:
                issue = db.query(Issue).filter(
                    or_(
                        Issue.issue_key.ilike(target_key),
                        Issue.issue_key.ilike(f"%{target_key}%")
                    )
                ).first()

            if issue:
                old_stage = issue.dev_stage
                target_stage = "QA_VERIFICATION"
                
                # Auto-transition status to QA_VERIFICATION
                issue.dev_stage = target_stage
                
                # Record Audit Log
                audit_note = f"Auto-transitioned by Git commit #{commit_id}: \"{msg[:60]}\""
                WorkflowService.log_action(
                    db,
                    issue.id,
                    1, # System / Lead Admin ID
                    "GIT_WEBHOOK_AUTO_TRANSITION",
                    old_stage,
                    target_stage,
                    audit_note
                )
                db.commit()
                db.refresh(issue)

                updated_issues.append({
                    "issue_id": issue.id,
                    "issue_key": issue.issue_key,
                    "title": issue.title,
                    "previous_stage": old_stage,
                    "new_stage": issue.dev_stage,
                    "commit_id": commit_id,
                    "message": msg
                })

    return {
        "status": "success",
        "processed_commits_count": len(commit_messages),
        "updated_issues_count": len(updated_issues),
        "updated_issues": updated_issues,
        "message": f"Successfully processed Git Webhook. {len(updated_issues)} issue(s) transitioned to QA_VERIFICATION."
    }

# 2. CI/CD Build Pipeline Failure Webhook
@router.post("/cicd")
async def cicd_webhook(req: Request, db: Session = Depends(get_db)):
    body = await req.json()
    pipeline_name = body.get("pipeline_name", "GitHub Actions CI")
    status = body.get("status", "FAILED")
    logs = body.get("error_logs", "Pipeline failure at test step")

    if status.upper() in ["FAILED", "ERROR"]:
        # Auto-create bug report for CI/CD failure
        from .issues import generate_next_issue_key
        project = db.query(Project).first()
        issue_key = generate_next_issue_key(db, project) if project else "BF-999"

        new_issue = Issue(
            issue_key=issue_key,
            project_id=project.id if project else 1,
            title=f"CI/CD Failure in {pipeline_name}",
            description=f"Automated pipeline failure report:\n{logs}",
            affected_module="CI/CD Runner",
            severity="MAJOR",
            priority="HIGH",
            priority_score=9.0,
            dev_stage="REPORTED",
            reporter_id=1,
            estimated_effort=4.0
        )
        db.add(new_issue)
        db.commit()
        return {"status": "created", "issue_key": new_issue.issue_key}

    return {"status": "ignored", "message": "Pipeline status is healthy"}
