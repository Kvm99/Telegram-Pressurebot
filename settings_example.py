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

if __name__ == "__main__":
	config()
	cursor()
