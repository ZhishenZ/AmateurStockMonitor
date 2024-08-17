from flask import Flask
from config import setup_db, app
from routes import register_routes

setup_db()

register_routes(app)

if __name__ == "__main__":
    app.run()
