import dspy

lm = dspy.LM('gemini/gemini-2.0-flash')
dspy.configure(lm=lm)

def count_words(text):
    """Count the number of words in text"""
    return len(text.split())

def count_sentences(text):
    """Count the number of sentences in text"""
    import re
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])

def extract_keywords(text, min_length=4):
    """Extract words longer than min_length"""
    words = text.split()
    keywords = [w.strip('.,!?;:') for w in words if len(w.strip('.,!?;:')) >= min_length]
    return list(set(keywords))

# Define a class-based Signature
class TextAnalysisSignature(dspy.Signature):
    """Analyze text document and provide detailed statistics"""
    
    document = dspy.InputField(desc="The text document to analyze")
    word_count = dspy.OutputField(desc="Total number of words in the document")
    sentence_count = dspy.OutputField(desc="Total number of sentences")
    keywords = dspy.OutputField(desc="List of important keywords")
    summary = dspy.OutputField(desc="A brief summary of the analysis")

# Create CodeAct with class-based signature
text_act = dspy.CodeAct(
    TextAnalysisSignature,
    tools=[count_words, count_sentences, extract_keywords]
) # <1>

sample_text = "DSPy is amazing!. It makes building AI applications much easier. CodeAct is a powerful feature."
result = text_act(document=sample_text)

print(f"\nWord Count: {result.word_count}")
print(f"Sentence Count: {result.sentence_count}")
print(f"Keywords: {result.keywords}")
print(f"Summary: {result.summary}")
