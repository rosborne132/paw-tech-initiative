from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from utils.db_client import connect_to_db

db_connection = connect_to_db()


# Define the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

def fetch_data_from_in_flight_table(ti):
    """Fetch data from the in_flight table."""
    # Define the SQL query to fetch data from the in_flight table
    sql_query = "SELECT * FROM in_flight WHERE status = 'in_progress'"

    # Execute the SQL query
    cursor = db_connection.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchall()

    # Push the fetched data to XCom
    ti.xcom_push(key="in_flight_data", value=result)

with DAG(
    dag_id="transform_fetch_data",
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=timedelta(hours=4),
    catchup=False,
) as dag:
    # Task 1: Pull data from in_flight table
    fetch_data_task = PythonOperator(
        task_id="fetch_data_task",
        python_callable=fetch_data_from_in_flight_table,
    )

    # Task 2: Transform data
    # Task 3: Load transformed data into the database

    # Define task dependencies
    fetch_data_task
