def insert_environment_data(conn, data):
    """
    Insert environment data into the animal_environment table.
    :param conn: Database connection object
    :param data: JSON string containing environment data
    :return: Data id of the inserted environment
    """
    try:
        with conn.cursor() as cursor:
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
        return environment_id
    except Exception as e:
        print(f"Error inserting environment data: {e}")
        return None
