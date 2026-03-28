"""
exports/pdf_export.py
Exports a daily productivity summary as a clean PDF timesheet.
"""

import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from database import get_sessions
from processor import daily_summary


def export_pdf(date_str: str, output_dir: str = "exports/output"):
    """
    Exports a daily timesheet as a PDF.
    File is saved as: exports/output/timesheet_YYYY-MM-DD.pdf
    """
    sessions = get_sessions(date_str)
    summary  = daily_summary(date_str)

    if not sessions:
        print(f"No sessions found for {date_str}.")
        return

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"timesheet_{date_str}.pdf")

    doc    = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story  = []

    # ── Title ─────────────────────────────────────────────────────────────────
    story.append(Paragraph(f"Timesheet — {date_str}", styles["Title"]))
    story.append(Spacer(1, 12))

    # ── Summary Table ─────────────────────────────────────────────────────────
    story.append(Paragraph("Daily Summary", styles["Heading2"]))
    story.append(Spacer(1, 6))

    summary_data = [["Category", "Minutes", "Hours"]]
    for category, minutes in summary.items():
        summary_data.append([category, round(minutes, 1), round(minutes / 60, 2)])

    summary_table = Table(summary_data, colWidths=[180, 100, 100])
    summary_table.setStyle(_table_style(header_color=colors.HexColor("#4A90D9")))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # ── Sessions Table ────────────────────────────────────────────────────────
    story.append(Paragraph("Session Log", styles["Heading2"]))
    story.append(Spacer(1, 6))

    session_data = [["App", "Category", "Start", "End", "Mins"]]
    for s in sessions:
        session_data.append([
            s["app"],
            s["category"],
            s["start"][-8:-3],   # HH:MM
            s["end"][-8:-3],     # HH:MM
            round(s["duration"], 1)
        ])

    session_table = Table(session_data, colWidths=[120, 100, 80, 80, 60])
    session_table.setStyle(_table_style(header_color=colors.HexColor("#555555")))
    story.append(session_table)

    doc.build(story)
    print(f"Saved: {filepath}")


# ── Table Style Helper ────────────────────────────────────────────────────────

def _table_style(header_color) -> TableStyle:
    return TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  header_color),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("GRID",        (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ])


# ── Run directly ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    export_pdf(date.today().strftime("%Y-%m-%d"))