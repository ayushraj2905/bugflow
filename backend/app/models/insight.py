from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from ..database import Base

class UserTriageInsight(Base):
    __tablename__ = 'user_triage_insights'

    id = Column(Integer, primary_key=True, index=True)
    dev_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bug_score = Column(Integer, default=85) # 1 to 100
    team_efficiency = Column(Float, default=92.5) # %
    backlog_progression = Column(String(100), default='On Track - 14 issues cleared this cycle')
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    developer = relationship('User', back_populates='triage_insights')

class HistoricalBugFix(Base):
    __tablename__ = 'historical_bug_fixes'

    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, ForeignKey('individual_bug_saga.id'), nullable=False)
    dev_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    past_fixes = Column(Text, nullable=True)
    code_changes = Column(Text, nullable=True) # Commit diff or reference
    resolution_time = Column(Float, default=2.5) # hours
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship('Issue', back_populates='historical_fix')
    developer = relationship('User', back_populates='historical_fixes')

class BugFlowUserPortal(Base):
    __tablename__ = 'bugflow_user_portals'

    id = Column(Integer, primary_key=True, index=True)
    portal_type = Column(String(50), nullable=False) # Web Dashboard, Developer API, Reporter Mobile App, CI/CD Console
    portal_name = Column(String(100), nullable=False)
    version = Column(String(20), default='v2.4.0')
    endpoint_url = Column(String(255), default='/api/v1')
    status = Column(String(20), default='ONLINE')
