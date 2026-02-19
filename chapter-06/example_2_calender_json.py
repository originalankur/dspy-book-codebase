import dspy
import json
import mlflow
import mlflow.dspy
from dspy.teleprompt import BootstrapFewShot

# <1>
teacher_model = dspy.LM("gemini/gemini-2.5-pro", max_tokens=2000) 
student_model = dspy.LM("gemini/gemini-2.5-flash", max_tokens=2000)
dspy.settings.configure(lm=student_model)

mlflow.set_experiment("Calendar_Event_Creator")

# 2. DEFINE SIGNATURE <2>
class TextToAPIPayload(dspy.Signature):
    """Transform a natural language calendar command into a valid JSON payload for the API.
    Ensure dates are ISO 8601 format and all required fields are present."""
    
    user_command = dspy.InputField(desc="The natural language request from the user")
    api_payload = dspy.OutputField(desc="The JSON string payload for the /events/create endpoint")

# 3. DEFINE MODULE <3>
class PayloadGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(TextToAPIPayload)
    
    def forward(self, user_command):
        return self.prog(user_command=user_command)

# 4. LOAD DATA <4>
# Training data will be loaded in the main function

# 5. DEFINE METRIC WITH MLFLOW LOGGING <5>
# The metric checks if the output is valid JSON and matches the gold standard
def json_match_metric(gold, pred, trace=None):
    # Track individual metric evaluations
    metric_result = {
        'valid_json': False,
        'required_fields_present': False,
        'no_extra_fields': False,
        'exact_match': False,
        'final_score': 0
    }
    
    # 1. Check if it's valid JSON
    try:
        pred_json = json.loads(pred.api_payload)
        gold_json = json.loads(gold.api_payload)
        metric_result['valid_json'] = True
    except:
        mlflow.log_metric("metric_failures_invalid_json", 1)
        return 0  # Fail if invalid JSON
    
    # 2. Check required fields are present
    required_fields = ['summary', 'start_time', 'duration_minutes']
    for field in required_fields:
        if field not in pred_json:
            mlflow.log_metric("metric_failures_missing_required", 1)
            return 0
    metric_result['required_fields_present'] = True
    
    # 3. Check only allowed fields are present (no extra fields)
    allowed_fields = {'summary', 'start_time', 'duration_minutes', 'attendees', 'recurrence'}
    for field in pred_json.keys():
        if field not in allowed_fields:
            mlflow.log_metric("metric_failures_extra_fields", 1)
            return 0  # Reject if unknown fields are present
    metric_result['no_extra_fields'] = True
    
    # 4. Strict comparison for exact match
    # For bootstrapping, we want the teacher to generate strictly correct examples
    exact_match = pred_json == gold_json
    metric_result['exact_match'] = exact_match
    metric_result['final_score'] = 1 if exact_match else 0
    
    # Log successful metric evaluation
    if exact_match:
        mlflow.log_metric("metric_successes", 1)
    else:
        mlflow.log_metric("metric_failures_inexact_match", 1)
    
    return metric_result['final_score']

def load_training_data(file_path='calendar_demos.json'):
    """Load and prepare training data from JSON file."""
    with open(file_path, 'r') as f:
        raw_data = json.load(f)
    
    trainset = [
        dspy.Example(
            user_command=x['user_command'], 
            api_payload=x['api_payload']
        ).with_inputs('user_command') 
        for x in raw_data
    ]
    return trainset

def compile_calendar_assistant(trainset, teacher_model, student_model):
    """Compile the calendar assistant using BootstrapFewShot optimization."""
    fewshot_optimizer = BootstrapFewShot(
        metric=json_match_metric,
        max_bootstrapped_demos=4,
        max_labeled_demos=16,
        max_rounds=1,
        max_errors=5,
        teacher_settings=dict(lm=teacher_model)
    )
    
    print("Starting BootstrapFewShot compilation...")
    return fewshot_optimizer.compile(
        student=PayloadGenerator(),
        trainset=trainset
    )

def log_compilation_results(compiled_model):
    """Log compilation results to MLflow."""
    try:
        if hasattr(compiled_model, 'prog') and hasattr(compiled_model.prog, 'demos'):
            mlflow.log_metric("compiled_demos_count", len(compiled_model.prog.demos))
        else:
            mlflow.log_metric("compiled_demos_count", 0)
    except Exception as e:
        print(f"Could not access demos from compiled program: {e}")
        mlflow.log_metric("compiled_demos_count", 0)

def test_and_inspect(compiled_model, test_command):
    """Test the compiled model and inspect the prompt."""
    result = compiled_model(user_command=test_command)
    
    # Log test results
    mlflow.log_param("test_input", test_command)
    mlflow.log_text(result.api_payload, "test_output.json")
    
    print("Generated API Payload:")
    print(result.api_payload)
    
    # Show the last prompt sent to LM
    print("\n" + "="*50)
    print("LAST PROMPT SENT TO LM:")
    print("="*50)
    history = dspy.inspect_history(n=1)
    if history:
        print(history[0].prompt if hasattr(history[0], 'prompt') else history[0])
    print("="*50)
    
    return result

def main():
    """Main execution function."""
    # Load training data
    trainset = load_training_data()
    
    # 6. OPTIMIZE WITH MLFLOW TRACKING <6>
    with mlflow.start_run(run_name="BootstrapFewShot_Compilation"):
        # Log hyperparameters
        mlflow.log_params({
            "teacher_model": "google/gemini-pro-3",
            "student_model": "google/gemini-flash-2.5",
            "max_bootstrapped_demos": 4,
            "max_labeled_demos": 16,
            "max_rounds": 1,
            "max_errors": 5,
            "training_set_size": len(trainset)
        })
        
        # Log training data statistics
        mlflow.log_metric("total_training_examples", len(trainset))
        
        # Compile the model
        calendar_assistant_compiled = compile_calendar_assistant(trainset, teacher_model, student_model)
        
        # Log compilation results
        log_compilation_results(calendar_assistant_compiled)
        
        # Log the compiled program as an artifact
        mlflow.dspy.log_model(
            dspy_model=calendar_assistant_compiled,
            name="calendar_assistant_model",
            registered_model_name="CalendarAPIGenerator"
        )
        
        # Test and inspect results
        test_command = "Yash said tentatively he can do podcast at 9:30 am tomorrow, let me send him an invite and see if he accepts."
        test_and_inspect(calendar_assistant_compiled, test_command)
        
        # Log final prompt structure for analysis
        prompt_info = {
            "instruction_present": True,
            "labeled_demos_count": 12,
            "bootstrapped_demos_count": 4,
            "reasoning_examples_included": True
        }
        mlflow.log_dict(prompt_info, "final_prompt_structure.json")

if __name__ == "__main__":
    main()


