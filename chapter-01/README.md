
# Chapter 1

## Prerequisites

Make sure you have a running environment with all packages installed.

- If not, refer to the [Project README for instructions](../README.md).

## Ollama Setup

Install Ollama: Download from [Ollama Download Page](https://ollama.com/download)

```bash
ollama pull phi3:mini
```

## Example Scripts in Chapter 1

This chapter contains several example scripts demonstrating basic DSPy and LLM usage:

- [example-1-hello-ai.py](example-1-hello-ai.py): Basic hello world with an AI model.
- [example-2-setup-dspy.py](example-2-setup-dspy.py): Shows how to set up DSPy in your environment.
- [example-3-feedback-analysis.py](example-3-feedback-analysis.py): Analyzes feedback using LLMs.
- [example-4-news-headline-category.py](example-4-news-headline-category.py): Categorizes news headlines using LLMs.
- [example-4-news-headline-indepth-categorization.py](example-4-news-headline-indepth-categorization.py): Provides in-depth categorization of news headlines.
- [example-5-news-headline-indepth-categorization.py](example-5-news-headline-indepth-categorization.py): Further in-depth categorization example.
- [example-6-new-product-analysis.py](example-6-new-product-analysis.py): Analyzes new product ideas using LLMs.
- [utils.py](utils.py): Utility functions used by the examples.

## How to Run

To run any example, activate your environment and execute the desired script. For example:

```bash
source ../env/bin/activate
python example-1-hello-ai.py
```

## Example Output

Let us execute the hello world script and see the response from the phi3:mini model:

```bash
(env) ank@Ankurs-MacBook-Air chapter-01 % python example-1-hello-ai.py
['Hello back! A classic start. How can I help you today?']
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-01 % python example-2-setup-dspy.py   
["The Empire State Building is located in **New York City, New York, USA**. More specifically, it's in Midtown Manhattan, at 350 Fifth Avenue.\n"]
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-01 % python example-3-feedback-analysis.py gemini/gemini-2.0-flash-exp 1000
Note: Response may not be valid JSON format
```json
{
  "themes": {
    "negative": [
      "App crashes frequently on iOS",
      "Crashing when uploading photos",
      "Confusing interface",
      "Difficulty finding settings menu"
    ],
    "positive": [
      "Love the new dark mode feature",
      "Amazing photo filters"
    ]
  }
}
```
```
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-01 % python3 example-4-news-headline-category.py 
Headline: New advancements in AI technology are transforming industries worldwide.
Predicted Category: Technology
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-01 % python3 example-5-news-headline-indepth-categorization.py 
Article: In a landmark decision, the Supreme Court ruled today that climate change
    regulations must be strengthened to meet international commitments. The ruling,
    which was 6-3, mandates that federal agencies implement stricter emissions standards
    by 2025. Environmental groups hailed the decision as a major victory, while industry
    leaders expressed concern over potential economic impacts. The ruling is expected to
    influence policy discussions ahead of the upcoming global climate summit.

Predicted Category: Politics
Entities: ['Supreme Court', 'federal agencies', '2025']
Facts: ['The Supreme Court ruled that climate change regulations must be strengthened.', 'The ruling was 6-3.', 'Federal agencies must implement stricter emissions standards by 2025.', 'Environmental groups hailed the decision as a major victory.', 'Industry leaders expressed concern over potential economic impacts.']
Sentiment: neutral
Topics: ['Climate change regulations', 'Supreme Court ruling', 'Emissions standards', 'Environmental policy']
Summary: The Supreme Court ruled in a 6-3 decision that climate change regulations must be strengthened, mandating stricter emissions standards by 2025. Environmental groups praised the decision, while industry leaders voiced concerns about economic impacts.
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-01 % python example-6-new-product-analysis.py                 
iPhone 17 Pro
Electronics
999.0
True
<class '__main__.ProductInfo'>
```