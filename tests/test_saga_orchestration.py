"""Tests for Cross-System SAGA Orchestration Engine."""

import pytest
from src.agents.saga_coordinator import SagaCoordinator
from src.storage.repository import SessionRepository

@pytest.fixture
def saga_coordinator():
    return SagaCoordinator()

def test_uc_2_1_equipment_procurement_duplicate_handled(saga_coordinator):
    # Monitor request triggers duplicate scan against INC0000827
    res = saga_coordinator.execute_equipment_procurement(
        session_id="session-test-01",
        employee_id="EMP-62",
        equipment_type="27-inch Monitor"
    )
    assert res["status"] in ("SUCCESS", "DISAMBIGUATION_REQUIRED")

def test_uc_2_2_medical_leave_success(saga_coordinator):
    res = saga_coordinator.execute_medical_leave(
        session_id="session-test-02",
        employee_id="EMP-62",
        start_date="2026-09-07",
        end_date="2026-09-11",
        days=5.0
    )
    assert res["status"] == "SUCCESS"
    assert "ticket_id" in res
    assert "Medical leave booked" in res["message"]

def test_uc_2_2_medical_leave_compensation_on_ticket_fail(saga_coordinator):
    # Simulates ServiceImmediately failure triggering Cloud Workflows SAGA Compensation
    res = saga_coordinator.execute_medical_leave(
        session_id="session-test-03",
        employee_id="EMP-62",
        start_date="2026-09-14",
        end_date="2026-09-18",
        days=5.0,
        simulate_ticket_fail=True
    )
    assert res["status"] == "COMPENSATED"
    assert "Jane Doe" in res["message"]
    assert "SAGA-MED-" in res["saga_id"]

def test_uc_2_3_employee_relocation(saga_coordinator):
    res = saga_coordinator.execute_employee_relocation(
        session_id="session-test-04",
        employee_id="EMP-62",
        new_address="London Office, 1 St Giles High St, London WC2H 8AG",
        phone="+44 20 7031 3000"
    )
    assert res["status"] == "SUCCESS"
    assert "£5,000" in res["message"]
    assert "ticket_id" in res

def test_uc_privacy_01_gdpr_rtbf_purge(saga_coordinator):
    # First record a turn in AlloyDB
    SessionRepository.get_or_create_session("session-purge-01", "EMP-62")
    SessionRepository.record_turn("session-purge-01", 1, "user", "Sensitive personal chat")

    # Execute purge
    res = saga_coordinator.execute_gdpr_rtbf_purge("EMP-62")
    assert res["status"] == "SUCCESS"
    assert "receipt_hash" in res
    assert res["receipt_hash"].startswith("RTBF-")
    assert res["purged_sessions_count"] >= 1

    # Verify session is erased
    turns = SessionRepository.get_turns("session-purge-01")
    assert len(turns) == 0
