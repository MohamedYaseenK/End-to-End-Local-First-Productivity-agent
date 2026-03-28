"""
processor.py
Aggregates raw sessions into daily summaries and weekly trends.
Identifies peak focus hours and top distractions.
"""

import pandas as pd
from datetime import datetime, timedelta
from database import get_sessions, get_daily_summary


# ── Daily Summary ─────────────────────────────────────────────────────────────

def daily_summary(date: str) -> dict:
    """
    Returns total time per category for a given date.
    Example: { "Work": 320, "Distraction": 40, "Idle": 60 }
    """
    return get_daily_summary(date)


# ── Weekly Summary ────────────────────────────────────────────────────────────

def weekly_summary(end_date: str) -> pd.DataFrame:
    """
    Returns a DataFrame with daily category totals for the past 7 days.
    Columns: date, Work, Learning, Communication, Distraction, Idle
    """
    rows = []

    for i in range(6, -1, -1):
        date = _offset_date(end_date, -i)
        summary = get_daily_summary(date)
        summary["date"] = date
        rows.append(summary)

    df = pd.DataFrame(rows).fillna(0)
    df = df.set_index("date")
    return df


# ── Peak Hours ────────────────────────────────────────────────────────────────

def peak_focus_hours(date: str) -> list[int]:
    """
    Returns the top 3 hours of the day with the most Work time.
    Example: [9, 10, 14]
    """
    sessions = get_sessions(date)
    if not sessions:
        return []

    df = pd.DataFrame(sessions)
    df = df[df["category"] == "Work"]
    df["hour"] = pd.to_datetime(df["start"]).dt.hour

    top_hours = (
        df.groupby("hour")["duration"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .index.tolist()
    )

    return top_hours


# ── Top Distractions ──────────────────────────────────────────────────────────

def top_distractions(date: str) -> list[dict]:
    """
    Returns the top 3 distracting apps for a given date.
    Example: [{ "app": "YouTube", "minutes": 35 }, ...]
    """
    sessions = get_sessions(date)
    if not sessions:
        return []

    df = pd.DataFrame(sessions)
    df = df[df["category"] == "Distraction"]

    top = (
        df.groupby("app")["duration"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
        .rename(columns={"duration": "minutes"})
    )

    return top.to_dict(orient="records")


# ── Helper ────────────────────────────────────────────────────────────────────

def _offset_date(date: str, days: int) -> str:
    """Returns a date string offset by N days."""
    base = datetime.strptime(date, "%Y-%m-%d")
    return (base + timedelta(days=days)).strftime("%Y-%m-%d")