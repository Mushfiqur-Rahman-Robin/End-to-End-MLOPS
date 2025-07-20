from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# define function for each task
def start_number(**context):
    context["ti"].xcom_push(key="current_value", value=10)
    print("Starting number is: ", context["ti"].xcom_pull(key="current_value"))

def add_five(**context):
    current_value = context["ti"].xcom_pull(key="current_value", task_ids="start_task")
    new_value = current_value + 5
    context["ti"].xcom_push(key="current_value", value=new_value)
    print("New number is: ", context["ti"].xcom_pull(key="current_value"))

def multiply_by_two(**context):
    current_value = context["ti"].xcom_pull(key="current_value", task_ids="add_five_task")
    new_value = current_value * 2
    context["ti"].xcom_push(key="current_value", value=new_value)
    print("New number is: ", context["ti"].xcom_pull(key="current_value"))

def subtract_three(**context):
    current_value = context["ti"].xcom_pull(key="current_value", task_ids="multiply_by_two_task")
    new_value = current_value - 3
    context["ti"].xcom_push(key="current_value", value=new_value)
    print("New number is: ", context["ti"].xcom_pull(key="current_value"))

def square_number(**context):
    current_value = context["ti"].xcom_pull(key="current_value", task_ids="subtract_three_task")
    new_value = current_value * current_value
    context["ti"].xcom_push(key="current_value", value=new_value)
    print("New number is: ", context["ti"].xcom_pull(key="current_value"))

# define DAG
with DAG("math_operations", start_date=datetime(2025, 1, 1), schedule="@daily", catchup=False) as dag:
    start_task = PythonOperator(task_id="start_task", python_callable=start_number)
    add_five_task = PythonOperator(task_id="add_five_task", python_callable=add_five)
    multiply_by_two_task = PythonOperator(task_id="multiply_by_two_task", python_callable=multiply_by_two)
    subtract_three_task = PythonOperator(task_id="subtract_three_task", python_callable=subtract_three)
    square_number_task = PythonOperator(task_id="square_number_task", python_callable=square_number)

    start_task >> add_five_task >> multiply_by_two_task >> subtract_three_task >> square_number_task
