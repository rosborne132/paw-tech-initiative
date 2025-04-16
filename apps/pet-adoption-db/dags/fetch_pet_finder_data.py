from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import json
import requests

from utils.client_utils import insert_data_to_raw_data_table_task

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

PF_CLIENT_ID = os.getenv("PF_CLIENT_ID")
PF_CLIENT_SECRET = os.getenv("PF_CLIENT_SECRET")

def extract_token(ti):
    """Extract the token from the authentication response."""
    response = ti.xcom_pull(task_ids="auth_task")  # Pull the response from the auth_task
    response_json = json.loads(response)  # Parse the JSON response
    return response_json["access_token"]  # Return the token (adjust the key based on your API response)

def prepare_headers(ti):
    """Prepare headers for the API call using the token."""
    token = ti.xcom_pull(task_ids="extract_token_task")  # Pull the token from the previous task
    return {"Authorization": f"Bearer {token}"}  # Return the headers

def fetch_paginated_data(ti):
    """Fetch paginated data from the API."""
    base_url = "https://api.petfinder.com/v2/animals"
    headers = ti.xcom_pull(task_ids="prepare_headers_task")  # Fetch headers from XCom
    params = {
        "after": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
        "limit": 100,
        "page": 1,
    }
    all_data = []

    while True:
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break

        data = response.json()
        all_data.extend(data.get("animals", []))  # Append the animals data

        # Check if there is a next page
        pagination = data.get("pagination", {})
        if not pagination.get("_links", {}).get("next"):
            break

        # Move to the next page
        params["page"] += 1

    # Push the collected data to XCom
    ti.xcom_push(key="paginated_data", value=all_data)

with DAG(
    dag_id="fetch_petfinder_data",
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=timedelta(hours=24),
    catchup=False,
) as dag:
    # Task 1: Authenticate and get the token
    auth_task = SimpleHttpOperator(
        task_id="auth_task",
        http_conn_id="petfinder_api",
        endpoint="/v2/oauth2/token",
        method="POST",
        data={
            "grant_type": "client_credentials",
            "client_id": PF_CLIENT_ID,
            "client_secret": PF_CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        response_check=lambda response: response.status_code == 200,
    )

    # Task 2: Extract the token from the auth response
    extract_token_task = PythonOperator(
        task_id="extract_token_task",
        python_callable=extract_token,
    )

    # Task 3: Prepare headers for the API call
    prepare_headers_task = PythonOperator(
        task_id="prepare_headers_task",
        python_callable=prepare_headers,
    )

    # Task 4: Fetch paginated data
    fetch_paginated_data_task = PythonOperator(
        task_id="fetch_paginated_data_task",
        python_callable=fetch_paginated_data,
    )

    # Task 5: Insert data into PostgreSQL
    insert_data_task = PythonOperator(
        task_id="insert_data_task",
        python_callable=insert_data_to_raw_data_table_task,
        op_kwargs={
            "task_id": "fetch_paginated_data_task",  # Task ID to pull data from
            "task_key": "paginated_data",  # Key to pull data from XCom
            "source_name": "Pet Finder",  # Source name
        },
    )

    # Define task dependencies
    auth_task >> extract_token_task >> prepare_headers_task >> fetch_paginated_data_task >> insert_data_task
