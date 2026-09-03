"""In-Memory / Hermetic Mock Enterprise Services Server (WorkWeek & ServiceImmediately).

Strictly conforms to SDD Section 5.2, 5.3, and OpenAPI specification v1.0.0.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import copy

class MockEnterpriseBackend:
    """Hermetic in-memory store matching the live Mock SaaS API."""

    def __init__(self):
        self.reset_data()

    def reset_data(self):
        self.employees = {
            "EMP-62": {
                "employee_id": "EMP-62",
                "first_name": "Sunivy",
                "last_name": "Employee",
                "email": "sunivy@google.com",
                "job_title": "Solutions Acceleration Architect",
                "department": "Google Forge (Customer Engineering)",
                "role": "Individual Contributor",
                "hire_date": "2026-07-28",
                "manager_id": "EMP-1",
                "manager_name": "Vicky Falconer",
                "home_address": "Singapore Office, 80 Pasir Panjang Rd, Singapore",
                "phone_number": "+65 9123 4567",
                "supervisory_org": None,
            },
            "EMP-603": {
                "employee_id": "EMP-603",
                "first_name": "Chandlerding",
                "last_name": "Employee",
                "email": "chandlerding@google.com",
                "job_title": "Solutions Acceleration Architect",
                "department": "Google Forge (Customer Engineering)",
                "role": "Individual Contributor",
                "hire_date": "2026-07-28",
                "manager_id": "EMP-1",
                "manager_name": "Vicky Falconer",
                "home_address": "Singapore Office, 80 Pasir Panjang Rd, Singapore",
                "phone_number": "+65 9123 4567",
                "supervisory_org": None,
            }
        }
        self.timeoff_balances = {
            "EMP-62": {
                "employee_id": "EMP-62",
                "vacation_accrued": 20.0,
                "vacation_used": 2.0,
                "sick_accrued": 10.0,
                "sick_used": 0.0,
                "vacation_remaining": 18.0,
                "sick_remaining": 10.0,
            },
            "EMP-603": {
                "employee_id": "EMP-603",
                "vacation_accrued": 20.0,
                "vacation_used": 4.0,
                "sick_accrued": 14.0,
                "sick_used": 4.0,
                "vacation_remaining": 16.0,
                "sick_remaining": 10.0,
            }
        }
        self.timeoff_requests = {
            "EMP-62": [],
            "EMP-603": []
        }
        self.ticket_counter = 830
        self.tickets = {
            "INC0000827": {
                "ticket_id": "INC0000827",
                "requested_by": "EMP-62",
                "caller_name": "Sunivy Employee",
                "category": "Hardware",
                "short_description": "Request for 27-inch Monitor for remote work setup. Delivery address: Singapore Office, 80 Pasir Panjang Rd, Singapore.",
                "status": "New",
                "priority": "3 - Moderate",
                "assignment_group": "Service Desk",
                "assigned_to": "",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin",
                "comments": [
                    {
                        "id": 1235,
                        "ticket_id": "INC0000827",
                        "author": "System",
                        "comment_text": "Ticket created by user via API.",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                ]
            },
            "INC0000009": {
                "ticket_id": "INC0000009",
                "requested_by": "EMP-62",
                "caller_name": "Sunivy Employee",
                "category": "Software",
                "short_description": "VPN access configuration for remote environment",
                "status": "In Progress",
                "priority": "3 - Moderate",
                "assignment_group": "Network Operations",
                "assigned_to": "NetOps Specialist",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "NetOps Specialist",
                "comments": [
                    {
                        "id": 1009,
                        "ticket_id": "INC0000009",
                        "author": "NetOps Specialist",
                        "comment_text": "Configuring certificate routing profile.",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                ]
            },
            "INC882910": {
                "ticket_id": "INC882910",
                "requested_by": "EMP-62",
                "caller_name": "Sunivy Employee",
                "category": "Hardware",
                "short_description": "Headset replacement request",
                "status": "New",
                "priority": "4 - Low",
                "assignment_group": "Service Desk",
                "assigned_to": "",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "admin",
                "comments": []
            },
            "INC0003709": {
                "ticket_id": "INC0003709",
                "requested_by": "EMP-603",
                "caller_name": "Chandlerding Employee",
                "category": "Hardware",
                "short_description": "Singapore Office hardware requisition and peripheral setup.",
                "status": "In Progress",
                "priority": "3 - Moderate",
                "assignment_group": "Service Desk",
                "assigned_to": "Vicky Falconer",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "comments": []
            }
        }

    # ==================== WORKWEEK API ====================

    def get_profile(self, employee_id: str) -> Optional[Dict[str, Any]]:
        emp = self.employees.get(employee_id)
        return copy.deepcopy(emp) if emp else None

    def update_profile(self, employee_id: str, address: Optional[str] = None, phone: Optional[str] = None) -> Optional[Dict[str, Any]]:
        emp = self.employees.get(employee_id)
        if not emp:
            return None
        if address:
            emp["home_address"] = address
        if phone:
            emp["phone_number"] = phone
        return {
            "message": "Contact details updated successfully",
            "employee_id": employee_id,
            "home_address": emp["home_address"],
            "phone_number": emp["phone_number"]
        }

    def get_timeoff(self, employee_id: str) -> Optional[Dict[str, Any]]:
        bal = self.timeoff_balances.get(employee_id)
        return copy.deepcopy(bal) if bal else None

    def submit_timeoff(self, employee_id: str, start_date: str, end_date: str, leave_type: str, days: float) -> Tuple[bool, Dict[str, Any]]:
        bal = self.timeoff_balances.get(employee_id)
        if not bal:
            return False, {"detail": "Employee timeoff profile not found"}

        # Validate dates
        try:
            d_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            d_end = datetime.strptime(end_date, "%Y-%m-%d").date()
            if d_start > d_end:
                return False, {"detail": "start_date cannot be after end_date"}
            num_calendar_days = (d_end - d_start).days + 1
            if days > num_calendar_days:
                return False, {
                    "detail": f"Requested duration ({days:.1f} days / {days*8:.1f} hours) exceeds calendar range ({num_calendar_days} day(s)). Single-day booking cannot exceed 8 hours. Transaction rolled back.",
                    "error_code": "ERR_WW_DURATION_LIMIT_EXCEEDED"
                }
        except ValueError:
            return False, {"detail": "Invalid date format. Use YYYY-MM-DD"}

        # Balance check
        if leave_type.lower() == "vacation":
            if days > bal["vacation_remaining"]:
                return False, {"detail": f"Insufficient vacation balance. Remaining: {bal['vacation_remaining']} days"}
            bal["vacation_used"] += days
            bal["vacation_remaining"] -= days
            rem = bal["vacation_remaining"]
        elif leave_type.lower() in ("sick", "medical"):
            if days > bal["sick_remaining"]:
                return False, {"detail": f"Insufficient sick leave balance. Remaining: {bal['sick_remaining']} days"}
            bal["sick_used"] += days
            bal["sick_remaining"] -= days
            rem = bal["sick_remaining"]
        else:
            rem = 0.0

        req_record = {
            "request_id": f"REQ-{len(self.timeoff_requests.get(employee_id, [])) + 101}",
            "start_date": start_date,
            "end_date": end_date,
            "leave_type": leave_type,
            "days": days,
            "status": "APPROVED",
            "submitted_at": datetime.now(timezone.utc).isoformat()
        }
        self.timeoff_requests.setdefault(employee_id, []).append(req_record)

        return True, {
            "message": "Time off request submitted successfully",
            "employee_id": employee_id,
            "leave_type": leave_type,
            "days": days,
            f"remaining_{leave_type.lower()}_days": rem
        }

    # ==================== SERVICEIMMEDIATELY API ====================

    def get_tickets(self, requested_by: Optional[str] = None) -> List[Dict[str, Any]]:
        tix = list(self.tickets.values())
        if requested_by:
            tix = [t for t in tix if t.get("requested_by") == requested_by]
        return copy.deepcopy(tix)

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        t = self.tickets.get(ticket_id)
        return copy.deepcopy(t) if t else None

    def create_ticket(self, requested_by: str, category: str, short_description: str, priority: str = "3 - Moderate", assignment_group: str = "Service Desk") -> Dict[str, Any]:
        self.ticket_counter += 1
        ticket_id = f"INC{self.ticket_counter:07d}"
        now_iso = datetime.now(timezone.utc).isoformat()

        emp = self.employees.get(requested_by, {})
        caller_name = f"{emp.get('first_name', 'Employee')} {emp.get('last_name', '')}".strip()

        ticket = {
            "ticket_id": ticket_id,
            "requested_by": requested_by,
            "caller_name": caller_name,
            "category": category,
            "short_description": short_description,
            "status": "New",
            "priority": priority,
            "assignment_group": assignment_group,
            "assigned_to": "",
            "created_at": now_iso,
            "updated_at": now_iso,
            "updated_by": requested_by,
            "comments": [
                {
                    "id": len(self.tickets) + 100,
                    "ticket_id": ticket_id,
                    "author": "System",
                    "comment_text": f"Incident created via Enterprise HR Agent for {requested_by}",
                    "created_at": now_iso
                }
            ]
        }
        self.tickets[ticket_id] = ticket
        return {
            "ticket_id": ticket_id,
            "requested_by": requested_by,
            "status": "New",
            "message": "Incident created successfully"
        }

    def add_comment(self, ticket_id: str, author: str, comment_text: str) -> Optional[Dict[str, Any]]:
        t = self.tickets.get(ticket_id)
        if not t:
            return None
        now_iso = datetime.now(timezone.utc).isoformat()
        t["comments"].append({
            "id": len(t["comments"]) + 100,
            "ticket_id": ticket_id,
            "author": author,
            "comment_text": comment_text,
            "created_at": now_iso
        })
        t["updated_at"] = now_iso
        return {
            "message": "Comment added successfully",
            "ticket_id": ticket_id
        }

    def update_status(self, ticket_id: str, status: str, resolution_notes: str = "", updated_by: str = "Service Desk") -> Tuple[bool, Dict[str, Any]]:
        t = self.tickets.get(ticket_id)
        if not t:
            return False, {"detail": "Ticket not found"}

        # Enforce FSM state machine rules
        current_status = t.get("status")
        if current_status == "New" and status == "Closed":
            return False, {"detail": f"Ticket {ticket_id} cannot be closed directly from 'New'. It must first be moved to 'Resolved' with notes."}

        t["status"] = status
        t["resolution_notes"] = resolution_notes
        t["updated_by"] = updated_by
        t["updated_at"] = datetime.now(timezone.utc).isoformat()
        return True, {
            "message": "Status updated successfully",
            "ticket_id": ticket_id,
            "status": status
        }

# Global singleton for in-memory backend
mock_backend = MockEnterpriseBackend()
