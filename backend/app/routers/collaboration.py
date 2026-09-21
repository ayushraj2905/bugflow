import os
import shutil
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.issue import Issue, Comment, Attachment, AuditLog
from ..models.user import User
from ..schemas import CommentCreate
from ..services.auth_service import get_current_user
from ..services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/v1/collaboration", tags=["Collaboration, Comments & Attachments"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. Post Comment
@router.post("/issues/{issue_id}/comments")
def post_comment(
    issue_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 1
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    new_comment = Comment(
        bug_id=issue.id,
        user_id=user_id,
        content=data.content,
        code_reference=data.code_reference
    )
    db.add(new_comment)
    
    # Audit log
    author_name = current_user.full_name if current_user else "User"
    WorkflowService.log_action(
        db, issue.id, user_id, "COMMENT_ADDED", None, None,
        f"{author_name} commented: \"{data.content[:50]}\""
    )
    db.commit()
    db.refresh(new_comment)

    return {
        "message": "Comment posted successfully",
        "comment": {
            "id": new_comment.id,
            "user_name": new_comment.author.full_name if new_comment.author else "Team Member",
            "content": new_comment.content,
            "code_reference": new_comment.code_reference,
            "created_at": new_comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

# 2. Get Comments
@router.get("/issues/{issue_id}/comments")
def get_comments(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    comments = db.query(Comment).filter(Comment.bug_id == issue.id).order_by(Comment.created_at.asc()).all()
    return [{
        "id": c.id,
        "user_id": c.user_id,
        "user_name": c.author.full_name if c.author else "Team Member",
        "content": c.content,
        "code_reference": c.code_reference,
        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for c in comments]

# 3. Upload File Attachment
@router.post("/issues/{issue_id}/attachments")
async def upload_attachment(
    issue_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 1
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Generate unique filename on disk
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex[:10]}_{file.filename}"
    saved_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save to disk
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(saved_path)
    file_url = f"/uploads/{unique_filename}"

    attachment = Attachment(
        bug_id=issue.id,
        filename=file.filename,
        file_path=file_url,
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        uploaded_by=user_id,
        uploaded_at=datetime.utcnow()
    )
    db.add(attachment)

    # Audit log
    author_name = current_user.full_name if current_user else "User"
    WorkflowService.log_action(
        db, issue.id, user_id, "ATTACHMENT_UPLOADED", None, file.filename,
        f"{author_name} uploaded file: {file.filename} ({round(file_size/1024, 1)} KB)"
    )
    db.commit()
    db.refresh(attachment)

    return {
        "message": "File uploaded successfully",
        "attachment": {
            "id": attachment.id,
            "filename": attachment.filename,
            "file_url": attachment.file_path,
            "file_type": attachment.file_type,
            "file_size": attachment.file_size,
            "uploaded_by": author_name,
            "uploaded_at": attachment.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

# 4. Get Attachments
@router.get("/issues/{issue_id}/attachments")
def get_attachments(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    attachments = db.query(Attachment).filter(Attachment.bug_id == issue.id).order_by(Attachment.uploaded_at.desc()).all()
    return [{
        "id": a.id,
        "filename": a.filename,
        "file_url": a.file_path,
        "file_type": a.file_type,
        "file_size": a.file_size,
        "uploaded_by": a.uploader.full_name if a.uploader else "User",
        "uploaded_at": a.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")
    } for a in attachments]
