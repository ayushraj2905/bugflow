import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Index
from sqlalchemy.orm import relationship
from ..database import Base

class DevStageEnum(str, enum.Enum):
    REPORTED = 'REPORTED'
    TRIAGED = 'TRIAGED'
    ASSIGNED = 'ASSIGNED'
    IN_PROGRESS = 'IN_PROGRESS'
    CODE_REVIEW = 'CODE_REVIEW'
    QA_VERIFICATION = 'QA_VERIFICATION'
    QA_TESTING = 'QA_TESTING'
    RESOLVED = 'RESOLVED'
    CLOSED = 'CLOSED'

class SeverityEnum(str, enum.Enum):
    CRITICAL = 'CRITICAL'
    MAJOR = 'MAJOR'
    MINOR = 'MINOR'
    TRIVIAL = 'TRIVIAL'
    LOW = 'LOW'

class PriorityEnum(str, enum.Enum):
    URGENT = 'URGENT'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'

class Issue(Base):
    __tablename__ = 'individual_bug_saga'

    id = Column(Integer, primary_key=True, index=True)
    issue_key = Column(String(20), unique=True, index=True, nullable=False) # e.g. BF-101
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('bug_categories.id'), nullable=True, index=True)
    
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    reproduction_steps = Column(Text, nullable=True)
    environment_info = Column(String(255), default='Production - Linux x86_64')
    affected_module = Column(String(100), default='Backend API')
    
    severity = Column(String(20), default='MINOR', index=True)
    priority = Column(String(20), default='MEDIUM', index=True)
    priority_score = Column(Float, default=6.0) # Calculated: Severity_Weight * Urgency_Weight
    dev_stage = Column(String(30), default='REPORTED', index=True)
    
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    assignee_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    sprint_id = Column(Integer, ForeignKey('sprints.id'), nullable=True, index=True)
    
    estimated_effort = Column(Float, default=4.0) # hours
    actual_effort = Column(Float, default=0.0) # hours
    duplicate_of_id = Column(Integer, ForeignKey('individual_bug_saga.id'), nullable=True)
    resolution_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Composite Performance Indexes for High Scale (50,000+ records)
    __table_args__ = (
        Index('idx_project_stage', 'project_id', 'dev_stage'),
        Index('idx_assignee_stage', 'assignee_id', 'dev_stage'),
        Index('idx_severity_priority', 'severity', 'priority'),
    )

    # Relationships
    project = relationship('Project', back_populates='issues')
    category = relationship('BugCategory', back_populates='issues')
    reporter = relationship('User', foreign_keys=[reporter_id], back_populates='reported_issues')
    assignee = relationship('User', foreign_keys=[assignee_id], back_populates='assigned_issues')
    sprint = relationship('Sprint', back_populates='issues')
    
    comments = relationship('Comment', back_populates='issue', cascade='all, delete-orphan')
    attachments = relationship('Attachment', back_populates='issue', cascade='all, delete-orphan')
    audit_logs = relationship('AuditLog', back_populates='issue', cascade='all, delete-orphan')
    assignments = relationship('IssueAssignment', back_populates='issue', cascade='all, delete-orphan')
    reporter_tracking = relationship('ReporterIssueTracking', back_populates='issue', cascade='all, delete-orphan')
    historical_fix = relationship('HistoricalBugFix', back_populates='issue', uselist=False)

class Attachment(Base):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, ForeignKey('individual_bug_saga.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), default='application/octet-stream')
    file_size = Column(Integer, default=0) # in bytes
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship('Issue', back_populates='attachments')
    uploader = relationship('User')

class IssueAssignment(Base):
    __tablename__ = 'issue_assignments'

    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, ForeignKey('individual_bug_saga.id'), nullable=False, index=True)
    dev_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    estimated_effort = Column(Float, default=4.0)
    priority = Column(String(20), default='Medium')
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), default='ACTIVE')

    issue = relationship('Issue', back_populates='assignments')
    developer = relationship('User')

class ReporterIssueTracking(Base):
    __tablename__ = 'reporter_issue_tracking'

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    bug_id = Column(Integer, ForeignKey('individual_bug_saga.id'), nullable=False, index=True)
    related_case = Column(String(100), nullable=True)
    expected_resolution = Column(DateTime, nullable=True)
    progress = Column(Integer, default=0) # 0 to 100%

    issue = relationship('Issue', back_populates='reporter_tracking')
    reporter = relationship('User')

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, ForeignKey('individual_bug_saga.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    code_reference = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship('Issue', back_populates='comments')
    author = relationship('User', back_populates='comments')

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, ForeignKey('individual_bug_saga.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String(50), nullable=False) # e.g. STATUS_CHANGE, ASSIGNMENT, PRIORITY_UPDATE
    previous_state = Column(String(100), nullable=True)
    new_state = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    issue = relationship('Issue', back_populates='audit_logs')
    user = relationship('User')
