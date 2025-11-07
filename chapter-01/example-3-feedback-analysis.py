import json
import sys

import dspy
from utils import setup_dspy

class FeedbackAnalysisSignature(dspy.Signature):
    """Analyze customer feedback and extract key themes categorized as positive or
    negative."""
    feedback = dspy.InputField(desc="Customer feedback text to analyze")
    analysis = dspy.OutputField(desc="JSON format with themes categorized as 'positive' or 'negative'. Overall structure of JSON to resemble {'themes':{'negative':[], 'positive':[]}}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <model_name> <max_tokens>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    max_tokens = int(sys.argv[2])
    lm = setup_dspy(model_name, max_tokens)
    customer_feedback = """"The app crashes frequently on iOS, especially when
        uploading photos. The interface is confusing and I can't find the settings menu.
        However, I love the new dark mode feature and the photo filters are amazing so
        please fix the issues so I don't have to try other apps."""
    
    # Create the predictor
    feedback_analyzer = dspy.Predict(FeedbackAnalysisSignature)
    result = feedback_analyzer(feedback=customer_feedback)
    try:
        analysis_json = json.loads(result.analysis)
        print("\nParsed Analysis:")
        print(json.dumps(analysis_json, indent=2))
    except json.JSONDecodeError:
        print("Note: Response may not be valid JSON format")
        print(result.analysis)