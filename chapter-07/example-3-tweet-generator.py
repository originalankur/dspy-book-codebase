import os
import re
from dataclasses import dataclass
from typing import List, Optional

import dspy
import mlflow
import mlflow.dspy
from mlflow.entities import SpanType


@dataclass
class EvaluationScores:
    engagement: float
    hashtags: float


@dataclass
class EvaluationResult:
    tweet: str
    reasoning: str
    scores: EvaluationScores
    mlflow_run_id: str


class Config:
    SCORE_QUESTION, SCORE_CTA, SCORE_EMOJI = 0.3, 0.3, 0.4
    OPTIMAL_HASHTAGS_MIN, OPTIMAL_HASHTAGS_MAX = 1, 3
    SCORE_PERFECT = 1.0
    SCORE_NO_HASHTAGS, SCORE_TOO_MANY_HASHTAGS = 0.0, 0.5
    EMOJI_PATTERN = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        flags=re.UNICODE,
    )
    HASHTAG_PATTERN = re.compile(r"#\w+")
    CTA_WORDS = ["check out", "learn", "discover", "join", "try", "share", "retweet", "follow"]
    GEMINI_MODEL = "gemini/gemini-2.5-flash"
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "tweet_generator")
    SPAN_GENERATION = "tweet_generation"
    METRIC_ENGAGEMENT, METRIC_HASHTAGS = "check_engagement", "check_hashtags"


