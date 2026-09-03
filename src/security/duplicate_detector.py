"""ServiceImmediately Guardrails & Duplicate Mitigation Engine.

Strictly conforms to SDD Section 1.2, 5.3, and TC-ITSM-DUP-01 calibration.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
import math

class DuplicateDetector:
    """Hybrid Temporal & Semantic Similarity Duplicate Mitigation with User Override."""

    def __init__(self, window_minutes: int = 120, similarity_threshold: float = 0.88):
        self.window_minutes = window_minutes
        self.similarity_threshold = similarity_threshold

    def _cosine_similarity(self, text_a: str, text_b: str) -> float:
        """Computes word-vector cosine similarity (fallback embedding representation)."""
        words_a = set(re_words(text_a.lower()))
        words_b = set(re_words(text_b.lower()))
        if not words_a or not words_b:
            return 0.0
        intersection = words_a.intersection(words_b)
        return len(intersection) / (math.sqrt(len(words_a)) * math.sqrt(len(words_b)))

    def check_duplicate(
        self,
        employee_id: str,
        category: str,
        description: str,
        existing_tickets: List[Dict[str, Any]],
        user_override: bool = False
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Evaluates whether an incoming ticket request is a duplicate.
        
        Returns:
            (is_duplicate_blocked, conflicting_ticket, disambiguation_message)
        """
        if user_override:
            # User chose to override disambiguation and file as separate new ticket
            return False, None, None

        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(minutes=self.window_minutes)

        for ticket in existing_tickets:
            # Only compare active/open tickets belonging to the same employee
            if ticket.get("requested_by") != employee_id:
                continue
            if ticket.get("status") in ("Closed", "Cancelled"):
                continue

            # Check temporal window (created_at within 120 mins)
            created_at_str = ticket.get("created_at")
            if created_at_str:
                try:
                    # Clean ISO format
                    dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if dt < cutoff_time:
                        continue
                except Exception:
                    pass

            # Check semantic similarity of description
            existing_desc = ticket.get("short_description", "")
            sim = self._cosine_similarity(description, existing_desc)

            if sim >= self.similarity_threshold or (category == ticket.get("category") and sim >= 0.80):
                ticket_id = ticket.get("ticket_id", "UNKNOWN")
                msg = (
                    f"We noticed an active ticket ({ticket_id}: '{existing_desc[:60]}...') "
                    f"submitted recently. Would you like to add a comment to that ticket, "
                    f"or proceed with filing this as a separate ticket?"
                )
                return True, ticket, msg

        return False, None, None


def re_words(text: str) -> List[str]:
    import re
    return re.findall(r"\b\w{3,}\b", text)
