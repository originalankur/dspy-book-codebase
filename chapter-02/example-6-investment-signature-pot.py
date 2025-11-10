import dspy
from dspy.predict.program_of_thought import PythonInterpreter # <1>

lm = dspy.LM('gemini/gemini-2.0-flash')
dspy.configure(lm=lm)

class InvestmentSignature(dspy.Signature):
    """Calculate investment returns and portfolio metrics"""
    initial_investment = dspy.InputField(desc="Initial investment amount") # <2>
    monthly_contribution = dspy.InputField(desc="Monthly contribution amount")
    annual_return = dspy.InputField(desc="Expected annual return rate (percentage)")
    years = dspy.InputField(desc="Investment period in years")
    code:dspy.Code["python"] = dspy.OutputField(desc="Python code for investment calculations") # <3>
    final_value = dspy.OutputField(desc="Final portfolio value")
    total_contributions = dspy.OutputField(desc="Total amount contributed")
    total_earnings = dspy.OutputField(desc="Total earnings from investments")

investment_calculator = dspy.ProgramOfThought(InvestmentSignature, 
    interpreter=PythonInterpreter()) # <4>

result = investment_calculator(
    initial_investment="$10,000",
    monthly_contribution="$500",
    annual_return="7.5%",
    years="20"
)

print(f"Calculation Code:\n{result.code}\n") 
print(f"Final Portfolio Value: {result.final_value}")
print(f"Total Contributions: {result.total_contributions}")
print(f"Total Earnings: {result.total_earnings}")
