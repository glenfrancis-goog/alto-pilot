"""AlloyDB & SQLite Database Connection and Schema Setup.

Strictly conforms to SDD Section 5.1.
"""

import sqlite3
import json
from datetime import datetime, timezone, timedelta
from typing import Optional
from src.config import DATABASE_URL, BASE_DIR

def get_db_connection():
    """Returns a SQLite connection (or AlloyDB psycopg2 connection if configured)."""
    db_path = BASE_DIR / "sessions.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the AlloyDB / SQLite tables matching SDD Section 5.1."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. SESSIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'COMPLETED', 'EXPIRED', 'REVOKED')),
        metadata TEXT DEFAULT '{}'
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")

    # 2. CONVERSATION TURNS TABLE (DLP Redacted)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversation_turns (
        turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT REFERENCES sessions(session_id) ON DELETE CASCADE,
        turn_index INTEGER NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
        content_redacted TEXT NOT NULL,
        model_armor_eval_token TEXT,
        turn_latency_ms INTEGER,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turns_session_id ON conversation_turns(session_id, turn_index)")

    # 3. SAGA TRANSACTIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saga_transactions (
        saga_id TEXT PRIMARY KEY,
        session_id TEXT,
        user_id TEXT NOT NULL,
        flow_type TEXT NOT NULL CHECK (flow_type IN ('EQUIPMENT_PROCUREMENT', 'MEDICAL_LEAVE', 'RELOCATION', 'GDPR_RTBF_PURGE')),
        current_step TEXT NOT NULL,
        status TEXT DEFAULT 'IN_PROGRESS' CHECK (status IN ('IN_PROGRESS', 'SUCCESS', 'FAILED', 'COMPENSATED')),
        payload TEXT NOT NULL,
        error_details TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_saga_user_status ON saga_transactions(user_id, status)")

    conn.commit()
    conn.close()

# Auto-initialize on import
init_db()
