import psycopg2
import os

DB_HOST = os.getenv("DB_HOST", "localhost")  # Default to "localhost" if DB_HOST is not set
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = "pet_adoption_db"
TABLE_NAME = "raw_data"

def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
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
            # Insert into the raw_data table
            cursor.execute(
                """
                INSERT INTO raw_data (source, raw_data)
                VALUES (%s, %s)
                """,
                (source, row)
            )
        conn.commit()
        cursor.close()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")