import dspy
lm = dspy.LM('gemini/gemini-2.0-flash')

dspy.configure(lm=lm)

class InvestmentStrategySignature(dspy.Signature):
    """Compare multiple investment strategies."""
    client_profile = dspy.InputField(desc="Client risk profile and goals")
    market_conditions = dspy.InputField(desc="Current market conditions")
    time_horizon = dspy.InputField(desc="Investment time horizon")
    recommended_strategy = dspy.OutputField(desc="Recommended investment strategy")
    expected_return = dspy.OutputField(desc="Expected annual return")
    risk_assessment = dspy.OutputField(desc="Risk assessment")

class InvestmentStrategyModule(dspy.Module): # <1>
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(InvestmentStrategySignature)
        self.compare = dspy.MultiChainComparison(InvestmentStrategySignature, M=4) # <2>
    
    def forward(self, client_profile, market_conditions, time_horizon):
        # Generate M completions
        completions = []
        for i in range(4):
            completion = self.generate(
                client_profile=client_profile,
                market_conditions=market_conditions,
                time_horizon=time_horizon
            )
            completions.append(completion)
            print(f"\n{'='*60}")
            print(f"CHAIN {i+1}:")
            print(f"{'='*60}")
            print(f"Strategy: {completion.recommended_strategy}")
            print(f"Expected Return: {completion.expected_return}")
            print(f"Risk Assessment: {completion.risk_assessment}")
        
        # Compare and select the best
        print(f"\n{'='*60}")
        print("COMPARING ALL CHAINS AND SELECTING BEST...")
        print(f"{'='*60}")
        result = self.compare(
            client_profile=client_profile,
            market_conditions=market_conditions,
            time_horizon=time_horizon,
            completions=completions
        )
        return result

strategy_comparer = InvestmentStrategyModule()

result = strategy_comparer(
    client_profile="Age 45, moderate risk tolerance, $500K portfolio, goal: retirement at 65",
    market_conditions="Bull market, low interest rates, high inflation (6%)",
    time_horizon="20 years"
) # <3>

print(f"\n{'='*60}")
print("FINAL SELECTED STRATEGY:")
print(f"{'='*60}")
print(f"Recommended Strategy: {result.recommended_strategy}")
print(f"Expected Return: {result.expected_return}")
print(f"Risk Assessment: {result.risk_assessment}")
