import dspy
from typing import Optional

def setup_dspy(model: str, max_tokens: int = 4000, api_key: Optional[str] = None, **args) -> dspy.LM:
    """
    Setup DSPy language model configuration.
    
    Parameters:
        model (str): The name/identifier of the language model to use
        max_tokens (int): Maximum number of tokens for model responses, defaults to 4000
        api_key (str, optional): API key for authentication with the model provider
        **kwargs: Arbitrary keyword arguments for model-specific configuration
    
    Returns:
        dspy.LM: Configured DSPy language model instance
    """
    if model is None:
        raise Exception("Model cannot be None")
    
    lm = None
    try:
        lm = dspy.LM(model=model, max_tokens=max_tokens, api_key=api_key, **args)
        dspy.configure(lm=lm)
    except Exception as e:
        raise e
    
    return lm

if __name__ == "__main__":
    lm = setup_dspy("gemini/gemini-2.0-flash-exp", max_tokens=4000)
    response = lm("Where is Empire State Building?.")
    print(response)