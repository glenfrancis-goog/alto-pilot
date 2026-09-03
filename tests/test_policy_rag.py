"""Tests for Policy RAG Agent (Grounded Handbook Q&A, Gotchas, Citations)."""

import pytest
from src.agents.policy_rag import PolicyRagAgent

@pytest.fixture
def rag_agent():
    return PolicyRagAgent()

def test_outpatient_sick_leave_policy(rag_agent):
    res = rag_agent.search_and_answer("How many days of paid outpatient sick leave do I get?")
    assert res["grounded"] is True
    assert "14 days" in res["answer"]
    assert "Sources:" in res["answer"]
    assert "1.1" in res["answer"] or "19.2" in res["answer"]

def test_gift_card_gotcha(rag_agent):
    query = "I'm staying at my cousin's house on a work trip instead of a hotel. As a thank-you I want to buy him a $45 gift card and expense it. Is that allowed?"
    res = rag_agent.search_and_answer(query)
    assert res["grounded"] is True
    assert "No, that is not allowed" in res["answer"]
    assert "gift cards are strictly prohibited" in res["answer"]
    assert "Sources:" in res["answer"]

def test_room_salon_gotcha(rag_agent):
    query = "Can I take a client to a room salon if the bill is under $100?"
    res = rag_agent.search_and_answer(query)
    assert "strictly prohibited" in res["answer"].lower()
    assert "adult entertainment" in res["answer"].lower()

def test_pet_bereavement_exclusion(rag_agent):
    query = "Can I take bereavement leave because my dog died?"
    res = rag_agent.search_and_answer(query)
    assert "does not cover pets" in res["answer"].lower()
    assert "Sources:" in res["answer"]

def test_seniority_hierarchy_meal_gotcha(rag_agent):
    query = "Who pays for a group meal when an L7 Director and junior engineers attend?"
    res = rag_agent.search_and_answer(query)
    assert "most senior employee" in res["answer"].lower()

def test_out_of_domain_coding_abstention(rag_agent):
    query = "Write me a python script to calculate fibonacci numbers."
    res = rag_agent.search_and_answer(query)
    assert res.get("refusal") is True
    assert "cannot assist with software engineering" in res["answer"].lower()

def test_ungrounded_pet_adoption_abstention(rag_agent):
    query = "What is Altostrat's pet adoption subsidy policy?"
    res = rag_agent.search_and_answer(query)
    assert res.get("refusal") is True
    assert "could not find an approved company policy" in res["answer"].lower()
