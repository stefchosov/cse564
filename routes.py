from flask import Blueprint, render_template, request, redirect, url_for, session
from utils import login_required, create_user, validate_user_credentials

# Define the blueprint for the main routes
main_bp = Blueprint("main", __name__)

# Menu options for the application
MENU_OPTIONS = [
    ("view", "View Walkable Cities"),
    ("add", "Add a New City"),
    ("login", "Log in User for Research"),
    ("lookup", "Lookup Census Block Group from Address"),
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
    return render_template("index.html", menu=MENU_OPTIONS, mode=mode, message=None)

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
        str: Renders the index.html template with the lookup form or the result.
    """
    if request.method == "POST":
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")

        if not (street and city and state):
            message = "Please fill all fields."
            return render_template("index.html", mode="lookup", message=message)

        from get_census_block import get_block_group_geoid
        block_group = get_block_group_geoid(street, city, state)
        return render_template("index.html", mode="block_result", block_group=block_group)

    return render_template("index.html", mode="lookup")
