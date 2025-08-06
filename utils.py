import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import bcrypt
from functools import wraps
from flask import session, redirect, url_for
from get_census_block import *

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
    print(f"Executed query: {query} with params: {params}")
    return results

def grab_name(user_id):
    """
    Grabs name of user for menu using a stored procedure.

    Args:
        user_id (int): session id of the user

    Returns:
        String: Name of user
    """
    try:
        # Load environment variables from .env file
        load_dotenv()
        host_val = os.getenv("DB_HOST")
        user_val = os.getenv("DB_USER")
        password_val = os.getenv("DB_PASSWORD")
        database_val = os.getenv("DB_NAME")

        # Establish database connection
        connection = mysql.connector.connect(
            host=host_val,
            user=user_val,
            password=password_val,
            database=database_val
        )
        cursor = connection.cursor(dictionary=True)  # Use dictionary=True for row results as dicts

        # Call the stored procedure directly
        cursor.callproc('GetUserName', [user_id])

        for result in cursor.stored_results():
         rows = result.fetchall()
        print(rows)
        # Close the cursor and connection
        cursor.close()
        connection.close()

        return rows[0]['name'] if rows else None
    except Error as e:
        print(f"Error fetching user name: {str(e)}")
        return None

def get_walkability_values(census_block):
    """
    Grabs walkability values for the user based on census block.

    Args:
        user_id (int): The ID of the user.
        census_block (str): The census block identifier.

    Returns:
        dict: A dictionary containing walkability values or an error message.
    """
    try:
        sql_query = """
        SELECT intersection_density, transit_access, job_housing_mix, population_employment_density, NatWalkInd FROM WalkabilityIndex WHERE census_block = %s
        """
        params = (census_block, )
        results = execute_query(sql_query, params)
        if results:
            return results[0]  # Return the first result as a dictionary
        else:
            return {"error": "No walkability data found for the given census block."}

    except Exception as e:
        print(f"Error fetching walkability values: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

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
        # Call the stored procedure
        cursor.callproc('AddUser', [username, name, email, hashed_password])
        conn.commit()
        # Fetch the last inserted ID
        cursor.execute("SELECT LAST_INSERT_ID()")
        user_id = cursor.fetchone()[0]

        # Close the cursor and connection
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
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('GetUserCredentials', [username])

        for result in cursor.stored_results():
            user_record = result.fetchone()
            if user_record:
                hashed_password = user_record["password"]
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    return user_record["id"]
        return None
    except Exception as e:
        print(f"Error validating user credentials: {str(e)}")
        return None

def save_search(user_id, street, city, state):
    """
    Saves a search record for a user in the database.

    Args:
        user_id (int): The ID of the user.
        street (str): The street address.
        city (str): The city name.
        state (str): The state name.

    Returns:
        Val or bool: Walkability index if the search was saved successfully, False otherwise.
    """
    census_block = get_block_group_geoid(street, city, state)
    try:
        # Check if the search record already exists for the user
        query_exists = """
        SELECT COUNT(*) FROM searches WHERE user_id = %s AND street = %s AND city = %s AND state = %s
        """
        params_exists = (user_id, street, city, state)
        exists = execute_query(query_exists, params_exists)[0]['COUNT(*)']
        if not (isinstance(census_block, int) or (isinstance(census_block, str) and census_block.isdigit())):
            return f"Error: Could not find census block for address {street, city, state}. Potentially an invalid address."
        sql_query = """
        SELECT intersection_density, transit_access, job_housing_mix, population_employment_density, NatWalkInd FROM WalkabilityIndex WHERE census_block = %s
        """
        params = (census_block, )
        results = execute_query(sql_query, params)
        if results:
            # If the search does not exist, save it
            # Get the census block for the address
            if not exists and user_id is not None:
                # Generate a new search ID for the user
                new_search_id = generate_search_id(user_id)
                try:
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
                    cursor = connection.cursor(dictionary=True)
                    cursor.callproc('SaveSearch', [user_id, new_search_id, street, city, state, census_block])
                    connection.commit()
                    cursor.close()
                    connection.close()
                except Exception as e:
                    print(f"Error inserting search user credentials: {str(e)}")
                    return None
            return results[0]  # Return the first result as a dictionary
        else:
            return "No walkability data found for the provided address."
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

def get_distinct_options(user_id, column, dependent_column=None, dependent_value=None):
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


def get_saved_addresses(user_id, attribute, city_filter=None, state_filter=None, sort="DESC"):
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
    #query = "SELECT street, city, state, census_block FROM searches WHERE user_id = %s"
    query = f"""
        SELECT s.user_id, s.street, s.city, s.state, w.{attribute} as value
        FROM WalkabilityIndex AS w
        JOIN searches AS s ON s.census_block = w.census_block
        WHERE s.user_id = %s
    """    
    params = [user_id]
    if city_filter is not None:
        query += " AND city = %s"
        params.append(city_filter)
    if state_filter is not None:
        query += " AND state = %s"
        params.append(state_filter)
    if sort == "Low":
        sort="ASC"
    else:
        sort="DESC"

    query += f" ORDER BY w.{attribute} {sort}"
    # Use execute_query to fetch the addresses
    quer = execute_query(query, params)
    return quer

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
            try:
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
                cursor = connection.cursor(dictionary=True)
                cursor.callproc('DeleteSavedAddress', [user_id, street, city, state])
                connection.commit()
                cursor.close()
                connection.close()
            except Exception as e:
                print(f"Error inserting search user credentials: {str(e)}")
                return None
        print(f"Deleted addresses: {addresses}")
    except Exception as e:
        print(f"Error deleting saved addresses: {str(e)}")