from airflow.models import Connection
from airflow.settings import Session

def create_connection(conn_id, conn):
    """Create a connection in Airflow."""

    session = Session()

    if not session.query(Connection).filter(Connection.conn_id == conn_id).first():
        session.add(conn)
        session.commit()
        print(f"Connection '{conn_id}' created successfully.")
    else:
        print(f"Connection '{conn_id}' already exists.")

def main():
    # HTTP Connections
    pet_finder_conn = Connection(
        conn_id="petfinder_api",
        conn_type="http",
        host="https://api.petfinder.com",
    )

    # Create connections
    create_connection("petfinder_api", pet_finder_conn)

if __name__ == "__main__":
    main()
