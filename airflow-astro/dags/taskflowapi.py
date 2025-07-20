from airflow import DAG
from airflow.decorators import task
from datetime import datetime

# define DAG
with DAG("math_operations_taskflowapi", start_date=datetime(2025, 1, 1), schedule="@daily", catchup=False) as dag:
    # task 1
    @task
    def start_number():
        initial_value = 10
        print(f"Initial value: {initial_value}")
        return initial_value
    
    # task 2
    @task
    def add_five(current_value):
        new_value = current_value + 5
        print(f"New value: {new_value}")
        return new_value
    
    # task 3
    @task
    def multiply_by_two(current_value):
        new_value = current_value * 2
        print(f"New value: {new_value}")
        return new_value
    
    # task 4
    @task
    def subtract_three(current_value):
        new_value = current_value - 3
        print(f"New value: {new_value}")
        return new_value
    
    # task 5
    @task
    def square_number(current_value):
        new_value = current_value * current_value
        print(f"New value: {new_value}")
        return new_value
    
    # set task dependencies
    start_number_task = start_number()
    add_five_task = add_five(start_number_task)
    multiply_by_two_task = multiply_by_two(add_five_task)
    subtract_three_task = subtract_three(multiply_by_two_task)
    square_number_task = square_number(subtract_three_task)