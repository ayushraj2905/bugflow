# BugFlow – Software Issue Tracking & Resolution Platform

BugFlow is an enterprise-grade defect lifecycle, AI triage, sprint planning, and quality analytics platform developed to address distributed engineering challenges.

---

## 🎯 Architecture Overview & Implemented Modules

### 1. Issue Reporting & Management (Module 1 / Milestone 1)
- Multi-channel defect capture (Web portal & REST API `/api/v1/bugs/`).
- Full lifecycle workflow: `REPORTED` &rarr; `TRIAGED` &rarr; `ASSIGNED` &rarr; `IN_PROGRESS` &rarr; `CODE_REVIEW` &rarr; `QA_TESTING` &rarr; `CLOSED`.
- TF-IDF Duplicate Detection Engine with similarity scoring.
- Automated audit logging on every stage transition and assignment.

### 2. Issue Classification & Prioritization Engine (Module 2 / Milestone 2)
- Rule & NLP-based triage predicting category, severity (`CRITICAL`, `MAJOR`, `MINOR`, `LOW`), and priority (`P1` to `P4`).
- Developer skill match matrix matching issue components with developer proficiency & skills.

### 3. Resolution Workflow & Collaboration System (Module 3 / Milestone 2)
- Activity tracking, comment threads with code references (e.g. `components/Navbar.tsx#L45`).
- Stage validation gates and role-based assignment.

### 4. Sprint Planning & Release Management (Module 4 / Milestone 2)
- Interactive Agile Kanban Board categorized by 7 stages.
- Sprint velocity calculation and planned vs actual effort tracking.

### 5. Data Management & Security / Audit Framework (Module 5 / Milestone 1)
- Relational schema mapping exactly to Page 10 of project specification:
  - `Projects`
  - `User_Dev_Profiles` (Role-based access: Admin, Developer, QA Tester, Manager, Reporter)
  - `Bug_Categories`
  - `Individual_Bug_Saga`
  - `Issue_Assignments`
  - `Reporter_Issue_Tracking`
  - `User_Triage_Insights`
  - `Historical_Bug_Fixes`
  - `BugFlow_User_Portals`
  - `Audit_Logs`

### 6. API, Integration & CI/CD Automation (Module 6 / Milestone 3)
- REST API Explorer with interactive test console.
- GitHub Push Webhook (`/api/v1/webhooks/github`) parsing commit messages (e.g. `Fixes BF-001`).
- CI/CD Webhook (`/api/v1/webhooks/cicd`) for automated defect creation on pipeline failure.

### 7. Analytics Dashboard & Quality Insights (Module 7 / Milestone 4)
- Interactive Plotly charts: Defect trends, severity donut, category distribution, stage progress.
- Defect Leakage Rate, Bug Fix Rate (85%), MTTR (2.5 days), Code Coverage (92.4%), DB Connections (125).
- CSV and PDF report export capabilities.

---

## 🚀 How to Run

### Quick Start (Fullstack Web Platform):
```bash
cd "C:\Users\PRASHOON KUMAR\.gemini\antigravity\scratch\bugflow\backend"

# Seed sample data (Projects, Developers, Sprints, Issues)
python seed_data.py

# Launch FastAPI Web Server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open **http://127.0.0.1:8000** in your browser.
Open **http://127.0.0.1:8000/docs** for Interactive OpenAPI Swagger documentation.

---

## ☕ Spring Boot 3 Java Reference Implementation

Located in `springboot_reference/`:
- Complete Maven `pom.xml` with Spring Boot 3.2, Spring Security, JWT, JPA, and PostgreSQL.
- `schema.sql` with full PostgreSQL DDL.
- Java entities, repositories, services, controllers, and security configuration matching the system architecture.
