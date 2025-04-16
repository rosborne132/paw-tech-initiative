import json

from utils.db_client import connect_to_db, get_organizations_id_by_name, insert_organization_data, insert_data_to_raw_data_table, insert_animal_data, insert_environment_data, insert_attribute_data

from utils.pet_finder_client import PetFinderClient
from utils.recuse_groups_client import RescueGroupsClient

PetFinderClient = PetFinderClient()
RescueGroupsClient = RescueGroupsClient()

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

def create_animal_data_with_payload(conn, animal_payload):
    """
    Create or update animal data in the database.
    :param conn: Database connection object
    :param animal_payload: JSON string containing animal data
    :return: Animal id
    """
    try:
        animal_id = insert_animal_data(conn, animal_payload)
        print(f"Animal id: {animal_id}")
        return animal_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting or updating animal data: {e}")
        raise ValueError(e)

def create_organization_data_for_pet_finder(conn, organization_payload):
    """
    Create organization data for Pet Finder in the database.
    :param conn: Database connection object
    :param organization_payload: JSON string containing organization data
    :return: Organization id
    """
    try:
        # Check if the organization already exists
        organization_id = get_organizations_id_by_name(conn, organization_payload.get("name"))

        if not organization_id:
            print("Organization not found")
            # Use PetFinderClient to get the organization data
            try:
                organization_response = PetFinderClient.fetch_organization_by_id(organization_payload.get("platform_organization_id"))
                print(f"Organization response: {organization_response}")
            except Exception as e:
                print(f"Error fetching organizations data: {e}")
                raise ValueError("Failed to fetch organization data from PetFinder")

            # Create the organization data
            organization_id = create_organization_data_with_payload(conn, {
                "platform_organization_id": organization_payload.get("platform_organization_id"),
                "name": organization_response.get("name"),
                "city": organization_response.get("address", {}).get("city"),
                "state": organization_response.get("address", {}).get("state"),
                "posting_source": organization_payload.get("posting_source")
            })

        print(f"Organization id: {organization_id}")
        return organization_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error creating organization data: {e}")
        raise ValueError(e)

def create_attribute_data_with_payload(conn, attribute_payload):
    """
    Create attribute data in the database.
    :param conn: Database connection object
    :param attribute_payload: JSON string containing attribute data
    :return: Attribute id
    """
    try:
        attribute_id = insert_attribute_data(conn, attribute_payload)
        print(f"Attribute id: {attribute_id}")
        return attribute_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting or updating attribute data: {e}")
        raise ValueError(e)

def create_environment_data_with_payload(conn, environment_payload):
    """
    Create environment data in the database.
    :param conn: Database connection object
    :param environment_payload: JSON string containing environment data
    :return: Environment id
    """
    try:
        environment_id = insert_environment_data(conn, environment_payload)
        print(f"Environment id: {environment_id}")
        return environment_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting or updating environment data: {e}")
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
        "Large": "large",
        "MED": "medium",
        "Medium": "medium",
        "SMALL": "small",
        "Small": "small",
    }

    return size_map.get(size)

def determine_age_by_mapping(age):
    """
    Determine the age of the animal based on a mapping.
    :param age: Age string from the data source
    :return: Age string for the database
    """
    age_map = {
        "Young": "young",
        "Adult": "adult",
        "Senior": "senior",
    }

    return age_map.get(age)

def determine_age_label_by_month_count(month_count):
    """
    Convert month count into age labels: 'kitten', 'adult', 'senior'.
    :param month_count: Total months of age
    :return: Age label ('kitten', 'adult', 'senior')
    """
    if month_count < 12:
        return "young"
    elif month_count < 96:  # Less than 8 years
        return "adult"
    else:
        return "senior"
