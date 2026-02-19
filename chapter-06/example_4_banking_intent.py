import dspy
from dspy.teleprompt import GEPA
import json
import os

task_lm = dspy.LM(model='gemini/gemini-2.0-flash', max_tokens=1000) # <1>
eval_lm = dspy.LM(model='gemini/gemini-2.5-pro', max_tokens=5000) # <2>

dspy.settings.configure(lm=task_lm)

class FinancialRiskExtraction(dspy.Signature): # <3>
    """Analyze transcripts to find risks like liquidity stress or leadership instability."""
    transcript = dspy.InputField()
    risk_summary = dspy.OutputField(desc="Numbered list of specific financial risks.")

class RiskJudgeSignature(dspy.Signature): # <4>
    """Grade the quality of a risk extraction based on accuracy and jargon detection."""
    transcript = dspy.InputField()
    gold_risks = dspy.InputField()
    predicted_risks = dspy.InputField()
    
    score = dspy.OutputField(desc="A value between 0.0 and 1.0.")
    feedback = dspy.OutputField(desc="Actionable feedback for the extractor model.")

def llm_judge_metric(gold, pred, trace=None, pred_name=None, pred_trace=None): # <1>
    with dspy.context(lm=eval_lm): # <2>
        judge = dspy.ChainOfThought(RiskJudgeSignature) # <3>
        assessment = judge(
            transcript=gold.transcript,
            gold_risks=gold.risk_summary,
            predicted_risks=pred.risk_summary
        )
    
    try:
        score = float(assessment.score)
    except:
        score = 0.5
    
    rationale = getattr(assessment, 'rationale', "No rationale provided.")
    feedback = getattr(assessment, 'feedback', "No feedback provided.")
    
    return dspy.Prediction( # <4>
        score=score, 
        feedback=feedback, 
        rationale=rationale
    )

def load_data(filename="finance_data.json"):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found. Please run your data generation script first.")
        return []
    with open(filename, "r") as f:
        data = json.load(f)
    
    return [dspy.Example(
        transcript=x["transcript"], 
        risk_summary="\n".join(x.get("risk_summary", x.get("risk_analysis", [])))
    ).with_inputs("transcript") for x in data]

def optimize():
    all_data = load_data()
    if not all_data: return
    
    trainset = all_data[:16]
    valset = all_data[16:20]

    teleprompter = GEPA( # <1>
        metric=llm_judge_metric,
        reflection_lm=eval_lm, # <2>
        auto="medium",
        reflection_minibatch_size=5,
        num_threads=4
    )

    print(f"Starting GEPA Optimization (Train: {len(trainset)}, Val: {len(valset)})...")
    
    optimized_program = teleprompter.compile( # <3>
        dspy.Predict(FinancialRiskExtraction), 
        trainset=trainset,
        valset=valset
    )

    save_path = "optimized_financial_risk_v1.json"
    optimized_program.save(save_path) # <4>
    print(f"Optimized program saved to {save_path}")
    
    print("-" * 30)
    print("Optimization Complete.")
    print(f"Evolved Instructions: {optimized_program.predictors()[0].signature.instructions}")

if __name__ == "__main__":
    optimize()