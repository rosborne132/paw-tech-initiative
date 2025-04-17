# Clients
from utils.clients.db_clients.db import DBClient

db_client = DBClient()
conn = db_client.connect()

def delete_row_by_id(row_id):
    """
    Delete a row from the in_flight_data table by ID.
    :param row_id: ID of the row to delete
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM in_flight_data WHERE id = %s
                """,
                (row_id,)
            )
        conn.commit()
        print(f"Row with ID {row_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting row: {e}")
