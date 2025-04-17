import psycopg2
import os

class DBClient:
    """Singleton class for managing a PostgreSQL database connection."""
    _instance = None
    _connection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DBClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def connect(self):
        """Establish a connection to the PostgreSQL database if not already connected."""
        if not self._connection:
            try:
                self._connection = psycopg2.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    database=os.getenv("DB_NAME", "postgres"),
                    user=os.getenv("DB_USER", "postgres"),
                    password=os.getenv("DB_PASSWORD", "postgres")
                )
            except Exception as e:
                print(f"Error connecting to the database: {e}")
                self._connection = None
        return self._connection

    def get_connection(self):
        """Get the existing database connection."""
        return self._connection
