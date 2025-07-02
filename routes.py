from flask import Blueprint, render_template, request, redirect, url_for, session
from utils import *

# Define the blueprint for the main routes
main_bp = Blueprint("main", __name__)

# List to store cities and their walkability scores
cities = []

@main_bp.route("/", methods=["GET", "POST"])
def index():
    """
    Handles the home page of the application.

    Args:
        None

    Returns:
        str: Renders the index.html template with the appropriate mode and menu options.
    """
    mode = request.args.get("mode", "welcome")  # Default to "welcome" mode

    # Check if the user is logged in
    if 'user_id' in session and session['user_id'] is not None:
        if mode == "menu":  # Render the logged-in menu
            return render_template("index.html", mode="menu", message=None, name = grab_name(session.get("user_id")))
        elif mode == "welcome":  # Redirect to the menu if the user is authenticated
            return redirect(url_for("main.index", mode="menu"))

    # If the user is not logged in, render the appropriate mode
    if mode == "login":
        return render_template("index.html", mode="login", message=None)
    elif mode == "register":
        return render_template("index.html", mode="register", message=None)

    # Default to the welcome screen for unauthenticated users
    return render_template("index.html", mode="welcome", message=None)

@main_bp.route("/choose", methods=["POST"])
@login_required
def menu_choice():
    """
    Handles menu selection after login.

    Args:
        None

    Returns:
        str: Renders the appropriate template based on the user's menu choice.
    """
    choice = request.form.get("choice")
    if choice == "lookup":
        return render_template("index.html", mode="lookup", message=None)

    elif choice == "saved_searches":
        return redirect(url_for("main.saved_searches"))  # Redirect to the saved searches route

    elif choice == "remove_saved_addresses":
        return redirect(url_for("main.remove_saved_addresses"))  # Redirect to the remove saved addresses route

    elif choice == "logout":
        return redirect(url_for("main.logout"))

    else:
        message = "Unknown choice."
        return render_template("index.html", mode="message", message=message)

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles user registration.

    Args:
        None

    Returns:
        str: Renders the index.html template with a success or error message.
    """
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")  # Full name field
        email = request.form.get("email")  # Email field
        password = request.form.get("password")  # Password field

        try:
            # Use the create_user helper method to add the user to the database
            result = create_user(username, name, email, password)

            if result["success"]:
                print(f"User created with ID: {result['user_id']}, Username: {username}")
                session['user_id'] = result["user_id"]  # Store the user ID in the session
                name = grab_name(session.get("user_id"))
                return redirect(url_for("main.index", mode="menu", name=name))
            else:
                # Handle specific error messages returned by create_user
                message = result["error"]
                return render_template("index.html", mode="register", message=message)
        except Exception as e:
            # Handle unexpected exceptions
            message = f"An unexpected error occurred during registration: {str(e)}"
            return render_template("index.html", mode="register", message=message)

    # Render the registration page for GET requests
    return render_template("index.html", mode="register", message=None)

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.

    Args:
        None

    Returns:
        str: Renders the index.html template with a success or error message.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            # Validate user credentials using the helper method
            user_id = validate_user_credentials(username, password)
            if user_id:
                session['user_id'] = user_id  # Store the user ID in the session
                name = grab_name(session.get("user_id"))
                return render_template("index.html", mode="menu", name=name)  # Redirect to the menu after successful login
            else:
                message = "Invalid username or password."
                return render_template("index.html", mode="login", message=message)
        except Exception as e:
            message = f"Error during login: {str(e)}"
            return render_template("index.html", mode="login", message=message)
    name = grab_name(session.get("user_id"))
    return render_template("index.html", mode="login", name=name)


@main_bp.route("/logout", methods=["GET"])
def logout():
    """
    Handles user logout.

    Args:
        None

    Returns:
        str: Redirects to the login page after clearing the session.
    """
    if request.method == "GET":
        # Clear the session to log out the user
        session.pop('user_id', None)
        session.clear()
     # Remove the user ID from the session
    return redirect(url_for("main.index", mode="welcome"))

@main_bp.route("/addresses/lookup", methods=["GET", "POST"])
def addresses_lookup():
    """
    Handles the protected route for looking up census block group information.

    Args:
        None

    Returns:
        str: Renders the index.html template with the lookup form, the result, or redirects to the menu.
    """
    if request.method == "POST":
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")

        if not (street and city and state):
            message = "Please fill all fields."
            return render_template("index.html", mode="lookup", message=message)

        user_id = session.get('user_id')
        walkability=save_search(user_id, street, city, state)
        return render_template("index.html", mode="walkability_display", walkability=walkability)

    # Render the lookup form
    return render_template("index.html", mode="lookup")

@main_bp.route("/addresses/saved", methods=["GET"])
@login_required
def saved_searches():
    """
    Displays the saved searches for the logged-in user, with optional filtering and dropdown options.

    Args:
        None

    Returns:
        str: Renders the index.html template with the saved searches and dropdown options.
    """
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        if not user_id:
            return redirect(url_for("main.index", mode="login"))  # Redirect to login if not authenticated

        # Get filtering and sorting parameters from the query string
        city_filter = request.args.get("city", None)
        state_filter = request.args.get("state", None)
        sort_by = request.args.get("sort_by", "city")  # Default sort by city

        # Fetch saved searches for the user from the database
        searches = fetch_saved_addresses(user_id, city_filter, state_filter, sort_by)

        # Fetch distinct cities and states for dropdown options with dependent filtering
        distinct_cities = fetch_distinct_options(user_id, "city", "state", state_filter)
        distinct_states = fetch_distinct_options(user_id, "state", "city", city_filter)

        return render_template(
            "index.html",
            mode="saved_searches",
            searches=searches,
            city_filter=city_filter,
            state_filter=state_filter,
            sort_by=sort_by,
            distinct_cities=distinct_cities,
            distinct_states=distinct_states,
        )
    except Exception as e:
        print(f"Error fetching saved searches: {str(e)}")
        message = "Unable to fetch saved searches."
        return render_template("index.html", mode="message", message=message)

@main_bp.route("/remove_saved_addresses", methods=["GET", "POST"])
@login_required
def remove_saved_addresses():
    """
    Handles the removal of saved addresses with optional filtering by city and state.

    Args:
        None

    Returns:
        str: Renders the index.html template with the filtered addresses or removes selected addresses.
    """
    user_id = session.get('user_id')  # Get the logged-in user's ID
    if not user_id:
        return redirect(url_for("main.index", mode="login"))  # Redirect to login if not authenticated

    if request.method == "POST":
        # Handle address removal
        selected_addresses = request.form.getlist("addresses")  # Get selected addresses
        try:
            from utils import delete_saved_addresses
            delete_saved_addresses(user_id, selected_addresses)  # Remove selected addresses from the database
            message = "Selected addresses have been removed successfully."
            return render_template("index.html", mode="message", message=message)
        except Exception as e:
            message = f"Error removing addresses: {str(e)}"
            return render_template("index.html", mode="message", message=message)

    # Handle filtering
    city_filter = request.args.get("city", None)
    state_filter = request.args.get("state", None)

    # Fetch filtered addresses for the user
    addresses = fetch_saved_addresses(user_id, city_filter, state_filter)

    # Fetch distinct states based on the selected city
    distinct_states = fetch_distinct_options(user_id, "state", "city", city_filter)

    # Fetch distinct cities based on the selected state
    distinct_cities = fetch_distinct_options(user_id, "city", "state", state_filter)

    return render_template(
        "index.html",
        mode="remove_saved_addresses",
        addresses=addresses,
        distinct_cities=distinct_cities,
        distinct_states=distinct_states,
        city_filter=city_filter,
        state_filter=state_filter,
    )
