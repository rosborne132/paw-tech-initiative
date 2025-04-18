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
        "Extra Large": "large",
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
    :return: Age label ('young', 'adult', 'senior')
    """
    if month_count < 12:
        return "young"
    elif month_count < 96:  # Less than 8 years
        return "adult"
    else:
        return "senior"
