import dspy
import socket

lm = dspy.LM('gemini/gemini-2.0-flash')
dspy.configure(lm=lm)

def check_domain_availability_func(domain: str) -> dict:
    """Checks if a domain name is registered by performing a DNS lookup."""
    try:
        socket.gethostbyname(domain)
        return {"domain": domain, "status": "Taken"}
    except socket.gaierror:
        return {"domain": domain, "status": "Available"}
    except Exception as e:
        return {"domain": domain, "status": f"Uncertain ({e})"}

class GenerateAndCheckDomains(dspy.Signature):
    """
    Generate three, three-word .com domain name suggestions for a web app idea.
    For each suggestion, use the provided tool to check availability.
    Report the final list with the status (Available / Taken / Uncertain).
    """ # <1>
    app_idea = dspy.InputField(
        desc="A brief description of the web app idea for which to suggest domains.")
    domain_suggestions = dspy.OutputField(
        desc="A formatted string of 3 suggested domains with their availability.")

if __name__ == "__main__":
    domain_availability_tool = dspy.Tool(name="check_domain_availability", # <2>
        func=check_domain_availability_func,
        desc="Checks if a domain name is registered by performing a DNS lookup.")

    agent = dspy.ReAct(GenerateAndCheckDomains, tools=[domain_availability_tool],
        max_iters=5) # <3>

    app_idea = (
        "A finance app that analyzes your portfolio from a value investing perspective.")
    result = agent(app_idea=app_idea) # <4>

    print(f"\n--- Finding Domain Names for: '{app_idea}' ---\n")
    print("\n--- Final Domain Suggestions ---")
    print(result.domain_suggestions)
