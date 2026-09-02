# AltoPilot: Enterprise HR Agentic Solution (MVP 1)

AltoPilot is a secure, conversational AI assistant designed to provide employees with immediate self-service access to HR policies, leave management, and helpdesk operations.

Built using Google's **Agent Development Kit (ADK)** and powered by **Gemini 2.5 Pro** on **Vertex AI**, AltoPilot bridges enterprise knowledge and transactional backends (WorkWeek HCM, ServiceImmediately ITSM) while enforcing zero-trust security and deterministic policy guardrails.

---

## Architecture & Capabilities

* **Hybrid Brain (OKF + RAG):** Combines Open Knowledge Format (OKF) concept navigation for exact negative prohibitions/gotchas with semantic vector search (Vertex AI Search / Discovery Engine) for broad discovery.
* **Autonomous Transactions:** Books and validates paid time off, outpatient sick leave, and hospitalizations against real-time HCM records.
* **Cross-System Orchestration:** Chains multi-step intents across policy verification, WorkWeek employee profiles, and ServiceImmediately incident tickets.
* **Enterprise Guardrails:** Enforces strict boundary checks, prompt injection screening, and origin-authenticated execution headers (`X-Origin-Automation: HR-Agentic-MVP1`).

---

## Quick Start

### 1. Prerequisites
* Python 3.11+
* [`uv`](https://docs.astral.sh/uv/) package manager
* Google Cloud Project with Vertex AI and Discovery Engine APIs enabled

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your Google Cloud Project ID and credentials
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Run Policy Knowledge Verification
```bash
uv run python knowledge/check_okf.py
```

### 5. Run Evaluation Suite
```bash
# Evaluate against the 13 baseline benchmark scenarios
uv run python evals/run_eval.py --mode hybrid --target agent

# Evaluate against held-out test cases
uv run python evals/run_eval.py --mode hybrid --target agent --eval-file evals/policy_eval_heldout.json
```

---

## Directory Layout
* `agent/`: ADK agent definition, system prompts, configuration, and state machine.
* `knowledge/`: Altostrat Singapore HR Policy catalog indexed in Open Knowledge Format (OKF).
* `tools/`: Bounded tool execution perimeters (`okf_tool.py`, `rag_tool.py`, `employee_db.py`, `date_calculator.py`).
* `evals/`: Automated evaluation harness, LLM judges, rubrics, and held-out test suites.
* `schemas/`: Pydantic data contracts for HCM and ITSM transactions.
* `rag/`: Discovery Engine indexing and semantic mock fallback engines.
