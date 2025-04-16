from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import json
import requests

from utils.clients.db_clients.db_client import connect_to_db
from utils.clients.db_clients.dbs.raw_data import insert_data_to_raw_data_table
from utils.client_utils import insert_data_to_raw_data_table_task

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

def fetch_data(ti):
    """Fetch data from the Long Beach API."""
    base_url = "https://data.longbeach.gov/api/explore/v2.1/catalog/datasets/animal-shelter-intakes-and-outcomes/records"
    cat_params = [
        ("refine", f"outcome_date:{(datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')}"),
        ("refine", "animal_type:CAT"),
    ]
    dog_params = [
        ("refine", f"outcome_date:{(datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')}"),
        ("refine", "animal_type:DOG"),
    ]
    all_cat_data = []
    all_dog_data = []
    all_data = []

    print(f"Fetching data from {base_url} with params: {cat_params} and {dog_params}")

    # Fetch data for cats
    cat_response = requests.get(base_url, params=cat_params)
    if cat_response.status_code != 200:
        print(f"Failed to fetch cat data: {cat_response.status_code}")
    else:
        cat_data = cat_response.json()
        all_cat_data.extend(cat_data.get("results", []))

    # Fetch data for dogs
    dog_response = requests.get(base_url, params=dog_params)
    if dog_response.status_code != 200:
        print(f"Failed to fetch dog data: {dog_response.status_code}")
    else:
        dog_data = dog_response.json()
        all_dog_data.extend(dog_data.get("results", []))

    # Combine the all_cat_data and all_dog_data into all_data
    all_data.extend(all_cat_data)
    all_data.extend(all_dog_data)

    # Push the collected data to XCom
    ti.xcom_push(key="all_data", value=all_data)

with DAG(
    dag_id="fetch_long_beach_data",
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=timedelta(hours=24),
    catchup=False,
) as dag:
    # Task 1: Fetch data from the Long Beach API
    fetch_data_task = PythonOperator(
        task_id="fetch_data_task",
        python_callable=fetch_data,
    )

    # Task 2: Insert data into the raw_data table
    insert_data_task = PythonOperator(
        task_id="insert_data_task",
        python_callable=insert_data_to_raw_data_table_task,
        op_kwargs={
            "conn": connect_to_db(),  # Pass the database connection
            "task_id": "fetch_data_task",  # Task ID to pull data from
            "task_key": "all_data",  # Key to pull data from XCom
            "source_name": "City of Long Beach Animal Shelter",  # Source name
        },
    )

    # Define task dependencies
    fetch_data_task >> insert_data_task
