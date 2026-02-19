import dspy
import json
import numpy as np
from dspy.teleprompt import KNNFewShot
from sentence_transformers import SentenceTransformer

gemini = dspy.LM('gemini/gemini-2.5-flash')
dspy.configure(lm=gemini)

# Mock e-commerce data across different categories
data = [
    {"cat": "Electronics", "rev": "Battery dead in an hour.", "sent": "Negative"},
    {"cat": "Electronics", "rev": "Fastest processor I've used.", "sent": "Positive"},
    {"cat": "Apparel", "rev": "Fabric is rough and itchy.", "sent": "Negative"},
    {"cat": "Apparel", "rev": "Perfect fit, great summer color.", "sent": "Positive"},
    {"cat": "Home", "rev": "Blender is too loud but works.", "sent": "Positive"},
    {"cat": "Books", "rev": "Plot was predictable and dull.", "sent": "Negative"},
    {"cat": "Beauty", "rev": "Cleared my skin in two days.", "sent": "Positive"},
    {"cat": "Toys", "rev": "Broke immediately after unboxing.", "sent": "Negative"}
]

trainset = [
    dspy.Example(
        category=x['cat'], 
        review=x['rev'], 
        sentiment=x['sent']
    ).with_inputs('category', 'review') 
    for x in data
]

devset = trainset[-3:]  # Use last 3 for evaluation

# Setup multilingual sentence transformer for embeddings <1>
st_model = SentenceTransformer('all-MiniLM-L6-v2')  # Alternative model

def embedder(texts): # <2>
    return st_model.encode(texts, convert_to_numpy=True)

class SentimentSig(dspy.Signature):
    """Classify e-commerce review sentiment based on category."""
    category = dspy.InputField()
    review = dspy.InputField()
    sentiment = dspy.OutputField(desc="Positive or Negative")

class Classifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(SentimentSig)
    
    def forward(self, category, review):
        return self.predict(category=category, review=review)

# KNN retrieves 2 most similar examples for every query <3>
knn_optimizer = KNNFewShot(
    k=2, # <4>
    trainset=trainset, # <5>
    vectorizer=dspy.Embedder(embedder) # <6>
)

compiled_app = knn_optimizer.compile(Classifier()) # <7>

# Test with a new apparel review
test_input = {
    "category": "Apparel", 
    "review": "The stitching on these boots is falling apart."
}

res = compiled_app(**test_input) # <8>

print(f"\nTest Review: {test_input['review']}")
print(f"Predicted: {res.sentiment}")
print(f"Reasoning: {res.reasoning}")