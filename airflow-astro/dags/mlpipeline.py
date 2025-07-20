from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# define task 1
def preprocess_data():
    print("Preprocessing data...")

# define task 2
def train_model():
    print("Training model...")

# define task 3
def evaluate_model():
    print("Evaluating model...")

# define the DAG
with DAG("mlpipeline", start_date=datetime(2025, 1, 1), schedule="@daily", catchup=False) as dag:
    preprocess_task = PythonOperator(task_id="preprocess_data", python_callable=preprocess_data)
    train_task = PythonOperator(task_id="train_model", python_callable=train_model)
    evaluate_task = PythonOperator(task_id="evaluate_model", python_callable=evaluate_model)

    preprocess_task >> train_task >> evaluate_task  # define task dependencies
