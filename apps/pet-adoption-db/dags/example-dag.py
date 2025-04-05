import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

# Define a Python function to make the HTTP request
def fetch_todo():
    url = "https://jsonplaceholder.typicode.com/todos/1"
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

# Define the DAG
with DAG(
    'fetch_todo_dag',
    default_args=default_args,
    description='A DAG to fetch a TODO item and log the response',
    schedule_interval=timedelta(hours=12),  # Run every 12 hours
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    fetch_todo_task = PythonOperator(
        task_id='fetch_todo',
        python_callable=fetch_todo,
    )
