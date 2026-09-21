import csv
import io
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.issue import Issue
from ..services.analytics_service import AnalyticsService
from ..services.pdf_export_service import PDFExportService

router = APIRouter(tags=["Analytics, Quality Scorecard & Exports"])

# 1. Quality Metrics Scorecard
@router.get("/api/v1/analytics/quality-metrics")
def get_quality_metrics_api(db: Session = Depends(get_db)):
    return AnalyticsService.get_quality_metrics(db)

# 2. Defect Trends Data (14-Day Red/Green Line Chart)
@router.get("/api/v1/analytics/defect-trends")
def get_defect_trends_api(db: Session = Depends(get_db)):
    return AnalyticsService.get_14_day_defect_trends(db)

# 3. Analytics Charts Data (For /analytics page)
@router.get("/api/v1/analytics/charts")
def get_charts_api(db: Session = Depends(get_db)):
    return AnalyticsService.get_charts_data(db)

# 4. Ready-to-render Plotly Chart Configs (For /milestone3 page)
@router.get("/api/v1/analytics/plotly-charts")
def get_plotly_charts_api(db: Session = Depends(get_db)):
    return AnalyticsService.get_plotly_chart_configs(db)

# 5. Developer Workload & Productivity Matrix (Milestone 4 Requirement)
@router.get("/api/v1/analytics/developer-workload")
def get_developer_workload_api(db: Session = Depends(get_db)):
    return AnalyticsService.get_developer_workload_matrix(db)

# 6. Executive PDF Report Exporter
@router.get("/api/v1/export/pdf")
@router.get("/api/v1/analytics/export/pdf")
def export_pdf_report(db: Session = Depends(get_db)):
    metrics = AnalyticsService.get_quality_metrics(db)
    issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
    pdf_bytes = PDFExportService.generate_quality_report(metrics, issues)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=BugFlow_Quality_Report.pdf"
        }
    )

# 7. Raw Bug Registry CSV Exporter
@router.get("/api/v1/export/csv")
@router.get("/api/v1/analytics/export/csv")
def export_csv_report(db: Session = Depends(get_db)):
    issues = db.query(Issue).order_by(Issue.id.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Key", "Title", "Severity", "Priority", "Priority Score",
        "Stage", "Project", "Category", "Assignee", "Reporter",
        "Environment", "Affected Module", "Estimated Effort (hrs)", "Created At"
    ])

    for i in issues:
        writer.writerow([
            i.id,
            i.issue_key,
            i.title,
            i.severity,
            i.priority,
            i.priority_score or 6.0,
            i.dev_stage,
            i.project.project_name if i.project else "N/A",
            i.category.category_name if i.category else "N/A",
            i.assignee.full_name if i.assignee else "Unassigned",
            i.reporter.full_name if i.reporter else "System",
            i.environment_info,
            i.affected_module,
            i.estimated_effort,
            i.created_at.strftime("%Y-%m-%d %H:%M:%S") if i.created_at else ""
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=BugFlow_Defect_Registry.csv"
        }
    )
