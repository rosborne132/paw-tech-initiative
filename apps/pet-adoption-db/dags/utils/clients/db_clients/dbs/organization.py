# Clients
from utils.clients.db_clients.db import DBClient

db_client = DBClient()
conn = db_client.connect()

def insert_organization_data(data):
    """
    Insert organization data into the organization table.
    :param data: JSON string containing organization data
    :return: Data id of the inserted organization
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO organizations (platform_organization_id, name, city, state, posting_source)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    data.get("platform_organization_id"),
                    data.get("name"),
                    data.get("city"),
                    data.get("state"),
                    data.get("posting_source")
                )
            )
            org_id = cursor.fetchone()[0]
        conn.commit()
        return org_id
    except Exception as e:
        print(f"Error inserting organization data: {e}")
        return None

def get_organizations_id_by_name(name):
    """
    Get organization data by name.
    :param name: Name of the organization
    :return: Organization data id
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM organizations WHERE name = %s
                """,
                (name,)
            )
            org_id = cursor.fetchone()[0]
        return org_id
    except Exception as e:
        print(f"Error fetching organizations data: {e}")
        return None
