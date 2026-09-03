"""Tests for ServiceImmediately ITSM Agent."""

import pytest
from src.agents.service_immediately import ServiceImmediatelyAgent

@pytest.fixture
def si_agent():
    return ServiceImmediatelyAgent()

def test_list_tickets(si_agent):
    res = si_agent.list_tickets("EMP-62")
    assert res["status"] == "SUCCESS"
    assert res["count"] >= 1
    assert any(t["ticket_id"] == "INC0000827" for t in res["tickets"])

def test_create_ticket_duplicate_detected(si_agent):
    # Attempting to file identical monitor request within 120 minutes
    res = si_agent.create_incident(
        requested_by="EMP-62",
        category="Hardware",
        short_description="Request for 27-inch Monitor for remote work setup. Delivery address: Singapore Office, 80 Pasir Panjang Rd, Singapore."
    )
    assert res["status"] == "DISAMBIGUATION_REQUIRED"
    assert res["conflict_ticket_id"] == "INC0000827"
    assert len(res["options"]) == 2

def test_create_ticket_user_override(si_agent):
    # User override enables legitimate consecutive filing
    res = si_agent.create_incident(
        requested_by="EMP-62",
        category="Hardware",
        short_description="Request for 27-inch Monitor for remote work setup. Delivery address: Singapore Office, 80 Pasir Panjang Rd, Singapore.",
        user_override=True
    )
    assert res["status"] == "SUCCESS"
    assert res["ticket_id"].startswith("INC")
    assert res["ticket_id"] != "INC0000827"

def test_add_comment_to_ticket(si_agent):
    res = si_agent.add_comment("INC0000827", "Sunivy Employee", "Please note delivery is urgent.")
    assert res["status"] == "SUCCESS"
    assert res["ticket_id"] == "INC0000827"

def test_fsm_illegal_transition_blocked(si_agent):
    # Direct New -> Closed is blocked by FSM rules
    res = si_agent.update_status("INC0000827", "Closed")
    assert res["status"] == "ERROR"
    assert "cannot be closed directly from 'New'" in res["message"]

def test_fsm_valid_transition(si_agent):
    # New -> Resolved is permitted
    res = si_agent.update_status("INC0000827", "Resolved", resolution_notes="Monitor handed over")
    assert res["status"] == "SUCCESS"
    assert res["status_code"] if "status_code" in res else True
