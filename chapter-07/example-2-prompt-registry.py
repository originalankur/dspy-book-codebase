import mlflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")

optimized_prompt_file_handler = open("medical_diagnostic_recommender.json", "r")
initial_template = optimized_prompt_file_handler.read()
optimized_prompt_file_handler.close()

prompt = mlflow.genai.register_prompt(
    name="medical_diagnostic_recommender",
    template=initial_template,
    commit_message="Initial commit - v1",
    tags={
        "author": "ankur@dspyweekly.com",
        "task": "Suggest Valid Test",
        "language": "en",
    },
)