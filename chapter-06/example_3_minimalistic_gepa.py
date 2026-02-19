import dspy
from dspy.teleprompt import GEPA

lm = dspy.LM("gemini/gemini-2.0-flash")
dspy.configure(lm=lm)

training_data = [
    dspy.Example(query="I lost my wallet at the bar.", intent="block_card").with_inputs("query"),
    dspy.Example(query="I want to cancel my Netflix subscription.", intent="stop_payment").with_inputs("query"),
    dspy.Example(query="Block Spotify from charging me again.", intent="stop_payment").with_inputs("query"),
    dspy.Example(query="Cancel that weird charge from Uber yesterday.", intent="dispute_charge").with_inputs("query"),
    dspy.Example(query="Stop my card, it's been compromised.", intent="block_card").with_inputs("query"),
    dspy.Example(query="I see a double charge for my coffee.", intent="dispute_charge").with_inputs("query"),
    dspy.Example(query="I don't want to pay for GymShark anymore.", intent="stop_payment").with_inputs("query"),
]

validation_data = [
    dspy.Example(query="My card is missing.", intent="block_card").with_inputs("query"),
    dspy.Example(query="Freeze the payment to Hulu.", intent="stop_payment").with_inputs("query"), # "Freeze" usually implies card
    dspy.Example(query="I never authorized this transaction.", intent="dispute_charge").with_inputs("query"),
]

class IntentSignature(dspy.Signature):
    """
    Classify the user's banking query into exactly one of these intents: 
    [block_card, stop_payment, dispute_charge].
    """
    query = dspy.InputField(desc="The user's raw message")
    intent = dspy.OutputField(desc="The classification label")

class IntentClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(IntentSignature)

    def forward(self, query):
        return self.classify(query=query)

def gepa_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
    return gold.intent.strip().lower() == pred.intent.strip().lower()

optimizer = GEPA(
    metric=gepa_metric,
    reflection_lm=lm,
    auto="medium",
    num_threads=10,
    log_dir="./gepa_logs",
    track_stats=True,
    seed=42
)

print("Running GEPA to evolve instructions...")
print("(Note: If the model gets 100% on the first try, GEPA won't change anything.)")

optimized_program = optimizer.compile(
    student=IntentClassifier(),
    trainset=training_data,
    valset=validation_data
)

print("\n--- Final Optimized Instructions ---")
print(optimized_program.classify)

print("\n--- Test Output ---")
tricky_query = "Card not there, stop transactions."
pred = optimized_program(query=tricky_query)

print(f"Query: {tricky_query}")
print(f"Predicted Intent: {pred.intent}")
print(f"Reasoning: {pred.reasoning}")
lm.inspect_history(n=1)