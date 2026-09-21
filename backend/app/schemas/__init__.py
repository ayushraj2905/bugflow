from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str = 'DEVELOPER'
    team: str = 'Core Team'
    core_skills: str = 'Python, REST APIs'
    proficiency: str = 'Mid'

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

# Issue Schemas
class IssueCreate(BaseModel):
    project_id: int
    title: str
    description: str
    reproduction_steps: Optional[str] = None
    category_id: Optional[int] = None
    affected_module: Optional[str] = 'Core Module'
    environment_info: Optional[str] = 'Production - Linux x86_64'
    severity: Optional[str] = 'MINOR'
    priority: Optional[str] = 'P3'
    estimated_effort: Optional[float] = 4.0
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reproduction_steps: Optional[str] = None
    category_id: Optional[int] = None
    affected_module: Optional[str] = None
    environment_info: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    dev_stage: Optional[str] = None
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None
    estimated_effort: Optional[float] = None
    actual_effort: Optional[float] = None
    resolution_summary: Optional[str] = None

class CommentCreate(BaseModel):
    content: str
    code_reference: Optional[str] = None

class TransitionRequest(BaseModel):
    target_stage: str
    note: Optional[str] = ''

class DuplicateCheckRequest(BaseModel):
    title: str
    description: str

# Sprint Schemas
class SprintCreate(BaseModel):
    project_id: int
    sprint_name: str
    goal: Optional[str] = None
    start_date: date
    end_date: date
    planned_velocity: int = 30

# Webhook Schemas
class GitHubWebhookPayload(BaseModel):
    ref: Optional[str] = 'refs/heads/main'
    repository: Optional[dict] = {}
    commits: Optional[List[dict]] = []

class CICDWebhookPayload(BaseModel):
    pipeline_id: str
    project_key: str
    status: str # FAILED, SUCCESS
    error_log: str
    failed_stage: str
    branch: str
