"""The Detective Evaluator & Hill-Climbing Test Harness for HR Policy Agent."""

import json
import pathlib
import sys
import time

BASE_DIR = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from agent.hr_agent import evaluate_hr_request

def run_evaluation_suite(model: str = "gemini-2.5-pro"):
    eval_file = BASE_DIR / "evals" / "eval_dataset.json"
    with open(eval_file, "r") as f:
        test_cases = json.load(f)

    print("=" * 80)
    print("🔍 THE DETECTIVE EVALUATOR: HR Policy Agent Automated Audit")
    print(f"Target Model: {model} | Benchmark Cases: {len(test_cases)}")
    print("=" * 80)

    passed_count = 0
    results = []

    for idx, case in enumerate(test_cases, 1):
        case_id = case["id"]
        category = case["category"]
        prompt = case["prompt"]
        expected_status = case["expected_status"]
        expected_days = case["expected_approved_days"]

        print(f"\n[{idx}/{len(test_cases)}] Running {case_id}: {category}...")
        start_time = time.time()

        try:
            decision = evaluate_hr_request(prompt, model=model)
            latency = round(time.time() - start_time, 2)

            status_match = decision.status == expected_status
            days_match = decision.approved_days == expected_days

            reason_match = True
            if "expected_reason_snippet" in case:
                reason_match = case["expected_reason_snippet"].lower() in decision.reasoning.lower()

            overall_pass = status_match and days_match and reason_match

            if overall_pass:
                print(f"  ✔ PASS ({latency}s) | Status: {decision.status} | Approved: {decision.approved_days}d")
                passed_count += 1
            else:
                print(f"  ✖ FAIL ({latency}s)")
                print(f"    Expected Status: {expected_status} | Got: {decision.status}")
                print(f"    Expected Days:   {expected_days} | Got: {decision.approved_days}")
                print(f"    Reasoning:       {decision.reasoning[:120]}...")

            results.append({
                "id": case_id,
                "category": category,
                "passed": overall_pass,
                "latency_sec": latency,
                "status": decision.status,
                "approved_days": decision.approved_days,
                "citations": len(decision.citations)
            })

        except Exception as e:
            print(f"  ✖ ERROR ({case_id}): {e}")
            results.append({
                "id": case_id,
                "category": category,
                "passed": False,
                "error": str(e)
            })

    # Summary Report
    score_pct = round((passed_count / len(test_cases)) * 100, 1)
    print("\n" + "=" * 80)
    print("📊 EVALUATION REPORT CARD & HILL-CLIMBING METRICS")
    print("=" * 80)
    print(f"Total Cases Evaluated: {len(test_cases)}")
    print(f"Passed:                {passed_count}")
    print(f"Failed:                {len(test_cases) - passed_count}")
    print(f"Overall Accuracy:      {score_pct}%")

    if score_pct == 100.0:
        print("\n🎉 ALL VERIFICATION CRITERIA SATISFIED! Ready for production deployment.")
    else:
        print(f"\n⚠ REGRESSION DETECTED: {len(test_cases) - passed_count} cases failed. Inspect traces above to hill-climb.")
    print("=" * 80)

if __name__ == "__main__":
    target_model = sys.argv[1] if len(sys.argv) > 1 else "gemini-2.5-pro"
    run_evaluation_suite(model=target_model)
