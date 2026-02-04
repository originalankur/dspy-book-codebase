import os
import re
import json
import dspy
from dspy.teleprompt import MIPROv2
from dspy.evaluate import Evaluate

TRAIN_SIZE = 10
DEV_SIZE = 10

lm = dspy.LM(f"gemini/gemini-2.0-flash")
dspy.configure(lm=lm)

class InsuranceDataset:
    def __init__(self):
        with open('chapter-06/claims_dataset.json', 'r') as f:
            self.data = json.load(f) * 4

    def get_splits(self):
        examples = [
            dspy.Example(
                claim_details=x["claim_details"],
                policy_text=x["policy_text"],
                policy_section=x["policy_section"],
                denial_reason=x["denial_reason"],
                customer_name=x["customer_name"]
            ).with_inputs("claim_details", "policy_text", "denial_reason", "customer_name")
            for x in self.data
        ]
        
        return examples[:TRAIN_SIZE], examples[TRAIN_SIZE:TRAIN_SIZE+DEV_SIZE]

class DenialLetterSignature(dspy.Signature):
    """Write a formal insurance claim denial letter. 
    The letter must be legally accurate but also empathetic and easy to understand."""
    
    customer_name = dspy.InputField()
    claim_details = dspy.InputField()
    policy_text = dspy.InputField()
    denial_reason = dspy.InputField()
    
    denial_letter = dspy.OutputField(desc="The full body of the denial letter")

class EmpathyJudgeSignature(dspy.Signature):
    """Rate the empathy and tone of a denial letter on a scale of 1-5.
    5 = Extremely kind, professional, clear, and human.
    1 = Cold, robotic, aggressive, or overly bureaucratic.
    Return ONLY the integer."""
    
    letter_text = dspy.InputField()
    score = dspy.OutputField(desc="Integer 1-5")

class ComplianceJudgeSignature(dspy.Signature):
    """Check if the letter cites the specific policy text provided.
    Return 'True' if the policy text or meaning is clearly cited as the reason.
    Return 'False' if the letter is vague or misses the specific exclusion clause."""
    
    policy_text_source = dspy.InputField()
    letter_text = dspy.InputField()
    is_compliant = dspy.OutputField(desc="True or False")

def calculate_readability(text):
    """Simple heuristic for reading ease (Proxy for Flesch-Kincaid)"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if len(s.strip()) > 0]
    words = text.split()
    if not sentences or not words: return 0
    
    avg_sentence_length = len(words) / len(sentences)
    
    score = max(0, min(1, 1 - ((avg_sentence_length - 10) / 20)))
    return score

def empathy_compliance_metric(gold, pred, trace=None):
    """
    The Composite Business Metric:
    Score = (Compliance * 0.4) + (Empathy * 0.3) + (Readability * 0.3)
    """
    letter = pred.denial_letter
    
    compliance_check = dspy.Predict(ComplianceJudgeSignature)
    comp_result = compliance_check(policy_text_source=gold.policy_text, letter_text=letter)
    is_compliant = 1.0 if "True" in comp_result.is_compliant else 0.0
    
    empathy_check = dspy.Predict(EmpathyJudgeSignature)
    emp_result = empathy_check(letter_text=letter)
    try:
        empathy_score = int(re.search(r'\d', emp_result.score).group())
        empathy_normalized = empathy_score / 5.0
    except:
        empathy_normalized = 0.5
        
    readability_score = calculate_readability(letter)
    
    final_score = (is_compliant * 0.4) + (empathy_normalized * 0.3) + (readability_score * 0.3)
    
    if trace is not None:
        return final_score >= 0.7
    
    return final_score

def print_rule(title, style="="):
    print(f"\n{style*20} {title} {style*20}")

def main():
    print_rule("DSPy MIPROv2: Insurance Denial Optimization")
    
    dataset = InsuranceDataset()
    trainset, devset = dataset.get_splits()
    print(f"Loaded {len(trainset)} training examples and {len(devset)} dev examples.")

    initial_program = dspy.ChainOfThought(DenialLetterSignature)

    print_rule("BASELINE EVALUATION")
    evaluator = Evaluate(devset=devset, num_threads=4, display_progress=True, display_table=0)
    
    avg_score_before = evaluator(initial_program, metric=empathy_compliance_metric)
    print(f"Average Baseline Score: {avg_score_before}")

    print_rule("STARTING MIPROv2 OPTIMIZATION")
    print("MIPROv2 will now generate instructions and select few-shot examples")
    print("to maximize the (Compliance + Empathy + Readability) score.")
    
    teleprompter = MIPROv2(
        metric=empathy_compliance_metric,
        auto="light", 
        num_threads=4,
        max_errors=10,
        verbose=True,
        track_stats=True,
        log_dir="/tmp/"        
    )
    
    optimized_program = teleprompter.compile(
        student=initial_program,
        trainset=trainset,
        valset=devset,
        requires_permission_to_run=False,
        minibatch=False,
    )
    
    print_rule("OPTIMIZED EVALUATION")
    avg_score_after = evaluator(optimized_program, metric=empathy_compliance_metric)
    print(f"Average Optimized Score: {avg_score_after}")
    
    print_rule("QUALITATIVE COMPARISON")
    
    example = devset[0]
    pred_old = initial_program(**example.inputs())
    pred_new = optimized_program(**example.inputs())
    
    score_old = empathy_compliance_metric(example, pred_old)
    score_new = empathy_compliance_metric(example, pred_new)
    
    print("-" * 60)
    print(f"SCENARIO:\nCustomer: {example.customer_name}\nIssue: {example.claim_details}")
    print("-" * 60)
    print(f"BASELINE (Score: {score_old:.2f}):")
    print(f"{pred_old.denial_letter[:300]}...")
    print("-" * 60)
    print(f"OPTIMIZED (Score: {score_new:.2f}):")
    print(f"{pred_new.denial_letter[:300]}...")
    print("-" * 60)
    
    with open('letter_output.txt', 'w') as f:
        f.write(f"OPTIMIZED DENIAL LETTER\n")
        f.write(f"Customer: {example.customer_name}\n")
        f.write(f"Score: {score_new:.2f}\n")
        f.write(f"{'='*60}\n\n")
        f.write(pred_new.denial_letter)
    
    optimized_program.save("optimized_insurance_denial.json")
    print("Saved optimized program to optimized_insurance_denial.json")
    print("Saved letter output to letter_output.txt")

if __name__ == "__main__":
    main()
