from flask import Blueprint, render_template, request, redirect, url_for, session
from utils import login_required, create_user, validate_user_credentials

main_bp = Blueprint("main", __name__)

MENU_OPTIONS = [
    ("view", "View Walkable Cities"),
    ("add", "Add a New City"),
    ("login", "Log in User for Research"),
    ("lookup", "Lookup Census Block Group from Address"),
]

cities = []

@main_bp.route("/", methods=["GET", "POST"])
def index():
    mode = request.args.get("mode", "welcome")  # Default to "welcome" mode
    return render_template("index.html", menu=MENU_OPTIONS, mode=mode, message=None)

@main_bp.route("/choose", methods=["POST"])
@login_required
def menu_choice():
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
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")  # Full name field
        email = request.form.get("email")  # Email field
        password = request.form.get("password")  # Password field

        try:
            # Use the create_user helper method
            user_id = create_user(username, name, email, password)
            session['user_id'] = user_id
            return redirect(url_for("main.index"))
        except Exception as e:
            message = f"Error creating user: {str(e)}"
            return render_template("index.html", mode="register", message=message)

    return render_template("index.html", mode="register")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            user_id = validate_user_credentials(username, password)
            if user_id:
                session['user_id'] = user_id
                # Redirect to the menu after successful login
                return redirect(url_for("main.index", mode="menu"))
            else:
                message = "Invalid username or password."
                return render_template("index.html", mode="login", message=message)
        except Exception as e:
            message = f"Error during login: {str(e)}"
            return render_template("index.html", mode="login", message=message)

    return render_template("index.html", mode="login")

@main_bp.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for("main.index", mode="login"))

@main_bp.route("/protected_route", methods=["GET", "POST"])
@login_required
def protected_route():
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
