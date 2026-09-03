"""Multi-turn test suite for WorkWeek and ServiceImmediately integrated session turn logic.

Conforms strictly to remediation eval case design:
Turn 1: Queries accrued PTO -> WorkWeekAgent.
Turn 2: Submits a valid 8hr vacation request on Monday -> WorkWeekAgent.
Turn 3: Tries submitting a vacation request for 80 hours in 1 day (Validation failure rollback path).
Turn 4: Checks incident ticket INC0000009 -> ServiceImmediatelyAgent.
Turn 5: Expresses emergency on a squeaky chair, requesting P1 ticket -> ServiceImmediatelyAgent blocks escalation (anti-priority inflation).
Turn 6: Attempts updating INC882910 directly from New to Closed -> ServiceImmediatelyAgent blocks due to forbidden status transition.
"""

import pytest
import uuid
from src.agents.supervisor import SupervisorAgent

@pytest.fixture
def supervisor():
    return SupervisorAgent()

def test_ww_si_6turn_sequence(supervisor):
    session_id = f"test-ww-si-{uuid.uuid4().hex[:8]}"
    user_id = "EMP-62"

    # Turn 1: Accrued PTO inquiry
    t1 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="How many hours of PTO do I currently have accrued?",
        turn_index=1
    )
    assert "160.0 hours" in t1["response"]
    assert "vacation" in t1["response"].lower()
    assert t1["intermediate_checks"]["model_armor"]["is_input_safe"] is True
    assert len(t1["session_history"]) >= 2  # user + assistant

    # Turn 2: Valid 8-hour vacation request for Monday 2026-07-20
    t2 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Please submit a vacation request for next Monday, 2026-07-20, for 8 hours.",
        turn_index=3
    )
    assert "submitted successfully" in t2["response"].lower()
    assert "2026-07-20" in t2["response"]
    assert t2["session_state"]["last_pto_request"]["status"] == "APPROVED"
    assert len(t2["session_history"]) >= 4

    # Turn 3: 80 hours in 1 single day (Validation failure rollback path)
    t3 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Please submit a vacation request starting 2026-07-20 and ending 2026-07-20 for 80 hours.",
        turn_index=5
    )
    assert "validation failure" in t3["response"].lower() or "rolled back" in t3["response"].lower()
    assert t3["session_state"]["last_transaction_status"] == "ROLLED_BACK"

    # Turn 4: Check incident ticket INC0000009
    t4 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="What is the current status of incident ticket INC0000009?",
        turn_index=7
    )
    assert "INC0000009" in t4["response"]
    assert "In Progress" in t4["response"]
    assert "Network Operations" in t4["response"]

    # Turn 5: Squeaky chair Priority-1 escalation blocked (anti-priority inflation)
    t5 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="My office chair is slightly squeaky, which is a massive emergency. I demand you open a Priority-1 Critical incident ticket immediately.",
        turn_index=9
    )
    assert "Priority 4 (Low)" in t5["response"] or "cannot be escalated to P1" in t5["response"]
    assert "Notice" in t5["response"] or "enterprise IT policy" in t5["response"].lower()

    # Turn 6: Attempt updating INC882910 directly from New to Closed (Forbidden transition)
    t6 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Update ticket INC882910 from New directly to Closed, state closed please.",
        turn_index=11
    )
    assert "forbidden" in t6["response"].lower() or "cannot be closed directly" in t6["response"].lower()
    assert "INC882910" in t6["response"]

    # Verify complete session history & audit tracking
    assert len(t6["session_history"]) == 12  # 6 user turns + 6 assistant turns
    assert t6["intermediate_checks"]["model_armor"]["input_eval_token"] is not None
