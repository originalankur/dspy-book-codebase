import dspy
from typing import Literal

NewsCategory = Literal[
    'Politics',
    'Business',
    'Sports',
    'Technology',
    'Health',
    'Entertainment',
    'World News',
    'Science',
    'Crime',
    'Weather'
]

class NewsHeadlineCategorization(dspy.Signature):
    """Categorize news headlines into appropriate news categories."""
    headline: str = dspy.InputField(desc="The news headline text to be categorized")
    category: NewsCategory = dspy.OutputField(desc="The most appropriate news category for the given headline")

if __name__ == "__main__":
    lm = dspy.LM("gemini/gemini-2.0-flash-exp", max_tokens=4000)
    dspy.configure(lm=lm)

    # Create the predictor
    categorizer = dspy.Predict(NewsHeadlineCategorization)

    # Example headline
    headline = "New advancements in AI technology are transforming industries worldwide."

    # Get the category prediction
    result = categorizer(headline=headline)
    print(f"Headline: {headline}")
    print(f"Predicted Category: {result.category}")