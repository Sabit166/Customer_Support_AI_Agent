import asyncio
from typing import Any

from ..data.models import UserContext, ServiceResponse, ComplaintTicket, TechnicalResponse
from agents import Runner
from ..agent.agent import customer_support_agent


async def main():
    """Simple CLI harness to exercise the Customer Support agent.

    Mirrors the pattern in `demo_cli.py` but uses the project's package imports
    and the README-defined agent behavior.
    """
    print("🤖 Customer Support Agent CLI")
    print("=" * 60)

    # Create a simple user context for examples/tests
    user_context = UserContext()

    test_queries = [
        "Tell me about the area your service ."
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        try:
            # Runner.run is used elsewhere in the project; call it the same way
            response = await Runner.run(customer_support_agent, query, context=user_context)

            # Many agent runners return a structure with `final_output` or similar.
            final = getattr(response, "final_output", response)

            # If it's already a ServiceResponse, print nicely
            if isinstance(final, ServiceResponse):
                print(f"📋 Response Type: {final.response_type.value}")
                print(f"💬 Content: {final.content}")
                if final.actions_taken:
                    print(f"⚡ Actions: {', '.join(final.actions_taken)}")
                if final.ticket_id:
                    print(f"🎫 Ticket ID: {final.ticket_id}")
                if final.next_steps:
                    print(f"➡️  Next Steps: {final.next_steps}")
                if final.escalation_needed:
                    print(f"🚨 Escalation Required: {final.escalation_needed}")

            elif isinstance(final, TechnicalResponse):
                print(f"🔧 Technical Support Response")
                print(f"   Issue Type: {final.issue_type}")
                print(f"   Diagnosis: {final.diagnosis}")
                if final.solution_steps:
                    print(f"   Solution Steps:")
                    for i, step in enumerate(final.solution_steps, 1):
                        print(f"      {i}. {step}")
                if final.equipment_involved:
                    print(f"   Equipment: {', '.join(final.equipment_involved)}")
                if final.estimated_resolution_time:
                    print(f"   Est. Resolution: {final.estimated_resolution_time}")
                print(f"   Customer Instructions: {final.customer_instructions}")
                print(f"   Escalation Level: {final.escalation_level}")
                if final.requires_technician:
                    print(f"   🚨 Technician Required: Yes")
                if final.follow_up_needed:
                    print(f"   📞 Follow-up Required: Yes")

            elif isinstance(final, ComplaintTicket):
                print(f"🎫 Complaint Ticket Created")
                print(f"   ID: {final.ticket_id}")
                print(f"   Customer: {final.customer_name}")
                print(f"   Description: {final.complaint_description}")
                print(f"   Priority: {final.priority}")
                print(f"   Category: {final.category}")
                print(f"   Assigned Agent: {final.assigned_agent}")
                print(f"   Status: {final.status}")

            else:
                # Best-effort rendering for ad-hoc outputs
                out_str = str(final)
                print(f"  {out_str}")

        except Exception as exc:  # pragma: no cover - CLI runtime errors
            print(f"❌ Error while processing query: {exc}")

        print("-" * 50)

    print("\n✅ Customer Support Agent CLI run completed!")


if __name__ == "__main__":
    asyncio.run(main())
