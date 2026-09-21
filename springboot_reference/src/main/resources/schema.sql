-- ==========================================================
-- BugFlow Enterprise Database Schema (PostgreSQL DDL)
-- Matching Page 10 Architecture Diagram & System Spec
-- ==========================================================

CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    codebase VARCHAR(255) NOT NULL,
    development_cycle TEXT DEFAULT 'Agile Scrum',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_dev_profiles (
    dev_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    team VARCHAR(50) NOT NULL,
    core_skills VARCHAR(255) NOT NULL,
    proficiency VARCHAR(20) NOT NULL, -- Junior, Mid, Senior, Lead
    role VARCHAR(30) DEFAULT 'DEVELOPER',
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bug_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    urgency_enum VARCHAR(20) NOT NULL -- Critical, High, Medium, Low
);

CREATE TABLE IF NOT EXISTS individual_bug_saga (
    saga_id SERIAL PRIMARY KEY,
    issue_key VARCHAR(20) UNIQUE NOT NULL,
    project_id INT REFERENCES projects(project_id) ON DELETE CASCADE,
    category_id INT REFERENCES bug_categories(category_id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    reproduction_steps TEXT,
    affected_module VARCHAR(100),
    environment_info VARCHAR(255),
    severity VARCHAR(20) DEFAULT 'MINOR',
    priority VARCHAR(10) DEFAULT 'P3',
    dev_stage VARCHAR(30) DEFAULT 'REPORTED', -- REPORTED, TRIAGED, ASSIGNED, IN_PROGRESS, CODE_REVIEW, QA_TESTING, CLOSED
    reporter_id INT REFERENCES user_dev_profiles(dev_id),
    assignee_id INT REFERENCES user_dev_profiles(dev_id),
    estimated_effort NUMERIC(5,2) DEFAULT 4.0,
    actual_effort NUMERIC(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS issue_assignments (
    assignment_id SERIAL PRIMARY KEY,
    bug_id INT REFERENCES individual_bug_saga(saga_id) ON DELETE CASCADE,
    dev_id INT REFERENCES user_dev_profiles(dev_id),
    title VARCHAR(200) NOT NULL,
    estimated_effort NUMERIC(5,2),
    priority VARCHAR(20),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reporter_issue_tracking (
    tracking_id SERIAL PRIMARY KEY,
    reporter_id INT REFERENCES user_dev_profiles(dev_id),
    bug_id INT REFERENCES individual_bug_saga(saga_id) ON DELETE CASCADE,
    related_case VARCHAR(100),
    expected_resolution TIMESTAMP,
    progress INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_triage_insights (
    triage_id SERIAL PRIMARY KEY,
    dev_id INT REFERENCES user_dev_profiles(dev_id),
    bug_score INT DEFAULT 85,
    team_efficiency NUMERIC(5,2) DEFAULT 90.0,
    backlog_progression TEXT
);

CREATE TABLE IF NOT EXISTS historical_bug_fixes (
    fix_id SERIAL PRIMARY KEY,
    bug_id INT REFERENCES individual_bug_saga(saga_id),
    dev_id INT REFERENCES user_dev_profiles(dev_id),
    past_fixes TEXT,
    code_changes TEXT,
    resolution_time NUMERIC(5,2)
);

CREATE TABLE IF NOT EXISTS bugflow_user_portals (
    portal_id SERIAL PRIMARY KEY,
    portal_type VARCHAR(50) NOT NULL, -- Web Dashboard, Developer API, Reporter Mobile App, CI/CD Console
    portal_name VARCHAR(100) NOT NULL,
    version VARCHAR(20) DEFAULT 'v2.4.0'
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    bug_id INT REFERENCES individual_bug_saga(saga_id) ON DELETE CASCADE,
    user_id INT REFERENCES user_dev_profiles(dev_id),
    action VARCHAR(50) NOT NULL,
    previous_state VARCHAR(100),
    new_state VARCHAR(100),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
