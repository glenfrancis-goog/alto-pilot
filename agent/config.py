"""Configuration for Altostrat HR Policy Agent."""

import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

# Model selection
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8")

# Retrieval mode: "okf" | "rag" | "hybrid"
RETRIEVAL_MODE = os.getenv("RETRIEVAL_MODE", "okf").lower()

# Paths
REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "projectelevatelabs")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

VERTEX_AI_SEARCH_LOCATION = os.getenv("VERTEX_AI_SEARCH_LOCATION", "global")
VERTEX_AI_DATA_STORE_ID = os.getenv("VERTEX_AI_DATA_STORE_ID", "hr-policies-lab-store")
VERTEX_AI_SEARCH_ENGINE_ID = os.getenv("VERTEX_AI_SEARCH_ENGINE_ID", "hr-policies-lab-engine")

APP_NAME = "altostrat_hr_policy_agent"
