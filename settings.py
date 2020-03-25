import tokens
import psycopg2


PROXY = {
    'proxy_url': tokens.PROXY_URL,
    'urllib3_proxy_kwargs': {
        'username': tokens.PROXY_USERNAME,
        'password': tokens.PROXY_PASSWORT,
    }
}


def config():
    connection = psycopg2.connect(
        user=tokens.POSTGRES_USER,
        password=tokens.POSTGRES_PASSW,
        host='127.0.0.1',
        port='5432',
        database=tokens.DB_NAME
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
