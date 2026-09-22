# BugFlow: Software Issue Tracking & Resolution Platform
## Enterprise Defect Lifecycle, AI Triage & Agile Sprint Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker)](https://www.docker.com)
[![PyTest](https://img.shields.io/badge/PyTest-100%25%20Passed-brightgreen.svg?style=flat&logo=pytest)](https://docs.pytest.org)

---

## 📌 Project Overview

**BugFlow** is an end-to-end, high-scale Software Defect Tracking and Quality Management platform designed for modern Agile and DevOps teams. It automates bug reporting, NLP/rule-based AI triage, developer workload balancing, 7-stage state machine transitions, CI/CD Git webhook auto-advancement, and interactive Plotly telemetry.

---

## 🚀 Key Features

* **🧮 Smart Priority Calculator:** $\text{Priority Score} = \text{Severity Weight} \times \text{Category Urgency Weight}$ (e.g. CRITICAL $4 \times 3 = 12 \rightarrow \text{URGENT}$).
* **🧑‍💻 Developer Workload Matcher:** Skill matching with active workload penalty to prevent engineer burnout.
* **🤖 Automated CI/CD Git Webhooks:** Ingests commit messages (e.g. `fixes #2`) and auto-advances defects to `QA_VERIFICATION` with audit logs.
* **🏃‍♂️ Agile Sprint & Kanban Board:** Side-by-side active sprints vs product backlog with 1-click issue assignment and velocity tracking.
* **📈 Interactive Plotly Analytics:** 14-day defect ingestion vs resolution trend lines, severity donut charts, and workflow pipeline bars.
* **📄 One-Click PDF & CSV Exporters:** Server-side ReportLab executive PDF reports and Excel-compatible CSV exports.
* **⚡ High-Scale Database Optimization:** PostgreSQL composite indexing and connection pooling designed for 50,000+ defect capacity.
* **🧪 100% PyTest Automated Coverage:** Full test coverage across auth, issues, sprints, and analytics.

---

## 🏗️ Tech Stack

* **Backend:** FastAPI (Python 3.11+), Uvicorn ASGI Server
* **Database & ORM:** SQLAlchemy 2.0 (PostgreSQL 15 / SQLite) with Connection Pooling
* **Frontend:** Tailwind CSS, Jinja2 Template Engine, FontAwesome 6, Plotly.js
* **Reporting:** ReportLab PDF Engine
* **Containerization:** Docker & Docker Compose
* **Testing:** PyTest Suite (`pytest tests/ -v`)

---

## ⚡ Quick Start Guide

### Option 1: Run Locally on Windows / Mac / Linux

```bash
# 1. Clone or navigate to the repository
cd bugflow/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed initial database
python seed_data.py

# 4. Start the server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* **Web UI Dashboard:** `http://127.0.0.1:8000`
* **Swagger API Docs:** `http://127.0.0.1:8000/docs`
* **ReDoc API Manual:** `http://127.0.0.1:8000/redoc`
* **Health Check:** `http://127.0.0.1:8000/health`

---

### Option 2: Run with Docker Compose

```bash
# Start FastAPI and PostgreSQL 15 containers
docker compose up --build -d
```

---

## 🧪 Running Automated Tests

```bash
cd backend
pytest tests/ -v
```

---

## 🔑 Default User Accounts & Roles

| Username | Password | Role | Team | Proficiency |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `admin123` | `ADMIN` | Engineering Leadership | Lead |
| `jdoe` | `password123` | `DEVELOPER` | Backend Core | Mid |
| `sconnor` | `password123` | `DEVELOPER` | Frontend UX | Senior |
| `dkim` | `password123` | `DEVELOPER` | DevOps & Cloud | Senior |
| `asmith` | `password123` | `QA_TESTER` | Quality Assurance | Senior |
| `ppatel` | `password123` | `PROJECT_MANAGER` | Product & Agile | Lead |
