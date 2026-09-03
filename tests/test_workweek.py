"""Tests for WorkWeek HCM Agent."""

import pytest
from src.agents.workweek import WorkWeekAgent

@pytest.fixture
def ww_agent():
    return WorkWeekAgent()

def test_get_profile(ww_agent):
    res = ww_agent.get_profile("EMP-62")
    assert res["status"] == "SUCCESS"
    assert res["profile"]["first_name"] == "Sunivy"
    assert res["profile"]["email"] == "sunivy@google.com"

def test_get_leave_balances(ww_agent):
    res = ww_agent.get_timeoff_balance("EMP-62")
    assert res["status"] == "SUCCESS"
    assert res["vacation_remaining"] == 18.0
    assert res["sick_remaining"] == 10.0

def test_prepare_leave_confirmation(ww_agent):
    res = ww_agent.prepare_leave_confirmation(
        employee_id="EMP-62",
        start_date="2026-09-03",
        end_date="2026-09-04",
        leave_type="Vacation",
        days=2.0
    )
    assert res["status"] == "CONFIRMATION_REQUIRED"
    assert res["card_type"] == "PREFLIGHT_CONFIRMATION"
    assert res["parameters"]["balance_after"] == 16.0

def test_leave_balance_exceeded(ww_agent):
    res = ww_agent.prepare_leave_confirmation(
        employee_id="EMP-62",
        start_date="2026-09-03",
        end_date="2026-09-30",
        leave_type="Vacation",
        days=25.0
    )
    assert res["status"] == "REJECTED"
    assert res["error_code"] == "ERR_WW_BALANCE_EXCEEDED_007"

def test_execute_leave_submission(ww_agent):
    res = ww_agent.execute_leave_submission(
        employee_id="EMP-62",
        start_date="2026-09-03",
        end_date="2026-09-04",
        leave_type="Vacation",
        days=2.0
    )
    assert res["status"] == "SUCCESS"
    assert res["remaining_days"] == 16.0

def test_update_contact_profile(ww_agent):
    res = ww_agent.update_profile("EMP-62", address="London Office, 1 St Giles High St", phone="+44 20 7031 3000")
    assert res["status"] == "SUCCESS"
    assert res["updated_data"]["home_address"] == "London Office, 1 St Giles High St"
