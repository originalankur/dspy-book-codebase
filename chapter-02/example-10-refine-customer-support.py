import dspy
lm = dspy.LM('gemini/gemini-2.0-flash')

dspy.configure(lm=lm)

class SupportResponseSignature(dspy.Signature):
    """Generate and refine customer support responses."""
    customer_message = dspy.InputField(desc="Customer's message")
    ticket_history = dspy.InputField(desc="Previous ticket interactions")
    product_info = dspy.InputField(desc="Relevant product information")
    previous_response = dspy.InputField(desc="Previous draft (for refinement)")  # <1>
    refined_response = dspy.OutputField(desc="Improved response")
    improvements = dspy.OutputField(desc="What was improved")

def reward_fn(example, prediction, trace=None):  # <2>
    """Evaluate the quality of the refined response using generic criteria."""
    response = prediction.refined_response
    improvements = prediction.improvements
    
    score = 0.0
    
    # Check for substantial, detailed response
    if len(response) > 100:
        score += 0.3
    
    # Check for empathy and acknowledgment
    empathy_words = ["understand", "apologize", "sorry", "appreciate", "frustrating"]
    if any(word in response.lower() for word in empathy_words):
        score += 0.2
    
    # Check for actionable information or next steps
    action_words = ["will", "can", "please", "steps", "solution", "resolve"]
    if any(word in response.lower() for word in action_words):
        score += 0.3
    
    # Check that improvements were documented
    if improvements and len(improvements) > 20:
        score += 0.2
    
    return score

# Create a predictor module first
predictor = dspy.ChainOfThought(SupportResponseSignature)

response_refiner = dspy.Refine(  # <3>
    predictor,  # Pass the predictor module, not just the signature
    reward_fn=reward_fn,
    threshold=0.8,  # Stop refining when score reaches 0.8
    N=3  # Refine up to 3 times
)

result = response_refiner(
    customer_message="I've been trying to export my data for 3 days and keep getting errors. This is unacceptable!",
    ticket_history="Customer reported issue 3 days ago, received generic troubleshooting steps",
    product_info="Data export feature, known issue with large datasets >10GB, fix deployed yesterday",
    previous_response="We're sorry for the inconvenience. Please try again."
)

print(f"Final Refined Response:\n{result.refined_response}\n")  # <4>
print(f"Improvements Made:\n{result.improvements}")