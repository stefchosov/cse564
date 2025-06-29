import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import bcrypt
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    """
    Decorator to enforce login for protected routes.

    Args:
        f (function): The route function to be wrapped.

    Returns:
        function: The wrapped function that checks if the user is logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Checking session in login_required:", session)
        if 'user_id' not in session or session['user_id'] is None:
            # Redirect to login page if user is not authenticated
            return redirect(url_for('main.index', mode='login'))
        return f(*args, **kwargs)
    return decorated_function

def execute_query(query, params=None):
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
        host_val = os.getenv("DB_HOST")
        user_val = os.getenv("DB_USER")
        password_val = os.getenv("DB_PASSWORD")
        database_val = os.getenv("DB_NAME")

        # Establish connection to the database
        connection = mysql.connector.connect(
            host=host_val,
            user=user_val,
            password=password_val,
            database=database_val
        )
    except Error as e:
        # Print error if connection fails
        print(f"Error connecting to database: {e}")
        return None
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for row results as dicts
            
    # Execute the query with parameters if provided
    if params:
        try:
            cursor.execute(query, params)
        except Error as e:
            print(f"Error executing query: {str(e)}")
            return []
    else:
        try:
            cursor.execute(query)
        except Error as e:
            print(f"Error executing query: {str(e)}")
            return []
    # Fetch all results
    results = cursor.fetchall()

    # Commit changes if it's an INSERT/UPDATE/DELETE query
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return results

def grab_name(user_id):
    """
    Grabs name of user for menu

    Args:
        user_id (int): session id of the user

    Returns:
        String: Name of user
    """
    try:
        sql_query = """
        SELECT name FROM users WHERE id = %s
        """
        params = (user_id, )
        # Use execute_query to fetch the user record
        name = execute_query(sql_query, params)[0]['name']
        return name
    except Exception as e:
        print(f"Error grabbing name: {str(e)}")
        return None


def create_user(username: str, name: str, email: str, password: str):
    """
    Creates a new user in the database.

    Args:
        username (str): The username of the user.
        name (str): The full name of the user.
        email (str): The email address of the user.
        password (str): The plaintext password of the user.

    Returns:
        dict: A dictionary containing the result of the operation.
              Example: {"success": True, "user_id": 123} or {"success": False, "error": "Username already exists"}
    """
    hashed_password = hash_password(password)
    try:
        conn = mysql.connector.connect(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), host='localhost', database=os.getenv("DB_NAME"))
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "error": "The username already exists. Please choose a different username."}

        # Check if the email already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "error": "The email address is already registered. Please use a different email."}

        # Insert the new user into the database
        sql_insert_query = """
        INSERT INTO users (username, name, email, password)
        VALUES (%s, %s, %s, %s)
        """
        params = (username, name, email, hashed_password)

        cursor.execute(sql_insert_query, params)
        conn.commit()

        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        print(f"User created with ID: {user_id}, Username: {username}, Name: {name}, Email: {email}")
        return {"success": True, "user_id": user_id}

    except mysql.connector.IntegrityError as e:
        # Handle database integrity errors (e.g., duplicate keys)
        print(f"Database integrity error: {str(e)}")
        return {"success": False, "error": "A database integrity error occurred. Please check your input."}

    except mysql.connector.Error as e:
        # Handle database-specific errors
        print(f"Database error: {str(e)}")
        return {"success": False, "error": f"Database error: {str(e)}"}

    except Exception as e:
        # Handle general errors
        print(f"Unexpected error: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def hash_password(plain_password: str) -> bytes:
    """
    Hashes a plain text password using bcrypt.

    Args:
        plain_password (str): The plain text password to be hashed.

    Returns:
        bytes: The hashed password.
    """
    # Generate a salt for bcrypt hashing
    salt = bcrypt.gensalt()
    # Hash the password using bcrypt and the generated salt
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed

def validate_user_credentials(username: str, password: str) -> int:
    """
    Validates a user's credentials by checking the username and hashed password in the database.

    Args:
        username (str): The username of the user.
        password (str): The plaintext password provided by the user.

    Returns:
        int: The user ID if the credentials are valid, or None if invalid.
    """
    try:
        # Query to fetch the user record based on the username
        sql_query = """
        SELECT id, password FROM users WHERE username = %s
        """
        params = (username, )

        # Use execute_query to fetch the user record
        results = execute_query(sql_query, params)

        if results:
            user_record = results[0]
            hashed_password = user_record["password"]

            # Validate the provided password against the hashed password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return user_record["id"]  # Return the user ID if credentials are valid

        print("Invalid username or password.")
        return None
    except Exception as e:
        print(f"Error validating user credentials: {str(e)}")
        return None

def save_search(user_id, street, city, state, census_block):
    """
    Saves a search record for a user in the database.

    Args:
        user_id (int): The ID of the user.
        street (str): The street address.
        city (str): The city name.
        state (str): The state name.

    Returns:
        bool: True if the search was saved successfully, False otherwise.
    """
    try:
        # Generate a unique search_id for the user
        new_search_id = generate_search_id(user_id)

        # Check if the search record already exists for the user
        query_exists = """
        SELECT COUNT(*) FROM searches WHERE user_id = %s AND street = %s AND city = %s AND state = %s AND census_block = %s
        """
        params_exists = (user_id, street, city, state, census_block)
        exists = execute_query(query_exists, params_exists)[0]['COUNT(*)']

        if exists > 0:
            print(f"Search with address {street, city, state} already exists for user {user_id}.")
            return False

        # Insert the new search record
        query_insert = """
        INSERT INTO searches (user_id, search_id, street, city, state, census_block)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params_insert = (user_id, new_search_id, street, city, state, census_block)
        execute_query(query_insert, params_insert)

        print(f"Search {new_search_id} saved for user {user_id} with address {street, city, state}")
        return True
    except Exception as e:
        print(f"Error saving search: {str(e)}")
        return False

