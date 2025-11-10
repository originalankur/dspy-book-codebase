import dspy

lm = dspy.LM('gemini/gemini-2.0-flash')
dspy.configure(lm=lm)

class DiseaseClassification(dspy.Signature):
    """Classify disease based on patient symptoms."""
    symptoms = dspy.InputField(desc="Patient symptoms")
    disease = dspy.OutputField(desc="Disease classification")
    confidence = dspy.OutputField(desc="Confidence level")

class TestRecommendation(dspy.Signature):
    """Recommend diagnostic tests for classified disease."""
    disease = dspy.InputField(desc="Classified disease")
    confidence = dspy.InputField(desc="Confidence level")
    tests = dspy.OutputField(desc="Recommended diagnostic tests")

class MedicalDiagnosisPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classifier = dspy.ChainOfThought(DiseaseClassification)
        self.recommender = dspy.Predict(TestRecommendation)
    
    def forward(self, symptoms):
        classification = self.classifier(symptoms=symptoms)
        recommendation = self.recommender(
            disease=classification.disease,
            confidence=classification.confidence
        )
        return dspy.Prediction(
            disease=classification.disease,
            confidence=classification.confidence,
            tests=recommendation.tests
        )

# Usage
pipeline = MedicalDiagnosisPipeline()

cases = [
    "Persistent cough, fever 101°F, difficulty breathing, chest pain",
]

for i, symptoms in enumerate(cases, 1):
    result = pipeline(symptoms=symptoms)
    print(f"\nCase {i}: {result.disease} ({result.confidence})")
    print(f"Tests: {result.tests}")