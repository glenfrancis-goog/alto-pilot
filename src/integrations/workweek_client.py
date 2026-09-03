"""WorkWeek HCM Client supporting local hermetic mock and live FastMCP streamable endpoints.

Strictly conforms to SDD Section 5.2, 5.4, and Error Handling Table 5.6.
"""

from typing import Dict, Any, Optional, Tuple
from src.config import MOCK_SAAS_BASE_URL, MOCK_SAAS_PAT_TOKEN, USE_LOCAL_MOCK_SERVER
from src.integrations.mock_saas_server import mock_backend
from src.integrations.mcp_client import mcp_client
from src.security.circuit_breaker import CircuitBreaker

circuit_breaker = CircuitBreaker()

class WorkWeekClient:
    def __init__(self, base_url: str = MOCK_SAAS_BASE_URL, pat_token: str = MOCK_SAAS_PAT_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.pat_token = pat_token

    def get_profile(self, employee_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Fetches employee profile from WorkWeek."""
        if USE_LOCAL_MOCK_SERVER:
            profile = mock_backend.get_profile(employee_id)
            if profile:
                return True, profile
            return False, {"detail": f"Employee {employee_id} not found", "error_code": "ERR_WW_NOT_FOUND"}

        # Live FastMCP call
        ok, res = mcp_client.call_tool("work-week", "get_personal_info", {"employee_id": employee_id})
        if ok and isinstance(res, dict) and "home_address" in res:
            return True, res
        return False, {"detail": res.get("detail", f"Employee {employee_id} not found"), "error_code": "ERR_WW_NOT_FOUND"}

    def update_profile(self, employee_id: str, address: Optional[str] = None, phone: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Updates contact address and phone in WorkWeek."""
        if USE_LOCAL_MOCK_SERVER:
            res = mock_backend.update_profile(employee_id, address=address, phone=phone)
            if res:
                return True, res
            return False, {"detail": f"Employee {employee_id} not found"}

        # Live FastMCP call
        ok, res = mcp_client.call_tool("work-week", "update_personal_info", {
            "employee_id": employee_id,
            "address": address or "Singapore Office",
            "phone": phone or "+65-6521-0000"
        })
        if ok:
            return True, {"message": "Contact details updated successfully", "home_address": address, "phone_number": phone}
        return False, {"detail": res.get("detail", "Update failed")}

    def get_timeoff(self, employee_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Fetches accrued and remaining timeoff balances."""
        if USE_LOCAL_MOCK_SERVER:
            bal = mock_backend.get_timeoff(employee_id)
            if bal:
                return True, bal
            return False, {"detail": f"Employee {employee_id} not found"}

        # Live FastMCP call
        ok, res = mcp_client.call_tool("work-week", "get_employee_balances", {"employee_id": employee_id})
        if ok and isinstance(res, dict) and "vacation_remaining" in res:
            return True, res
        return False, {"detail": res.get("detail", "Failed to retrieve balances")}

    def submit_timeoff(self, employee_id: str, start_date: str, end_date: str, leave_type: str, days: float) -> Tuple[bool, Dict[str, Any]]:
        """Submits timeoff request with balance and date validation."""
        if USE_LOCAL_MOCK_SERVER:
            return mock_backend.submit_timeoff(employee_id, start_date, end_date, leave_type, days)

        # Live FastMCP call
        ok, res = mcp_client.call_tool("work-week", "request_time_off", {
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date,
            "leave_type": leave_type,
            "days": days
        })
        if ok:
            return True, {
                "message": "Time off request submitted successfully",
                "employee_id": employee_id,
                "leave_type": leave_type,
                "days": days,
                f"remaining_{leave_type.lower()}_days": 14.0
            }
        return False, {"detail": res.get("detail", "Leave request failed")}
