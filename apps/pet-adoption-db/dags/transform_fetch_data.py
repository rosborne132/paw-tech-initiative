from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json

from utils.db_client import connect_to_db, delete_row_by_id
from utils.transform_data_utils import label_query_results, transform_and_insert_data_by_source

# Connect to the database
db_connection = connect_to_db()

# Define the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

def fetch_data_from_in_flight_table(ti):
    """Fetch data from the in_flight table."""
    # Check if the database connection is established
    if not db_connection:
        print("Failed to connect to the database.")
        return

    # Define the SQL query to fetch data from the in_flight table
    sql_query = "SELECT * FROM in_flight_data LIMIT 1000;"

    # Execute the SQL query
    cursor = db_connection.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchall()

    labeled_result = label_query_results(result)

    # Push the fetched data to XCom
    ti.xcom_push(key="in_flight_data", value=labeled_result)

def transform_data(ti):
    """Transform the data fetched from the in_flight table."""
    # Pull data from XCom
    data = ti.xcom_pull(key="in_flight_data", task_ids="fetch_data_task")

    if not data or len(data) == 0:
        print("No data to transform.")
        return

    print(f"Fetched {len(data)} records from in_flight table.")

    for row in data:
        row_id = json.loads(row).get("id")
        raw_data = json.loads(row).get("raw_data")
        source = json.loads(row).get("source")

        try:
            transform_and_insert_data_by_source(db_connection, raw_data, source)
        except Exception as e:
            print(f"Error creating JSON object: {e}")
            continue

        # delete_row_by_id(db_connection, row_id)


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
    transform_data_task = PythonOperator(
        task_id="transform_data_task",
        python_callable=transform_data,
    )

    # Define task dependencies
    fetch_data_task >> transform_data_task