def generate_search_id(user_id):
    """
    Generates a unique search ID for a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        int: The next search ID for the user.
    """
    query = "SELECT MAX(search_id) FROM searches WHERE user_id = %s"
    params = (user_id,)
    result = execute_query(query, params)

    if result and result[0]['MAX(search_id)'] is not None:
        return result[0]['MAX(search_id)'] + 1  # Increment the highest search_id for the user
    else:
        return 1  # Start with ID 1 if the user has no searches

def fetch_distinct_options(user_id, column, dependent_column=None, dependent_value=None):
    """
    Fetch distinct values for a column (e.g., city or state) with optional dependent filtering.

    Args:
        user_id (int): The ID of the user.
        column (str): The column to fetch distinct values for (e.g., "city" or "state").
        dependent_column (str): The column to filter by (e.g., "state" or "city").
        dependent_value (str): The value to filter the dependent column by.

    Returns:
        list: A list of distinct values for the specified column.
    """
    query = f"SELECT DISTINCT {column} FROM searches WHERE user_id = %s"
    params = [user_id]

    if dependent_column and dependent_value:
        query += f" AND {dependent_column} = %s"
        params.append(dependent_value)

    query += f" ORDER BY {column}"  # Sort results alphabetically

    # Use execute_query to fetch distinct options
    results = execute_query(query, params)

    # Extract values from the dictionaries
    return [row[column] for row in results]

def fetch_saved_addresses(user_id, city_filter=None, state_filter=None, sort_by="city"):
    """
    Fetch saved addresses for a user with optional filtering and sorting.

    Args:
        user_id (int): The ID of the user.
        city_filter (str): Optional city filter.
        state_filter (str): Optional state filter.
        sort_by (str): Sort by "city" or "state".

    Returns:
        list: A list of saved addresses.
    """
    query = "SELECT street, city, state, census_block FROM searches WHERE user_id = %s"
    params = [user_id]

    if city_filter:
        query += " AND city = %s"
        params.append(city_filter)
    if state_filter:
        query += " AND state = %s"
        params.append(state_filter)

    query += f" ORDER BY {sort_by}, street"

    # Use execute_query to fetch the addresses
    return execute_query(query, params)

def delete_saved_addresses(user_id, addresses):
    """
    Deletes saved addresses for a specific user from the database.

    Args:
        user_id (int): The ID of the user.
        addresses (list): A list of addresses to delete.

    Returns:
        None
    """
    try:
        for address in addresses:
            street, city, state = address.split(", ")
            query = "DELETE FROM searches WHERE user_id = %s AND street = %s AND city = %s AND state = %s"
            params = (user_id, street, city, state)

            # Use execute_query to delete the address
            execute_query(query, params)

        print(f"Deleted addresses: {addresses}")
    except Exception as e:
        print(f"Error deleting saved addresses: {str(e)}")