from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import csv
import sys
import json

from utils.client_utils import insert_data_to_raw_data_table_task

include_folder = os.path.join(os.path.dirname(__file__), '..', 'include')

def read_csv_file(file_path):
    """Read data from a CSV file and return a list of dictionaries."""
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)  # Automatically uses the first row as headers
            data = [row for row in csv_reader]  # Each row is a dictionary
        return data
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def load_csv_file(ti):
    """Load CSV data from files and push to XCom."""
    # Define the paths to the CSV files
    montgomery_county_path = os.path.join(include_folder, 'adoptable_pets_catalog.csv')
    sonoma_county_path = os.path.join(include_folder, 'animal_shelter_intake_outcome_mar_2025.csv')

    # Read the CSV files
    montgomery_county_data = read_csv_file(montgomery_county_path)
    sonoma_county_data = read_csv_file(sonoma_county_path)

    # Push the data to XCom
    ti.xcom_push(key="montgomery_county_data", value=montgomery_county_data)
    ti.xcom_push(key="sonoma_county_data", value=sonoma_county_data)

# Define the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='load_csv_data',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    # Task 1: Load CSV data
    load_csv_task = PythonOperator(
        task_id='load_csv_file',
        python_callable=load_csv_file,
    )

    # Task 2: Insert data Montgomery County data into PostgreSQL
    insert_montgomery_data_task = PythonOperator(
        task_id='insert_montgomery_data_task',
        python_callable=insert_data_to_raw_data_table_task,
        op_kwargs={
            "task_id": "load_csv_file",
            "task_key": "montgomery_county_data",
            "source_name": "Montgomery County Animal Services",
        },
    )

    # Task 3: Insert data Sonoma County data into PostgreSQL
    insert_sonoma_data_task = PythonOperator(
        task_id='insert_sonoma_data_task',
        python_callable=insert_data_to_raw_data_table_task,
        op_kwargs={
            "task_id": "load_csv_file",
            "task_key": "sonoma_county_data",
            "source_name": "Sonoma County Department of Health Services",
        },
    )

    load_csv_task >> insert_montgomery_data_task >> insert_sonoma_data_task
