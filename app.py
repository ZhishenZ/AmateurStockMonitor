from flask import Flask
from config import setup_db, app
from routes import register_routes_auth

setup_db()

register_routes_auth(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
