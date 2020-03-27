import psycopg2
import os


PROXY = {
    'proxy_url': os.environ.get('PROXY_URL'),
    'urllib3_proxy_kwargs': {
        'username': os.environ.get('PROXY_USERNAME'),
        'password': os.environ.get('PROXY_PASSWORT'),
    }
}


def config():
    connection = psycopg2.connect(
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSW'),
        host='127.0.0.1',
        port='5432',
        database=os.environ.get('DB_NAME'),
    )

    return connection


def cursor():
    try:
        connection = config()
        cursor = connection.cursor()

        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to -", record, "\n")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed")
