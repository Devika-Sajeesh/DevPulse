# backend/services/db_service.py

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

DB_PATH = "devpulse.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # SCHEMA UPDATE: Added git_sha, ai_metrics, code_health_score, historical_risk_score
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_url TEXT,
        git_sha TEXT,          -- NEW
        timestamp TEXT,
        radon TEXT,
        cloc TEXT,
        pylint TEXT,
        ai_metrics TEXT,       -- Replaces ai_summary, stores w2/recommendations
        code_health_score REAL, -- NEW
        historical_risk_score REAL -- NEW
    )
    """)
    conn.commit()
    conn.close()

# Update save_report signature and logic
def save_report(
    repo_url: str, 
    git_sha: str,  # NEW
    radon: Dict, 
    cloc: Dict, 
    pylint: Dict, 
    ai_metrics: Dict, # Changed name
    code_health_score: float, # NEW
    historical_risk_score: float # NEW
) -> int:
    """Save a report into the SQLite database with new predictive fields."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reports (
            repo_url, git_sha, timestamp, radon, cloc, pylint, 
            ai_metrics, code_health_score, historical_risk_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        repo_url,
        git_sha, # Save Git SHA
        datetime.utcnow().isoformat(),
        json.dumps(radon),
        json.dumps(cloc),
        json.dumps(pylint),
        json.dumps(ai_metrics),
        code_health_score,
        historical_risk_score
    ))
    conn.commit()
    report_id = cur.lastrowid
    conn.close()
    return report_id

# Update get_report to return new fields
def get_report(report_id: int):
    """Retrieve a report by ID and deserialize JSON fields."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE id=?", (report_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    # Map column index to field names (assuming schema order is maintained)
    return {
        "id": row[0],
        "repo_url": row[1],
        "git_sha": row[2], # New field at index 2
        "timestamp": row[3],
        "radon": json.loads(row[4]),
        "cloc": json.loads(row[5]),
        "pylint": json.loads(row[6]),
        "ai_metrics": json.loads(row[7]), # ai_summary is now ai_metrics
        "code_health_score": row[8],
        "historical_risk_score": row[9]
    }


def list_reports():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Note: git_sha added to select list
    cur.execute("SELECT id, repo_url, git_sha, timestamp FROM reports ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "repo_url": r[1], "git_sha": r[2], "timestamp": r[3]} for r in rows]