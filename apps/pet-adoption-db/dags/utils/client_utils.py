import json

# DB Helpers
from utils.clients.db_clients.dbs.animal import insert_animal_data
from utils.clients.db_clients.dbs.organization import insert_organization_data, get_organizations_id_by_name
from utils.clients.db_clients.dbs.raw_data import insert_data_to_raw_data_table
from utils.clients.db_clients.dbs.environment import insert_environment_data
from utils.clients.db_clients.dbs.attribute import insert_attribute_data

# Clients
from utils.clients.db_clients.db import DBClient
from utils.clients.api_clients.pet_finder import PetFinderClient
from utils.clients.api_clients.recuse_groups import RescueGroupsClient

db_client = DBClient()
conn = db_client.connect()
PetFinderClient = PetFinderClient()
RescueGroupsClient = RescueGroupsClient()

def insert_data_to_raw_data_table_task(ti, task_id, task_key, source_name):
    """Insert data into the raw_data table."""
    # Fetch the collected data from XCom
    all_data = ti.xcom_pull(task_ids=task_id, key=task_key)

    if not all_data or len(all_data) == 0:
        print("No data to insert.")
        return

    print(f"Fetched {len(all_data)} records.")
    print(f"Sample data: {all_data[:1]}")  # Print the first record for debugging

    # Insert data into the raw_data table
    insert_data_to_raw_data_table(all_data, source_name)

    conn.close()

def create_organization_data_with_payload(organization_payload):
    """
    Create organization data in the database.
    :param organization_payload: JSON string containing organization data
    :return: Organization id
    """
    try:
        organization_id = get_organizations_id_by_name(organization_payload.get("name"))

        if not organization_id:
            print("Organization not found")
            print("Inserting organization data")
            organization_id = insert_organization_data(organization_payload)

        return organization_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting organization data: {e}")
        raise ValueError(e)

def create_animal_data_with_payload(animal_payload):
    """
    Create or update animal data in the database.
    :param animal_payload: JSON string containing animal data
    :return: Animal id
    """
    try:
        animal_id = insert_animal_data(animal_payload)
        print(f"Animal id: {animal_id}")
        return animal_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting or updating animal data: {e}")
        raise ValueError(e)

def create_organization_data_for_pet_finder(organization_payload):
    """
    Create organization data for Pet Finder in the database.
    :param organization_payload: JSON string containing organization data
    :return: Organization id
    """
    try:
        # Check if the organization already exists
        organization_id = get_organizations_id_by_name(organization_payload.get("name"))

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
            organization_id = create_organization_data_with_payload({
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

def create_organization_data_for_rescue_groups(organization_payload):
    """
    Create organization data for Rescue Groups in the database.
    :param organization_payload: JSON string containing organization data
    :return: Organization id
    """
    try:
        # Check if the organization already exists
        organization_id = get_organizations_id_by_name(organization_payload.get("name"))

        if not organization_id:
            print("Organization not found by name - first check")
            # Use RescueGroupsClient to get the organization data
            try:
                organization_response = RescueGroupsClient.fetch_organization_by_id(organization_payload.get("platform_organization_id"))
                print(f"Organization response: {organization_response}")
            except Exception as e:
                print(f"Error fetching organizations data: {e}")
                raise ValueError("Failed to fetch organization data from RescueGroups")

            # Create the organization data
            organization_id = create_organization_data_with_payload({
                "platform_organization_id": organization_payload.get("platform_organization_id"),
                "name": organization_response.get("attributes").get("name"),
                "city": organization_response.get("attributes").get("city"),
                "state": organization_response.get("attributes").get("state"),
                "posting_source": organization_payload.get("posting_source")
            })

        print(f"Organization id: {organization_id}")
        return organization_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error creating organization data: {e}")
        raise ValueError(e)

def create_attribute_data_with_payload(attribute_payload):
    """
    Create attribute data in the database.
    :param attribute_payload: JSON string containing attribute data
    :return: Attribute id
    """
    try:
        attribute_id = insert_attribute_data(attribute_payload)
        print(f"Attribute id: {attribute_id}")
        return attribute_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting or updating attribute data: {e}")
        raise ValueError(e)

def create_environment_data_with_payload(environment_payload):
    """
    Create environment data in the database.
    :param environment_payload: JSON string containing environment data
    :return: Environment id
    """
    try:
        environment_id = insert_environment_data(environment_payload)
        print(f"Environment id: {environment_id}")
        return environment_id
    except Exception as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting or updating environment data: {e}")
        raise ValueError(e)

def determine_species(species):
    """
    Determine the species of the animal.
    :param species: Species string from the data source
    :return: Species string for the database
    """
    species_map = {
        "3": "cat",
        "8": "dog"
    }

    return species_map.get(species)

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
        "Baby": "young",
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

def determine_rescue_groups_breed_by_id(breed_id):
    """
    Determine the breed of the animal using Rescue Groups API.
    :param breed_id: Breed ID from the data source
    :return: Breed string for the database
    """
    try:
        breed_response = RescueGroupsClient.fetch_breed_by_id(breed_id)
        return breed_response.get("attributes").get("name")
    except Exception as e:
        print(f"Error fetching breed data: {e}")
        raise ValueError("Failed to fetch breed data from RescueGroups")
