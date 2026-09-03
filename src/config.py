"""Enterprise HR Agentic Solution Configuration.

Strictly conforms to SDD Specifications (SDD-HR-AGENT-MVP1-001).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Foundation Model Configuration (Gemini 3.7 Flash)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
THINKING_BUDGET_INSTANT = int(os.getenv("THINKING_BUDGET_INSTANT", "0"))
THINKING_BUDGET_ORCHESTRATION = int(os.getenv("THINKING_BUDGET_ORCHESTRATION", "1024"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))

# Google Cloud Platform & Vertex AI
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "elevate-279")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
DATA_STORE_ID = os.getenv("DATA_STORE_ID", "hr-policies-datastore")

# Knowledge Retrieval Configuration
RETRIEVAL_MODE = os.getenv("RETRIEVAL_MODE", "okf")  # okf | rag | hybrid
OKF_KNOWLEDGE_DIR = Path(os.getenv("OKF_KNOWLEDGE_DIR", str(BASE_DIR / "knowledge"))).resolve()

# Mock Enterprise Services API (WorkWeek & ServiceImmediately)
MOCK_SAAS_BASE_URL = os.getenv("MOCK_SAAS_BASE_URL", "https://mock-saas.aishprabhat.demo.altostrat.com")
MOCK_SAAS_PAT_TOKEN = os.getenv("MOCK_SAAS_PAT_TOKEN", "mock-saas-pat-token-2026-secret")
USE_LOCAL_MOCK_SERVER = os.getenv("USE_LOCAL_MOCK_SERVER", "true").lower() in ("true", "1", "yes")

# Security, Rate Limiting & Guardrails
DUPLICATE_TICKET_WINDOW_MINS = int(os.getenv("DUPLICATE_TICKET_WINDOW_MINS", "120"))
DUPLICATE_SEMANTIC_THRESHOLD = float(os.getenv("DUPLICATE_SEMANTIC_THRESHOLD", "0.88"))
USER_RATE_LIMIT_RPM = int(os.getenv("USER_RATE_LIMIT_RPM", "60"))
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
CIRCUIT_BREAKER_RESET_TIMEOUT_SECS = int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT_SECS", "30"))

# State Persistence & AlloyDB
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'sessions.db'}")
SESSION_TTL_DAYS = int(os.getenv("SESSION_TTL_DAYS", "30"))
