from datetime import datetime
import json
import re

from utils.client_utils import determine_gender, determine_size, create_organization_data_with_payload, create_animal_data, determine_age_label_by_month_count

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

    return determine_age_label_by_month_count(total_months)

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

def convert_date_string(date):
    """
    Convert a date string in the format 'MM/DD/YYYY' to a datetime object.
    :param date: Date string
    :return: Datetime object
    """
    date_format = "%m/%d/%Y"
    date_object = datetime.strptime(date, date_format)

def calculate_months_from_date(date_string):
    """
    Calculate the number of months from the given date to the current date.
    :param date_string: Date string in the format 'MM/DD/YYYY'
    :return: Number of months as an integer
    """
    try:
        date_format = "%m/%d/%Y"
        given_date = datetime.strptime(date_string, date_format)
        current_date = datetime.now()

        # Calculate the difference in months
        months_difference = (current_date.year - given_date.year) * 12 + (current_date.month - given_date.month)
        return months_difference
    except Exception as e:
        print(f"Error calculating months from date: {e}")
        return None

# ------------------------------------------------------------
sonoma_county_source_label = "Sonoma County Department of Health Services"
montgomery_county_source_label = "Montgomery County Animal Services"
long_beach_source_label = "City of Long Beach Animal Shelter"
pet_finder_source_label = "Pet Finder"
rescue_groups_source_label = "Rescue Groups"

def sonoma_county(conn, data):
    """
    Sonoma County Department of Health Services case executed
    :param conn: Database connection
    :param data: Data to transform
    :return: void
    """
    print("Sonoma County Department of Health Services case executed")
    print(f"Data: {data}")

    outcome_type = data.get("Outcome Type")
    species = data.get("Type").lower()

    # Checking the data -------------
    if outcome_type != "ADOPTION":
        print(f"Outcome type not supported: {outcome_type}")
        return

    if species != "dog" and species != "cat":
        print(f"Species not supported: {species}")
        return

    # Convert and clean the data ---
    gender = determine_gender(data.get("Sex"))
    size = determine_size(data.get("Size"))
    age = calculate_months_from_date(data.get("Date Of Birth"))

    if not gender:
        print("Gender couldn't be determined")
        return

    # Creating the organization item ---
    organization_id = create_organization_data_with_payload(conn, {
        "platform_organization_id": None,
        "name": sonoma_county_source_label,
        "city": "Sonoma",
        "state": "CA",
        "posting_source": sonoma_county_source_label
    })

    # Creating the animal item ---------
    create_animal_data(conn, {
        "platform_animal_id": data.get("Animal ID"),
        "name": format_string(data.get("Name")),
        "age": determine_age_label_by_month_count(age),
        "species": species,
        "breed": data.get("Breed"),
        "sex": gender,
        "size": size,
        "description": data.get("Color"),
        "adopted": True,
        "organization_id": organization_id,
        "posting_img_count": None,
        "posting_source": sonoma_county_source_label,
        "intake_date": data.get("Intake Date"),
        "outcome_date": data.get("Outcome Date")
    })

def montgomery_county(conn, data):
    """
    Montgomery County Animal Services case executed
    :param conn: Database connection
    :param data: Data to transform
    :return: void
    """
    print("Montgomery County Animal Services case executed")
    print(f"Data: {data}")

    species = data.get("Animal Type").lower()

    # Checking the data -------------
    if species != "dog" and species != "cat":
        print(f"Species not supported: {species}")
        return

    # Convert and clean the data ---
    age = get_montgomery_county_age_label(data.get("Pet Age"))
    gender = determine_gender(data.get("Sex"))
    size = determine_size(data.get("Pet Size"))

    if not gender:
        print("Gender couldn't be determined")
        return

    if not size:
        print("Size counldn't be determined")
        return

    # Creating the organization item ---
    organization_id = create_organization_data_with_payload(conn, {
        "platform_organization_id": None,
        "name": montgomery_county_source_label,
        "city": "Montgomery",
        "state": "MD",
        "posting_source": montgomery_county_source_label
    })

    # Creating the animal item ---------
    create_animal_data(conn, {
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
        "posting_source": montgomery_county_source_label,
        "intake_date": data.get("In Date"),
        "outcome_date": None
    })

def long_beach(conn, data):
    """
    City of Long Beach Animal Shelter case executed
    :param conn: Database connection
    :param data: Data to transform
    :return: void
    """
    print("City of Long Beach Animal Shelter case executed")
    print(f"Data: {data}")

    outcome_type = data.get("outcome_type")
    species = data.get("animal_type").lower()

    # Checking the data -------------
    if outcome_type != "ADOPTION":
        print(f"Outcome type not supported: {outcome_type}")
        return

    if species != "dog" and species != "cat":
        print(f"Species not supported: {species}")
        return

    # Convert and clean the data ---
    gender = determine_gender(data.get("sex"))

    # Creating the organization item ---
    organization_id = create_organization_data_with_payload(conn, {
        "platform_organization_id": None,
        "name": long_beach_source_label,
        "city": "Long Beach",
        "state": "CA",
        "posting_source": long_beach_source_label
    })

    # Creating the animal item ---------
    create_animal_data(conn, {
        "platform_animal_id": data.get("animal_id"),
        "name": format_string(data.get("animal_name")),
        "age": None,
        "species": species,
        "breed": None,
        "sex": gender,
        "size": None,
        "description": data.get("primary_color"),
        "adopted": True,
        "organization_id": organization_id,
        "posting_img_count": None,
        "posting_source": long_beach_source_label,
        "intake_date": data.get("intake_date"),
        "outcome_date": data.get("outcome_date")
    })

def pet_finder(conn, data):
    print("Pet Finder case executed")
    print(f"Data: {data}")

    # Checking the data -------------

    # Convert and clean the data ---

    # Creating the organization item ---

    # Creating the animal item ---------

    # Creating the environment item ----

    # Creating the attribute item ------

    raise ValueError("Don't continue")
    # TODO

def rescue_group(conn, data):
    print("Rescue Groups case executed")
    print(f"Data: {data}")

    # Checking the data -------------

    # Convert and clean the data ---

    # Creating the organization item ---

    # Creating the animal item ---------

    # Creating the environment item ----

    # Creating the attribute item ------

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
