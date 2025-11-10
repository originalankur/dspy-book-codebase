import dspy

lm = dspy.LM('gemini/gemini-2.0-flash')
dspy.configure(lm=lm)

class QA(dspy.Signature):  # <1>
    """Answer questions with step-by-step reasoning."""
    question = dspy.InputField()
    answer = dspy.OutputField()

cot_predict = dspy.ChainOfThought(QA)  # <2>
question = "If a train travels 120 miles in 2 hours, what is its speed?"

cot_result = cot_predict(question=question)  # <3>
print(f"Reasoning: {cot_result.reasoning}")  # <4>
print(f"Answer: {cot_result.answer}")