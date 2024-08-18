from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from stock_utils.priceFetcher import get_stock_price
from stock_utils.dataFetcher import get_fundamental_data
from models import db, Stock, Indicator

load_dotenv()

database_user = os.getenv("POSTGRES_USER")
database_password = os.getenv("POSTGRES_PASSWORD")
database_host = os.getenv("POSTGRES_HOST")
database_name = os.getenv("POSTGRES_DB")
database_path = (
    f"postgresql://{database_user}:{database_password}@{database_host}/{database_name}"
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

def setup_db():
    with app.app_context():
        db.drop_all()  # Drop all tables
        db.create_all()  # Create all tables
        initialize_sample_data()  # add dummy stock data


def add_stock_to_database(symbol: str) -> Stock:
    current_price = get_stock_price(symbol)
    if current_price is None:
        print(f"Error: Could not retrieve price for {symbol}.")
        return None

    stock = Stock(symbol=symbol, current_price=current_price)
    try:
        db.session.add(stock)
        db.session.commit()  # Commit to generate an ID for the stock
        print(f"Stock {symbol} added to database with ID {stock.id}.")
        return stock
    except Exception as e:
        print(f"Error while adding stock to database: {e}")
        db.session.rollback()
        return None

def add_indicator_to_stock(stock: Stock, indicator_type: str) -> Indicator:
    fundamental_data_result = get_fundamental_data(stock.symbol, indicator_type)
    if fundamental_data_result.error_message is not None:
        print(fundamental_data_result.error_message)
        return None

    indicator_value = fundamental_data_result.value
    if indicator_value is None:
        print(f"Error: Indicator value for {indicator_type} is None.")
        return None

    latest_trading_day = fundamental_data_result.latest_trading_day
    if latest_trading_day is None:
        print(f"Error: Time stamp for {latest_trading_day} is None.")
        return None

    indicator = Indicator(
        stock_id=stock.id,
        indicator_type=indicator_type,
        value=indicator_value,
        latest_trading_day=latest_trading_day,
    )

    try:
        db.session.add(indicator)
        db.session.commit()
        print(
            f"Indicator {indicator_type} added to database for stock ID {stock.id}."
        )
        return indicator
    except Exception as e:
        print(f"Error while adding indicator to database: {e}")
        db.session.rollback()
        return None

def add_indicator_to_all_stocks(indicator_type: str) -> bool:
    try:
        stocks = Stock.query.all()

        if not stocks:
            print("No stocks found in the database.")
            return False

        # Iterate through each stock and add the indicator
        for stock in stocks:
            # Attempt to add the indicator to the current stock
            if not add_indicator_to_stock(stock, indicator_type):
                # If adding the indicator fails, log the error
                print(f"Failed to add indicator {indicator_type} to stock {stock.symbol}.")
                return False

        # If all indicators were successfully added, return True
        return True

    except Exception as e:
        # Catch any unexpected exceptions and log the error
        print(f"An error occurred while adding indicator {indicator_type} to all stocks: {e}")
        return False


def initialize_sample_data() -> bool:

    symbols = ["NVDA", "AMD"]
    indicators = ["PERatio","PEGRatio", "200DayMovingAverage"]

    for symbol in symbols:
        stock  = add_stock_to_database(symbol)
        if stock is None:
            return False

        for indicator in indicators:
            indicator_return = add_indicator_to_stock(stock, indicator)
