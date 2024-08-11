from config import (
    app,
    setup_db,
    Stock,
    Indicator,
    add_indicator_to_all_stocks,
    db,
    add_stock_to_database,
    add_indicator_to_stock,
)
from flask import render_template, jsonify, request

setup_db()


def load_stock_data():
    stocks = Stock.query.all()
    indicator_header = set()
    for stock in stocks:
        for indicator in stock.indicators:
            indicator_header.add(indicator.indicator_type)
    indicator_header = sorted(indicator_header)

    return stocks, indicator_header


@app.route("/")
def index():
    stocks, indicator_header = load_stock_data()

    return render_template(
        "index.html", stocks=stocks, indicator_header=indicator_header
    )


# Get all stocks - return only the stock symbols
@app.route("/stocks", methods=["GET"])
def get_stocks():
    stocks = Stock.query.all()
    stock_list = [stock.symbol for stock in stocks]
    return jsonify(stock_list)


# Get all indicators
@app.route("/indicators", methods=["GET"])
def get_indicators():
    indicators = Indicator.query.all()
    # Use a set to remove duplicates
    indicator_set = {indicator.indicator_type for indicator in indicators}
    # Convert the set back to a list
    indicator_list = list(indicator_set)
    return jsonify(indicator_list)


# Get all information and indicators for a specific stock by symbol
@app.route("/stocks/<symbol>", methods=["GET"])
def get_stock_by_symbol(symbol):
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        return jsonify({"error": "Stock not found"}), 404

    stock_info = {
        "id": stock.id,
        "symbol": stock.symbol,
        "current_price": stock.current_price,
    }

    # Add each indicator to the stock_info dictionary
    for indicator in stock.indicators:
        stock_info[indicator.indicator_type] = indicator.value

    return jsonify(stock_info)


@app.route("/indicators", methods=["POST"])
def add_indicator():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()

        # Check if 'indicator_type' is in the request data
        if not data or "indicator_type" not in data:
            return jsonify({"error": "Indicator type is required."}), 400

        indicator_type = data["indicator_type"]

        # Add the indicator to all stocks
        success = add_indicator_to_all_stocks(indicator_type)

        if success:
            return (
                jsonify(
                    {
                        "message": f"Indicator '{indicator_type}' added to all stocks successfully."
                    }
                ),
                201,
            )
        else:
            return (
                jsonify(
                    {
                        "error": f"Failed to add indicator '{indicator_type}' to all stocks."
                    }
                ),
                500,
            )

    except Exception as e:
        # Catch unexpected exceptions and return a generic error message
        print(f"An error occurred: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


# Delete an indicator from all stocks
@app.route("/indicators/<indicator_type>", methods=["DELETE"])
def delete_indicator(indicator_type):
    try:
        # Query all indicators of the given type
        indicators = Indicator.query.filter_by(indicator_type=indicator_type).all()

        if not indicators:
            return jsonify({"error": f"Indicator '{indicator_type}' not found."}), 404

        # Delete each indicator from the database
        for indicator in indicators:
            db.session.delete(indicator)

        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Indicator '{indicator_type}' deleted from all stocks successfully."
                }
            ),
            200,
        )

    except Exception as e:
        # Catch unexpected exceptions and return a generic error message
        print(f"An error occurred: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


# Add a new stock by symbol (using JSON data)
@app.route("/stocks", methods=["POST"])
def add_stock():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()

        # Check if 'symbol' is in the request data
        if not data or "symbol" not in data:
            return jsonify({"error": "Stock symbol is required."}), 400

        symbol = data["symbol"]

        # Check if the stock already exists
        existing_stock = Stock.query.filter_by(symbol=symbol).first()
        if existing_stock:
            return jsonify({"error": f"Stock '{symbol}' already exists."}), 400

        # Add the new stock (assuming add_stock_to_database is a function that adds the stock)
        stock = add_stock_to_database(symbol)
        # Use a set to remove duplicates
        indicator_set = {
            indicator.indicator_type for indicator in Indicator.query.all()
        }

        for indicator in indicator_set:
            add_indicator_to_stock(stock, indicator)

        return (
            jsonify(
                {
                    "message": f"Stock '{symbol}' added successfully.",
                    "stock": stock.symbol,
                }
            ),
            201,
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


# Delete a stock by symbol
@app.route("/stocks/<symbol>", methods=["DELETE"])
def delete_stock(symbol):
    try:
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({"error": f"Stock '{symbol}' not found."}), 404

        Indicator.query.filter_by(stock_id=stock.id).delete()
        db.session.delete(stock)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Stock '{symbol}' and all associated indicators deleted successfully."
                }
            ),
            200,
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


# Partially update a stock's information
@app.route("/stocks/<symbol>", methods=["PATCH"])
def update_stock(symbol):
    try:
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return jsonify({"error": f"Stock '{symbol}' not found."}), 404

        data = request.get_json()
        if "current_price" in data:
            stock.current_price = data["current_price"]

        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Stock '{symbol}' updated successfully.",
                    "stock": stock.symbol,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


if __name__ == "__main__":
    app.run()
