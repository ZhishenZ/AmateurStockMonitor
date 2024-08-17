import unittest
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import Stock, Indicator, db
from routes import register_routes

# Define your Flask app and database configuration for testing
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///:memory:"  # In-memory database for testing
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)


STOCK_1 = "AAPL"
STOCK_2 = "AMD"
INDICATOR_1 = "PERatio"
INDICATOR_2 = "200DayMovingAverage"


class StockAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client and initialize the database."""
        # Create the test client
        self.app = app.test_client()
        self.app.testing = True

        # Set up the test database
        with app.app_context():

            # Create some dummy data for the unit test
            stock1 = Stock(symbol=STOCK_1, current_price=150.0)
            stock2 = Stock(symbol=STOCK_2, current_price=120.0)
            indicator1_1 = Indicator(
                indicator_type=INDICATOR_1,
                value="30.0",
                stock=stock1,
                latest_trading_day="2024-01-01",
            )
            indicator1_2 = Indicator(
                indicator_type=INDICATOR_2,
                value="160.0",
                stock=stock1,
                latest_trading_day="2024-01-01",
            )
            indicator2_1 = Indicator(
                indicator_type=INDICATOR_1,
                value="50.0",
                stock=stock2,
                latest_trading_day="2024-01-01",
            )
            indicator2_2 = Indicator(
                indicator_type=INDICATOR_2,
                value="90.0",
                stock=stock2,
                latest_trading_day="2024-01-01",
            )

            db.create_all()  # Create all tables

            db.session.add(stock1)
            db.session.add(stock2)
            db.session.add(indicator1_1)
            db.session.add(indicator1_2)
            db.session.add(indicator2_1)
            db.session.add(indicator2_2)

            db.session.commit()

        register_routes(app)

    def tearDown(self):
        """Tear down the database after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Drop all tables

    def test_index(self):
        """Test the index route."""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

        # Decode response.data to a string
        response_data = response.data.decode("utf-8")
        self.assertIn(STOCK_1, response_data)
        self.assertIn(STOCK_2, response_data)

    def test_get_stocks(self):
        """Test getting all stocks."""
        response = self.app.get("/stocks")
        self.assertEqual(response.status_code, 200)
        stock_list = json.loads(response.data)
        self.assertIn(STOCK_1, stock_list)
        self.assertIn(STOCK_2, stock_list)

    def test_get_indicators(self):
        """Test getting all indicators."""
        response = self.app.get("/indicators")
        self.assertEqual(response.status_code, 200)
        indicator_list = json.loads(response.data)
        self.assertIn(INDICATOR_1, indicator_list)
        self.assertIn(INDICATOR_2, indicator_list)

    def test_get_stock_by_symbol(self):
        """Test getting a specific stock by symbol."""
        response = self.app.get('/stocks/AAPL')
        self.assertEqual(response.status_code, 200)
        stock_info = json.loads(response.data)
        self.assertEqual(stock_info["symbol"], STOCK_1)
        self.assertEqual(stock_info["current_price"], 150.0)
        self.assertEqual(stock_info["PERatio"], '30.0')

    def test_add_stock(self):
        new_stock = {"symbol": "GOOG"}
        response = self.app.post('/stocks', json=new_stock)
        self.assertEqual(response.status_code, 201)

        response = self.app.get('/stocks')
        stock_list = json.loads(response.data)
        self.assertIn("GOOG", stock_list)

    # Since the API from alphavantage is limited for request per minute
    # this unit is currently deactivated for the free alphavantage API
    # def test_add_indicator(self):
    #     """Test adding an indicator to all stocks."""
    #     new_indicator = {"indicator_type": "DividendYield"}
    #     response = self.app.post('/indicators', json=new_indicator)
    #     self.assertEqual(response.status_code, 201)

    #     response = self.app.get('/stocks/AAPL')
    #     stock_info = json.loads(response.data)
    #     self.assertIn("DividendYield", stock_info)

    def test_update_stock(self):
        """Test updating a stock's current price."""
        update_data = {"current_price": 200.0}
        response = self.app.patch('/stocks/AAPL', json=update_data)
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/stocks/AAPL')
        stock_info = json.loads(response.data)
        self.assertEqual(stock_info["current_price"], 200.0)

    def test_delete_indicator(self):
        """Test deleting an indicator from all stocks."""
        response = self.app.delete('/indicators/PERatio')
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/stocks/AAPL')
        stock_info = json.loads(response.data)
        self.assertNotIn("PERatio", stock_info)

    def test_delete_stock(self):
        """Test deleting a stock."""
        response = self.app.delete('/stocks/AAPL')
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/stocks')
        stock_list = json.loads(response.data)
        self.assertNotIn(STOCK_1, stock_list)


if __name__ == "__main__":
    unittest.main()
