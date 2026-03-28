"""
database.py
Handles all SQLite read and write operations.
One table: sessions — everything else is queried from it.
"""

import os
import sqlite3
from datetime import datetime


DB_PATH = "data/activity.db"


# ── Connection (auto-creates folder + table) ──────────────────────────────────

def _connect() -> sqlite3.Connection:
    """Opens a connection, creating the data folder and table if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            app       TEXT,
            title     TEXT,
            category  TEXT,
            start     TEXT,
            end       TEXT,
            duration  REAL
        )
    """)
    conn.commit()
    return conn


# ── Setup ─────────────────────────────────────────────────────────────────────

def init_db():
    """Explicit init — kept for use in main.py startup."""
    _connect()


# ── Write ─────────────────────────────────────────────────────────────────────

def save_session(app: str, title: str, category: str, start: float, end: float):
    """Saves a completed session to the database."""
    duration = round((end - start) / 60, 2)  # seconds → minutes

    with _connect() as conn:
        conn.execute("""
            INSERT INTO sessions (app, title, category, start, end, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            app,
            title,
            category,
            _to_str(start),
            _to_str(end),
            duration
        ))


# ── Read ──────────────────────────────────────────────────────────────────────

def get_sessions(date: str) -> list[dict]:
    """Returns all sessions for a given date (YYYY-MM-DD)."""
    with _connect() as conn:
        rows = conn.execute("""
            SELECT app, title, category, start, end, duration
            FROM sessions
            WHERE DATE(start) = ?
            ORDER BY start ASC
        """, (date,)).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_daily_summary(date: str) -> dict:
    """Returns total minutes per category for a given date."""
    with _connect() as conn:
        rows = conn.execute("""
            SELECT category, ROUND(SUM(duration), 2) as total
            FROM sessions
            WHERE DATE(start) = ?
            GROUP BY category
        """, (date,)).fetchall()

    return {row[0]: row[1] for row in rows}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_str(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def _row_to_dict(row: tuple) -> dict:
    return {
        "app":      row[0],
        "title":    row[1],
        "category": row[2],
        "start":    row[3],
        "end":      row[4],
        "duration": row[5]
    }