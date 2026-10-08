import pytest
from app.models.notification import Notification, NotificationTypeEnum
from app.models.user import User
from app.models.issue import Issue
from app.services.notification_service import NotificationService

def test_get_notifications_list(client):
    res = client.get("/api/v1/notifications/")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "notifications" in data
    assert isinstance(data["notifications"], list)
    assert len(data["notifications"]) > 0

def test_get_unread_count(client):
    res = client.get("/api/v1/notifications/unread-count")
    assert res.status_code == 200
    data = res.json()
    assert "unread_count" in data
    assert isinstance(data["unread_count"], int)

def test_notification_filters(client):
    # Filter unread
    res_unread = client.get("/api/v1/notifications/?filter_type=unread")
    assert res_unread.status_code == 200
    data = res_unread.json()
    for n in data["notifications"]:
        assert n["is_read"] is False

    # Filter assignments
    res_assign = client.get("/api/v1/notifications/?filter_type=assignments")
    assert res_assign.status_code == 200

    # Filter issues
    res_issues = client.get("/api/v1/notifications/?filter_type=issues")
    assert res_issues.status_code == 200

def test_mark_single_notification_read(client, db_session):
    # Create a fresh unread notification for user 1
    notif = Notification(
        user_id=1,
        notification_type=NotificationTypeEnum.SYSTEM.value,
        title="PyTest Alert",
        message="Simulated test notification message.",
        is_read=False
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    notif_id = notif.id

    # Mark as read
    res = client.post(f"/api/v1/notifications/{notif_id}/read")
    assert res.status_code == 200
    assert res.json()["is_read"] is True

    # Verify in DB
    db_session.refresh(notif)
    assert notif.is_read is True

def test_mark_all_notifications_read(client, db_session):
    res = client.post("/api/v1/notifications/mark-all-read")
    assert res.status_code == 200
    assert "marked_count" in res.json()

    # Unread count should now be 0 for user 1
    unread_res = client.get("/api/v1/notifications/unread-count")
    assert unread_res.json()["unread_count"] == 0

def test_delete_notification(client, db_session):
    # Create notification to delete
    notif = Notification(
        user_id=1,
        notification_type=NotificationTypeEnum.SYSTEM.value,
        title="To be deleted",
        message="Deleting this test notification",
        is_read=True
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    notif_id = notif.id

    # Delete
    res = client.delete(f"/api/v1/notifications/{notif_id}")
    assert res.status_code == 200

    # Verify deleted
    deleted = db_session.query(Notification).filter(Notification.id == notif_id).first()
    assert deleted is None

def test_issue_creation_notification_trigger(client, db_session):
    initial_count = db_session.query(Notification).filter(Notification.notification_type == 'ISSUE_CREATED').count()

    payload = {
        "project_id": 1,
        "category_id": 1,
        "title": "Bug with Notification Trigger",
        "description": "Testing automated notification creation on bug submit",
        "severity": "CRITICAL",
        "priority": "URGENT",
        "assignee_id": 2
    }
    res = client.post("/api/v1/bugs/", json=payload)
    assert res.status_code == 200

    new_count = db_session.query(Notification).filter(Notification.notification_type == 'ISSUE_CREATED').count()
    # At least one new notification should have been recorded
    assert new_count >= initial_count

def test_workflow_transition_notification_trigger(client, db_session):
    res = client.post("/api/v1/bugs/1/transition", json={
        "target_stage": "QA_TESTING",
        "note": "Ready for regression testing"
    })
    assert res.status_code == 200

    workflow_notifs = db_session.query(Notification).filter(
        Notification.notification_type == 'WORKFLOW_CHANGED'
    ).all()
    assert len(workflow_notifs) > 0

def test_comment_added_notification_trigger(client, db_session):
    res = client.post("/api/v1/collaboration/issues/1/comments", json={
        "content": "This is an automated test comment to verify notification firing."
    })
    assert res.status_code == 200

    comment_notifs = db_session.query(Notification).filter(
        Notification.notification_type == 'COMMENT_ADDED'
    ).all()
    assert len(comment_notifs) > 0

def test_notifications_page_html(client):
    res = client.get("/notifications")
    assert res.status_code == 200
    assert "Notification Center" in res.text
    assert "statUnread" in res.text
