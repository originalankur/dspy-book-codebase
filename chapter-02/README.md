# Chapter 2

## Prerequisites

Make sure you have a running environment with all packages installed.

- If not, refer to the [Project README for instructions](../README.md).

## Deno Setup

Install Deno: Download from [Deno Download Page](https://docs.deno.com/runtime/getting_started/installation/)

NOTE - Deno is needed by CodeAct and PoT.

## Example Scripts in Chapter 2

This chapter contains advanced DSPy examples demonstrating modules, signatures, and various prediction techniques:

- [example-1-custom-dspy-module.py](example-1-custom-dspy-module.py): Creating custom DSPy modules for news classification.
- [example-2-dspy-predict-few-shot-learning.py](example-2-dspy-predict-few-shot-learning.py): Few-shot learning with medical coding examples.
- [example-3-chain_of_thought.py](example-3-chain_of_thought.py): Chain of Thought reasoning for step-by-step problem solving.
- [example-4-ticket-classification.py](example-4-ticket-classification.py): Support ticket classification with SLA routing.
- [example-5-domain-name-react.py](example-5-domain-name-react.py): ReAct pattern for domain name generation and availability checking.
- [example-6-investment-signature-pot.py](example-6-investment-signature-pot.py): Program of Thought for investment calculations with Python code generation.
- [example-7-text-processing-cot.py](example-7-text-processing-cot.py): CodeAct for text analysis using custom tools.
- [example-8-investment-strategy-multi-chain.py](example-8-investment-strategy-multi-chain.py): MultiChainComparison for evaluating multiple investment strategies.
- [example-9-ecom-product-description-best-of-n.py](example-9-ecom-product-description-best-of-n.py): BestOfN sampling with custom scoring for product descriptions.
- [example-10-refine-customer-support.py](example-10-refine-customer-support.py): Iterative refinement of customer support responses.
- [example-11-parallel.py](example-11-parallel.py): Parallel processing of multiple predictions.
- [example-12-pipeline.py](example-12-pipeline.py): Building multi-stage pipelines for medical diagnosis.

## How to Run

To run any example, activate your environment and execute the desired script. For example:

```bash
# macOS / Linux
source ../env/bin/activate
python example-1-custom-dspy-module.py

# Windows (PowerShell)
../env/Scripts/Activate.ps1
python example-1-custom-dspy-module.py

# Windows (cmd.exe)
..\env\Scripts\activate.bat
python example-1-custom-dspy-module.py
```
> Tip: On many macOS / Linux systems you may use `python3` and `pip3`. On Windows, `python` and `pip` are typically the correct commands.

## Example Output

```bash
(env) ank@Ankurs-MacBook-Air chapter-02 % python example-1-custom-dspy-module.py
Business
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-02 % python example-2-dspy-predict-few-shot-learning.py
ICD-10 Codes: I11.0, I50.9
Rationale: The clinical note indicates hypertensive heart disease with heart failure. I11.0 maps to Hypertensive heart disease with heart failure and I50.9 maps to Heart failure, unspecified.
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-02 % python3 example-3-chain_of_thought.py 
Reasoning: To find the speed of the train, we need to divide the distance traveled by the time it took to travel that distance.
Speed = Distance / Time
In this case, the distance is 120 miles and the time is 2 hours.
Answer: Speed = 120 miles / 2 hours = 60 miles per hour

The speed of the train is 60 miles per hour.
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-02 % python example-4-ticket-classification.py
Classification Reasoning:
The payment gateway being down and causing lost sales is a critical issue. It affects all customers, indicating a widespread outage. The customer is an Enterprise tier, which requires the highest level of support. Therefore, this is a P1 priority. The category is payment processing. The routing team should be the payment team. The SLA deadline should be immediate.

Category: Payment Processing
Priority: P1
SLA Deadline: Immediate
Routing: Payment Team
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-02 % python example-5-domain-name-react.py

--- Finding Domain Names for: 'A finance app that analyzes your portfolio from a value investing perspective.' ---


--- Final Domain Suggestions ---
1. intrinsicvalueinsights.com - Available
2. valuecompassanalytics.com - Available
3. prudentcapitaladvisor.com - Available
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-02 % python3 example-6-investment-signature-pot.py
Calculation Code:
```python
def calculate_investment(initial_investment, monthly_contribution, annual_return, years):
    initial_investment = float(initial_investment.replace('$', '').replace(',', ''))
    monthly_contribution = float(monthly_contribution.replace('$', '').replace(',', ''))
    annual_return = float(annual_return.replace('%', '')) / 100
    years = int(years)

    monthly_return = annual_return / 12
    months = years * 12

    # Future value of initial investment
    fv_initial = initial_investment * (1 + monthly_return)**months

    # Future value of monthly contributions (annuity)
    fv_annuity = monthly_contribution * ((1 + monthly_return)**months - 1) / monthly_return

    # Total future value
    total_fv = fv_initial + fv_annuity

    # Total contributions
    total_contributions = initial_investment + (monthly_contribution * months)

    # Total earnings
    total_earnings = total_fv - total_contributions

    return {
        "final_value": round(total_fv, 2),
        "total_contributions": round(total_contributions, 2),
        "total_earnings": round(total_earnings, 2)
    }

# Example usage
investment_details = calculate_investment("$10,000", "$500", "7.5%", "20")
print(investment_details)
```

Final Portfolio Value: 321473.53
Total Contributions: 130000.0
Total Earnings: 191473.53
```
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-02 % python example-11-parallel.py 
Processed 5 / 5 examples: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  2.82it/s]

Input 1: Classify: Patient has fever and cough
Output: Illness

Input 2: Classify: Transaction amount $5000 from foreign country
Output: Fraud

Input 3: Classify: Customer complaint about billing
Output: Billing Complaint

Input 4: Classify: Request for password reset
Output: Password Reset Request

Input 5: Classify: Medication refill request
Output: Medication
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-02 % python example-12-pipeline.py

Case 1: Pneumonia (High)
Tests: *   **Complete Blood Count (CBC):** To evaluate white blood cell count, which can indicate infection.
*   **Chest X-ray:** To visualize the lungs and identify areas of consolidation or inflammation.
*   **Sputum Culture and Gram Stain:** To identify the causative bacteria or fungi.
*   **Blood Cultures:** To detect bacteremia (bacteria in the bloodstream).
*   **Pulse Oximetry:** To measure oxygen saturation levels in the blood.
*   **Arterial Blood Gas (ABG):** To assess blood pH, oxygen, and carbon dioxide levels (especially in severe cases).
*   **Influenza and RSV testing:** If viral pneumonia is suspected, especially during flu season.
*   **COVID-19 PCR test:** To rule out COVID-19.
```
