from flask import Flask
from routes import main_bp  # Import blueprint from routes.py

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)





