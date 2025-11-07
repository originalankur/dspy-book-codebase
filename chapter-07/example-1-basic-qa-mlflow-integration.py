import dspy
import mlflow

def setup_mlflow():
    mlflow.dspy.autolog(
        log_traces=True,
        log_compiles=True,
        log_evals=True,
        log_traces_from_compile=True
    )
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("dspy-mlops-integration")

class QuestionAnswering(dspy.Signature):
    """
    For a given question, provide a concise and accurate answer based on general
    knowledge.
    """
    question: str = dspy.InputField(description="A question about general knowledge.")
    answer: str = dspy.OutputField(description="The answer to the question.")

def call_predict(question):
    predict = dspy.Predict(QuestionAnswering)
    response = predict(question=question)
    print(f"Question: {question}")
    print(f"Answer: {response.answer}")

if __name__ == "__main__":
    dspy.configure(lm=dspy.LM('gemini/gemini-2.5-flash'))
    setup_mlflow()
    call_predict(question="What's the full form of CoT in the AI field?")