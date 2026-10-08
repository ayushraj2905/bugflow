from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.notification import Notification, NotificationTypeEnum
from ..models.user import User
from ..models.issue import Issue, Comment
from ..models.sprint import Sprint
from ..models.project import Project

class NotificationService:

    @classmethod
    def create_notification(
        cls,
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = NotificationTypeEnum.SYSTEM.value,
        issue_id: Optional[int] = None,
        project_id: Optional[int] = None
    ) -> Notification:
        """Create and persist a single user notification."""
        notif = Notification(
            user_id=user_id,
            issue_id=issue_id,
            project_id=project_id,
            notification_type=notification_type,
            title=title,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @classmethod
    def notify_issue_created(cls, db: Session, issue: Issue, actor: Optional[User] = None):
        """Notify Admin & Project Manager users when an issue is created."""
        actor_id = actor.id if actor else None
        recipients = db.query(User).filter(
            User.role.in_(["ADMIN", "PROJECT_MANAGER"]),
            User.is_active == True
        ).all()

        for user in recipients:
            if actor_id and user.id == actor_id:
                continue
            cls.create_notification(
                db=db,
                user_id=user.id,
                title=f"New issue {issue.issue_key} reported",
                message=f"New issue {issue.issue_key} ('{issue.title}') has been reported under {issue.affected_module} with Severity {issue.severity} and Priority {issue.priority}.",
                notification_type=NotificationTypeEnum.ISSUE_CREATED.value,
                issue_id=issue.id,
                project_id=issue.project_id
            )

    @classmethod
    def notify_issue_assigned(cls, db: Session, issue: Issue, assignee_id: int, actor: Optional[User] = None):
        """Notify assigned developer."""
        actor_id = actor.id if actor else None
        if assignee_id and assignee_id != actor_id:
            assignee = db.query(User).filter(User.id == assignee_id).first()
            if assignee:
                cls.create_notification(
                    db=db,
                    user_id=assignee.id,
                    title=f"Issue {issue.issue_key} has been assigned to you",
                    message=f"You have been assigned to {issue.issue_key}: '{issue.title}' (Priority: {issue.priority}, Stage: {issue.dev_stage}).",
                    notification_type=NotificationTypeEnum.ISSUE_ASSIGNED.value,
                    issue_id=issue.id,
                    project_id=issue.project_id
                )

    @classmethod
    def notify_workflow_transition(
        cls,
        db: Session,
        issue: Issue,
        old_stage: str,
        new_stage: str,
        actor: Optional[User] = None
    ):
        """Notify reporter and assignee about workflow status changes."""
        actor_id = actor.id if actor else None
        recipient_ids = set()

        if issue.reporter_id and issue.reporter_id != actor_id:
            recipient_ids.add(issue.reporter_id)
        if issue.assignee_id and issue.assignee_id != actor_id:
            recipient_ids.add(issue.assignee_id)

        # Also notify Admin lead
        admin_users = db.query(User.id).filter(User.role == "ADMIN", User.is_active == True).all()
        for (a_id,) in admin_users:
            if a_id != actor_id:
                recipient_ids.add(a_id)

        # Determine notification type & wording
        if new_stage.upper() == "RESOLVED":
            notif_type = NotificationTypeEnum.ISSUE_RESOLVED.value
            title = f"Issue {issue.issue_key} resolved"
            message = f"Issue {issue.issue_key} ('{issue.title}') has been marked as RESOLVED and is ready for verification."
        elif new_stage.upper() == "CLOSED":
            notif_type = NotificationTypeEnum.ISSUE_CLOSED.value
            title = f"Issue {issue.issue_key} closed"
            message = f"Issue {issue.issue_key} ('{issue.title}') has been successfully verified and CLOSED."
        else:
            notif_type = NotificationTypeEnum.WORKFLOW_CHANGED.value
            title = f"Workflow status updated for {issue.issue_key}"
            message = f"{issue.issue_key} status changed from {old_stage} to {new_stage}."

        for uid in recipient_ids:
            cls.create_notification(
                db=db,
                user_id=uid,
                title=title,
                message=message,
                notification_type=notif_type,
                issue_id=issue.id,
                project_id=issue.project_id
            )

    @classmethod
    def notify_comment_added(cls, db: Session, issue: Issue, comment: Comment, author: Optional[User] = None):
        """Notify reporter and assignee when a comment is posted."""
        author_id = author.id if author else None
        author_name = author.full_name if author else "A team member"
        recipient_ids = set()

        if issue.reporter_id and issue.reporter_id != author_id:
            recipient_ids.add(issue.reporter_id)
        if issue.assignee_id and issue.assignee_id != author_id:
            recipient_ids.add(issue.assignee_id)

        for uid in recipient_ids:
            cls.create_notification(
                db=db,
                user_id=uid,
                title=f"New comment on {issue.issue_key}",
                message=f"{author_name} commented on {issue.issue_key}: \"{comment.content[:80]}\"",
                notification_type=NotificationTypeEnum.COMMENT_ADDED.value,
                issue_id=issue.id,
                project_id=issue.project_id
            )

    @classmethod
    def notify_sprint_event(
        cls,
        db: Session,
        sprint: Sprint,
        title: str,
        message: str,
        event_type: str = NotificationTypeEnum.SPRINT_EVENT.value,
        issue: Optional[Issue] = None
    ):
        """Notify project members / active devs about sprint events."""
        users = db.query(User).filter(User.is_active == True).all()
        for u in users:
            cls.create_notification(
                db=db,
                user_id=u.id,
                title=title,
                message=message,
                notification_type=event_type,
                issue_id=issue.id if issue else None,
                project_id=sprint.project_id if sprint else None
            )

    @classmethod
    def notify_git_webhook_transition(
        cls,
        db: Session,
        issue: Issue,
        commit_id: str,
        commit_msg: str
    ):
        """Notify assignee and reporter upon CI/CD git auto-transition."""
        recipient_ids = set()
        if issue.reporter_id:
            recipient_ids.add(issue.reporter_id)
        if issue.assignee_id:
            recipient_ids.add(issue.assignee_id)

        # Also notify Admin
        admins = db.query(User.id).filter(User.role == "ADMIN").all()
        for (a_id,) in admins:
            recipient_ids.add(a_id)

        for uid in recipient_ids:
            cls.create_notification(
                db=db,
                user_id=uid,
                title=f"CI/CD Git Commit: {issue.issue_key} advanced",
                message=f"{issue.issue_key} automatically advanced to QA_VERIFICATION via commit #{commit_id[:7]}: \"{commit_msg[:60]}\"",
                notification_type=NotificationTypeEnum.WORKFLOW_CHANGED.value,
                issue_id=issue.id,
                project_id=issue.project_id
            )

    @classmethod
    def seed_default_notifications_if_empty(cls, db: Session, target_user_id: Optional[int] = None):
        """Seed realistic notifications per user if empty."""
        users = {u.username: u for u in db.query(User).all()}
        admin = users.get("admin")
        jdoe = users.get("jdoe")
        asmith = users.get("asmith")
        sconnor = users.get("sconnor")
        dkim = users.get("dkim")
        ppatel = users.get("ppatel")

        issues = {i.issue_key: i for i in db.query(Issue).all()}
        bf1 = issues.get("BF-001") or db.query(Issue).first()
        bf2 = issues.get("BF-002") or db.query(Issue).first()
        bf3 = issues.get("BF-003") or db.query(Issue).first()
        bf4 = issues.get("BF-004") or db.query(Issue).first()

        now = datetime.utcnow()
        seed_data = []

        # Admin notifications
        if admin and (target_user_id is None or target_user_id == admin.id):
            if db.query(Notification).filter(Notification.user_id == admin.id).count() == 0:
                seed_data.extend([
                    Notification(
                        user_id=admin.id,
                        issue_id=bf1.id if bf1 else None,
                        project_id=bf1.project_id if bf1 else 1,
                        notification_type=NotificationTypeEnum.ISSUE_CREATED.value,
                        title=f"New issue {bf1.issue_key if bf1 else 'BF-001'} reported",
                        message=f"New issue {bf1.issue_key if bf1 else 'BF-001'} ('{bf1.title if bf1 else 'Payment Gateway Timeout'}') reported by QA team with severity CRITICAL.",
                        is_read=False,
                        created_at=now - timedelta(minutes=15)
                    ),
                    Notification(
                        user_id=admin.id,
                        issue_id=bf4.id if bf4 else None,
                        project_id=bf4.project_id if bf4 else 1,
                        notification_type=NotificationTypeEnum.ISSUE_RESOLVED.value,
                        title=f"Issue {bf4.issue_key if bf4 else 'BF-004'} resolved",
                        message=f"Issue {bf4.issue_key if bf4 else 'BF-004'} ('Database connection pool exhaustion') was marked as RESOLVED by J.Doe.",
                        is_read=True,
                        created_at=now - timedelta(hours=2)
                    ),
                    Notification(
                        user_id=admin.id,
                        issue_id=None,
                        project_id=1,
                        notification_type=NotificationTypeEnum.SPRINT_EVENT.value,
                        title="Sprint Sprint-01 status update",
                        message="Sprint Sprint-01 has reached 85% completion velocity with 8 defects closed.",
                        is_read=False,
                        created_at=now - timedelta(hours=5)
                    ),
                    Notification(
                        user_id=admin.id,
                        issue_id=None,
                        project_id=1,
                        notification_type=NotificationTypeEnum.SYSTEM.value,
                        title="System Health & Scale Alert",
                        message="High-performance connection pool initialized (125 active capacity, avg response 145ms).",
                        is_read=True,
                        created_at=now - timedelta(days=1)
                    )
                ])

        # J.Doe notifications (Backend Dev)
        if jdoe and (target_user_id is None or target_user_id == jdoe.id):
            if db.query(Notification).filter(Notification.user_id == jdoe.id).count() == 0:
                seed_data.extend([
                    Notification(
                        user_id=jdoe.id,
                        issue_id=bf1.id if bf1 else None,
                        project_id=bf1.project_id if bf1 else 1,
                        notification_type=NotificationTypeEnum.ISSUE_ASSIGNED.value,
                        title=f"Issue {bf1.issue_key if bf1 else 'BF-001'} assigned to you",
                        message=f"You have been assigned to {bf1.issue_key if bf1 else 'BF-001'}: '{bf1.title if bf1 else 'Payment Gateway Timeout'}'.",
                        is_read=False,
                        created_at=now - timedelta(minutes=25)
                    ),
                    Notification(
                        user_id=jdoe.id,
                        issue_id=bf2.id if bf2 else None,
                        project_id=bf2.project_id if bf2 else 1,
                        notification_type=NotificationTypeEnum.COMMENT_ADDED.value,
                        title=f"New comment on {bf2.issue_key if bf2 else 'BF-002'}",
                        message=f"A.Smith commented on {bf2.issue_key if bf2 else 'BF-002'}: \"Verified on staging environment build #420.\"",
                        is_read=False,
                        created_at=now - timedelta(minutes=50)
                    ),
                    Notification(
                        user_id=jdoe.id,
                        issue_id=bf1.id if bf1 else None,
                        project_id=bf1.project_id if bf1 else 1,
                        notification_type=NotificationTypeEnum.WORKFLOW_CHANGED.value,
                        title=f"Workflow updated for {bf1.issue_key if bf1 else 'BF-001'}",
                        message=f"{bf1.issue_key if bf1 else 'BF-001'} status changed from ASSIGNED to IN_PROGRESS.",
                        is_read=True,
                        created_at=now - timedelta(hours=3)
                    )
                ])

        # Sarah Connor (Frontend UI)
        if sconnor and (target_user_id is None or target_user_id == sconnor.id):
            if db.query(Notification).filter(Notification.user_id == sconnor.id).count() == 0:
                seed_data.extend([
                    Notification(
                        user_id=sconnor.id,
                        issue_id=bf2.id if bf2 else None,
                        project_id=bf2.project_id if bf2 else 1,
                        notification_type=NotificationTypeEnum.ISSUE_ASSIGNED.value,
                        title=f"Issue {bf2.issue_key if bf2 else 'BF-002'} assigned to you",
                        message=f"You have been assigned to {bf2.issue_key if bf2 else 'BF-002'}: '{bf2.title if bf2 else 'Frontend modal alignment issue'}'.",
                        is_read=False,
                        created_at=now - timedelta(minutes=40)
                    ),
                    Notification(
                        user_id=sconnor.id,
                        issue_id=None,
                        project_id=1,
                        notification_type=NotificationTypeEnum.SPRINT_EVENT.value,
                        title="Sprint Sprint-01 milestone kickoff",
                        message="Sprint Sprint-01 planning session completed. Backlog items committed.",
                        is_read=True,
                        created_at=now - timedelta(days=2)
                    )
                ])

        # QA Tester A.Smith
        if asmith and (target_user_id is None or target_user_id == asmith.id):
            if db.query(Notification).filter(Notification.user_id == asmith.id).count() == 0:
                seed_data.extend([
                    Notification(
                        user_id=asmith.id,
                        issue_id=bf3.id if bf3 else None,
                        project_id=bf3.project_id if bf3 else 1,
                        notification_type=NotificationTypeEnum.WORKFLOW_CHANGED.value,
                        title=f"Issue {bf3.issue_key if bf3 else 'BF-003'} moved to QA_TESTING",
                        message=f"{bf3.issue_key if bf3 else 'BF-003'} is ready for regression test verification.",
                        is_read=False,
                        created_at=now - timedelta(minutes=30)
                    ),
                    Notification(
                        user_id=asmith.id,
                        issue_id=bf4.id if bf4 else None,
                        project_id=bf4.project_id if bf4 else 1,
                        notification_type=NotificationTypeEnum.ISSUE_CLOSED.value,
                        title=f"Issue {bf4.issue_key if bf4 else 'BF-004'} closed",
                        message=f"Defect {bf4.issue_key if bf4 else 'BF-004'} has passed QA regression and is marked CLOSED.",
                        is_read=True,
                        created_at=now - timedelta(hours=4)
                    )
                ])

        # Priya Patel (PM)
        if ppatel and (target_user_id is None or target_user_id == ppatel.id):
            if db.query(Notification).filter(Notification.user_id == ppatel.id).count() == 0:
                seed_data.extend([
                    Notification(
                        user_id=ppatel.id,
                        issue_id=bf1.id if bf1 else None,
                        project_id=bf1.project_id if bf1 else 1,
                        notification_type=NotificationTypeEnum.ISSUE_CREATED.value,
                        title=f"New issue {bf1.issue_key if bf1 else 'BF-001'} reported",
                        message=f"Critical issue {bf1.issue_key if bf1 else 'BF-001'} was submitted and needs sprint allocation.",
                        is_read=False,
                        created_at=now - timedelta(minutes=10)
                    ),
                    Notification(
                        user_id=ppatel.id,
                        issue_id=None,
                        project_id=1,
                        notification_type=NotificationTypeEnum.SPRINT_EVENT.value,
                        title="Sprint Sprint-01 Velocity on Track",
                        message="Sprint-01 velocity is tracking at 92% of commitment.",
                        is_read=False,
                        created_at=now - timedelta(hours=1)
                    )
                ])

        for n in seed_data:
            db.add(n)
        if seed_data:
            db.commit()