def setup() -> None:
    """Initialize DSPy and MLflow."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    lm = dspy.LM(Config.GEMINI_MODEL, api_key=api_key, max_tokens=10000, temperature=0.8)
    dspy.settings.configure(lm=lm)
    mlflow.set_tracking_uri(Config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(Config.EXPERIMENT_NAME)
    mlflow.dspy.autolog()


class GenerateTweet(dspy.Signature):
    """Generate an engaging tweet from a given idea."""
    tweet_idea = dspy.InputField(desc="The main idea or topic for the tweet")
    tweet = dspy.OutputField(desc="A well-crafted, engaging tweet with hashtags. Don't exceed 280 characters.")


class TweetGenerator(dspy.Module):
    """DSPy module for generating tweets with reasoning."""
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(GenerateTweet)
    
    def forward(self, tweet_idea: str) -> dspy.Prediction:
        result = self.generate(tweet_idea=tweet_idea)
        return dspy.Prediction(
            tweet=result.tweet,
            reasoning=getattr(result, "reasoning", "")
        )


class TweetAnalyzer:
    """Analyzes tweet quality across multiple dimensions."""
    @staticmethod
    def check_engagement(tweet: str) -> float:
        """Score tweet engagement based on questions, CTAs, and emojis."""
        tweet_lower = tweet.lower()
        score = 0.0
        if "?" in tweet_lower:
            score += Config.SCORE_QUESTION
        if any(word in tweet_lower for word in Config.CTA_WORDS):
            score += Config.SCORE_CTA
        if Config.EMOJI_PATTERN.search(tweet):
            score += Config.SCORE_EMOJI
        return min(score, 1.0)

    @staticmethod
    def check_hashtags(tweet: str) -> float:
        """Score tweet based on hashtag count (optimal: 1-3)."""
        num_hashtags = len(Config.HASHTAG_PATTERN.findall(tweet))
        if Config.OPTIMAL_HASHTAGS_MIN <= num_hashtags <= Config.OPTIMAL_HASHTAGS_MAX:
            return Config.SCORE_PERFECT
        return Config.SCORE_NO_HASHTAGS if num_hashtags == 0 else Config.SCORE_TOO_MANY_HASHTAGS
        
    @staticmethod
    def calculate_all_scores(tweet: str) -> EvaluationScores:
        """Calculate all evaluation scores for a tweet."""
        engagement_score = TweetAnalyzer.check_engagement(tweet)
        hashtag_score = TweetAnalyzer.check_hashtags(tweet)
        return EvaluationScores(
            engagement=engagement_score,
            hashtags=hashtag_score,
        )


class MLflowLogger:
    """Handles all MLflow logging operations."""
    @staticmethod
    def log_evaluation_feedback(trace_id: str, tweet: str, scores: EvaluationScores) -> None:
        """Log evaluation feedback to MLflow trace."""
        try:
            hashtags = Config.HASHTAG_PATTERN.findall(tweet)
            mlflow.log_feedback(
                trace_id=trace_id,
                name=Config.METRIC_ENGAGEMENT,
                value=scores.engagement,
                rationale="Engagement elements detected in tweet",
                metadata={
                    "has_question": "?" in tweet,
                    "has_cta": any(word in tweet.lower() for word in Config.CTA_WORDS),
                    "has_emoji": bool(Config.EMOJI_PATTERN.search(tweet)),
                }
            )
            mlflow.log_feedback(
                trace_id=trace_id,
                name=Config.METRIC_HASHTAGS,
                value=scores.hashtags,
                rationale=f"Found {len(hashtags)} hashtag(s) (optimal: {Config.OPTIMAL_HASHTAGS_MIN}-{Config.OPTIMAL_HASHTAGS_MAX})",
                metadata={"num_hashtags": len(hashtags), "hashtags": hashtags}
            )
        except Exception:
            pass

    @staticmethod
    def log_metrics(scores: EvaluationScores, tweet: str, reasoning: str) -> None:
        """Log evaluation metrics to MLflow."""
        hashtags = Config.HASHTAG_PATTERN.findall(tweet)
        mlflow.log_metric("engagement_score", scores.engagement)
        mlflow.log_metric("hashtag_score", scores.hashtags)
        mlflow.log_metric("num_hashtags", len(hashtags))
        if reasoning:
            mlflow.log_text(reasoning, "reasoning.txt")

    @staticmethod
    def log_params(tweet_idea: str) -> None:
        """Log run parameters to MLflow."""
        mlflow.log_param("tweet_idea", tweet_idea)
        mlflow.log_param("model", Config.GEMINI_MODEL)


def generate_and_evaluate_tweet(
    tweet_idea: str, generator: Optional[TweetGenerator] = None
) -> EvaluationResult:
    """Generate and evaluate a tweet with comprehensive MLflow logging."""
    if generator is None:
        generator = TweetGenerator()
    
    with mlflow.start_run(run_name=f"tweet_{tweet_idea[:30]}"):
        MLflowLogger.log_params(tweet_idea)
        
        with mlflow.start_span(name=Config.SPAN_GENERATION, span_type=SpanType.LLM) as span:
            result = generator(tweet_idea=tweet_idea)
            generated_tweet = result.tweet
            reasoning = getattr(result, "reasoning", "")
            span.set_inputs({"tweet_idea": tweet_idea})
            span.set_outputs({"tweet": generated_tweet, "reasoning": reasoning})
            trace_id = getattr(span, "request_id", None)
        
        scores = TweetAnalyzer.calculate_all_scores(generated_tweet)
        
        if trace_id:
            MLflowLogger.log_evaluation_feedback(trace_id, generated_tweet, scores)
        
        MLflowLogger.log_metrics(scores, generated_tweet, reasoning)
        mlflow.log_text(generated_tweet, "generated_tweet.txt")
        
        return EvaluationResult(
            tweet=generated_tweet,
            reasoning=reasoning,
            scores=scores,
            mlflow_run_id=mlflow.active_run().info.run_id,
        )


def main() -> None:
    """Main execution function."""
    setup()
    generator = TweetGenerator()
    for idea in ["What makes DSPy awesome?.", "Why coffee is the best productivity hack?."]:
        result = generate_and_evaluate_tweet(idea, generator)
        print(f"Generated: {result.tweet}")
        print(f"Engagement: {result.scores.engagement:.2f}, Hashtags: {result.scores.hashtags:.2f}\n")


if __name__ == "__main__":
    main()
