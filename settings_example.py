import psycopg2

TOKEN = "bot_token"
PROXY = {
    'proxy_url': 'your_proxy',
    'urllib3_proxy_kwargs': {
        'username': 'your_proxy_username',
        'password': 'your_proxy_password)'
    }
}


def config():
    connection = psycopg2.connect(
        user='username',
        password="password",
        host='127.0.0.1',
        port='5432',
        database='database_name'
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


if __name__ == "__main__":
    config()
    cursor()
