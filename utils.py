import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

def connect_to_database(host, user, password, database):
    """
    Establishes a connection to the MySQL database.

    Args:
        host (str): Hostname or IP address of the MySQL server.
        user (str): Username for the MySQL database.
        password (str): Password for the MySQL database.
        database (str): Name of the MySQL database.

    Returns:
        mysql.connector.connection_cext.CMySQLConnection: Connection object to the database.

    Raises:
        mysql.connector.Error: If an error occurs during connection.
    """
    try:
        # Load environment variables from .env file
        load_dotenv()

        # Retrieve credentials from environment variables
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", host),
            user=os.getenv("DB_USER", user),
            password=os.getenv("DB_PASSWORD", password),
            database=os.getenv("DB_NAME", database)
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        raise   