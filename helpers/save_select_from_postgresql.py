import psycopg2
from settings import config


def save_pressure_to_postgresql(
        username, systolic, diastolic, timestamp, arm, pulse=None
        ):
    """
    save username(unique), systolic, diastolic, timestamp, date, arm
    """
    connection = config()
    cursor = connection.cursor()
    try:
        postgres_insert_users = """INSERT INTO users (username) VALUES (%s)"""
        record_to_users = username
        cursor.execute(postgres_insert_users, [record_to_users])
    except psycopg2.errors.UniqueViolation:
        connection.rollback()

    finally:
        postgres_insert_pressure = """
        INSERT INTO pressure (
            username, systolic, diastolic, timestamp, arm, pulse
            )
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        records_to_pressure = (
            username,
            systolic,
            diastolic,
            timestamp,
            arm,
            pulse
            )

        cursor.execute(postgres_insert_pressure, records_to_pressure)
        cursor.close()
        connection.commit()
        connection.close()


def save_user_to_postgresql(
        user_name, sex, age, weight, work
        ):
    """
    save user data to postgresql
    """
    connection = config()
    cursor = connection.cursor()
    try:
        postgres_insert_users = """
        INSERT INTO users
        (username, sex, age, weight, work)
        VALUES (%s, %s, %s, %s, %s)"""
        records_to_users = (
            user_name,
            sex,
            age,
            weight,
            work
            )
        cursor.execute(postgres_insert_users, records_to_users)

    except psycopg2.errors.UniqueViolation:
        connection.rollback()

        postgres_insert_users = """
        UPDATE users SET
        sex=%s, age=%s, weight=%s, work=%s WHERE username=%s
        """
        records_to_users = (sex, age, weight, work, user_name)
        cursor.execute(postgres_insert_users, records_to_users)

    finally:
        cursor.close()
        connection.commit()
        connection.close()


def select_data_from_postgresql(user, first_date, last_date):
    """
    select data for the user and time period
    """
    connection = config()
    cursor = connection.cursor()
    postgreSQL_select_query = """
            SELECT * FROM pressure WHERE username = %s
            AND timestamp >= %s AND timestamp <= %s;
        """
    details = [user, first_date, last_date]
    cursor.execute(postgreSQL_select_query, details)

    pressure_data = cursor.fetchall()
    cursor.close()
    connection.close()

    return pressure_data
