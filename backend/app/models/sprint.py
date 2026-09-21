from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from ..database import Base

class Sprint(Base):
    __tablename__ = 'sprints'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    sprint_name = Column(String(100), nullable=False)
    goal = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    planned_velocity = Column(Integer, default=30)
    status = Column(String(20), default='ACTIVE') # PLANNING, ACTIVE, COMPLETED
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship('Project', back_populates='sprints')
    issues = relationship('Issue', back_populates='sprint')
