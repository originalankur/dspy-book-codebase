import dspy
from typing import Literal, List


class NewsArticleCategorization(dspy.Signature):
    """Analyze and categorize news articles with comprehensive information
    extraction."""

    article: str = dspy.InputField(desc="The complete news article text to be analyzed")
    category: Literal[
        "Politics",
        "Business",
        "Sports",
        "Technology",
        "Health",
        "Entertainment",
        "World News",
        "Science",
        "Crime",
        "Weather",
    ] = dspy.OutputField(desc="The most appropriate news category for the article")
    entities: List[str] = dspy.OutputField(
        desc="Key people, organizations, locations, and other named entities mentioned in the article"
    )
    facts: List[str] = dspy.OutputField(
        desc="Important factual statements and key information from the article"
    )
    sentiment: Literal["positive", "negative", "neutral"] = dspy.OutputField(
        desc="Overall emotional tone and sentiment of the article"
    )
    topics: List[str] = dspy.OutputField(
        desc="Main themes and subject matters discussed in the article"
    )
    summary: str = dspy.OutputField(
        desc="Concise summary capturing the essential points of the article"
    )

if __name__ == "__main__":
    lm = dspy.LM("gemini/gemini-2.0-flash-exp", max_tokens=10000)
    dspy.configure(lm=lm)

    # Create the predictor
    categorizer = dspy.Predict(NewsArticleCategorization)

    # Example news article
    article = """In a landmark decision, the Supreme Court ruled today that climate change
    regulations must be strengthened to meet international commitments. The ruling,
    which was 6-3, mandates that federal agencies implement stricter emissions standards
    by 2025. Environmental groups hailed the decision as a major victory, while industry
    leaders expressed concern over potential economic impacts. The ruling is expected to
    influence policy discussions ahead of the upcoming global climate summit."""

    # Get the categorization prediction
    result = categorizer(article=article)
    print(f"Article: {article}\n")
    print(f"Predicted Category: {result.category}")
    print(f"Entities: {result.entities}")
    print(f"Facts: {result.facts}")
    print(f"Sentiment: {result.sentiment}")
    print(f"Topics: {result.topics}")
    print(f"Summary: {result.summary}")