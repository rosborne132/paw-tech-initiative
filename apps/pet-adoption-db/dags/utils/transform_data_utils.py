import json
import re

from utils import db_client

def create_json_object(data):
    """
    Create a JSON object from an array.
    :param data: Array item
    :return: JSON object
    """
    try:
        return json.dumps({
            "id": data[0],
            "source": data[1],
            "raw_data": data[2]
        }, indent=2)
    except Exception as e:
        print(f"Error creating JSON object: {e}")
        return None

def label_query_results(data):
    """Transform data into JSON objects."""
    return [create_json_object(row) for row in data]

def get_montgomery_county_age_label(age_string):
    """
    Convert age strings like '3 YEARS' or '1 YEAR 3 MONTHS' into labels: 'kitten', 'adult', 'senior'.
    :param age_string: Age string (e.g., '3 YEARS', '1 YEAR 3 MONTHS')
    :return: Age label ('kitten', 'adult', 'senior')
    """
    # Extract years and months from the string
    years = 0
    months = 0

    if "YEAR" in age_string:
        years = int(age_string.split("YEAR")[0].strip())
    if "MONTH" in age_string:
        months_part = age_string.split("MONTH")[0]
        months = int(months_part.split()[-1]) if "YEAR" in months_part else int(months_part.strip())

    # Convert total age to months
    total_months = years * 12 + months

    # Determine the label
    if total_months < 12:
        return "kitten"
    elif total_months < 96:  # Less than 8 years
        return "adult"
    else:
        return "senior"

def format_string(input_string):
    """
    Capitalize the first letter of each word and remove special characters.
    :param input_string: The string to format
    :return: Formatted string
    """
    # Remove special characters using regex
    cleaned_string = re.sub(r'[^a-zA-Z0-9\s]', '', input_string)
    # Capitalize the first letter of each word
    formatted_string = cleaned_string.title()
    return formatted_string


# ------------------------------------------------------------
sonoma_county_source_label = "Sonoma County Department of Health Services"
montgomery_county_source_label = "Montgomery County Animal Services"
long_beach_source_label = "City of Long Beach Animal Shelter"
pet_finder_source_label = "Pet Finder"
rescue_groups_source_label = "Rescue Groups"

def sonoma_county(conn, data):
    print("Sonoma County Department of Health Services case executed")
    print(f"Data: {data}")

    raise ValueError("Don't continue")
    # TODO

def montgomery_county(conn, data):
    print("Montgomery County Animal Services case executed")
    print(f"Data: {data}")

    species = data.get("Animal Type").lower()
    gender = data.get("Sex")
    size = data.get("Pet Size")
    age = get_montgomery_county_age_label(data.get("Pet Age"))

    # Checking the data -------------
    if species != "dog" and species != "cat":
        print(f"Species not supported: {species}")
        return

    print("Species supported")

    if gender == "N":
        gender = "male"
    elif gender == "S":
        gender = "female"
    else:
        print("Gender counldn't be determined")
        return

    if size == "SMALL":
        size = "small"
    elif size == "MED":
        size = "medium"
    elif size == "LARGE":
        size = "large"
    else:
        print("Size counldn't be determined")
        return


    # Creating the organization item ---
    organization_id = db_client.get_organizations_id_by_name(conn, montgomery_county_source_label)

    if not organization_id:
        print("Organization not found")
        print("Inserting organization data")
        organization_data = {
            "platform_organization_id": None,
            "name": montgomery_county_source_label,
            "city": "Montgomery",
            "state": "MD",
            "posting_source": montgomery_county_source_label
        }
        organization_id = db_client.insert_organization_data(conn, organization_data)

    print(f"Organization id: {organization_id}")

    # Creating the animal item ---------
    animal_payload =  {
        "platform_animal_id": data.get("Animal ID"),
        "name": format_string(data.get("Pet name")),
        "age": age,
        "species": species,
        "breed": data.get("Breed"),
        "sex": gender,
        "size": size,
        "description": data.get("Color"),
        "adopted": False,
        "organization_id": organization_id,
        "posting_img_count": 1,
        "posting_source": montgomery_county_source_label
    }

    try:
        print(f"New animal payload: {animal_payload}")

        animal_id = db_client.insert_animal_data(conn, animal_payload)

        print(f"New animal id: {animal_id}")
        return
    except Exception as e:
        raise ValueError(e);

def long_beach(conn, data):
    print("City of Long Beach Animal Shelter case executed")
    print(f"Data: {data}")

    raise ValueError("Don't continue")
    # TODO

def pet_finder(conn, data):
    print("Pet Finder case executed")
    print(f"Data: {data}")

    raise ValueError("Don't continue")
    # TODO

def rescue_group(conn, data):
    print("Rescue Groups case executed")
    print(f"Data: {data}")

    raise ValueError("Don't continue")
    # TODO

def default_case():
    print("Source not found, default case executed")
    print(f"Data: {data}")
    return None

def switch_example(conn, source, data):
    """Switch case example using dictionary mapping."""
    switch = {
        sonoma_county_source_label: lambda: sonoma_county(conn, data),
        montgomery_county_source_label: lambda: montgomery_county(conn, data),
        long_beach_source_label: lambda: long_beach(conn, data),
        pet_finder_source_label: lambda: pet_finder(conn, data),
        rescue_groups_source_label: lambda: rescue_group(conn, data)
    }

    return switch.get(source, lambda: default_case())()  # Call the function with the argument

def transform_and_insert_data_by_source(conn, data, source):
    """
    Transform and insert data by source.
    :param conn: Database connection
    :param data: Data to transform
    :param source: Source of the data
    :return: void
    """
    switch_example(conn, source, data)
