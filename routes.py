from flask import Blueprint, render_template, request, redirect, url_for, session
from utils import login_required, create_user, validate_user_credentials, save_search, fetch_distinct_options, fetch_saved_searches

# Define the blueprint for the main routes
main_bp = Blueprint("main", __name__)

# Menu options for the application
MENU_OPTIONS = [
    ("login", "Log in User for Research"),
    ("lookup", "Lookup Address for Walkability"),
]

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
        if mode == "welcome":  # Redirect to the logged-in menu if the user is authenticated
            return redirect(url_for("main.index", mode="menu"))
        elif mode == "menu":
            return render_template("index.html", menu=MENU_OPTIONS, mode="menu", message=None)

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

    if choice == "view":
        message = "Feature coming soon: View Walkable Cities."
        return render_template("index.html", menu=MENU_OPTIONS, mode="message", message=message)

    elif choice == "lookup":
        return render_template("index.html", menu=MENU_OPTIONS, mode="lookup", message=None)

    elif choice == "saved_searches":
        return redirect(url_for("main.saved_searches"))  # Redirect to the saved searches route

    elif choice == "remove_saved_addresses":
        return redirect(url_for("main.remove_saved_addresses"))  # Redirect to the remove saved addresses route

    elif choice == "logout":
        return redirect(url_for("main.logout"))

    else:
        message = "Unknown choice."
        return render_template("index.html", menu=MENU_OPTIONS, mode="message", message=message)

@main_bp.route("/add_city", methods=["POST"])
@login_required
def add_city():
    """
    Handles adding a new city and its walkability score.

    Args:
        None

    Returns:
        str: Renders the index.html template with a success or error message.
    """
    city_name = request.form.get("city_name")
    walk_score = request.form.get("walkability_score")
    if city_name and walk_score:
        cities.append({"name": city_name, "score": walk_score})
        message = f"Added city '{city_name}' with walkability score {walk_score}."
    else:
        message = "Please provide valid city information."
    return render_template("index.html", menu=MENU_OPTIONS, mode="message", message=message)

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
            user_id = create_user(username, name, email, password)
            session['user_id'] = user_id  # Store the user ID in the session
            return redirect(url_for("main.index"))
        except Exception as e:
            message = f"Error creating user: {str(e)}"
            return render_template("index.html", mode="register", message=message)

    return render_template("index.html", mode="register")

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
                return redirect(url_for("main.index", mode="menu"))  # Redirect to the menu after successful login
            else:
                message = "Invalid username or password."
                return render_template("index.html", mode="login", message=message)
        except Exception as e:
            message = f"Error during login: {str(e)}"
            return render_template("index.html", mode="login", message=message)

    return render_template("index.html", mode="login")

@main_bp.route("/logout")
def logout():
    """
    Handles user logout.

    Args:
        None

    Returns:
        str: Redirects to the login page after clearing the session.
    """
    session.pop('user_id', None)  # Remove the user ID from the session
    return redirect(url_for("main.index", mode="login"))

@main_bp.route("/protected_route", methods=["GET", "POST"])
@login_required
def protected_route():
    """
    Handles the protected route for looking up census block group information.

    Args:
        None

    Returns:
        str: Renders the index.html template with the lookup form, the result, or redirects to the menu.
    """
    print("Session state in /protected_route:", session)  # Debugging log
    if request.method == "POST":
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")

        if not (street and city and state):
            message = "Please fill all fields."
            return render_template("index.html", mode="lookup", message=message)

        from get_census_block import get_block_group_geoid
        block_group = get_block_group_geoid(street, city, state)
        # Construct the address from the form inputs
        try:
            # Save the search details using the save_search function
            save_search(search_id=session.get('user_id'), street=street, city=city, state=state)
        except Exception as e:
            print(f"Error saving search: {str(e)}")
        return render_template("index.html", mode="block_result", block_group=block_group)

    return redirect(url_for("main.index", mode="menu"))

@main_bp.route("/lookup_city", methods=["GET", "POST"])
@login_required
def lookup_city():
    """
    Handles the lookup of city information.

    Args:
        None

    Returns:
        str: Renders the index.html template with the lookup form, the result, or redirects to the menu.
    """
    if request.method == "POST":
        city_name = request.form.get("city_name")

        if not city_name:
            message = "Please provide a valid city name."
            return render_template("index.html", mode="lookup_city", message=message)

        try:
            city_details = {"name": city_name, "walkability_score": 85}  # Mock data
            return render_template("index.html", mode="city_result", city_details=city_details)
        except Exception as e:
            message = f"Error during city lookup: {str(e)}"
            return render_template("index.html", mode="lookup_city", message=message)

    print("Redirecting to menu")
    return redirect(url_for("main.index", mode="menu"))

@main_bp.route("/saved_searches", methods=["GET"])
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
        from utils import fetch_saved_searches, fetch_distinct_options
        searches = fetch_saved_searches(user_id, city_filter, state_filter, sort_by)

        # Fetch distinct cities and states for dropdown options
        distinct_cities = fetch_distinct_options(user_id, "city")
        distinct_states = fetch_distinct_options(user_id, "state")

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

@main_bp.route("/lookup", methods=["GET", "POST"])
@login_required
def lookup():
    """
    Handles the lookup form for walkability.

    Args:
        None

    Returns:
        str: Renders the index.html template with the lookup form.
    """
    us_states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA",
        "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
        "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    return render_template("index.html", mode="lookup", us_states=us_states)

@main_bp.route("/remove_saved_addresses", methods=["GET", "POST"])
@login_required
def remove_saved_addresses():
    """
    Displays saved addresses for the logged-in user and allows them to delete selected addresses.

    Args:
        None

    Returns:
        str: Renders the index.html template with the saved addresses and delete functionality.
    """
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        if not user_id:
            return redirect(url_for("main.index", mode="login"))  # Redirect to login if not authenticated

        # Fetch saved searches for the user
        from utils import fetch_saved_searches
        searches = fetch_saved_searches(user_id)

        if request.method == "POST":
            # Get the list of addresses to delete
            addresses_to_delete = request.form.getlist("addresses")
            from utils import delete_saved_addresses
            delete_saved_addresses(user_id, addresses_to_delete)

            # Refresh the list of saved searches after deletion
            searches = fetch_saved_searches(user_id)

        return render_template("index.html", mode="remove_saved_addresses", searches=searches)
    except Exception as e:
        print(f"Error removing saved addresses: {str(e)}")
        message = "Unable to remove saved addresses."
        return render_template("index.html", mode="message", message=message)
