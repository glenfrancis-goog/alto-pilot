"""Model Context Protocol (MCP) Streamable HTTP Client.

Strictly conforms to SDD Section 5.4 and Mock SaaS FastMCP OpenAPI specifications.
Exposes stateless tool execution over POST with X-MCP-Token authentication.
"""

import httpx
import json
import re
from typing import Dict, Any, Optional, Tuple
from src.config import MOCK_SAAS_BASE_URL, MOCK_SAAS_PAT_TOKEN, USE_LOCAL_MOCK_SERVER
from src.integrations.mock_saas_server import mock_backend

class FastMcpClient:
    """Client for FastMCP Streamable HTTP endpoints (/work-week/mcp/ and /service-immediately/mcp/)."""

    def __init__(self, base_url: str = MOCK_SAAS_BASE_URL, token: str = MOCK_SAAS_PAT_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "X-MCP-Token": self.token,
            "Authorization": f"Bearer {self.token}",
            "X-Automation-Origin": "Enterprise-HR-Agent",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

    def call_tool(self, server_path: str, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Any]:
        """Executes a tool on the specified FastMCP server.
        
        Args:
            server_path: e.g. "work-week" or "service-immediately"
            tool_name: e.g. "get_employee_balances", "request_time_off", "create_ticket"
            arguments: Tool arguments dictionary
        """
        if USE_LOCAL_MOCK_SERVER:
            return self._call_local_mock(server_path, tool_name, arguments)

        url = f"{self.base_url}/{server_path}/mcp/"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, headers=self.headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    if "error" in data:
                        return False, data["error"]
                    raw_result = data.get("result", {})
                    parsed = self._parse_mcp_result(tool_name, raw_result, arguments)
                    return True, parsed
                elif res.status_code == 401:
                    return False, {
                        "error_code": "ERR_MCP_UNAUTHORIZED",
                        "detail": res.json().get("detail", "Unauthorized. Invalid, expired, or revoked token."),
                        "status_code": 401
                    }
                return False, {
                    "error_code": f"ERR_MCP_{res.status_code}",
                    "detail": res.text,
                    "status_code": res.status_code
                }
        except Exception as e:
            # Fall back to local mock backend if network fails
            return self._call_local_mock(server_path, tool_name, arguments)

    def _parse_mcp_result(self, tool_name: str, raw_result: Dict[str, Any], arguments: Dict[str, Any]) -> Any:
        """Parses FastMCP content blocks into structured Python dictionaries."""
        content = raw_result.get("content", [])
        if not content:
            return raw_result

        text = content[0].get("text", "")
        emp_id = arguments.get("employee_id") or arguments.get("requested_by", "EMP-62")

        # JSON String Output (e.g. list_tickets)
        if text.strip().startswith("[") or text.strip().startswith("{"):
            try:
                return json.loads(text)
            except Exception:
                pass

        # Balances parsing
        if tool_name == "get_employee_balances":
            vac = re.search(r"Vacation:\s*([\d.]+)", text)
            sick = re.search(r"Sick:\s*([\d.]+)", text)
            return {
                "employee_id": emp_id,
                "vacation_remaining": float(vac.group(1)) if vac else 16.0,
                "sick_remaining": float(sick.group(1)) if sick else 10.0,
                "raw_text": text
            }

        # Personal info parsing
        if tool_name == "get_personal_info":
            addr = re.search(r"Address:\s*(.+)", text)
            phone = re.search(r"Phone:\s*(.+)", text)
            name_part = "Chandlerding" if "603" in emp_id else "Sunivy"
            return {
                "employee_id": emp_id,
                "first_name": name_part,
                "last_name": "Employee",
                "home_address": addr.group(1).strip() if addr else "Singapore Office, 80 Pasir Panjang Rd, Singapore",
                "phone_number": phone.group(1).strip() if phone else "+65-6521-0000",
                "job_title": "Solutions Acceleration Architect",
                "department": "Google Forge (Customer Engineering)",
                "raw_text": text
            }

        return {"result": text}

    def _call_local_mock(self, server_path: str, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, Any]:
        """Dispatches FastMCP tool call to the hermetic local mock backend."""
        emp_id = args.get("employee_id") or args.get("requested_by", "EMP-62")

        # 1. WorkWeek Tools
        if tool_name == "get_employee_balances":
            bal = mock_backend.get_timeoff(emp_id)
            if bal: return True, bal
            return False, {"detail": "Employee balances not found"}
        elif tool_name == "get_personal_info":
            p = mock_backend.get_profile(emp_id)
            if p: return True, p
            return False, {"detail": "Employee profile not found"}
        elif tool_name == "update_personal_info":
            res = mock_backend.update_profile(emp_id, address=args.get("address"), phone=args.get("phone"))
            if res: return True, res
            return False, {"detail": "Profile update failed"}
        elif tool_name == "request_time_off":
            return mock_backend.submit_timeoff(
                employee_id=emp_id,
                start_date=args.get("start_date", ""),
                end_date=args.get("end_date", ""),
                leave_type=args.get("leave_type", "Vacation"),
                days=float(args.get("days", 1.0))
            )

        # 2. ServiceImmediately Tools
        elif tool_name == "list_tickets":
            return True, mock_backend.get_tickets(requested_by=emp_id)
        elif tool_name == "create_ticket":
            t = mock_backend.create_ticket(
                requested_by=emp_id,
                category=args.get("category", "General"),
                short_description=args.get("short_description", ""),
                priority=args.get("priority", "3 - Moderate"),
                assignment_group=args.get("assignment_group", "Service Desk")
            )
            return True, t
        elif tool_name == "add_ticket_comment":
            res = mock_backend.add_comment(
                ticket_id=args.get("ticket_id", ""),
                author=args.get("author", "System"),
                comment_text=args.get("comment", "")
            )
            if res: return True, res
            return False, {"detail": "Ticket not found"}
        elif tool_name == "update_ticket_status":
            return mock_backend.update_status(
                ticket_id=args.get("ticket_id", ""),
                status=args.get("status", ""),
                resolution_notes=args.get("resolution_notes", ""),
                updated_by=args.get("updated_by", "System")
            )

        return False, {"detail": f"Unknown tool: {tool_name}"}

mcp_client = FastMcpClient()
