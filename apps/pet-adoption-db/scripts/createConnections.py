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
    rescue_group_conn = Connection(
        conn_id="rescue_group_api",
        conn_type="http",
        host="https://api.rescuegroups.org",
    )
    long_beach_conn = Connection(
        conn_id="long_beach_api",
        conn_type="http",
        host="https://data.longbeach.gov",
    )

    # Create connections
    create_connection("petfinder_api", pet_finder_conn)
    create_connection("rescue_group_api", rescue_group_conn)
    create_connection("long_beach_api", long_beach_conn)

if __name__ == "__main__":
    main()
