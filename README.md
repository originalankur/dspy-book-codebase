# Repository To Accompany The DSPy Book

<!-- TOC -->
- [Repository To Accompany The DSPy Book](#repository-to-accompany-the-dspy-book)
  - [Setup](#setup)
    - [Python Environment](#python-environment)
    - [Language Model Configuration](#language-model-configuration)
      - [Default: Gemini](#default-gemini)
      - [Alternative Models](#alternative-models)
        - [OpenAI](#openai)
        - [Anthropic](#anthropic)
  - [Chapter wise Code and Description](#chapter-wise-code-and-description)
<!-- /TOC -->

## Setup

### Python Environment

These steps show a simple way to create a Python virtual environment and install dependencies using Python 3.12 or 3.13. Python installation instructions can be found on python.org or through package managers like pyenv.

1. Verify you have the right Python version available:

```bash
python3 --version
# or, if you have the 3.12 executable available explicitly:
python3.12 --version
```

2. Create a virtual environment (recommended):

```bash
python3 -m venv env
```

3. Activate the virtual environment:

```bash
# On macOS / Linux
source env/bin/activate
```

On Windows (PowerShell)

`env\Scripts\Activate.ps1`

On Windows (cmd.exe)

`env\Scripts\activate.bat`

1. Upgrade pip and install dependencies:

```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

On Windows you may use `pip` if `pip3` is not available:

`pip install --upgrade pip`

`pip install -r requirements.txt`

5. Verify DSPy version:

```bash
pip freeze | grep dspy
# Should show: dspy==3.0.3
```

> **Important**: This codebase requires DSPy 3.x. The older 2.x series is no longer maintained and will not work.

---

### Language Model Configuration

#### Default: Gemini

The codebase has been tested with Gemini 2.x series models. Simply export your API key as an environment variable:

```bash
export GEMINI_API_KEY=YOUR_API_KEY_HERE
```

To verify the key is set:

```bash
env | grep GEMINI_API_KEY
```

#### Alternative Models

You can configure other language models as follows:

##### OpenAI

```python
import dspy
lm = dspy.LM("openai/gpt-4o-mini", api_key="YOUR_OPENAI_API_KEY")
dspy.configure(lm=lm)
```

##### Anthropic

```python
import dspy
lm = dspy.LM("anthropic/claude-sonnet-4-5-20250929", api_key="YOUR_ANTHROPIC_API_KEY")
dspy.configure(lm=lm)
```

For model names and specifications, refer to:
- Anthropic: https://docs.claude.com/en/docs/intro
- OpenAI: https://platform.openai.com/docs/models 

---

## Chapter wise Code and Description  
- Each chapter's code is located in its respective folder

- [Chapter 1](chapter-01/): Introductory DSPy examples
  - [Chapter 1 README](chapter-01/README.md): Chapter-specific notes, prerequisites, Ollama setup, example script list, run instructions and sample outputs.
  - [example-1-hello-ai.py](chapter-01/example-1-hello-ai.py): Basic "hello AI" example demonstrating a minimal prompt and response flow with DSPy.
  - [example-2-setup-dspy.py](chapter-01/example-2-setup-dspy.py): Shows initializing and configuring DSPy (LM setup, environment checks).
  - [example-3-feedback-analysis.py](chapter-01/example-3-feedback-analysis.py): Script illustrating simple feedback analysis and aggregation using DSPy helpers.
  - [example-4-news-headline-category.py](chapter-01/example-4-news-headline-category.py): Basic classification of news headlines into categories.
  - [example-5-news-headline-indepth-categorization.py](chapter-01/example-5-news-headline-indepth-categorization.py): More detailed categorization pipeline for headlines with richer prompts/analysis.
  - [example-6-new-product-analysis.py](chapter-01/example-6-new-product-analysis.py): Example analyzing new product descriptions and extracting insights.
  - [utils.py](chapter-01/utils.py): Utility functions reused across the chapter examples.
- [Chapter 2](chapter-02/): Advanced DSPy Modules and Prediction Techniques
  - [Chapter 2 README](chapter-02/README.md): Chapter-specific notes, Deno setup for CodeAct/PoT, example script list, run instructions and sample outputs.
  - [example-1-custom-dspy-module.py](chapter-02/example-1-custom-dspy-module.py): Creating custom DSPy modules for news classification.
  - [example-2-dspy-predict-few-shot-learning.py](chapter-02/example-2-dspy-predict-few-shot-learning.py): Few-shot learning with medical coding examples.
  - [example-3-chain_of_thought.py](chapter-02/example-3-chain_of_thought.py): Chain of Thought reasoning for step-by-step problem solving.
  - [example-4-ticket-classification.py](chapter-02/example-4-ticket-classification.py): Support ticket classification with SLA routing.
  - [example-5-domain-name-react.py](chapter-02/example-5-domain-name-react.py): ReAct pattern for domain name generation and availability checking.
  - [example-6-investment-signature-pot.py](chapter-02/example-6-investment-signature-pot.py): Program of Thought for investment calculations with Python code generation.
  - [example-7-text-processing-cot.py](chapter-02/example-7-text-processing-cot.py): CodeAct for text analysis using custom tools.
  - [example-8-investment-strategy-multi-chain.py](chapter-02/example-8-investment-strategy-multi-chain.py): MultiChainComparison for evaluating multiple investment strategies.
  - [example-9-ecom-product-description-best-of-n.py](chapter-02/example-9-ecom-product-description-best-of-n.py): BestOfN sampling with custom scoring for product descriptions.
  - [example-10-refine-customer-support.py](chapter-02/example-10-refine-customer-support.py): Iterative refinement of customer support responses.
  - [example-11-parallel.py](chapter-02/example-11-parallel.py): Parallel processing of multiple predictions.
  - [example-12-pipeline.py](chapter-02/example-12-pipeline.py): Building multi-stage pipelines for medical diagnosis.
- [Chapter 3](chapter-03/): Guardrails and Evaluation Techniques
  - [Chapter 3 README](chapter-03/README.md): Chapter-specific notes on guardrails and evaluation, example script list, run instructions and sample outputs.
  - [example-1-guardrail-regex.py](chapter-03/example-1-guardrail-regex.py): Regex-based guardrails for detecting sensitive data (account numbers, folio numbers) and checking for legal disclaimers.
  - [example-2-guardrail-llm-as-judge.py](chapter-03/example-2-guardrail-llm-as-judge.py): Using LLM as a judge to evaluate investment compliance, detecting unlicensed advice and guaranteed return promises.
  - [example-3-support-bot.py](chapter-03/example-3-support-bot.py): Building and evaluating a customer support chatbot with custom quality metrics and DSPy's Evaluate framework.
- [Chapter 4](chapter-04/README.md) RepoRank - Capstone Project
  - [main.py](chapter-04/reporank/main.py): Main entry point for the RepoRank capstone project  
- [Chapter 7](chapter-07/): MLflow Integration Examples
  - [Chapter 7 README](chapter-07/README.md): Contains setup instructions for MLflow server and examples of:
    - [Basic QA MLflow Integration](chapter-07/example-1-basic-qa-mlflow-integration.py)
    - [Prompt Registry with MLflow](chapter-07/example-2-prompt-registry.py)
    - [Tweet Generator with MLflow Experiment Tracking](chapter-07/example-3-tweet-generator.py)

