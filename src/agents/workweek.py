"""WorkWeek HCM Sub-Agent.

Strictly conforms to SDD Section 3.1, 3.2 (Sequence 2), and Section 5.2.
"""

from typing import Dict, Any, Optional
from src.integrations.workweek_client import WorkWeekClient

class WorkWeekAgent:
    def __init__(self, client: Optional[WorkWeekClient] = None):
        self.client = client or WorkWeekClient()

    def get_profile(self, employee_id: str) -> Dict[str, Any]:
        success, data = self.client.get_profile(employee_id)
        if success:
            return {
                "status": "SUCCESS",
                "employee_id": employee_id,
                "profile": data,
                "message": f"Retrieved profile for {data.get('first_name')} {data.get('last_name')}"
            }
        return {"status": "ERROR", "detail": data.get("detail", "Profile retrieval failed")}

    def update_profile(self, employee_id: str, address: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        success, data = self.client.update_profile(employee_id, address=address, phone=phone)
        if success:
            return {
                "status": "SUCCESS",
                "employee_id": employee_id,
                "message": "Contact details updated successfully",
                "updated_data": data
            }
        return {"status": "ERROR", "detail": data.get("detail", "Profile update failed")}

    def get_timeoff_balance(self, employee_id: str) -> Dict[str, Any]:
        success, data = self.client.get_timeoff(employee_id)
        if success:
            return {
                "status": "SUCCESS",
                "employee_id": employee_id,
                "vacation_remaining": data.get("vacation_remaining"),
                "sick_remaining": data.get("sick_remaining"),
                "message": (
                    f"Your available leave balances: "
                    f"**Vacation:** {data.get('vacation_remaining')} days | "
                    f"**Sick Leave:** {data.get('sick_remaining')} days"
                )
            }
        return {"status": "ERROR", "detail": data.get("detail", "Timeoff balance query failed")}

    def prepare_leave_confirmation(self, employee_id: str, start_date: str, end_date: str, leave_type: str, days: float) -> Dict[str, Any]:
        """Pre-flight check and human-in-the-loop confirmation card generation."""
        success, bal = self.client.get_timeoff(employee_id)
        if not success:
            return {"status": "ERROR", "detail": "Could not verify leave balances."}

        rem = bal.get(f"{leave_type.lower()}_remaining", 0.0)
        if days > rem:
            return {
                "status": "REJECTED",
                "error_code": "ERR_WW_BALANCE_EXCEEDED_007",
                "message": f"Your leave request cannot be submitted because it exceeds your available balance (Remaining: {rem} days)."
            }

        bal_after = rem - days
        return {
            "status": "CONFIRMATION_REQUIRED",
            "card_type": "PREFLIGHT_CONFIRMATION",
            "action": "SUBMIT_LEAVE",
            "parameters": {
                "employee_id": employee_id,
                "start_date": start_date,
                "end_date": end_date,
                "leave_type": leave_type,
                "days": days,
                "balance_after": bal_after
            },
            "message": (
                f"Please confirm leave request: **{leave_type}**, **{days} days** ({start_date} to {end_date}). "
                f"Remaining balance after: **{bal_after} days**."
            )
        }

    def execute_leave_submission(self, employee_id: str, start_date: str, end_date: str, leave_type: str, days: float) -> Dict[str, Any]:
        """Executes the confirmed leave request."""
        success, res = self.client.submit_timeoff(employee_id, start_date, end_date, leave_type, days)
        if success:
            rem = res.get(f"remaining_{leave_type.lower()}_days")
            return {
                "status": "SUCCESS",
                "message": (
                    f"Your {leave_type.lower()} leave request for {start_date} to {end_date} ({days} days) "
                    f"has been submitted. Your remaining balance is {rem} days."
                ),
                "remaining_days": rem
            }
        return {
            "status": "ERROR",
            "message": res.get("detail", "Failed to submit leave request")
        }
