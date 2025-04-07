import os
import csv
import sys
import json

# Add the dags folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "../dags"))
from utils.db_client import connect_to_db, insert_data_to_raw_data_table

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

def main():
    conn = connect_to_db()
    if not conn:
        return

    montgomery_county_data = read_csv_file("./data/adoptable_pets_catalog.csv")
    sonoma_county_data = read_csv_file("./data/animal_shelter_intake_outcome_mar_2025.csv")

    if montgomery_county_data:
        insert_data_to_raw_data_table(conn, montgomery_county_data, "Montgomery County Animal Services")

    if sonoma_county_data:
        insert_data_to_raw_data_table(conn, sonoma_county_data, "Sonoma County Department of Health Services")

    conn.close()

if __name__ == "__main__":
    main()
