import dspy
from dspy.teleprompt import LabeledFewShot

lm = dspy.LM("gemini/gemini-2.5-pro")
dspy.configure(lm=lm)

class FriendlyRewriter(dspy.Signature):
    """Rewrite technical error messages into friendly, non-technical language."""
    technical_message = dspy.InputField(desc="The original technical error message")
    friendly_message = dspy.OutputField(desc="A user-friendly version of the message")

program = dspy.Predict(FriendlyRewriter)

trainset = [
    dspy.Example(
        technical_message="500 Internal Server Error",
        friendly_message="Oops! Something went wrong on our end. Please try again later."
    ).with_inputs("technical_message"), # <1>
    dspy.Example(
        technical_message="Error 404: Resource not found",
        friendly_message="We couldn't find what you're looking for. Let's get you back on track!"
    ).with_inputs("technical_message"),
    dspy.Example(
        technical_message="Authentication failed: Invalid credentials",
        friendly_message="Hmm, that password doesn't look right. Want to try again or reset it?"
    ).with_inputs("technical_message"),
    dspy.Example(
        technical_message="Connection timeout: Request exceeded 30s limit",
        friendly_message="This is taking longer than expected. Please check your connection and try again."
    ).with_inputs("technical_message"),
    dspy.Example(
        technical_message="Database query failed: Syntax error at line 42",
        friendly_message="We're having trouble loading your data right now. Our team is on it!"
    ).with_inputs("technical_message"),
    dspy.Example(
        technical_message="Permission denied: Insufficient privileges",
        friendly_message="You don't have access to this feature yet. Contact your admin if you need it!"
    ).with_inputs("technical_message"),
]

optimizer = LabeledFewShot(k=3) # <2>
optimized_program = optimizer.compile(student=program, trainset=trainset) # <3>

test_message = "SSL certificate verification failed: ERR_CERT_AUTHORITY_INVALID"
pred = optimized_program(technical_message=test_message)

print(f"Technical Message: {test_message}")
print(f"Friendly Version: {pred.friendly_message}")

lm.inspect_history(n=1)
