from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from ..database import Base

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), nullable=False)
    key = Column(String(10), unique=True, nullable=False)
    codebase = Column(String(255), nullable=False) # e.g. github.com/org/repo
    development_cycle = Column(String(50), default='Agile Scrum')
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    issues = relationship('Issue', back_populates='project', cascade='all, delete-orphan')
    sprints = relationship('Sprint', back_populates='project', cascade='all, delete-orphan')

class BugCategory(Base):
    __tablename__ = 'bug_categories'

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False)
    urgency_enum = Column(String(20), default='Medium') # High, Medium, Low, Critical
    description = Column(Text, nullable=True)

    issues = relationship('Issue', back_populates='category')
