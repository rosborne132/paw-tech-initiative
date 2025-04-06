from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import json


# TODO: This might not be needed if the airflow operator is good
from utils.db_client import connect_to_db, insert_data_to_raw_data_table

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

with DAG(
    dag_id="fetch_petfinder_data",
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

    # Task 4: Make the API call using the token
    api_call_task = SimpleHttpOperator(
        task_id="api_call_task",
        http_conn_id="petfinder_api",
        endpoint="/v2/animals?after=2025-04-04T10:30:00Z",
        method="GET",
        headers="{{ task_instance.xcom_pull(task_ids='prepare_headers_task') }}",  # Use headers from XCom
        log_response=True,
        response_check=lambda response: response.status_code == 200,
    )

    # Define task dependencies
    auth_task >> extract_token_task >> prepare_headers_task >> api_call_task
