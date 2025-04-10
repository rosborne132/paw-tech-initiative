import psycopg2
import os
import json

def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def insert_data_to_raw_data_table(conn, data, source):
    """
    Insert data into the raw_data table.
    :param conn: Database connection object
    :param data: List of dictionaries (rows of json data)
    :param source: Source name (e.g., CSV file name or API name)
    """
    try:
        cursor = conn.cursor()
        for row in data:
            json_data = json.dumps(row)

            # Insert into the raw_data table
            cursor.execute(
                """
                INSERT INTO raw_data (source, raw_data)
                VALUES (%s, %s)
                """,
                (source, json_data)
            )
        conn.commit()
        cursor.close()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")
