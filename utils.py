import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import bcrypt

def connect_to_database(host=None, user=None, password=None, database=None):
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
        host_val = os.getenv("DB_HOST", host)
        user_val = os.getenv("DB_USER", user)
        password_val = os.getenv("DB_PASSWORD", password)
        database_val = os.getenv("DB_NAME", database)
        # Retrieve credentials from environment variables
        connection = mysql.connector.connect(
            host=host_val,
            user=user_val,
            password=password_val,
            database=database_val
        )
        print(f"Connecting with host={host_val}, user={user_val}, database={database_val}")
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        raise  

def create_user(username: str, name: str, email: str, password: str):
    hashed_password = hash_password(password)
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to the database.")
        return False

    try:
        cursor = connection.cursor()

        sql_insert_query = """
        INSERT INTO users (username, name, email, password)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql_insert_query, (username, name, email, hashed_password.decode('utf-8')))
        connection.commit()
        new_user_id = cursor.lastrowid
        print(f"User created successfully with ID: {new_user_id}")
        return new_user_id


    except Error as e:
        print(f"Error while inserting user: {e}")
        return None

    finally:
        cursor.close()
        connection.close()


def hash_password(plain_password: str) -> bytes:
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed

def validate_user_credentials(username: str, plain_password: str) -> bool:
    """
    Validates user login by checking hashed password from the database.
    
    Args:
        username (str): The username or email used for login.
        plain_password (str): The plain text password entered by the user.
    
    Returns:
        bool: True if credentials are valid, False otherwise.
    """
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to the database.")
        return False

    try:
        cursor = connection.cursor()
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            stored_hash = result[0].encode('utf-8')
            if bcrypt.checkpw(plain_password.encode('utf-8'), stored_hash):
                print("Password is valid.")
                return True
            else:
                print("Invalid password.")
        else:
            print("User not found.")
        return False

    except Error as e:
        print(f"Error during authentication: {e}")
        return False

    finally:
        cursor.close()
        connection.close()

































