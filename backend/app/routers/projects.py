from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.project import Project, BugCategory
from ..models.insight import BugFlowUserPortal

router = APIRouter(prefix="/api/v1/projects", tags=["Projects & Portals"])

@router.get("/")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [{
        "id": p.id,
        "project_name": p.project_name,
        "key": p.key,
        "codebase": p.codebase,
        "development_cycle": p.development_cycle,
        "description": p.description,
        "issues_count": len(p.issues)
    } for p in projects]

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = db.query(BugCategory).all()
    return [{
        "id": c.id,
        "name": c.category_name,
        "urgency": c.urgency_enum,
        "description": c.description
    } for c in cats]

@router.get("/portals")
def get_portals(db: Session = Depends(get_db)):
    portals = db.query(BugFlowUserPortal).all()
    return [{
        "id": p.id,
        "portal_type": p.portal_type,
        "portal_name": p.portal_name,
        "version": p.version,
        "endpoint_url": p.endpoint_url,
        "status": p.status
    } for p in portals]
