from datetime import datetime
import json
import re

from utils.client_utils import create_organization_data_with_payload, create_animal_data_with_payload, create_attribute_data_with_payload, create_environment_data_with_payload, create_organization_data_for_pet_finder, create_organization_data_for_rescue_groups, determine_rescue_groups_breed_by_id

from utils.mapping_utils import determine_age_by_mapping, determine_gender, determine_size, determine_species, determine_age_label_by_month_count

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

def sonoma_county(data):
    """
    Sonoma County Department of Health Services case executed
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

    if species not in ["dog", "cat"]:
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
    organization_id = create_organization_data_with_payload({
        "platform_organization_id": None,
        "name": sonoma_county_source_label,
        "city": "Sonoma",
        "state": "CA",
        "posting_source": sonoma_county_source_label
    })

    # Creating the animal item ---------
    create_animal_data_with_payload({
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

def montgomery_county(data):
    """
    Montgomery County Animal Services case executed
    :param data: Data to transform
    :return: void
    """
    print("Montgomery County Animal Services case executed")
    print(f"Data: {data}")

    species = data.get("Animal Type").lower()

    # Checking the data -------------
    if species not in ["dog", "cat"]:
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
    organization_id = create_organization_data_with_payload({
        "platform_organization_id": None,
        "name": montgomery_county_source_label,
        "city": "Montgomery",
        "state": "MD",
        "posting_source": montgomery_county_source_label
    })

    # Creating the animal item ---------
    create_animal_data_with_payload({
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

def long_beach(data):
    """
    City of Long Beach Animal Shelter case executed
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

    if species not in ["dog", "cat"]:
        print(f"Species not supported: {species}")
        return

    # Convert and clean the data ---
    gender = determine_gender(data.get("sex"))

    # Creating the organization item ---
    organization_id = create_organization_data_with_payload({
        "platform_organization_id": None,
        "name": long_beach_source_label,
        "city": "Long Beach",
        "state": "CA",
        "posting_source": long_beach_source_label
    })

    # Creating the animal item ---------
    create_animal_data_with_payload({
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

def pet_finder(data):
    """
    Pet Finder case executed
    :param data: Data to transform
    :return: void
    """
    print("Pet Finder case executed")
    print(f"Data: {data}")

    # Checking the data -------------
    species = data.get("species").lower()

    if species not in ["dog", "cat"]:
        print(f"Species not supported: {species}")
        return

    # Convert and clean the data ---
    outcome_date = data.get("status_changed_at") if data.get("status") == "adopted" else None

    # Creating the organization item ---
    organization_id = create_organization_data_for_pet_finder({
        "platform_organization_id": data.get("organization_id"),
        "posting_source": pet_finder_source_label
    })

    # Creating the animal item ---------
    animal_id = create_animal_data_with_payload({
        "platform_animal_id": data.get("id"),
        "name": format_string(data.get("name")),
        "age": determine_age_by_mapping(data.get("age")),
        "species": species,
        "breed": data.get("breeds").get("primary"),
        "sex": determine_gender(data.get("gender")),
        "size": determine_size(data.get("size")),
        "description": data.get("description"),
        "adopted": data.get("status") == "adopted",
        "organization_id": organization_id,
        "posting_img_count": len(data.get("photos")),
        "posting_source": pet_finder_source_label,
        "intake_date": data.get("published_at"),
        "outcome_date": outcome_date
    })

    # Creating the environment item ----
    create_environment_data_with_payload({
        "animal_id": animal_id,
        "cats_ok": data.get("environment").get("cats"),
        "dogs_ok": data.get("environment").get("dogs"),
        "kids_ok": data.get("environment").get("children")
    })

    # Creating the attribute item ------
    create_attribute_data_with_payload({
        "animal_id": animal_id,
        "spayed_neutered": data.get("attributes").get("spayed_neutered"),
        "house_trained": data.get("attributes").get("house_trained"),
        "declawed": data.get("attributes").get("declawed"),
        "special_needs": data.get("attributes").get("special_needs"),
        "shots_current": data.get("attributes").get("shots_current")
    })

def rescue_group(data):
    """
    Rescue Groups case executed
    :param data: Data to transform
    :return: void
    """
    print("Rescue Groups case executed")
    print(f"Data: {data}")

    # Checking the data -------------
    status = data.get("relationships").get("statuses").get("data")[0].get("id")
    species_id = data.get("relationships").get("species").get("data")[0].get("id")
    species = determine_species(species_id)
    gender = determine_gender(data.get("attributes").get("sex"))

    if species not in ["dog", "cat"]:
        print(f"Species not supported: {species_id}")
        return

    if gender is None:
        print("Gender couldn't be determined")
        return

    # 1 = available, 3 = adopted
    if status not in ["1", "3"]:
        print(f"Status not supported: {status}")
        return

    # Convert and clean the data ---
    organization_id = data.get("relationships").get("orgs").get("data")[0].get("id")
    breed = determine_rescue_groups_breed_by_id(data.get("relationships").get("breeds").get("data")[0].get("id"))
    outcome_date = data.get("attributes").get("updatedDate") if status == "3" else None

    # Creating the organization item ---
    organization_id = create_organization_data_for_rescue_groups({
        "platform_organization_id": organization_id,
        "posting_source": rescue_groups_source_label
    })

    # Creating the animal item ---------
    animal_id = create_animal_data_with_payload({
        "platform_animal_id": data.get("id"),
        "name": format_string(data.get("attributes").get("name")),
        "age": determine_age_by_mapping(data.get("attributes").get("ageGroup")),
        "species": species,
        "breed": breed,
        "sex": gender,
        "size": determine_size(data.get("attributes").get("sizeGroup")),
        "description": data.get("attributes").get("descriptionText"),
        "adopted": status == "3",
        "organization_id": organization_id,
        "posting_img_count": data.get("attributes").get("pictureCount"),
        "posting_source": rescue_groups_source_label,
        "intake_date": data.get("attributes").get("createdDate"),
        "outcome_date": outcome_date
    })

    # Creating the environment item ----
    create_environment_data_with_payload({
        "animal_id": animal_id,
        "cats_ok": data.get("attributes").get("isCatsOk"),
        "dogs_ok": data.get("attributes").get("isDogsOk"),
        "kids_ok": data.get("attributes").get("isKidsOk")
    })

    # Creating the attribute item ------
    create_attribute_data_with_payload({
        "animal_id": animal_id,
        "spayed_neutered": None,
        "house_trained": data.get("attributes").get("isHousetrained"),
        "declawed": data.get("attributes").get("isDeclawed"),
        "special_needs": data.get("attributes").get("isSpecialNeeds"),
        "shots_current": None
    })

def default_case():
    print("Source not found, default case executed")
    print(f"Data: {data}")
    return None

def switch_example(source, data):
    """Switch case example using dictionary mapping."""
    switch = {
        sonoma_county_source_label: lambda: sonoma_county(data),
        montgomery_county_source_label: lambda: montgomery_county(data),
        long_beach_source_label: lambda: long_beach(data),
        pet_finder_source_label: lambda: pet_finder(data),
        rescue_groups_source_label: lambda: rescue_group(data)
    }

    return switch.get(source, lambda: default_case())()  # Call the function with the argument

def transform_and_insert_data_by_source(data, source):
    """
    Transform and insert data by source.
    :param conn: Database connection
    :param data: Data to transform
    :param source: Source of the data
    :return: void
    """
    switch_example(source, data)
