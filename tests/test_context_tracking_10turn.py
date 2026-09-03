"""10-turn dialogue test suite evaluating context tracking and state preservation.

Evaluates context-tracking across:
- Turns 1-3: Remote work monitor procurement eligibility, address update, order dispatch, and confirmation check.
- Turns 4-5: Short-term medical leave booking starting next Monday with delegate setup & SAGA distributed transaction.
- Turns 6-10: London office relocation, £5,000 allowance, DLP international phone validation, London badge ticket,
             session-wide context synthesis/summary, and GDPR RTBF consent withdrawal purge.
"""

import pytest
import uuid
from src.agents.supervisor import SupervisorAgent

@pytest.fixture
def supervisor():
    return SupervisorAgent()

def test_10turn_context_tracking_session(supervisor):
    session_id = f"test-ctx-10turn-{uuid.uuid4().hex[:8]}"
    user_id = "EMP-62"

    # Turn 1: Monitor eligibility & remote verification
    t1 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="I just read the remote work policy and saw I’m eligible for a home office monitor. Can you verify my remote status and order one for me?",
        turn_index=1
    )
    assert "Remote Work Policy" in t1["response"] or "eligible" in t1["response"].lower()
    assert t1["session_state"]["monitor_eligibility"] == "VERIFIED"
    assert t1["session_state"]["app_name"] == "hr_agents"
    assert t1["session_state"]["user_id"] == "EMP-62"

    # Turn 2: Submitting home delivery address
    t2 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="My home address is 123 Marina Bay, Singapore 018956. Please ship it there.",
        turn_index=3
    )
    assert "123 Marina Bay" in t2["response"]
    assert "INC" in t2["response"]
    assert t2["session_state"]["shipping_address"] == "123 Marina Bay, Singapore 018956"
    assert "monitor_ticket_id" in t2["session_state"]

    # Turn 3: Context-tracking check without re-supplying details
    t3 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Can you double-check if my request went through?",
        turn_index=5
    )
    assert "123 Marina Bay" in t3["response"]
    assert t2["session_state"]["monitor_ticket_id"] in t3["response"]

    # Turn 4: Initiate medical leave & access delegation
    t4 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="I need to take short-term medical leave starting next Monday and set up IT access delegation.",
        turn_index=7
    )
    assert "medical leave" in t4["response"].lower()
    assert "Jane Doe" in t4["response"] or "delegation" in t4["response"].lower()
    assert "pending_medical_leave" in t4["session_state"]

    # Turn 5: Confirm and submit medical leave SAGA
    t5 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Yes, please confirm and submit the medical leave.",
        turn_index=9
    )
    assert "medical leave" in t5["response"].lower() or "delegation" in t5["response"].lower()
    assert t5["session_state"]["medical_leave_status"] == "CONFIRMED"

    # Turn 6: London relocation allowance query
    t6 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="I am planning an international office transfer to London. What is the standard relocation allowance?",
        turn_index=11
    )
    assert "£5,000" in t6["response"]
    assert "30 days" in t6["response"]
    assert t6["session_state"]["relocation_destination"] == "London"

    # Turn 7: Update phone with international DLP inspection
    t7 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Please update my contact phone number for the London move to +44 20 7946 0991.",
        turn_index=13
    )
    assert "+44 20 7946 0991" in t7["response"]
    assert t7["session_state"]["contact_phone"] == "+44 20 7946 0991"
    # DLP check
    assert t7["intermediate_checks"]["dlp"]["is_redacted"] is True
    assert "PHONE_NUMBER" in t7["intermediate_checks"]["dlp"]["detected_infotypes"]

    # Turn 8: Set up London facilities badge
    t8 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Can you set up my London facilities badge and building access ticket?",
        turn_index=15
    )
    assert "Facilities badge" in t8["response"] or "INC" in t8["response"]
    assert "facilities_ticket_id" in t8["session_state"]

    # Turn 9: Context-memory synthesis across all 3 workflows
    t9 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Can you summarize all actions taken in this session across my monitor, medical leave, and London transfer?",
        turn_index=17
    )
    # Verifies that entities from turns 1-8 are preserved and synthesized
    assert "Home Office Monitor" in t9["response"]
    assert "Medical Leave" in t9["response"]
    assert "London Relocation" in t9["response"]
    assert "£5,000" in t9["response"]
    assert "123 Marina Bay" in t9["response"]

    # Turn 10: Privacy GDPR RTBF consent withdrawal
    t10 = supervisor.process_turn(
        session_id=session_id,
        user_id=user_id,
        prompt="Withdraw consent and purge all my personal data.",
        turn_index=19
    )
    assert "withdrawn" in t10["response"].lower() or "purged" in t10["response"].lower()
    assert "RTBF" in t10["response"]
