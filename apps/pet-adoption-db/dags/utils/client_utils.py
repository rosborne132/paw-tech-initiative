from utils.db_client import insert_data_to_raw_data_table

def insert_data_to_raw_data_table_task(ti, conn, task_id, task_key, source_name):
    """Insert data into the raw_data table."""
    if not conn:
        print("Failed to connect to the database.")
        return

    # Fetch the collected data from XCom
    all_data = ti.xcom_pull(task_ids=task_id, key=task_key)

    if not all_data or len(all_data) == 0:
        print("No data to insert.")
        return

    print(f"Fetched {len(all_data)} records.")
    print(f"Sample data: {all_data[:1]}")  # Print the first record for debugging

    # Insert data into the raw_data table
    insert_data_to_raw_data_table(conn, all_data, source_name)

    conn.close()
