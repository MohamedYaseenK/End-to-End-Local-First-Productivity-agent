"""
exports/csv_export.py
Exports a day's sessions as a CSV timesheet.
"""

import csv
import os
from database import get_sessions


def export_csv(date: str, output_dir: str = "exports/output"):
    """
    Exports all sessions for a given date to a CSV file.
    File is saved as: exports/output/timesheet_YYYY-MM-DD.csv
    """
    sessions = get_sessions(date)

    if not sessions:
        print(f"No sessions found for {date}.")
        return

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"timesheet_{date}.csv")

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["app", "title", "category", "start", "end", "duration"])
        writer.writeheader()
        writer.writerows(sessions)

    print(f"Saved: {filepath}")


# ── Run directly ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import date
    export_csv(date.today().strftime("%Y-%m-%d"))