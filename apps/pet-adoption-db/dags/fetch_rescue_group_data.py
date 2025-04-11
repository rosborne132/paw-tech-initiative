from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import json
import requests

from utils.db_client import connect_to_db
from utils.client_utils import insert_data_to_raw_data_table_task

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

RC_API_KEY = os.getenv("RC_API_KEY")

def fetch_paginated_data_by_type(animal_type):
    """Fetch paginated data from the Rescue Groups API for a specific animal type."""
    yesterdays_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    base_url = f"https://api.rescuegroups.org/v5/public/animals/search/{animal_type}"
    headers = {
        "Authorization": f"{RC_API_KEY}"
    }
    params = {
        "limit": 100,
        "page": 1,
        "sort": "-animals.updatedDate",
    }
    all_data = []

    while True:
        response = requests.get(base_url, headers=headers, params=params)
        temp_data = []
        should_stop = False
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break

        fetched_response = response.json()
        response_data = fetched_response.get("data", [])

        for item in response_data:
            updated_date = item.get("attributes", {}).get("updatedDate")
            status_id = item.get("relationships", {}).get("statuses", {}).get("data", [{}])[0].get("id")

            if updated_date and updated_date < yesterdays_date:
                should_stop = True
                break

            if status_id not in ["1", "3"]:
                continue

            temp_data.append(item)

        all_data.extend(temp_data)

        if should_stop:
            break
        else:
            params["page"] += 1

    return all_data

def fetch_paginated_data(ti):
    """Fetch data from the Rescue Groups API."""
    all_cat_data = fetch_paginated_data_by_type("cats")
    all_dog_data = fetch_paginated_data_by_type("dogs")
    all_data = []
    all_data.extend(all_cat_data)
    all_data.extend(all_dog_data)

    print(f"Total number of cat records fetched: {len(all_cat_data)}")
    print(f"Total number of dog records fetched: {len(all_dog_data)}")
    print(f"Total number of records fetched: {len(all_data)}")

    ti.xcom_push(key="all_data", value=all_data)

with DAG(
    dag_id="fetch_rescue_groups_data",
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=timedelta(hours=24),
    catchup=False,
) as dag:
    # Task 1: Fetch data from the Rescue Groups API
    fetch_data_task = PythonOperator(
        task_id="fetch_paginated_data",
        python_callable=fetch_paginated_data,
    )

    # Task 2: Insert data into the raw_data table
    insert_data_task = PythonOperator(
        task_id="insert_data_task",
        python_callable=insert_data_to_raw_data_table_task,
        op_kwargs={
            "conn": connect_to_db(),  # Pass the database connection
            "task_id": "fetch_paginated_data",  # Task ID to pull data from
            "task_key": "all_data",  # Key to pull data from XCom
            "source_name": "Rescue Groups",  # Source name
        },
    )

    # Define task dependencies
    fetch_data_task >> insert_data_task
