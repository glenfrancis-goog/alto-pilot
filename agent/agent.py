"""JetClimbers HR Policy Agent — entry point for Altostrat Singapore."""

import asyncio
import os
import sys
import pathlib

# Ensure scratch root is on sys.path
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agent import config
from agent.prompt import POLICY_AGENT_PROMPT

def select_tools(mode: str):
    """Return the list of tool callables for the given retrieval mode."""
    tools = []
    if mode in ("okf", "hybrid"):
        from tools.okf_tool import list_concepts, read_concept
        tools += [list_concepts, read_concept]
    if mode in ("rag", "hybrid"):
        from tools.rag_tool import search_policy_docs
        tools += [search_policy_docs]
    if not tools:
        raise ValueError(f"Unknown RETRIEVAL_MODE: {mode!r} (use okf | rag | hybrid)")
    return tools

# ---------------------------------------------------------------------------
# Construct the ADK LlmAgent
# ---------------------------------------------------------------------------
try:
    from google.adk.agents import LlmAgent
    root_agent = LlmAgent(
        model=config.GEMINI_MODEL,
        name="hr_policy_agent",
        description="JetClimbers HR Policy Assistant for Altostrat Singapore employees.",
        instruction=POLICY_AGENT_PROMPT,
        tools=select_tools(config.RETRIEVAL_MODE),
    )
except ImportError:
    root_agent = None

_session_service = None

def _ensure_runner():
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    global _session_service
    if root_agent is None:
        raise SystemExit("root_agent is None — google-adk is required to initialize the runner.")
    if _session_service is None:
        _session_service = InMemorySessionService()
    return Runner(
        app_name=config.APP_NAME,
        agent=root_agent,
        session_service=_session_service,
    )

def _ensure_session(user_id, session_id):
    """Create the session, tolerating both sync and async ADK builds."""
    try:
        _session_service.create_session_sync(
            app_name=config.APP_NAME, user_id=user_id, session_id=session_id
        )
    except AttributeError:
        asyncio.run(
            _session_service.create_session(
                app_name=config.APP_NAME, user_id=user_id, session_id=session_id
            )
        )
    except Exception:
        pass  # already exists

def run_query(query: str, user_id: str = "learner", session_id: str = "session-1") -> str:
    answer, _evidence = run_query_traced(query, user_id=user_id, session_id=session_id)
    return answer

def run_query_traced(query: str, user_id: str = "learner", session_id: str = "session-1"):
    """
    Returns (answer, evidence) where evidence is a list of
    {"tool": <tool name>, "payload": <the tool's return value>}.
    """
    from google.genai import types

    runner = _ensure_runner()
    _ensure_session(user_id, session_id)
    message = types.Content(role="user", parts=[types.Part(text=query)])
    final = ""
    evidence = []

    for event in runner.run(
        user_id=user_id, session_id=session_id, new_message=message
    ):
        if not (event.content and event.content.parts):
            continue
        for part in event.content.parts:
            fr = getattr(part, "function_response", None)
            if fr is not None:
                evidence.append(
                    {"tool": getattr(fr, "name", "?"), "payload": fr.response}
                )
        if event.is_final_response() and event.content.parts:
            texts = [p.text for p in event.content.parts if getattr(p, "text", None)]
            if texts:
                final = "\n".join(texts)
    return final, evidence

def _interactive():
    print(f"HR Policy Agent [{config.RETRIEVAL_MODE}] — type 'exit' to quit.")
    while True:
        try:
            q = input("\nyou > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"exit", "quit"}:
            break
        if q:
            print(f"\nagent > {run_query(q)}")

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if argv and argv[0] == "--interactive":
        _interactive()
    elif argv:
        print(run_query(" ".join(argv)))
    else:
        print('Usage: uv run python -m agent.agent "<question>"  |  --interactive')

if __name__ == "__main__":
    main()
