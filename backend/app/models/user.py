import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from ..database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = 'ADMIN'
    PROJECT_MANAGER = 'PROJECT_MANAGER'
    DEVELOPER = 'DEVELOPER'
    QA_TESTER = 'QA_TESTER'
    REPORTER = 'REPORTER'

class ProficiencyEnum(str, enum.Enum):
    JUNIOR = 'Junior'
    MID = 'Mid'
    SENIOR = 'Senior'
    LEAD = 'Lead'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default='DEVELOPER', nullable=False)
    team = Column(String(50), default='Core Team')
    core_skills = Column(String(255), default='Python, SQL, REST APIs')
    proficiency = Column(String(20), default='Mid')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assigned_issues = relationship('Issue', back_populates='assignee', foreign_keys='Issue.assignee_id')
    reported_issues = relationship('Issue', back_populates='reporter', foreign_keys='Issue.reporter_id')
    comments = relationship('Comment', back_populates='author')
    triage_insights = relationship('UserTriageInsight', back_populates='developer')
    historical_fixes = relationship('HistoricalBugFix', back_populates='developer')
