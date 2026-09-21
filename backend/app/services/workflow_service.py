from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.issue import Issue, AuditLog

class WorkflowService:
    # Supported stages
    VALID_STAGES = [
        'REPORTED',
        'TRIAGED',
        'ASSIGNED',
        'IN_PROGRESS',
        'CODE_REVIEW',
        'QA_VERIFICATION',
        'QA_TESTING',
        'RESOLVED',
        'CLOSED'
    ]

    @classmethod
    def transition_stage(cls, db: Session, issue: Issue, target_stage: str, user_id: int, note: str = '') -> Issue:
        target_stage = target_stage.upper()
        current_stage = (issue.dev_stage or 'REPORTED').upper()

        if target_stage not in cls.VALID_STAGES:
            raise HTTPException(status_code=400, detail=f'Invalid stage: {target_stage}. Valid stages: {cls.VALID_STAGES}')

        if target_stage == current_stage:
            return issue

        # Perform transition
        issue.dev_stage = target_stage
        issue.updated_at = datetime.utcnow()
        if target_stage in ['CLOSED', 'RESOLVED']:
            issue.closed_at = datetime.utcnow()
        else:
            issue.closed_at = None

        # Record in AuditLog
        audit_detail = f'Status changed from {current_stage} to {target_stage}'
        if note:
            audit_detail += f'. Note: {note}'

        audit = AuditLog(
            bug_id=issue.id,
            user_id=user_id,
            action='STATUS_CHANGED',
            previous_state=current_stage,
            new_state=target_stage,
            details=audit_detail
        )
        db.add(audit)
        db.commit()
        db.refresh(issue)
        return issue

    @classmethod
    def log_action(cls, db: Session, issue_id: int, user_id: int, action: str, prev_state: str, new_state: str, details: str):
        audit = AuditLog(
            bug_id=issue_id,
            user_id=user_id,
            action=action,
            previous_state=prev_state,
            new_state=new_state,
            details=details
        )
        db.add(audit)
        db.commit()
