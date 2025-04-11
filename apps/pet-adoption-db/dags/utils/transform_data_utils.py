import json

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


# ------------------------------------------------------------
"Sonoma County Department of Health Services"
"Montgomery County Animal Services"
"Pet Finder"
"City of Long Beach Animal Shelter"
"Rescue Groups"

def sonoma_county(conn, data):
    print("Sonoma County Department of Health Services case executed")
    # TODO

def montgomery_county(conn, data):
    print("Montgomery County Animal Services case executed")
    # TODO

def long_beach(conn, data):
    print("City of Long Beach Animal Shelter case executed")
    # TODO

def pet_finder(conn, data):
    print("Pet Finder case executed")
    # TODO

def rescue_group(conn, data):
    print("Rescue Groups case executed")
    # TODO

def default_case():
    print("Source not found, default case executed")

def switch_example(conn, source, data):
    """Switch case example using dictionary mapping."""
    switch = {
        "Sonoma County Department of Health Services": lambda: sonoma_county(conn, data),
        "Montgomery County Animal Services": lambda: montgomery_county(conn, data),
        "City of Long Beach Animal Shelter": lambda: long_beach(conn, data),
        "Pet Finder": lambda: pet_finder(conn, data),
        "Rescue Groups": lambda: rescue_group(conn, data)
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
