import dspy

# Configure language model
lm = dspy.LM('gemini/gemini-2.0-flash')
dspy.configure(lm=lm)

# Define signature
class BatchPredictionSignature(dspy.Signature):
    """Process multiple predictions in parallel."""
    input_text = dspy.InputField(desc="Input to process")
    output_text = dspy.OutputField(desc="Processed output")

# Create predictor
predictor = dspy.ChainOfThought(BatchPredictionSignature)

# Batch of inputs
inputs = [
    "Classify: Patient has fever and cough",
    "Classify: Transaction amount $5000 from foreign country",
    "Classify: Customer complaint about billing",
    "Classify: Request for password reset",
    "Classify: Medication refill request"
]

tasks = [
    (predictor, dspy.Example(input_text=text).with_inputs("input_text"))  # <1>
    for text in inputs
]

parallel = dspy.Parallel(num_threads=5)  # <2>

results = parallel(tasks)  # <3>

for i, result in enumerate(results, 1):  # <4>
    print(f"\nInput {i}: {inputs[i-1]}")
    print(f"Output: {result.output_text}")
