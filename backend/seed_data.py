import sys
import os
from datetime import datetime, timedelta, date

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.project import Project, BugCategory
from app.models.issue import Issue, Comment, Attachment, AuditLog, IssueAssignment, ReporterIssueTracking
from app.models.sprint import Sprint
from app.models.insight import UserTriageInsight, HistoricalBugFix, BugFlowUserPortal
from app.services.auth_service import hash_password

def seed_database():
    print("Re-initializing database schema with Priority Score & Attachments...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Seeding Users & Developer Profiles...")
    users = [
        User(
            username="admin",
            email="admin@bugflow.io",
            full_name="Admin (Lead Dev)",
            hashed_password=hash_password("admin123"),
            role="ADMIN",
            team="Engineering Leadership",
            core_skills="Architecture, Python, Java, Security, Spring Boot, PostgreSQL",
            proficiency="Lead"
        ),
        User(
            username="jdoe",
            email="j.doe@bugflow.io",
            full_name="J.Doe",
            hashed_password=hash_password("password123"),
            role="DEVELOPER",
            team="Backend Core",
            core_skills="Java, Spring Data JPA, PostgreSQL, REST APIs, Microservices, Python, SQL",
            proficiency="Mid"
        ),
        User(
            username="asmith",
            email="a.smith@bugflow.io",
            full_name="A.Smith",
            hashed_password=hash_password("password123"),
            role="QA_TESTER",
            team="Quality Assurance",
            core_skills="QA Automation, Selenium, PyTest, Regression Testing, Performance",
            proficiency="Senior"
        ),
        User(
            username="sconnor",
            email="s.connor@bugflow.io",
            full_name="Sarah Connor",
            hashed_password=hash_password("password123"),
            role="DEVELOPER",
            team="Frontend UX",
            core_skills="JavaScript, React, CSS, Tailwind, Responsive Layout, Plotly, HTML",
            proficiency="Senior"
        ),
        User(
            username="dkim",
            email="d.kim@bugflow.io",
            full_name="David Kim",
            hashed_password=hash_password("password123"),
            role="DEVELOPER",
            team="DevOps & Cloud",
            core_skills="Docker, Kubernetes, GitHub Actions, CI/CD, AWS, Nginx, Linux",
            proficiency="Senior"
        ),
        User(
            username="ppatel",
            email="p.patel@bugflow.io",
            full_name="Priya Patel",
            hashed_password=hash_password("password123"),
            role="PROJECT_MANAGER",
            team="Product & Agile",
            core_skills="Scrum, Agile Sprint Planning, Backlog Prioritization, Jira Sync",
            proficiency="Lead"
        )
    ]
    db.add_all(users)
    db.commit()

    print("Seeding Projects & Bug Categories...")
    p1 = Project(project_name="BugFlow Core Platform", key="BF", codebase="github.com/bugflow/core", development_cycle="Agile Scrum", description="Main issue lifecycle engine and REST API")
    p2 = Project(project_name="Authentication & IAM Service", key="AUTH", codebase="github.com/bugflow/auth-service", development_cycle="Agile Scrum", description="OAuth2, Spring Security & JWT Service")
    p3 = Project(project_name="Payment & Billing Engine", key="PAY", codebase="github.com/bugflow/billing", development_cycle="Kanban", description="Stripe & subscription handling microservice")
    p4 = Project(project_name="Analytics & Quality Insights", key="ANL", codebase="github.com/bugflow/analytics", development_cycle="Agile Scrum", description="Plotly telemetry & PDF report generator")
    db.add_all([p1, p2, p3, p4])
    db.commit()

    categories = [
        BugCategory(category_name="UI/UX & Frontend", urgency_enum="Low", description="Styling, rendering, responsiveness and web client glitches"),
        BugCategory(category_name="Authentication & Security", urgency_enum="High", description="Role access control, token validation, CSRF/XSS"),
        BugCategory(category_name="Database & Performance", urgency_enum="High", description="SQL query latency, connection pool, deadlocks"),
        BugCategory(category_name="API & Integrations", urgency_enum="Medium", description="REST endpoints, webhooks, JSON serialization"),
        BugCategory(category_name="CI/CD & DevOps", urgency_enum="Medium", description="Build pipeline, docker containers, deployment hooks")
    ]
    db.add_all(categories)
    db.commit()

    print("Seeding Sprints...")
    s1 = Sprint(
        project_id=p1.id,
        sprint_name="Sprint 1 - Foundation & Auth",
        goal="Milestone 1 & 2: Issue reporting, RBAC security, and lifecycle transitions",
        start_date=date.today() - timedelta(days=14),
        end_date=date.today() + timedelta(days=2),
        planned_velocity=35,
        status="ACTIVE"
    )
    db.add(s1)
    db.commit()

    print("Seeding Issues with Priority Math...")
    now = datetime.utcnow()

    # Issue 1: B-001 Minor UI Glitch (Severity: MINOR 2, Category: UI Low 1 -> Score: 2.0 -> LOW)
    i1 = Issue(
        issue_key="B-001",
        project_id=p1.id,
        category_id=categories[0].id,
        title="Minor UI Glitch in navigation dropdown",
        description="Navigation bar dropdown menu overflows slightly on mobile viewport (< 640px).",
        reproduction_steps="1. Open mobile browser\n2. Click profile icon\n3. Notice dropdown clipping on right edge",
        affected_module="Web UI Header",
        environment_info="Production - iOS Safari / Chrome Mobile",
        severity="MINOR",
        priority="LOW",
        priority_score=2.0,
        dev_stage="IN_PROGRESS",
        reporter_id=1,
        assignee_id=2, # J.Doe
        sprint_id=s1.id,
        estimated_effort=2.5,
        created_at=now - timedelta(days=4)
    )

    # Issue 2: B-002 Error on Login (Severity: MAJOR 3, Category: Auth High 3 -> Score: 9.0 -> HIGH)
    i2 = Issue(
        issue_key="B-002",
        project_id=p2.id,
        category_id=categories[1].id,
        title="Error on Login with special characters",
        description="Users with special characters in password receive 401 Unauthorized due to UTF-8 encoding bug in Auth token generator.",
        reproduction_steps="1. Register user with password containing '$'\n2. Attempt login\n3. 401 Unauthorized returned",
        affected_module="Authentication Service",
        environment_info="Production - Linux x86_64",
        severity="MAJOR",
        priority="HIGH",
        priority_score=9.0,
        dev_stage="ASSIGNED",
        reporter_id=3,
        assignee_id=2,
        sprint_id=s1.id,
        estimated_effort=6.0,
        created_at=now - timedelta(days=3)
    )

    # Issue 3: B-003 Minor UI Glitch (Severity: MINOR 2, Category: UI Low 1 -> Score: 2.0 -> LOW)
    i3 = Issue(
        issue_key="B-003",
        project_id=p1.id,
        category_id=categories[0].id,
        title="Button alignment in settings modal",
        description="The 'Save Preferences' button has inconsistent padding on Firefox Quantum 120.",
        affected_module="Settings UI",
        environment_info="Staging - Firefox 120 / macOS",
        severity="MINOR",
        priority="LOW",
        priority_score=2.0,
        dev_stage="REPORTED",
        reporter_id=4,
        assignee_id=None,
        sprint_id=None, # In Backlog
        estimated_effort=1.5,
        created_at=now - timedelta(days=2)
    )

    # Issue 4: BF-004 Database connection pool exhaustion (Severity: CRITICAL 4, Category: DB High 3 -> Score: 12.0 -> URGENT)
    i4 = Issue(
        issue_key="BF-004",
        project_id=p1.id,
        category_id=categories[2].id,
        title="Database connection pool exhaustion under simulated load",
        description="HikariCP connection pool ran out of connections when 500+ concurrent requests hit /api/v1/bugs/ endpoint.",
        reproduction_steps="Run locust load test with 500 virtual users for 2 minutes.",
        affected_module="Database / HikariCP Pool",
        environment_info="Staging - PostgreSQL 15 / Kubernetes",
        severity="CRITICAL",
        priority="URGENT",
        priority_score=12.0,
        dev_stage="CLOSED",
        reporter_id=5,
        assignee_id=2,
        sprint_id=s1.id,
        estimated_effort=12.0,
        actual_effort=9.5,
        created_at=now - timedelta(days=7),
        closed_at=now - timedelta(days=5),
        resolution_summary="Optimized SessionLocal lifecycle and tuned max_pool_size to 125 connections."
    )

    # Issue 5: BF-005 JWT token refresh race condition (Severity: MAJOR 3, Category: Auth High 3 -> Score: 9.0 -> HIGH)
    i5 = Issue(
        issue_key="BF-005",
        project_id=p2.id,
        category_id=categories[1].id,
        title="JWT token expiration race condition during parallel API calls",
        description="When multiple API calls fire concurrently with an expired access token, multiple refresh requests trigger token invalidation.",
        affected_module="Auth Middleware",
        environment_info="Production - Linux x86_64",
        severity="MAJOR",
        priority="HIGH",
        priority_score=9.0,
        dev_stage="IN_PROGRESS",
        reporter_id=1,
        assignee_id=6,
        sprint_id=s1.id,
        estimated_effort=8.0,
        created_at=now - timedelta(days=5)
    )

    db.add_all([i1, i2, i3, i4, i5])
    db.commit()

    print("Seeding Comments & Audit Trails...")
    c1 = Comment(bug_id=i1.id, user_id=2, content="Working on reproduction script and Tailwind responsive breakpoint fix.", code_reference="components/Navbar.tsx#L45-L52", created_at=now - timedelta(hours=5))
    c2 = Comment(bug_id=i1.id, user_id=3, content="Check attached log: Verified issue occurs only on screens < 640px.", created_at=now - timedelta(hours=3))
    db.add_all([c1, c2])

    a1 = AuditLog(bug_id=i1.id, user_id=1, action="STATUS_CHANGED", previous_state="REPORTED", new_state="IN_PROGRESS", details="Status changed from REPORTED to IN_PROGRESS [cite: 3]", timestamp=now - timedelta(days=2))
    a2 = AuditLog(bug_id=i1.id, user_id=1, action="ASSIGNMENT", previous_state=None, new_state="J.Doe", details="Assigned to user J.Doe [cite: 3]", timestamp=now - timedelta(days=2))
    db.add_all([a1, a2])

    db.commit()
    print("Database seeding completed! Total issues seeded:", db.query(Issue).count())
    db.close()

if __name__ == "__main__":
    seed_database()
