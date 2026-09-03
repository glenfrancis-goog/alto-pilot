"""Tests for FastMCP client integration."""

import pytest
from src.integrations.mcp_client import FastMcpClient

@pytest.fixture
def mcp():
    return FastMcpClient()

def test_workweek_mcp_get_balances(mcp):
    ok, res = mcp.call_tool("work-week", "get_employee_balances", {"employee_id": "EMP-62"})
    assert ok is True
    assert res["vacation_remaining"] == 18.0
    assert res["sick_remaining"] == 10.0

def test_workweek_mcp_get_profile(mcp):
    ok, res = mcp.call_tool("work-week", "get_personal_info", {"employee_id": "EMP-62"})
    assert ok is True
    assert res["first_name"] == "Sunivy"
    assert res["employee_id"] == "EMP-62"

def test_service_immediately_mcp_list_tickets(mcp):
    ok, res = mcp.call_tool("service-immediately", "list_tickets", {"employee_id": "EMP-62"})
    assert ok is True
    assert len(res) >= 1
    assert any(t["ticket_id"] == "INC0000827" for t in res)

def test_service_immediately_mcp_create_ticket(mcp):
    ok, res = mcp.call_tool("service-immediately", "create_ticket", {
        "requested_by": "EMP-62",
        "category": "Hardware",
        "short_description": "Ergonomic keyboard replacement",
        "priority": "3 - Moderate"
    })
    assert ok is True
    assert res["ticket_id"].startswith("INC")
