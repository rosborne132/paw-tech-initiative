def insert_attribute_data(conn, data):
    """
    Insert attribute data into the animal_attribute table.
    :param conn: Database connection object
    :param data: JSON string containing attribute data
    :return: Data id of the inserted attribute
    """
    try:
        with conn.cursor() as cursor:
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
        return attribute_id
    except Exception as e:
        print(f"Error inserting attribute data: {e}")
        return None
