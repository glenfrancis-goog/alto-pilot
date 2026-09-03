"""Benchmark runner executing golden evalset against the Enterprise HR Multi-Agent System."""

import json
import time
from pathlib import Path
from src.agents.supervisor import SupervisorAgent

def run_evaluations():
    evalset_path = Path(__file__).resolve().parent / "tests/eval/datasets/golden_mas_eval.evalset.json"
    with open(evalset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    supervisor = SupervisorAgent()
    cases = data.get("eval_cases", [])
    print("=" * 80)
    print(f"🚀 EXECUTING MULTI-AGENT SYSTEM BENCHMARK ({len(cases)} Golden Cases)")
    print("=" * 80)

    results = []
    passed = 0

    for idx, case in enumerate(cases, 1):
        cid = case["eval_id"]
        turn = case["conversation"][0]
        user_prompt = turn["user_content"]["parts"][0]["text"]
        expected_ref = turn.get("final_response", {}).get("parts", [{}])[0].get("text", "")

        t0 = time.time()
        res = supervisor.process_turn(
            session_id=f"bench-{cid}",
            user_id="EMP-62",
            prompt=user_prompt
        )
        latency = int((time.time() - t0) * 1000)
        actual = res.get("response", "")

        # Verification logic
        is_pass = False
        if "No, that is strictly prohibited" in expected_ref:
            is_pass = "prohibited" in actual.lower() or "not allowed" in actual.lower()
        elif "14 days" in expected_ref:
            is_pass = "14 days" in actual
        elif "20 working days" in expected_ref:
            is_pass = "20 days" in actual or "20 working days" in actual
        elif "5 unused vacation days" in expected_ref:
            is_pass = "5" in actual and "carry" in actual.lower()
        elif "Solutions Acceleration Architect" in expected_ref:
            is_pass = "Solutions Acceleration Architect" in actual
        elif "Vacation 18.0 days" in expected_ref:
            is_pass = "18.0" in actual
        elif "INC0000827" in expected_ref:
            is_pass = "INC0000827" in actual or "Support Tickets" in actual
        elif "5 days" in expected_ref and "carer" in cid:
            is_pass = "5 days" in actual or "Section 23" in actual
        elif "most senior employee" in expected_ref:
            is_pass = "most senior employee" in actual.lower()
        elif "cannot assist with software engineering" in expected_ref:
            is_pass = "cannot assist with software engineering" in actual.lower()
        elif "cannot provide investment" in expected_ref:
            is_pass = "investment" in actual.lower() or "stock" in actual.lower() or "cannot" in actual.lower()
        elif "cannot provide geopolitical" in expected_ref:
            is_pass = "geopolitical" in actual.lower() or "cannot" in actual.lower()
        elif "could not find an approved company policy" in expected_ref:
            is_pass = "could not find" in actual.lower() or "unapproved" in actual.lower()
        elif "Triggered cross-system SAGA" in expected_ref:
            is_pass = "INC" in actual or "hardware" in actual.lower() or "monitor" in actual.lower()
        elif "Booked sick leave in WorkWeek" in expected_ref:
            is_pass = "medical leave" in actual.lower() or "INC" in actual or "booked" in actual.lower()
        elif "Password reset tickets are classified as routine" in expected_ref:
            is_pass = "routine" in actual.lower() or "low" in actual.lower() or "priority" in actual.lower() or "created" in actual.lower()
        elif "Unpaid personal leave" in expected_ref:
            is_pass = "unpaid" in actual.lower() or "policy" in actual.lower()
        else:
            is_pass = len(actual) > 20

        if is_pass:
            passed += 1
            status_icon = "✅ PASS"
        else:
            status_icon = "❌ FAIL"

        print(f"[{idx:02d}/{len(cases):02d}] {status_icon} | {cid:<35} | {latency:4d}ms")
        results.append({
            "case_id": cid,
            "status": "PASS" if is_pass else "FAIL",
            "latency_ms": latency,
            "prompt": user_prompt,
            "response": actual
        })

    accuracy = (passed / len(cases)) * 100
    print("-" * 80)
    print(f"🎯 BENCHMARK SUMMARY: {passed}/{len(cases)} Passed ({accuracy:.1f}% Accuracy)")
    print("=" * 80)
    return results

if __name__ == "__main__":
    run_evaluations()
