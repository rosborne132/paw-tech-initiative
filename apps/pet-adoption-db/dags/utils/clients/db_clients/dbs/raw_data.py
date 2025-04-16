def insert_data_to_raw_data_table(conn, data, source):
    """
    Insert data into the raw_data table.
    :param conn: Database connection object
    :param data: List of dictionaries (rows of json data)
    :param source: Source name (e.g., CSV file name or API name)
    """
    try:
        with conn.cursor() as cursor:
            for row in data:
                json_data = json.dumps(row)
                cursor.execute(
                    """
                    INSERT INTO raw_data (source, raw_data)
                    VALUES (%s, %s)
                    """,
                    (source, json_data)
                )
        conn.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")
