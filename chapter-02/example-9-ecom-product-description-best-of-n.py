import dspy

lm = dspy.LM('gemini/gemini-2.0-flash')
dspy.configure(lm=lm)

PRODUCT_FEATURES = ["Wireless Bluetooth 5.2", "Active Noise-Cancelling", "20-hour battery"]
PRODUCT_NAME = "AuraSound Pro Headphones"
POWER_WORDS = ["discover", "upgrade", "essential", "perfect", "shop now", "get yours"]

class ProductDescriptionSignature(dspy.Signature):
    """Generate a compelling e-commerce product description."""
    product_name = dspy.InputField(desc="The name of the product.")
    features = dspy.InputField(desc="A list of key features, comma-separated.")
    description = dspy.OutputField(desc="A short, persuasive product description.")

    @staticmethod
    def score_product_description(args, pred, features_list): # <1>
        text = pred.description.lower() # <2>
        text_len = len(text)
        
        # Score based on description length
        if 150 < text_len < 300:
            score = 30  # Ideal length
        elif text_len < 150:
            score = -10  # Too short
        else:
            score = 0  # Too long
        
        # Score based on feature inclusion
        features_included = sum(1 for f in features_list if f.lower() in text)
        if features_included == len(features_list):
            score += 50  # All features mentioned
        else:
            score += features_included * 10  # Partial credit per feature
        
        if any(word in text for word in POWER_WORDS):
            score += 20
        
        return float(score) # <3>

all_attempts = [] # <4>

def scorer_fn_with_tracking(args, pred): # <5>
    score = ProductDescriptionSignature.score_product_description(args, pred, PRODUCT_FEATURES)
    all_attempts.append((pred, score)) # <6>
    return score

description_generator = dspy.BestOfN( # <7>
    dspy.Predict(ProductDescriptionSignature),
    N=3,
    reward_fn=scorer_fn_with_tracking, # <8>
    threshold=40.0 # <9>
)

best_description = description_generator(
    product_name=PRODUCT_NAME,
    features=", ".join(PRODUCT_FEATURES) # <10>
)

print(f"Product: {PRODUCT_NAME}")
print(f"Features: {PRODUCT_FEATURES}\n")

print(f"--- All {len(all_attempts)} Attempts ---")
for i, (pred, score) in enumerate(all_attempts, 1):
    print(f"\nAttempt {i} (Score: {score}):")
    print(pred.description)
    print("-" * 50)

print(f"\n--- Best Description ---")
print(best_description.description)

final_score = ProductDescriptionSignature.score_product_description(None, best_description, PRODUCT_FEATURES) # <11>
print(f"\nQuality Score: {final_score}")
