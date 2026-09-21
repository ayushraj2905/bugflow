import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class PDFExportService:
    @staticmethod
    def generate_quality_report(metrics: dict, issues: list) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#0f172a'),
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#64748b')
        )
        section_style = ParagraphStyle(
            'ReportSection',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#0369a1'),
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=6
        )
        cell_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1e293b')
        )
        cell_bold = ParagraphStyle(
            'CellTextBold',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0f172a')
        )

        elements = []

        # 1. Header & Title
        elements.append(Paragraph("BugFlow – Software Quality & Defect Status Report", title_style))
        elements.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')} • Milestone 3 Quality Analytics", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

        # 2. Executive KPI Scorecard Table
        elements.append(Paragraph("1. Executive Quality Scorecard & Metrics", section_style))
        
        kpi_data = [
            [
                Paragraph("<b>Total Issues</b>", cell_bold),
                Paragraph(str(metrics.get('total_bugs', 0)), cell_style),
                Paragraph("<b>Bug Fix Rate</b>", cell_bold),
                Paragraph(f"{metrics.get('fix_rate_percentage', 0)}%", cell_style),
            ],
            [
                Paragraph("<b>Resolved / Closed</b>", cell_bold),
                Paragraph(str(metrics.get('resolved_bugs', 0) + metrics.get('closed_bugs', 0)), cell_style),
                Paragraph("<b>MTTR (Avg Fix Time)</b>", cell_bold),
                Paragraph(f"{metrics.get('mean_time_to_resolution_hours', 0)} hrs ({metrics.get('mean_time_to_resolution_days', 0)} days)", cell_style),
            ],
            [
                Paragraph("<b>Open Critical Issues</b>", cell_bold),
                Paragraph(str(metrics.get('critical_bugs', 0)), cell_style),
                Paragraph("<b>Defect Leakage Rate</b>", cell_bold),
                Paragraph(f"{metrics.get('defect_leakage_rate_percentage', 0)}% (Prod Escapes)", cell_style),
            ],
            [
                Paragraph("<b>Active Workload</b>", cell_bold),
                Paragraph(str(metrics.get('open_bugs', 0)), cell_style),
                Paragraph("<b>Backlog Health Score</b>", cell_bold),
                Paragraph(f"<b>{metrics.get('backlog_health_score', 90)} / 100</b>", cell_style),
            ],
        ]

        t_kpi = Table(kpi_data, colWidths=[1.5*inch, 1.8*inch, 1.7*inch, 2.0*inch])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 12))

        # 3. Defect Registry Table
        elements.append(Paragraph("2. Active Defect Registry & Resolution Status", section_style))
        
        issue_rows = [
            [
                Paragraph("<b>Key</b>", cell_bold),
                Paragraph("<b>Title & Summary</b>", cell_bold),
                Paragraph("<b>Severity</b>", cell_bold),
                Paragraph("<b>Priority</b>", cell_bold),
                Paragraph("<b>Stage</b>", cell_bold),
                Paragraph("<b>Assignee</b>", cell_bold),
            ]
        ]

        for issue in issues[:15]:
            issue_rows.append([
                Paragraph(str(issue.issue_key), cell_bold),
                Paragraph(str(issue.title)[:38] + ('...' if len(issue.title) > 38 else ''), cell_style),
                Paragraph(str(issue.severity), cell_style),
                Paragraph(str(issue.priority), cell_style),
                Paragraph(str(issue.dev_stage), cell_style),
                Paragraph(issue.assignee.full_name if issue.assignee else 'Unassigned', cell_style),
            ])

        t_issues = Table(issue_rows, colWidths=[0.8*inch, 2.6*inch, 0.9*inch, 0.8*inch, 1.1*inch, 1.0*inch])
        t_issues.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0f2fe')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t_issues)
        elements.append(Spacer(1, 15))

        # 4. Footer Note
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=6))
        elements.append(Paragraph("Confidential • BugFlow Quality Engineering Platform • Verified Workflow Integrity &ge; 99%", subtitle_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
