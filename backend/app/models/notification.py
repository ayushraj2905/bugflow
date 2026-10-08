import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..database import Base

class NotificationTypeEnum(str, enum.Enum):
    ISSUE_CREATED = 'ISSUE_CREATED'
    ISSUE_ASSIGNED = 'ISSUE_ASSIGNED'
    WORKFLOW_CHANGED = 'WORKFLOW_CHANGED'
    COMMENT_ADDED = 'COMMENT_ADDED'
    ISSUE_RESOLVED = 'ISSUE_RESOLVED'
    ISSUE_CLOSED = 'ISSUE_CLOSED'
    SPRINT_EVENT = 'SPRINT_EVENT'
    SYSTEM = 'SYSTEM'

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    issue_id = Column(Integer, ForeignKey('individual_bug_saga.id'), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True, index=True)
    
    notification_type = Column(String(50), default='SYSTEM', index=True, nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    # Composite Index for fast user unread queries
    __table_args__ = (
        Index('idx_user_read_created', 'user_id', 'is_read', 'created_at'),
    )

    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='notifications')
    issue = relationship('Issue', foreign_keys=[issue_id], backref='notifications')
    project = relationship('Project', foreign_keys=[project_id], backref='notifications')
