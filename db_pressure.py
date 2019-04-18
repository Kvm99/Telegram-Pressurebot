import psycopg2
from db_settings import config

def create_tables():

	tables = (
		"""
		CREATE TABLE IF NOT EXISTS users (
		  username VARCHAR(50) PRIMARY KEY NOT NULL 
		);
        """,

		"""
		CREATE TABLE IF NOT EXISTS pressure(
            pressure_id SERIAL PRIMARY KEY,
            username VARCHAR(50),
            systolic VARCHAR(3) NOT NULL,
    		diastolic VARCHAR(3) NOT NULL,
    		timestamp timestamptz NOT NULL,
    		date DATE,
    		arm VARCHAR(50) NOT NULL,
            FOREIGN KEY (username) REFERENCES users
        );
		"""
		)
	try:
		connection = config()
		cursor = connection.cursor()

		for table in tables:
			cursor.execute(table)

		cursor.close()
		connection.commit()

	except (Exception, psycopg2.DatabaseError) as error:
		print(error)

	finally:
		if connection is not None:
			connection.close()

if __name__ == "__main__":
	create_tables()
