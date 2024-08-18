# Flask PostgreSQL Stock Tracker

This project is a Flask-based application that tracks stock information and fundamental indicators using PostgreSQL for data storage.

## Render Deployment

This API is deployed on Render: https://amateurstockmonitor.onrender.com

## Setup on Local Machine

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
POSTGRES_USER=<your_db_user>
POSTGRES_PASSWORD=<your_db_password>
POSTGRES_HOST=<your_db_host>
POSTGRES_DB=<your_db_name>
```

### PostgreSQL Docker Container

In the root directory of your project, build the Docker image with the following command:

```sh
docker build \
  --build-arg POSTGRES_USER=<your_db_user> \
  --build-arg POSTGRES_PASSWORD=<your_db_password> \
  --build-arg POSTGRES_DB=<your_db_name> \
  -t <your_docker_image_name> .´
```

After building the Docker image, run a PostgreSQL container with the following command:

```bash
docker run --name <your_container_name> \
  -e POSTGRES_USER=<your_db_user> \
  -e POSTGRES_PASSWORD=<your_db_password> \
  -e POSTGRES_DB=<your_db_name> \
  -p 5000:5000 \
  -d <your_docker_image_name>
```

To enter the running Docker container, use:

```bash
docker exec -it <your_docker_image_name> bash
```

## Run the Flask App

Start the Flask application by:

```sh
python app.py
```

By default, the Flask app will run on port 5000. You can change this by modifying the `app.run()` parameters in `app.py`.

## API Endpoints

To add new routes or update existing ones, modify the routes.py file. The `register_routes` function is used to set up routes without authentication, and `register_routes_auth` is use to apply authentication to the routes.

### Public Routes

- GET /: Displays the index page with stock data.
- GET /stocks: Returns a list of all stock symbols.
- GET /indicators: Returns a list of all indicators.

### Protected Routes

These routes require authentication:

- GET /stocks/<symbol>: Retrieves details of a specific stock by its symbol.
- POST /indicators: Adds a new indicator to all stocks.
- POST /stocks: Adds a new stock to the database.
- PATCH /stocks/<symbol>: Updates a stock's details.
- DELETE /indicators/<indicator_type>: Deletes an indicator from all stocks.
- DELETE /stocks/<symbol>: Deletes a specific stock and its associated indicators.

## Authentication

This application uses authentication for certain routes. Ensure that you have the necessary authentication configuration set up in the authentication.auth module.

### Get JWT Keys

To perform protected CRUD actions, you need a JWT (JSON Web Token). You can obtain a JWT by registering with your email or Google account:

[Register and Obtain JWT Key](https://zzs.eu.auth0.com/authorize?audience=stock-monitor-api&response_type=token&client_id=PqqwGQo7pfJCGlKCngKhOzfaCbFbIf3e&redirect_uri=https://127.0.0.1:8080/login-results)

Once you have the JWT, include it in the Authorization header of your requests as a Bearer token:

```
Authorization: Bearer <your_jwt_token>
```

## API Testing

To test the Flask CRUD API, run the unit tests using the following command:

```
python test.py
```
