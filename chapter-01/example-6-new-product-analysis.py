import dspy
from pydantic import BaseModel, Field

lm = dspy.LM('gemini/gemini-2.0-flash-exp')
dspy.configure(lm=lm)

class ProductInfo(BaseModel):
    name: str = Field(description="Product name")
    category: str = Field(description="Product category")
    price: float = Field(gt=0, description="Price in USD")
    in_stock: bool = Field(description="Whether product is in stock")

class ExtractProduct(dspy.Signature):
    """Extract structured product information from text."""
    text: str = dspy.InputField(desc="Raw text containing product information")
    product: ProductInfo = dspy.OutputField(desc="Structured product details")

# Get predictor module
predictor = dspy.Predict(ExtractProduct)

# Run the prediction
result = predictor(text="The iPhone 17 Pro is launched for $999 and currently in stock in India.")

# Access the validated Pydantic model
print(result.product.name) # "iPhone 15 Pro"
print(result.product.category) # e.g., "Electronics"
print(result.product.price) # 999.0 (validated float > 0)
print(result.product.in_stock) # True (validated bool)

# The entire object is a validated Pydantic instance
print(type(result.product)) # <class '__main__.ProductInfo'>