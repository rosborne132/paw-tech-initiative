import json

from utils.db_client import connect_to_db, get_organizations_id_by_name, insert_organization_data, insert_data_to_raw_data_table, insert_animal_data

def insert_data_to_raw_data_table_task(ti, conn, task_id, task_key, source_name):
    """Insert data into the raw_data table."""
    if not conn:
        print("Failed to connect to the database.")
        return

    # Fetch the collected data from XCom
    all_data = ti.xcom_pull(task_ids=task_id, key=task_key)

    if not all_data or len(all_data) == 0:
        print("No data to insert.")
        return

    print(f"Fetched {len(all_data)} records.")
    print(f"Sample data: {all_data[:1]}")  # Print the first record for debugging

    # Insert data into the raw_data table
    insert_data_to_raw_data_table(conn, all_data, source_name)

    conn.close()

def create_animal_data(conn, animal_payload):
    """
    Create animal data in the database.
    :param conn: Database connection object
    :param animal_payload: JSON string containing animal data
    """
    try:
        print(f"New animal payload: {animal_payload}")

        animal_id = insert_animal_data(conn, animal_payload)

        print(f"New animal id: {animal_id}")
        return
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting animal data: {e}")
        raise ValueError(e)

def create_organization_data_with_payload(conn, organization_payload):
    """
    Create organization data in the database.
    :param conn: Database connection object
    :param organization_payload: JSON string containing organization data
    :return: Organization id
    """
    try:
        organization_id = get_organizations_id_by_name(conn, organization_payload.get("name"))

        if not organization_id:
            print("Organization not found")
            print("Inserting organization data")
            organization_id = insert_organization_data(conn, organization_payload)

        print(f"Organization id: {organization_id}")
        return organization_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting organization data: {e}")
        raise ValueError(e)

def determine_gender(gender):
    """
    Determine the gender of the animal.
    :param gender:  Gender string from the data source
    :return: Gender string for the database
    """
    gender_map = {
        "Female": "female",
        "Male": "male",
        "N": "male",
        "Neutered": "male",
        "S": "female",
        "Spayed": "female",
    }

    return gender_map.get(gender)

def determine_size(size):
    """
    Determine the size of the animal.
    :param size: Size string from the data source
    :return: Size string for the database
    """
    size_map = {
        "KITTN": "small",
        "PUPPY": "small",
        "TOY": "small",
        "LARGE": "large",
        "MED": "medium",
        "SMALL": "small"
    }

    return size_map.get(size)

def determine_age_label_by_month_count(month_count):
    """
    Convert month count into age labels: 'kitten', 'adult', 'senior'.
    :param month_count: Total months of age
    :return: Age label ('kitten', 'adult', 'senior')
    """
    if month_count < 12:
        return "kitten"
    elif month_count < 96:  # Less than 8 years
        return "adult"
    else:
        return "senior"
