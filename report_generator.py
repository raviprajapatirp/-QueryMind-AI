"""
report_generator.py
Handles all export/download functionality: CSV, Excel, a formatted PDF
summary report (via ReportLab), and raw SQL file export. Charts/dashboard
screenshots are exported as PNG via Plotly's built-in image export
(kaleido) where available.
"""

import io
import pandas as pd
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Data") -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()


def to_sql_file(sql: str) -> bytes:
    return sql.encode("utf-8")


def build_pdf_report(title: str, profile: dict, stats_df: pd.DataFrame,
                      insights_text: str = "") -> bytes:
    """Builds a clean PDF report: title, KPI summary, stats table, AI insights."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#7C3AED"))
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], textColor=colors.HexColor("#111827"))

    elements = [
        Paragraph(title, title_style),
        Paragraph(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 16),
        Paragraph("Dataset Summary", heading_style),
    ]

    kpi_data = [["Metric", "Value"]] + [[k.replace("_", " ").title(), str(v)] for k, v in profile.items()
                                          if not isinstance(v, list)]
    kpi_table = Table(kpi_data, hAlign="LEFT")
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C3AED")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements += [kpi_table, Spacer(1, 20)]

    if stats_df is not None and not stats_df.empty:
        elements.append(Paragraph("Statistical Summary", heading_style))
        display_df = stats_df.reset_index().round(2)
        table_data = [list(display_df.columns)] + display_df.astype(str).values.tolist()
        stats_table = Table(table_data, hAlign="LEFT")
        stats_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#22D3EE")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        elements += [stats_table, Spacer(1, 20)]

    if insights_text:
        elements.append(Paragraph("AI-Generated Insights", heading_style))
        for line in insights_text.split("\n"):
            if line.strip():
                elements.append(Paragraph(line.replace("**", ""), styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    return buffer.getvalue()


def fig_to_png_bytes(fig) -> bytes:
    """Requires the `kaleido` package. Returns PNG bytes of a Plotly figure."""
    return fig.to_image(format="png", scale=2)
