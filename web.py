from flask import Flask
from routes import main_bp  # Import blueprint from routes.py
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

def create_app():
    """
    Creates and configures the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)  # Initialize the Flask app
    app.register_blueprint(main_bp)  # Register the main blueprint for routes
    app.secret_key = os.getenv('SECRET_KEY')  # Set the secret key for session management
    app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem-based sessions
    app.config['SESSION_PERMANENT'] = True  # Make sessions permanent
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Set session lifetime to 1 hour
    return app  # Return the configured app instance

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    """
    Entry point for running the Flask application.
    """
    app.run(debug=True, host="0.0.0.0")  # Run the app in debug mode and listen on all interfaces
