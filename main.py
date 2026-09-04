"""Main CLI & Server Entrypoint for JetClimbers Enterprise HR Agentic Solution (MVP 1).

Strictly conforms to SDD Specifications.
"""

import sys
import argparse
import uvicorn
from src.agents.supervisor import SupervisorAgent

def main():
    parser = argparse.ArgumentParser(description="JetClimbers Enterprise HR Virtual Assistant (MVP 1)")
    parser.add_argument("query", nargs="?", default=None, help="Single-turn user prompt to run directly")
    parser.add_argument("--serve", action="store_true", help="Start the FastAPI & Web UI server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--user-id", default="EMP-62", help="Simulated authenticated Employee ID")
    parser.add_argument("--session-id", default="cli-session-01", help="Session ID")
    args = parser.parse_args()

    if args.serve:
        print(f"Starting JetClimbers Enterprise HR Agent Web Server on http://{args.host}:{args.port}...")
        uvicorn.run("src.web.app:app", host=args.host, port=args.port, reload=False)
        return

    supervisor = SupervisorAgent()

    if args.query:
        print(f"\nUser ({args.user_id}): {args.query}")
        result = supervisor.process_turn(
            session_id=args.session_id,
            user_id=args.user_id,
            prompt=args.query
        )
        print(f"\nAssistant:\n{result.get('response')}\n")
        if "card" in result:
            print(f"[ACTION CARD]: {result['card'].get('card_type')} -> {result['card'].get('message')}")
        print(f"(Latency: {result.get('latency_ms')}ms | Thinking Budget: {result.get('thinking_budget')} | Model: {result.get('model')})\n")
    else:
        # Interactive terminal REPL
        profile_res = supervisor.workweek.get_profile(args.user_id)
        user_name = "Employee"
        if profile_res.get("status") == "SUCCESS":
            p = profile_res.get("profile", {})
            user_name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip() or "Employee"
        elif "603" in args.user_id:
            user_name = "Chandlerding Employee"

        print("=" * 70)
        print("JetClimbers Enterprise HR Virtual Assistant — Interactive Terminal Mode")
        print(f"Logged in as: {args.user_id} ({user_name}) | Model: Gemini 3.8")
        print("Type 'exit' or 'quit' to end session.")
        print("=" * 70)
        session_id = f"term-{args.session_id}"
        turn = 1
        while True:
            try:
                user_input = input("\nUser > ").strip()
                if user_input.lower() in ("exit", "quit"):
                    break
                if not user_input:
                    continue
                result = supervisor.process_turn(
                    session_id=session_id,
                    user_id=args.user_id,
                    prompt=user_input,
                    turn_index=turn
                )
                print(f"\nAssistant:\n{result.get('response')}")
                if "card" in result:
                    print(f"\n[CARD - {result['card'].get('card_type')}]: {result['card'].get('message')}")
                turn += 2
            except (KeyboardInterrupt, EOFError):
                break
        print("\nSession ended.")

if __name__ == "__main__":
    main()
