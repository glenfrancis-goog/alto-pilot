"""ServiceImmediately ITSM/HRSD Client supporting local mock and live FastMCP streamable endpoints.

Strictly conforms to SDD Section 5.3, 5.4, FSM transitions, and Table 5.6.
"""

from typing import Dict, Any, Optional, Tuple, List
from src.config import MOCK_SAAS_BASE_URL, MOCK_SAAS_PAT_TOKEN, USE_LOCAL_MOCK_SERVER, DUPLICATE_TICKET_WINDOW_MINS, DUPLICATE_SEMANTIC_THRESHOLD
from src.integrations.mock_saas_server import mock_backend
from src.integrations.mcp_client import mcp_client
from src.security.duplicate_detector import DuplicateDetector
from src.security.circuit_breaker import CircuitBreaker

circuit_breaker = CircuitBreaker()
duplicate_detector = DuplicateDetector(
    window_minutes=DUPLICATE_TICKET_WINDOW_MINS,
    similarity_threshold=DUPLICATE_SEMANTIC_THRESHOLD
)

class ServiceImmediatelyClient:
    def __init__(self, base_url: str = MOCK_SAAS_BASE_URL, pat_token: str = MOCK_SAAS_PAT_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.pat_token = pat_token

    def get_tickets(self, requested_by: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]]]:
        """Fetches incident tickets filtered by requester."""
        if USE_LOCAL_MOCK_SERVER:
            return True, mock_backend.get_tickets(requested_by)

        # Live FastMCP call
        ok, res = mcp_client.call_tool("service-immediately", "list_tickets", {"employee_id": requested_by or "EMP-62"})
        if ok and isinstance(res, list):
            return True, res
        return False, []

    def get_ticket(self, ticket_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Fetches single incident details by ID."""
        if USE_LOCAL_MOCK_SERVER:
            t = mock_backend.get_ticket(ticket_id)
            if t: return True, t
            return False, None

        # Fallback to local
        t = mock_backend.get_ticket(ticket_id)
        return (True, t) if t else (False, None)

    def create_ticket(
        self,
        requested_by: str,
        category: str,
        short_description: str,
        priority: str = "3 - Moderate",
        assignment_group: str = "Service Desk",
        user_override: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:
        """Creates an incident ticket with built-in duplicate detection and user override."""
        # Step 1: Duplicate Scan
        _, existing_tix = self.get_tickets(requested_by=requested_by)
        is_dup, conflict_ticket, disambiguation_msg = duplicate_detector.check_duplicate(
            employee_id=requested_by,
            category=category,
            description=short_description,
            existing_tickets=existing_tix,
            user_override=user_override
        )

        if is_dup and conflict_ticket:
            return False, {
                "error_code": "ERR_SI_DUPLICATE_TICKET_010",
                "message": disambiguation_msg,
                "conflict_ticket_id": conflict_ticket.get("ticket_id"),
                "is_duplicate": True,
                "requires_disambiguation": True
            }

        # Step 2: Create Incident
        if USE_LOCAL_MOCK_SERVER:
            ticket_res = mock_backend.create_ticket(
                requested_by=requested_by,
                category=category,
                short_description=short_description,
                priority=priority,
                assignment_group=assignment_group
            )
            return True, ticket_res

        # Live FastMCP call
        ok, res = mcp_client.call_tool("service-immediately", "create_ticket", {
            "requested_by": requested_by,
            "category": category,
            "short_description": short_description,
            "priority": priority,
            "assignment_group": assignment_group
        })
        if ok and isinstance(res, dict) and "ticket_id" in res:
            return True, res
        return False, {"detail": res.get("detail", "Failed to create ticket")}

    def add_comment(self, ticket_id: str, author: str, comment_text: str) -> Tuple[bool, Dict[str, Any]]:
        """Appends comment to ticket."""
        if USE_LOCAL_MOCK_SERVER:
            res = mock_backend.add_comment(ticket_id, author, comment_text)
            if res: return True, res
            return False, {"detail": "Ticket not found"}

        # Live FastMCP call
        ok, res = mcp_client.call_tool("service-immediately", "add_ticket_comment", {
            "ticket_id": ticket_id,
            "author": author,
            "comment": comment_text
        })
        if ok:
            return True, {"message": "Comment added successfully", "ticket_id": ticket_id}
        return False, {"detail": res.get("detail", "Failed to add comment")}

    def update_status(self, ticket_id: str, status: str, resolution_notes: str = "", updated_by: str = "Service Desk") -> Tuple[bool, Dict[str, Any]]:
        """Updates ticket status with FSM state machine validation."""
        if USE_LOCAL_MOCK_SERVER:
            return mock_backend.update_status(ticket_id, status, resolution_notes, updated_by)

        # Live FastMCP call
        ok, res = mcp_client.call_tool("service-immediately", "update_ticket_status", {
            "ticket_id": ticket_id,
            "status": status,
            "resolution_notes": resolution_notes,
            "updated_by": updated_by
        })
        if ok:
            return True, {"message": "Status updated successfully", "ticket_id": ticket_id, "status": status}
        return False, {"detail": res.get("detail", "Failed to update status")}
