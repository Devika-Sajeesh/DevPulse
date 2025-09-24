import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

DB_PATH = "devpulse.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_url TEXT,
        timestamp TEXT,
        radon TEXT,
        cloc TEXT,
        pylint TEXT,
        ai_summary TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_report(repo_url: str, radon: Dict, cloc: Dict, pylint: Dict, ai_summary: Dict) -> int:
    """Save a report into the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reports (repo_url, timestamp, radon, cloc, pylint, ai_summary)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        repo_url,
        datetime.utcnow().isoformat(),
        json.dumps(radon),
        json.dumps(cloc),
        json.dumps(pylint),
        json.dumps(ai_summary)  # serialize AI summary as JSON
    ))
    conn.commit()
    report_id = cur.lastrowid
    conn.close()
    return report_id

def get_report(report_id: int):
    """Retrieve a report by ID and deserialize JSON fields."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE id=?", (report_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "repo_url": row[1],
        "timestamp": row[2],
        "radon": json.loads(row[3]),
        "cloc": json.loads(row[4]),
        "pylint": json.loads(row[5]),
        "ai_summary": json.loads(row[6])  # deserialize JSON
    }


def list_reports():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, repo_url, timestamp FROM reports ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "repo_url": r[1], "timestamp": r[2]} for r in rows]

