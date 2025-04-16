import psycopg2
import os

def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
