
# Chapter 7

## Prerequisites

Make sure you have a running environment with all packages installed.

- If not, refer to the [Project README for instructions](../README.md).

## Running the MLflow Server

To run the local MLflow server, use the following command:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

## Expected Output

You will see output similar to the following (truncated for readability):

```bash
(env) ank@Ankurs-MacBook-Air dspy-book-codebase % mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
2025/11/07 11:56:33 INFO mlflow.store.db.utils: Creating initial MLflow database tables...
2025/11/07 11:56:33 INFO mlflow.store.db.utils: Updating database tables
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade  -> 451aebb31d03, add metric step
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 451aebb31d03 -> 90e64c465722, migrate user column to tags
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 90e64c465722 -> 181f10493468, allow nulls for metric values
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 181f10493468 -> df50e92ffc5e, Add Experiment Tags Table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade df50e92ffc5e -> 7ac759974ad8, Update run tags with larger limit
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 7ac759974ad8 -> 89d4b8295536, create latest metrics table
2025-11-07 11:56:33 INFO  [89d4b8295536_create_latest_metrics_table_py] Migration complete!
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 89d4b8295536 -> 2b4d017a5e9b, add model registry tables to db
2025-11-07 11:56:33 INFO  [2b4d017a5e9b_add_model_registry_tables_to_db_py] Adding registered_models and model_versions tables to database.
2025-11-07 11:56:33 INFO  [2b4d017a5e9b_add_model_registry_tables_to_db_py] Migration complete!
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 2b4d017a5e9b -> cfd24bdc0731, Update run status constraint with killed
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade cfd24bdc0731 -> 0a8213491aaa, drop_duplicate_killed_constraint
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 0a8213491aaa -> 728d730b5ebd, add registered model tags table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 728d730b5ebd -> 27a6a02d2cf1, add model version tags table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 27a6a02d2cf1 -> 84291f40a231, add run_link to model_version
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 84291f40a231 -> a8c4a736bde6, allow nulls for run_id
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade a8c4a736bde6 -> 39d1c3be5f05, add_is_nan_constraint_for_metrics_tables_if_necessary
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 39d1c3be5f05 -> c48cb773bb87, reset_default_value_for_is_nan_in_metrics_table_for_mysql
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade c48cb773bb87 -> bd07f7e963c5, create index on run_uuid
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade bd07f7e963c5 -> 0c779009ac13, add deleted_time field to runs table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 0c779009ac13 -> cc1f77228345, change param value length to 500
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade cc1f77228345 -> 97727af70f4d, Add creation_time and last_update_time to experiments table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 97727af70f4d -> 3500859a5d39, Add Model Aliases table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 3500859a5d39 -> 7f2a7d5fae7d, add datasets inputs input_tags tables
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 7f2a7d5fae7d -> 2d6e25af4d3e, increase max param val length from 500 to 8000
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 2d6e25af4d3e -> acf3f17fdcc7, add storage location field to model versions
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade acf3f17fdcc7 -> 867495a8f9d4, add trace tables
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 867495a8f9d4 -> 5b0e9adcef9c, add cascade deletion to trace tables foreign keys
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 5b0e9adcef9c -> 4465047574b1, increase max dataset schema size
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 4465047574b1 -> f5a4f2784254, increase run tag value limit to 8000
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade f5a4f2784254 -> 0584bdc529eb, add cascading deletion to datasets from experiments
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 0584bdc529eb -> 400f98739977, add logged model tables
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 400f98739977 -> 6953534de441, add step to inputs table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 6953534de441 -> bda7b8c39065, increase_model_version_tag_value_limit
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade bda7b8c39065 -> cbc13b556ace, add V3 trace schema columns
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade cbc13b556ace -> 770bee3ae1dd, add assessments table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 770bee3ae1dd -> a1b2c3d4e5f6, add spans table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade a1b2c3d4e5f6 -> de4033877273, create entity_associations table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade de4033877273 -> 1a0cddfcaa16, Add webhooks and webhook_events tables
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 1a0cddfcaa16 -> 534353b11cbc, add scorer tables
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 534353b11cbc -> 71994744cf8e, add evaluation datasets
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 71994744cf8e -> 3da73c924c2f, add outputs to dataset record
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Running upgrade 3da73c924c2f -> bf29a5ff90ea, add jobs table
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
2025/11/07 11:56:33 INFO mlflow.store.db.utils: Creating initial MLflow database tables...
2025/11/07 11:56:33 INFO mlflow.store.db.utils: Updating database tables
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
2025-11-07 11:56:33 INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
[MLflow] Security middleware enabled with default settings (localhost-only). To allow connections from other hosts, use --host 0.0.0.0 and configure --allowed-hosts and --cors-allowed-origins.
INFO:     Uvicorn running on http://127.0.0.1:5000 (Press CTRL+C to quit)
INFO:     Started parent process [22296]
INFO:     Started server process [22300]
INFO:     Waiting for application startup.
INFO:     Started server process [22299]
INFO:     Waiting for application startup.
INFO:     Started server process [22298]
INFO:     Started server process [22301]
INFO:     Waiting for application startup.
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Application startup complete.
INFO:     Application startup complete.
INFO:     Application startup complete.
```

## Troubleshooting

Your code will not work without the MLflow server running locally.

## References

[MLflow Quickstart Documentation](https://mlflow.org/docs/latest/ml/getting-started/quickstart/)

## Output of each example 

```bash
(env) ank@Ankurs-MacBook-Air chapter-07 % python example-1-basic-qa-mlflow-integration.py
2025/11/07 12:12:57 INFO mlflow.tracking.fluent: Experiment with name 'dspy-mlops-integration' does not exist. Creating a new experiment.
Question: What's the full form of CoT in the AI field?
Answer: Chain-of-Thought
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-07 % python example-2-prompt-registry.py 
2025/11/07 12:16:54 INFO mlflow.store.model_registry.abstract_store: Waiting up to 300 seconds for prompt version to finish creation. Prompt name: medical_diagnostic_recommender, version 1
(env) ank@Ankurs-MacBook-Air chapter-07 % 
```

```bash
(env) ank@Ankurs-MacBook-Air chapter-07 % python example-3-tweet-generator.py 
2025/11/07 12:26:05 INFO mlflow.tracking.fluent: Experiment with name 'tweet_generator' does not exist. Creating a new experiment.
🏃 View run tweet_What makes DSPy awesome?. at: http://127.0.0.1:5000/#/experiments/2/runs/97aa0f2b9c3f433086e8f5facd36dddd
🧪 View experiment at: http://127.0.0.1:5000/#/experiments/2
Generated: What makes DSPy truly awesome? ✨ It's the programmatic control over LLMs, optimizing prompts AND weights for better performance & reliability! Build robust, production-ready LLM applications with ease.

#DSPy #LLMs #AI #MachineLearning #PromptEngineering
Engagement: 1.00, Hashtags: 0.50

🏃 View run tweet_Why coffee is the best product at: http://127.0.0.1:5000/#/experiments/2/runs/f748d1fbeb314d58a36a666f9bb0bd8b
🧪 View experiment at: http://127.0.0.1:5000/#/experiments/2
Generated: Need a productivity hack? ☕️ Coffee isn't just a drink, it's your secret weapon! Boosts focus, sharpens alertness, and kickstarts your day. Unbeatable fuel for getting things done efficiently. What's your go-to productivity brew? #Coffee #ProductivityHack #Focus #EnergyBoost #WorkLife
Engagement: 0.70, Hashtags: 0.50
```