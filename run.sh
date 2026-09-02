#!/bin/bash
# Runner script for Altostrat Singapore HR Policy Agent (Elevate Module 0 Lab)

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

export RETRIEVAL_MODE="${RETRIEVAL_MODE:-okf}"
export GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-pro}"
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"

COMMAND="${1:-query}"
shift || true

case "$COMMAND" in
    check)
        echo "Validating OKF Knowledge Bundle..."
        python3 -c "from tools.okf_tool import list_concepts; cs=list_concepts()['concepts']; print(f'OKF Validated: {len(cs)} concepts discovered.')"
        ;;
    query)
        QUERY="${*:-How many days of paid outpatient sick leave do I get?}"
        echo "Running query: $QUERY"
        python3 -m agent.agent "$QUERY"
        ;;
    interactive)
        python3 -m agent.agent --interactive
        ;;
    eval)
        echo "Running Golden Evaluation Suite (Floor Check)..."
        python3 evals/run_eval.py --mode "$RETRIEVAL_MODE" --target agent "$@"
        ;;
    judge)
        echo "Running Full Rubric Scoring with LLM Judge..."
        python3 evals/run_eval.py --mode "$RETRIEVAL_MODE" --target agent --judge on "$@"
        ;;
    smoke)
        echo "Running 3-Case Smoke Subset..."
        python3 evals/run_eval.py --mode "$RETRIEVAL_MODE" --target agent --subset smoke "$@"
        ;;
    *)
        echo "Usage: ./run.sh [check|query <question>|interactive|eval|judge|smoke]"
        exit 1
        ;;
esac
