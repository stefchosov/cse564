from flask import Flask
from routes import main_bp  # Import blueprint from routes.py
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem-based sessions
    app.config['SESSION_PERMANENT'] = True  # Make sessions permanent
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Set session lifetime to 1 hour
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
