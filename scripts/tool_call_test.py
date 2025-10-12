"""Quick smoke test to verify agent tools can be called and spied on.

This script does not call the network. It replaces the tool references in
`src.agents.agent_common` with small spy stubs that record invocation and
return a fake result. Run this from the repository root.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agent import agent_config as ac


class Spy:
    def __init__(self, name, fake_result=None):
        self.name = name
        self.calls = []
        self.fake_result = fake_result if fake_result is not None else {"status": "ok", "tool": name}

    def __call__(self, *args, **kwargs):
        self.calls.append({"args": args, "kwargs": kwargs})
        print(f"[spy] {self.name} called with args={args} kwargs={kwargs}")
        return self.fake_result


def run_spy_test():
    # Create spies for each tool and patch them into agent_common
    search_spy = Spy("search_knowledge_base", fake_result={"results": ["plan A", "plan B"]})
    ticket_spy = Spy("create_complaint_ticket", fake_result={"ticket_id": "TICKET-123"})
    sheet_spy = Spy("log_to_google_sheets", fake_result={"logged": True})

    # Patch the module-level references used by agents
    ac.search_knowledge_base_tool = search_spy
    ac.create_complaint_ticket_tool = ticket_spy
    ac.log_to_google_sheets_tool = sheet_spy

    # Invoke each tool with sample inputs (don't rely on exact signature)
    try:
        r1 = ac.search_knowledge_base_tool("internet plans and pricing")
    except Exception as e:
        r1 = f"error: {e}"

    try:
        r2 = ac.create_complaint_ticket_tool({"customer_name": "Alice", "description": "no internet"})
    except Exception as e:
        r2 = f"error: {e}"

    try:
        r3 = ac.log_to_google_sheets_tool({"ticket_id": "TICKET-123", "customer": "Alice"})
    except Exception as e:
        r3 = f"error: {e}"

    print("\nResults:\n", r1, r2, r3)

    # Simple assertions
    all_called = bool(search_spy.calls) and bool(ticket_spy.calls) and bool(sheet_spy.calls)
    if all_called:
        print("\nSPY TEST PASS: All tools were invoked and recorded by spies.")
        return 0
    else:
        print("\nSPY TEST FAIL: One or more tools were not called.")
        return 2


if __name__ == "__main__":
    raise SystemExit(run_spy_test())
