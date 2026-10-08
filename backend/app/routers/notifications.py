from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.notification import Notification, NotificationTypeEnum
from ..models.user import User
from ..schemas import NotificationResponse, NotificationUnreadCount
from ..services.auth_service import get_current_user
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["Notification Center"])

# 1. Get User Notifications with Optional Filtering
@router.get("/")
def get_user_notifications(
    filter_type: Optional[str] = Query("all", description="Filter by type: all, unread, issues, assignments, workflow, comments, sprints, system"),
    is_read: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 1
    
    # Auto-seed initial notifications for this user if empty
    NotificationService.seed_default_notifications_if_empty(db, user_id)

    query = db.query(Notification).filter(Notification.user_id == user_id)


    # Apply Filter Type
    f = (filter_type or "all").lower()
    if f == "unread":
        query = query.filter(Notification.is_read == False)
    elif f in ["issues", "issue"]:
        query = query.filter(Notification.notification_type.in_([
            NotificationTypeEnum.ISSUE_CREATED.value,
            NotificationTypeEnum.ISSUE_RESOLVED.value,
            NotificationTypeEnum.ISSUE_CLOSED.value
        ]))
    elif f in ["assignments", "assignment"]:
        query = query.filter(Notification.notification_type == NotificationTypeEnum.ISSUE_ASSIGNED.value)
    elif f in ["workflow", "workflows"]:
        query = query.filter(Notification.notification_type == NotificationTypeEnum.WORKFLOW_CHANGED.value)
    elif f in ["comments", "comment"]:
        query = query.filter(Notification.notification_type == NotificationTypeEnum.COMMENT_ADDED.value)
    elif f in ["sprints", "sprint"]:
        query = query.filter(Notification.notification_type == NotificationTypeEnum.SPRINT_EVENT.value)
    elif f in ["system", "alerts"]:
        query = query.filter(Notification.notification_type == NotificationTypeEnum.SYSTEM.value)

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    total_count = query.count()
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for n in notifications:
        results.append({
            "id": n.id,
            "user_id": n.user_id,
            "issue_id": n.issue_id,
            "issue_key": n.issue.issue_key if n.issue else None,
            "issue_title": n.issue.title if n.issue else None,
            "project_id": n.project_id,
            "project_name": n.project.project_name if n.project else (n.issue.project.project_name if (n.issue and n.issue.project) else "BugFlow Core"),
            "notification_type": n.notification_type,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
            "created_at_iso": n.created_at.isoformat()
        })

    return {
        "total": total_count,
        "filter": f,
        "notifications": results
    }

# 2. Get Unread Count for Navbar Bell Badge
@router.get("/unread-count", response_model=NotificationUnreadCount)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 1
    NotificationService.seed_default_notifications_if_empty(db, user_id)
    
    count = db.query(Notification).filter(

        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()
    return {"unread_count": count}

# 3. Mark Single Notification as Read
@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 1
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return {
        "message": "Notification marked as read",
        "id": notif.id,
        "is_read": True
    }

# 4. Mark All Notifications as Read for Active User
@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 1
    unreads = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).all()

    for n in unreads:
        n.is_read = True
    db.commit()

    return {
        "message": "All notifications marked as read",
        "marked_count": len(unreads)
    }

# 5. Delete Notification
@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 1
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notif)
    db.commit()
    return {
        "message": "Notification deleted successfully",
        "id": notification_id
    }
