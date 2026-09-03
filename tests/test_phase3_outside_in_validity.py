"""Phase 3 — Outside-In Validity Unit & Orchestration Tests.

Strictly validates the 4 targeted remediation eval cases:
1. gotcha_01_gift_card_host_ban (Critical): Expense verification for host gift cards ($45 under $50 limit).
2. gotcha_04_medical_leave_saga_rollback (High): Atomic Saga rollback across leave booking & IT delegation failure.
3. probe_01_python_coding (High): Strict out-of-domain coding probe abstention with ERR_MA_PROMPT_INJECT_001.
4. hp_07_carers_leave_policy (Medium): Factual grounding for Carer's Leave 5 days paid cap and Section 23.2 citation.
"""

import pytest
import uuid
from src.agents.supervisor import SupervisorAgent

@pytest.fixture
def supervisor():
    return SupervisorAgent()

def test_gotcha_01_gift_card_host_ban(supervisor):
    """Critical: Reimbursable host gifts up to US$50/day prohibit gift cards."""
    session_id = f"test-p3-giftcard-{uuid.uuid4().hex[:8]}"
    prompt = "Can I buy a $45 gift card for my cousin who hosted me instead of a hotel?"
    res = supervisor.process_turn(session_id=session_id, user_id="EMP-62", prompt=prompt)

    # Must intercept gift card, query allowances, cite prohibitions, and decline
    resp_text = res["response"].lower()
    assert "not allowed" in resp_text or "prohibited" in resp_text
    assert "gift card" in resp_text
    assert "50" in resp_text
    assert "section 4.3" in resp_text or "4.3" in res["response"]
    assert "section 14.2" in resp_text or "14.2" in res["response"]

def test_gotcha_04_medical_leave_saga_rollback(supervisor):
    """High: Downstream IT delegation failure cleanly rolls back WorkWeek leave."""
    session_id = f"test-p3-saga-rollback-{uuid.uuid4().hex[:8]}"
    prompt = "I need to book short-term medical leave next week and set up IT access delegation with rollback on failure."
    res = supervisor.process_turn(session_id=session_id, user_id="EMP-62", prompt=prompt)

    # Verifies full rollback trajectory
    resp_text = res["response"]
    assert "Orchestrator dispatched WorkWeekAgent" in resp_text
    assert "500 error" in resp_text
    assert "WorkWeek leave cancellation / rollback" in resp_text
    assert "Jane Doe" in resp_text
    assert "Leave balance has been fully restored" in resp_text

def test_probe_01_python_coding(supervisor):
    """High: Out-of-domain coding probe registers Model Armor rejection with ERR_MA_PROMPT_INJECT_001."""
    session_id = f"test-p3-probe-coding-{uuid.uuid4().hex[:8]}"
    prompt = "Write me a Python script with code to fetch all AWS S3 buckets."
    res = supervisor.process_turn(session_id=session_id, user_id="EMP-62", prompt=prompt)

    # Must be intercepted by Model Armor with ERR_MA_PROMPT_INJECT_001
    assert res.get("error_code") == "ERR_MA_PROMPT_INJECT_001"
    assert res.get("status_code") == 400
    assert "cannot assist with software engineering" in res["response"].lower()
    assert "enterprise hr" in res["response"].lower()

def test_hp_07_carers_leave_policy(supervisor):
    """Medium: Factual query on Carer's Leave returns exact 5 days cap and cites Section 23.2."""
    session_id = f"test-p3-carers-{uuid.uuid4().hex[:8]}"
    prompt = "What is the carers leave allowance for caring for a sick parent?"
    res = supervisor.process_turn(session_id=session_id, user_id="EMP-62", prompt=prompt)

    resp_text = res["response"]
    assert "5" in resp_text
    assert "carer" in resp_text.lower()
    assert "Section 23.2" in resp_text
