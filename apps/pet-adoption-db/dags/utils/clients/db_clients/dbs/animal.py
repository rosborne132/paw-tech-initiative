# Clients
from utils.clients.db_clients.db import DBClient

db_client = DBClient()
conn = db_client.connect()

def insert_animal_data(data):
    """
    Insert animal data into the animal table.
    :param data: JSON string containing animal data
    :return: Data id of the inserted animal
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO animals (platform_animal_id, name, age, species, breed, sex, size, description, adopted, organization_id, posting_img_count, posting_source, intake_date, outcome_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    data.get("platform_animal_id"),
                    data.get("name"),
                    data.get("age"),
                    data.get("species"),
                    data.get("breed"),
                    data.get("sex"),
                    data.get("size"),
                    data.get("description"),
                    data.get("adopted"),
                    data.get("organization_id"),
                    data.get("posting_img_count"),
                    data.get("posting_source"),
                    data.get("intake_date"),
                    data.get("outcome_date")
                )
            )
            animal_id = cursor.fetchone()[0]
        conn.commit()
        return animal_id
    except Exception as e:
        print(f"Error inserting animal data: {e}")
        return None
