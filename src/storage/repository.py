"""Persistence Repository for Sessions, Turns, and SAGA Ledgers."""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from src.storage.database import get_db_connection
from src.config import SESSION_TTL_DAYS

class SessionRepository:
    @staticmethod
    def get_or_create_session(session_id: str, user_id: str) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        now = datetime.now(timezone.utc)

        if row:
            # Update updated_at
            cursor.execute("UPDATE sessions SET updated_at = ? WHERE session_id = ?", (now.isoformat(), session_id))
            conn.commit()
            res = dict(row)
            conn.close()
            return res

        expires_at = (now + timedelta(days=SESSION_TTL_DAYS)).isoformat()
        cursor.execute("""
        INSERT INTO sessions (session_id, user_id, created_at, updated_at, expires_at, status, metadata)
        VALUES (?, ?, ?, ?, ?, 'ACTIVE', '{}')
        """, (session_id, user_id, now.isoformat(), now.isoformat(), expires_at))
        conn.commit()
        conn.close()
        return {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "expires_at": expires_at,
            "status": "ACTIVE",
            "metadata": "{}"
        }

    @staticmethod
    def record_turn(session_id: str, turn_index: int, role: str, content_redacted: str, eval_token: str = "MA-SAFE-OK", latency_ms: int = 0):
        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO conversation_turns (session_id, turn_index, role, content_redacted, model_armor_eval_token, turn_latency_ms, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, turn_index, role, content_redacted, eval_token, latency_ms, now_iso))
        conn.commit()
        conn.close()

    @staticmethod
    def get_turns(session_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversation_turns WHERE session_id = ? ORDER BY turn_index ASC", (session_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_session_state(session_id: str) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT metadata FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row["metadata"]:
            try:
                return json.loads(row["metadata"])
            except Exception:
                return {}
        return {}

    @staticmethod
    def update_session_state(session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET metadata = ?, updated_at = ? WHERE session_id = ?", (json.dumps(updates), now_iso, session_id))
        conn.commit()
        conn.close()
        return updates

    @staticmethod
    def record_saga(saga_id: str, session_id: str, user_id: str, flow_type: str, current_step: str, status: str, payload: Dict[str, Any], error_details: Optional[Dict[str, Any]] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        payload_str = json.dumps(payload)
        err_str = json.dumps(error_details) if error_details else None

        cursor.execute("""
        INSERT OR REPLACE INTO saga_transactions (saga_id, session_id, user_id, flow_type, current_step, status, payload, error_details, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (saga_id, session_id, user_id, flow_type, current_step, status, payload_str, err_str, now_iso, now_iso))
        conn.commit()
        conn.close()

    @staticmethod
    def purge_user_data(user_id: str) -> int:
        """Executes GDPR Right-to-be-Forgotten purge on user sessions and turns."""
        conn = get_db_connection()
        cursor = conn.cursor()
        # Find all session_ids for user
        cursor.execute("SELECT session_id FROM sessions WHERE user_id = ?", (user_id,))
        session_ids = [r["session_id"] for r in cursor.fetchall()]
        for s_id in session_ids:
            cursor.execute("DELETE FROM conversation_turns WHERE session_id = ?", (s_id,))
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM saga_transactions WHERE user_id = ?", (user_id,))
        conn.commit()
        deleted_count = len(session_ids)
        conn.close()
        return deleted_count
