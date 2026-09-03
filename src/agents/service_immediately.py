"""ServiceImmediately ITSM Sub-Agent.

Strictly conforms to SDD Section 3.1, 5.3, and Table 5.6.
"""

from typing import Dict, Any, Optional, List
from src.integrations.service_immediately_client import ServiceImmediatelyClient

class ServiceImmediatelyAgent:
    def __init__(self, client: Optional[ServiceImmediatelyClient] = None):
        self.client = client or ServiceImmediatelyClient()

    def list_tickets(self, requested_by: str) -> Dict[str, Any]:
        success, tix = self.client.get_tickets(requested_by=requested_by)
        if success:
            return {
                "status": "SUCCESS",
                "tickets": tix,
                "count": len(tix),
                "message": f"Found {len(tix)} tickets for {requested_by}."
            }
        return {"status": "ERROR", "message": "Failed to retrieve tickets."}

    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        success, ticket = self.client.get_ticket(ticket_id)
        if success and ticket:
            return {"status": "SUCCESS", "ticket": ticket}
        return {"status": "ERROR", "message": f"Ticket {ticket_id} not found."}

    def create_incident(
        self,
        requested_by: str,
        category: str,
        short_description: str,
        priority: str = "3 - Moderate",
        assignment_group: str = "Service Desk",
        user_override: bool = False
    ) -> Dict[str, Any]:
        """Creates an incident ticket, rendering a disambiguation card if a duplicate is detected."""
        success, res = self.client.create_ticket(
            requested_by=requested_by,
            category=category,
            short_description=short_description,
            priority=priority,
            assignment_group=assignment_group,
            user_override=user_override
        )

        if not success:
            if res.get("requires_disambiguation"):
                conflict_id = res.get("conflict_ticket_id")
                return {
                    "status": "DISAMBIGUATION_REQUIRED",
                    "card_type": "DUPLICATE_DISAMBIGUATION",
                    "conflict_ticket_id": conflict_id,
                    "message": res.get("message"),
                    "options": [
                        {
                            "id": "ADD_COMMENT",
                            "label": f"Add Comment to Open Ticket ({conflict_id})",
                            "action": "APPEND_COMMENT",
                            "ticket_id": conflict_id
                        },
                        {
                            "id": "OVERRIDE_CREATE",
                            "label": "File as Separate New Ticket",
                            "action": "FORCE_CREATE_TICKET"
                        }
                    ]
                }
            return {
                "status": "ERROR",
                "error_code": res.get("error_code", "ERR_SI_CREATE_FAILED"),
                "message": res.get("message", "Incident creation failed.")
            }

        ticket_id = res.get("ticket_id")
        return {
            "status": "SUCCESS",
            "ticket_id": ticket_id,
            "message": f"Incident {ticket_id} has been created with priority '{priority}' and routed to {assignment_group}."
        }

    def add_comment(self, ticket_id: str, author: str, comment_text: str) -> Dict[str, Any]:
        success, res = self.client.add_comment(ticket_id, author, comment_text)
        if success:
            return {
                "status": "SUCCESS",
                "ticket_id": ticket_id,
                "message": f"Added note to ticket {ticket_id}: '{comment_text}'"
            }
        return {"status": "ERROR", "message": res.get("detail", "Failed to add comment")}

    def update_status(self, ticket_id: str, status: str, resolution_notes: str = "", updated_by: str = "Service Desk") -> Dict[str, Any]:
        success, res = self.client.update_status(ticket_id, status, resolution_notes, updated_by)
        if success:
            return {
                "status": "SUCCESS",
                "ticket_id": ticket_id,
                "ticket_status": status,
                "message": f"Ticket {ticket_id} transitioned to '{status}'."
            }
        return {"status": "ERROR", "message": res.get("detail", "Failed to update status")}
