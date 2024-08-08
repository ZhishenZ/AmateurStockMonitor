from config import app, setup_db

setup_db()

@app.route('/')
def index():
    return "The database is set up."

if __name__ == "__main__":
    app.run()
