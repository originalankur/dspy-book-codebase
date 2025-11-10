import dspy
from typing import Literal

lm = dspy.LM('gemini/gemini-2.0-flash')
dspy.configure(lm=lm)

class TicketClassificationSignature(dspy.Signature):
    """Classify support tickets and determine SLA routing."""
    ticket_subject = dspy.InputField(desc="Ticket subject line")  # <1>
    ticket_body = dspy.InputField(desc="Full ticket description")
    customer_tier: Literal["free", "pro", "enterprise"] = dspy.InputField(desc="Customer tier")
    previous_tickets = dspy.InputField(desc="Recent ticket history")
    category = dspy.OutputField(desc="Ticket category")  # <2>
    priority: Literal["P1", "P2", "P3", "P4"] = dspy.OutputField(
      desc="Priority: P1 (critical), P2 (high), P3 (medium), P4 (low)"
    )
    sla_deadline = dspy.OutputField(desc="SLA response deadline")  # <3>
    routing_team = dspy.OutputField(desc="Team to route to")

ticket_classifier = dspy.ChainOfThought(TicketClassificationSignature)  # <4>

result = ticket_classifier(
    ticket_subject="Payment processing completely down",
    ticket_body="Our payment gateway has been returning 500 errors for the past 15 minutes. We're losing sales. This is affecting all customers on our e-commerce platform.",
    customer_tier="Enterprise",
    previous_tickets="2 tickets in past month, both resolved within SLA"
)

print(f"Classification Reasoning:\n{result.reasoning}\n")
print(f"Category: {result.category}")
print(f"Priority: {result.priority}")
print(f"SLA Deadline: {result.sla_deadline}")
print(f"Routing: {result.routing_team}")