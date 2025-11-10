import dspy
lm = dspy.LM('gemini/gemini-2.0-flash')  # <1>
dspy.configure(lm=lm)

class ClassifyNews(dspy.Signature): # <2>
    """Classify a news article into a relevant category."""
    news_article = dspy.InputField(desc="The full text of the news article.")
    news_category: str = dspy.OutputField(desc="A single category, e.g., 'Politics', 'Sports', 'Technology', 'Other'.")

class NewsClassifier(dspy.Module): # <3>
    """A simple module that classifies news articles."""
    def __init__(self):
        super().__init__() # <4>
        self.classifier = dspy.Predict(ClassifyNews) # <5>
    
    def forward(self, news_article):  # <6>
        return self.classifier(news_article=news_article) # <7>

if __name__ == "__main__":
    classifier = NewsClassifier()
    result = classifier(news_article="India reduces GST rates.")
    print(result.news_category)