import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Audit Runs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_runs (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL,
        viewport TEXT NOT NULL,
        before_screenshot TEXT,
        after_screenshot TEXT,
        diff_screenshot TEXT,
        defects_found INTEGER DEFAULT 0,
        fix_applied INTEGER DEFAULT 0,
        verification_passed INTEGER DEFAULT 0,
        pr_number INTEGER,
        pr_url TEXT,
        summary TEXT,
        timeline TEXT,
        crop_screenshot TEXT,
        engine_used TEXT,
        confidence_score REAL
    )
    """)

    # Migration check: add new columns if they do not exist
    cursor.execute("PRAGMA table_info(audit_runs)")
    existing_cols = {row["name"] for row in cursor.fetchall()}
    for col_name, col_type in [
        ("timeline", "TEXT"),
        ("crop_screenshot", "TEXT"),
        ("engine_used", "TEXT"),
        ("confidence_score", "REAL")
    ]:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE audit_runs ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass
    
    # Defects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS defects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        defect_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        element_selector TEXT,
        description TEXT NOT NULL,
        bounding_box TEXT,
        proposed_fix TEXT,
        FOREIGN KEY (run_id) REFERENCES audit_runs (id)
    )
    """)
    
    # Patches Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        file_path TEXT NOT NULL,
        target_selector TEXT,
        original_css TEXT,
        repaired_css TEXT,
        unified_diff TEXT,
        applied_at TEXT,
        FOREIGN KEY (run_id) REFERENCES audit_runs (id)
    )
    """)
    
    conn.commit()
    conn.close()

def save_audit_run(run_data: Dict[str, Any]) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    timeline_json = json.dumps(run_data.get("timeline", [])) if run_data.get("timeline") is not None else "[]"
    crop_img = run_data.get("crop_screenshot") or run_data.get("cropped_defect_token_artifact")
    engine = run_data.get("engine_used", "")
    confidence = run_data.get("confidence_score")

    cursor.execute("""
    INSERT OR REPLACE INTO audit_runs (
        id, created_at, status, viewport, before_screenshot, after_screenshot,
        diff_screenshot, defects_found, fix_applied, verification_passed,
        pr_number, pr_url, summary, timeline, crop_screenshot, engine_used, confidence_score
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_data["id"],
        run_data.get("created_at", datetime.now().isoformat()),
        run_data.get("status", "completed"),
        run_data.get("viewport", "mobile"),
        run_data.get("before_screenshot"),
        run_data.get("after_screenshot"),
        run_data.get("diff_screenshot"),
        run_data.get("defects_found", 0),
        1 if run_data.get("fix_applied") else 0,
        1 if run_data.get("verification_passed") else 0,
        run_data.get("pr_number"),
        run_data.get("pr_url"),
        run_data.get("summary", ""),
        timeline_json,
        crop_img,
        engine,
        confidence
    ))
    
    # Save defects
    for d in run_data.get("defects", []):
        cursor.execute("""
        INSERT INTO defects (
            run_id, defect_type, severity, element_selector, description, bounding_box, proposed_fix
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            run_data["id"],
            d.get("type", "layout_anomaly"),
            d.get("severity", "high"),
            d.get("element", ""),
            d.get("description", ""),
            json.dumps(d.get("bounding_box", {})),
            d.get("proposed_fix", "")
        ))
        
    # Save patch if available
    patch = run_data.get("patch")
    if patch:
        cursor.execute("""
        INSERT INTO patches (
            run_id, file_path, target_selector, original_css, repaired_css, unified_diff, applied_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            run_data["id"],
            patch.get("file_path", "test-app/checkout.css"),
            patch.get("target_selector", ".checkout-action-btn"),
            patch.get("original_css", ""),
            patch.get("repaired_css", ""),
            patch.get("unified_diff", ""),
            datetime.now().isoformat()
        ))
        
    conn.commit()
    conn.close()
    return run_data["id"]

def _hydrate_run_dict(cursor, run_row) -> Dict[str, Any]:
    run_dict = dict(run_row)
    # Timeline
    try:
        run_dict["timeline"] = json.loads(run_dict["timeline"]) if run_dict.get("timeline") else []
    except Exception:
        run_dict["timeline"] = []
    
    # Expose crop screenshot alias
    run_dict["cropped_defect_token_artifact"] = run_dict.get("crop_screenshot")

    # Fetch defects for this run
    cursor.execute("SELECT * FROM defects WHERE run_id = ?", (run_dict["id"],))
    run_dict["defects"] = [
        {**dict(d), "bounding_box": json.loads(d["bounding_box"]) if d["bounding_box"] else {}}
        for d in cursor.fetchall()
    ]
    # Fetch patch
    cursor.execute("SELECT * FROM patches WHERE run_id = ?", (run_dict["id"],))
    p = cursor.fetchone()
    run_dict["patch"] = dict(p) if p else None
    return run_dict

def get_recent_runs(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_runs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    runs = [_hydrate_run_dict(cursor, r) for r in rows]
    conn.close()
    return runs

def get_run_by_id(run_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    run_dict = _hydrate_run_dict(cursor, row)
    conn.close()
    return run_dict

# Initialize DB on load
init_db()
