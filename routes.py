from flask import Blueprint, render_template, request, redirect, url_for
main_bp = Blueprint("main", __name__)

MENU_OPTIONS = [
    ("view", "View Walkable Cities"),
    ("add", "Add a New City"),
    ("login", "Log in User for Research"),
    ("lookup", "Lookup Census Block Group from Address"),
]

cities = []

@main_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html", menu=MENU_OPTIONS, mode="menu", message=None)

@main_bp.route("/choose", methods=["POST"])
def menu_choice():
    choice = request.form.get("choice")

    if choice == "view":
        message = "Feature coming soon: View Walkable Cities."
        return render_template("index.html", menu=MENU_OPTIONS, mode="message", message=message)

    elif choice == "add":
        return render_template("index.html", menu=MENU_OPTIONS, mode="add", message=None)

    elif choice == "login":
        return render_template("index.html", menu=MENU_OPTIONS, mode="login", message=None)
    
    elif choice == "lookup":
    	return render_template("index.html", menu=MENU_OPTIONS, mode="lookup", message=None)
    else:
        message = "Unknown choice."
        return render_template("index.html", menu=MENU_OPTIONS, mode="message", message=message)

@main_bp.route("/add_city", methods=["POST"])
def add_city():
    city_name = request.form.get("city_name")
    walk_score = request.form.get("walkability_score")
    if city_name and walk_score:
        cities.append({"name": city_name, "score": walk_score})
        message = f"Added city '{city_name}' with walkability score {walk_score}."
    else:
        message = "Please provide valid city information."

    return render_template("index.html", menu=MENU_OPTIONS, mode="message", message=message)

@main_bp.route("/login_user", methods=["POST"])
def login_user():
    username = request.form.get("username")
    password = request.form.get("password")

    # Dummy check: accept username "researcher" and password "pass123"
    if username == "researcher" and password == "pass123":
        message = f"Login successful! Welcome, {username}."
    else:
        message = "Login failed: Invalid username or password."

    return render_template("index.html", menu=MENU_OPTIONS, mode="message", message=message)

@main_bp.route("/lookup", methods=["GET", "POST"])
def lookup():
    if request.method == "POST":
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")

        if not (street and city and state):
            message = "Please fill all fields."
            return render_template("index.html", message=message)

        from get_census_block import get_block_group_geoid
        block_group=(get_block_group_geoid(street, city, state))
        print(block_group)
        return render_template("index.html", mode="block_result", block_group=block_group)

    return render_template("index.html", mode="lookup")

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
            conn.commit()
        conn.close()

        return redirect(url_for("main.index"))

    return render_template("register.html")
