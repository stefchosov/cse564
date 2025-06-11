from flask import Flask, render_template_string, request

app = Flask(__name__)

MENU_OPTIONS = [
    ("view", "View Walkable Cities"),
    ("add", "Add a New City"),
    ("login", "Log in User for Research"),
]

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Walkdata Web</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f9f9f9;
            color: #333;
            max-width: 600px;
            margin: 30px auto;
            padding: 20px;
            box-shadow: 0 0 12px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        h1, h2 {
            color: #2c3e50;
        }
        ul {
            list-style: none;
            padding-left: 0;
        }
        li {
            margin-bottom: 15px;
        }
        button {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 12px 20px;
            text-align: center;
            font-size: 1rem;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            width: 100%;
            max-width: 250px;
        }
        button:hover {
            background-color: #2980b9;
        }
        form {
            margin-bottom: 20px;
        }
        label {
            font-weight: 600;
        }
        input[type="text"],
        input[type="number"],
        input[type="password"] {
            width: 100%;
            padding: 8px 10px;
            margin: 6px 0 15px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 1rem;
        }
        p.message {
            color: #2c3e50;
            background: #d1ecf1;
            border-left: 5px solid #17a2b8;
            padding: 10px 15px;
            border-radius: 4px;
            margin-top: 0;
            max-width: 500px;
        }
        .back-button {
            background-color: #7f8c8d;
            margin-top: 10px;
            max-width: 150px;
        }
        .back-button:hover {
            background-color: #606b6f;
        }
    </style>
</head>
<body>

<h1>Welcome to Walkdata — Choose an action:</h1>

{% if mode == "menu" %}
<ul>
  {% for value, label in menu %}
    <li>
      <form method="post" action="{{ url_for('menu_choice') }}">
        <input type="hidden" name="choice" value="{{ value }}">
        <button type="submit">{{ label }}</button>
      </form>
    </li>
  {% endfor %}
</ul>

{% elif mode == "add" %}
  <h2>Add a New City</h2>
  <form method="post" action="{{ url_for('add_city') }}">
    <label for="city_name">City Name:</label><br>
    <input type="text" id="city_name" name="city_name" required><br>
    <label for="walkability_score">Walkability Score (1-100):</label><br>
    <input type="number" id="walkability_score" name="walkability_score" min="1" max="100" required><br>
    <button type="submit">Add City</button>
  </form>
  <form method="get" action="{{ url_for('index') }}">
    <button type="submit" class="back-button">Back to Menu</button>
  </form>

{% elif mode == "login" %}
  <h2>Log in User for Research</h2>
  <form method="post" action="{{ url_for('login_user') }}">
    <label for="username">Username:</label><br>
    <input type="text" id="username" name="username" required><br>
    <label for="password">Password:</label><br>
    <input type="password" id="password" name="password" required><br>
    <button type="submit">Log In</button>
  </form>
  <form method="get" action="{{ url_for('index') }}">
    <button type="submit" class="back-button">Back to Menu</button>
  </form>

{% else %}
  <p class="message">{{ message }}</p>
  <form method="get" action="{{ url_for('index') }}">
    <button type="submit" class="back-button">Back to Menu</button>
  </form>
{% endif %}

</body>
</html>
"""

cities = []

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, menu=MENU_OPTIONS, mode="menu", message=None)

@app.route("/choose", methods=["POST"])
def menu_choice():
    choice = request.form.get("choice")

    if choice == "view":
        message = "Feature coming soon: View Walkable Cities."
        return render_template_string(HTML_TEMPLATE, menu=MENU_OPTIONS, mode="message", message=message)

    elif choice == "add":
        return render_template_string(HTML_TEMPLATE, menu=MENU_OPTIONS, mode="add", message=None)

    elif choice == "login":
        return render_template_string(HTML_TEMPLATE, menu=MENU_OPTIONS, mode="login", message=None)

    else:
        message = "Unknown choice."
        return render_template_string(HTML_TEMPLATE, menu=MENU_OPTIONS, mode="message", message=message)

@app.route("/add_city", methods=["POST"])
def add_city():
    city_name = request.form.get("city_name")
    walk_score = request.form.get("walkability_score")
    if city_name and walk_score:
        cities.append({"name": city_name, "score": walk_score})
        message = f"Added city '{city_name}' with walkability score {walk_score}."
    else:
        message = "Please provide valid city information."

    return render_template_string(HTML_TEMPLATE, menu=MENU_OPTIONS, mode="message", message=message)

@app.route("/login_user", methods=["POST"])
def login_user():
    username = request.form.get("username")
    password = request.form.get("password")

    # Dummy check: accept username "researcher" and password "pass123"
    if username == "researcher" and password == "pass123":
        message = f"Login successful! Welcome, {username}."
    else:
        message = "Login failed: Invalid username or password."

    return render_template_string(HTML_TEMPLATE, menu=MENU_OPTIONS, mode="message", message=message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

