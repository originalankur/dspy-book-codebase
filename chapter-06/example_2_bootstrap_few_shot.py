import time
from datetime import datetime

import dspy
import json
import mlflow
import mlflow.dspy
from dspy.teleprompt import BootstrapFewShot

mlflow.set_experiment("medical-coding-bootstrap")

lm = dspy.LM("gemini/gemini-2.5-pro")
dspy.configure(lm=lm)

class MedicalCoding(dspy.Signature):
    """Convert clinical notes to specific ICD-10 codes for medical billing."""
    clinical_note = dspy.InputField(desc="Doctor's clinical documentation")
    icd10_code = dspy.OutputField(desc="Specific ICD-10 code (e.g., E11.621)")

class MedicalCodingProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(MedicalCoding)

    def forward(self, clinical_note):
        return self.predict(clinical_note=clinical_note)

def exact_code_match(example, prediction, trace=None):
    return example.icd10_code.strip() == prediction.icd10_code.strip()

def evaluate_program(program, testset):
    """Evaluate the program and return accuracy metrics."""
    correct = 0
    total = len(testset)
    
    for example in testset:
        pred = program(clinical_note=example.clinical_note)
        if exact_code_match(example, pred):
            correct += 1
    
    accuracy = correct / total if total > 0 else 0
    return {
        "accuracy": accuracy,
        "correct_predictions": correct,
        "total_predictions": total
    }

def load_medical_data(filename="samples.json"):
    """Load clinical notes and ICD-10 codes from JSON file."""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    trainset = []
    for item in data:
        example = dspy.Example(
            clinical_note=item["note"],
            icd10_code=item["code"]
        ).with_inputs("clinical_note")
        trainset.append(example)
    
    return trainset

trainset = load_medical_data()
print(f"Loaded {len(trainset)} training examples from samples.json")

train_data = trainset[:7]  # First 7 for training
test_data = trainset[7:]   # Last 3 for testing

with mlflow.start_run(run_name=f"bootstrap-medical-coding-{datetime.now().strftime('%Y%m%d-%H%M%S')}"):
    
    mlflow.log_param("optimizer", "BootstrapFewShot")
    mlflow.log_param("model", "gemini/gemini-2.5-pro")
    mlflow.log_param("training_examples", len(train_data))
    mlflow.log_param("test_examples", len(test_data))
    mlflow.log_param("max_bootstrapped_demos", 3)
    
    print("Evaluating baseline (unoptimized) program...")
    baseline_program = MedicalCodingProgram()
    baseline_metrics = evaluate_program(baseline_program, test_data)
    
    mlflow.log_metrics({
        "baseline_accuracy": baseline_metrics["accuracy"],
        "baseline_correct": baseline_metrics["correct_predictions"]
    })
    
    print(f"Baseline Accuracy: {baseline_metrics['accuracy']:.2%}")
    
    print("Starting BootstrapFewShot optimization...")
    optimizer = BootstrapFewShot(
        metric=exact_code_match, 
        max_bootstrapped_demos=3
    )
    
    start_time = time.time()
    
    compiled_program = optimizer.compile(MedicalCodingProgram(), trainset=train_data)
    
    optimization_time = time.time() - start_time
    mlflow.log_metric("optimization_time_seconds", optimization_time)
    
    print("Evaluating optimized program...")
    optimized_metrics = evaluate_program(compiled_program, test_data)
    
    mlflow.log_metrics({
        "optimized_accuracy": optimized_metrics["accuracy"],
        "optimized_correct": optimized_metrics["correct_predictions"],
        "accuracy_improvement": optimized_metrics["accuracy"] - baseline_metrics["accuracy"]
    })
    
    print(f"Optimized Accuracy: {optimized_metrics['accuracy']:.2%}")
    print(f"Improvement: {optimized_metrics['accuracy'] - baseline_metrics['accuracy']:+.2%}")
    
    # Log the optimized program as an artifact
    mlflow.dspy.log_model(compiled_program, "medical-coding-model")
    
    # Test with a new example
    test_note = "Patient with pneumonia and underlying COPD, requiring hospitalization."
    pred = compiled_program(clinical_note=test_note)
    
    print(f"\nTest Example:")
    print(f"Clinical Note: {test_note}")
    print(f"Medical Reasoning: {pred.reasoning}") # <1>
    print(f"ICD-10 Code: {pred.icd10_code}")
    
    # Log test example results
    mlflow.log_text(f"Test Note: {test_note}\nReasoning: {pred.reasoning}\nCode: {pred.icd10_code}", 
                    "test_example_output.txt")
    
    # Log prompt inspection
    lm.inspect_history(n=1)
    
    print(f"\nMLflow Run ID: {mlflow.active_run().info.run_id}")
    print("View results in MLflow UI: mlflow ui")

