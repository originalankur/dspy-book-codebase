# Chapter 6

## Prerequisites

Make sure you have a running environment with all packages installed.

- If not, refer to the [Project README for instructions](../README.md).

## Example Scripts in Chapter 6

This chapter explores advanced optimization techniques in DSPy, including `BootstrapFewShot`, `KNNFewShot`, `MIPROv2`, and the experimental `GEPA` (Generative Evolutionary Prompt Adjustment) optimizer. It also covers integration with MLflow and complex agentic workflows.

- [example_1_brand_voice_rewrite.py](example_1_brand_voice_rewrite.py): Rewrites technical error messages into a friendly brand voice using `LabeledFewShot`.
- [example_2_bootstrap_few_shot.py](example_2_bootstrap_few_shot.py): Medical coding example optimizing clinical note conversion to ICD-10 codes using `BootstrapFewShot` and tracked with MLflow.
- [example_2_calender_json.py](example_2_calender_json.py): Optimize natural language to JSON conversion for calendar events using `BootstrapFewShot`.
- [example_2_pareto.py](example_2_pareto.py): A standalone example demonstrating Pareto efficiency algorithms, a concept often used in multi-objective optimization.
- [example_3_knn.py](example_3_knn.py): Sentiment classification for e-commerce reviews using `KNNFewShot` and sentence embeddings.
- [example_3_minimalistic_gepa.py](example_3_minimalistic_gepa.py): A minimal introduction to the `GEPA` optimizer for banking intent classification.
- [example_4_banking_intent.py](example_4_banking_intent.py): Extracting financial risks from transcripts, optimized with `GEPA` and an LLM-based judge.
- [example_4_miprov2.py](example_4_miprov2.py): Generating insurance denial letters using `MIPROv2` to balance compliance, empathy, and readability.
- [example_5_self_evolving_fintech_compliance_agent.py](example_5_self_evolving_fintech_compliance_agent.py): A sophisticated self-evolving agent for FinTech compliance (SAR generation) using `GEPA`.

## How to Run

To run any example, activate your environment and execute the desired script. For example:

```bash
# macOS / Linux
source ../env/bin/activate
python example_1_brand_voice_rewrite.py

# Windows (PowerShell)
../env/Scripts/Activate.ps1
python example_1_brand_voice_rewrite.py

# Windows (cmd.exe)
..\env\Scripts\activate.bat
python example_1_brand_voice_rewrite.py
```

> Tip: On many macOS / Linux systems you may use `python3` and `pip3`. On Windows, `python` and `pip` are typically the correct commands.

## Example Output

```bash
(env) ank@Ankurs-MacBook-Air chapter-06 % python example_1_brand_voice_rewrite.py
Technical Message: SSL certificate verification failed: ERR_CERT_AUTHORITY_INVALID
Friendly Version: It looks like this connection isn't secure right now. We're keeping your data safe by stopping here.
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-06 % python example_3_minimalistic_gepa.py
Running GEPA to evolve instructions...
(Note: If the model gets 100% on the first try, GEPA won't change anything.)

--- Final Optimized Instructions ---
Classify the user's banking query into exactly one of these intents: 
[block_card, stop_payment, dispute_charge].
...

--- Test Output ---
Query: Card not there, stop transactions.
Predicted Intent: block_card
Reasoning: The user is reporting their card is missing ("Card not there") and wants to prevent further use ("stop transactions"). This aligns with blocking a lost or stolen card.
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-06 % python example_3_knn.py

Test Review: The stitching on these boots is falling apart.
Predicted: Negative
Reasoning: Produce the sentiment. The review explicitly mentions a defect ("stitching... falling apart"), which is a negative product attribute.
```
