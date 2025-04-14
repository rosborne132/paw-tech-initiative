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

def delete_row_by_id(conn, row_id):
    """
    Delete a row from the raw_data table by ID.
    :param conn: Database connection object
    :param row_id: ID of the row to delete
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM in_flight_data WHERE id = %s
            """,
            (row_id,)
        )
        conn.commit()
        cursor.close()
        print(f"Row with ID {row_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting row: {e}")

def insert_organization_data(conn, data):
    """
    Insert organization data into the organization table.
    :param conn: Database connection object
    :param data: JSON string containing organization data
    :return: Data id of the inserted organization
    """
    try:
        cursor = conn.cursor()
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
        cursor.close()

        return org_id
    except Exception as e:
        print(f"Error inserting organization data: {e}")
        return None

def insert_animal_data(conn, data):
    """
    Insert animal data into the animal table.
    :param conn: Database connection object
    :param data: JSON string containing animal data
    :return: Data id of the inserted animal
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO animals (platform_animal_id, name, age, species, breed, sex, size, description, adopted, organization_id, posting_img_count, posting_source, intake_date, outcome_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                data.get("platform_organization_id"),
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
        cursor.close()

        return animal_id
    except Exception as e:
        print(f"Error inserting animal data: {e}")
        return None

def insert_attribute_data(conn, data):
    """
    Insert attribute data into the animal_attribute table.
    :param conn: Database connection object
    :param data: JSON string containing attribute data
    :return: Data id of the inserted attribute
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attributes (animal_id, spayed_neutered, house_trained, declawed, special_needs, shots_current)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                data.get("animal_id"),
                data.get("spayed_neutered"),
                data.get("house_trained"),
                data.get("declawed"),
                data.get("special_needs"),
                data.get("shots_current"),
            )
        )
        attribute_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()

        return attribute_id
    except Exception as e:
        print(f"Error inserting attribute data: {e}")
        return None

def insert_environment_data(conn, data):
    """
    Insert environment data into the animal_environment table.
    :param conn: Database connection object
    :param data: JSON string containing environment data
    :return: Data id of the inserted environment
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO environment (animal_id, dogs_ok, cats_ok, kids_ok)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                data.get("animal_id"),
                data.get("dogs_ok"),
                data.get("cats_ok"),
                data.get("kids_ok")
            )
        )
        environment_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()

        return environment_id
    except Exception as e:
        print(f"Error inserting environment data: {e}")
        return None

def get_organizations_id_by_name(conn, name):
    """
    Get organization data by name.
    :param conn: Database connection object
    :param name: Name of the organization
    :return: Organization data id
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM organizations WHERE name = %s
            """,
            (name,)
        )
        org_id = cursor.fetchone()[0]
        cursor.close()

        return org_id
    except Exception as e:
        print(f"Error fetching organizations data: {e}")
        return None
