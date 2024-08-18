from flask import render_template, jsonify, request
from authentication.auth import AuthError, requires_auth
from config import (
    Stock,
    Indicator,
    add_indicator_to_all_stocks,
    db,
    add_stock_to_database,
    add_indicator_to_stock,
)

def load_stock_data():
    stocks = Stock.query.all()
    indicator_header = set()
    for stock in stocks:
        for indicator in stock.indicators:
            indicator_header.add(indicator.indicator_type)
    indicator_header = sorted(indicator_header)

    return stocks, indicator_header


def index():
    stocks, indicator_header = load_stock_data()
    return render_template(
        "index.html", stocks=stocks, indicator_header=indicator_header
    )


def get_stocks():
    stocks = Stock.query.all()
    stock_list = [stock.symbol for stock in stocks]
    return jsonify(stock_list)


def get_indicators():
    indicators = Indicator.query.all()
    indicator_set = {indicator.indicator_type for indicator in indicators}
    indicator_list = list(indicator_set)
    return jsonify(indicator_list)


def get_stock_by_symbol(symbol):
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        return jsonify({"error": "Stock not found"}), 404

    stock_info = {
        "id": stock.id,
        "symbol": stock.symbol,
        "current_price": stock.current_price,
    }

    for indicator in stock.indicators:
        stock_info[indicator.indicator_type] = indicator.value

    return jsonify(stock_info)


def add_indicator():
    try:
        data = request.get_json()
        if not data or "indicator_type" not in data:
            return jsonify({"error": "Indicator type is required."}), 400

        indicator_type = data["indicator_type"]
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
        print(f"An error occurred: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


def delete_indicator(indicator_type):
    try:
        indicators = Indicator.query.filter_by(indicator_type=indicator_type).all()

        if not indicators:
            return jsonify({"error": f"Indicator '{indicator_type}' not found."}), 404

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
        print(f"An error occurred: {e}")
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


def add_stock():
    try:
        data = request.get_json()
        if not data or "symbol" not in data:
            return jsonify({"error": "Stock symbol is required."}), 400

        symbol = data["symbol"]
        existing_stock = Stock.query.filter_by(symbol=symbol).first()
        if existing_stock:
            return jsonify({"error": f"Stock '{symbol}' already exists."}), 400

        stock = add_stock_to_database(symbol)
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

# for unit test without authentication
def register_routes(app):
    app.route("/")(index)
    app.route("/stocks", methods=["GET"])(get_stocks)
    app.route("/indicators", methods=["GET"])(get_indicators)
    app.route("/stocks/<symbol>", methods=["GET"])(get_stock_by_symbol)
    app.route("/indicators", methods=["POST"])(add_indicator)
    app.route("/stocks", methods=["POST"])(add_stock)
    app.route("/stocks/<symbol>", methods=["PATCH"])(update_stock)
    app.route("/indicators/<indicator_type>", methods=["DELETE"])(delete_indicator)
    app.route("/stocks/<symbol>", methods=["DELETE"])(delete_stock)

def register_routes_auth(app):
    app.route("/", endpoint='index')(index)
    app.route("/stocks", methods=["GET"], endpoint='get_stocks')(get_stocks)
    app.route("/indicators", methods=["GET"], endpoint='get_indicators')(get_indicators)

    app.route("/stocks/<symbol>", methods=["GET"], endpoint='get_stock_by_symbol')(
        requires_auth("get:stocks")(get_stock_by_symbol)
    )
    app.route("/indicators", methods=["POST"], endpoint='add_indicator')(
        requires_auth("post:indicators")(add_indicator)
    )
    app.route("/stocks", methods=["POST"], endpoint='add_stock')(
        requires_auth("post:stocks")(add_stock)
    )
    app.route("/stocks/<symbol>", methods=["PATCH"], endpoint='update_stock')(
        requires_auth("patch:stocks")(update_stock)
    )
    app.route("/indicators/<indicator_type>", methods=["DELETE"], endpoint='delete_indicator')(
        requires_auth("delete:indicators")(delete_indicator)
    )
    app.route("/stocks/<symbol>", methods=["DELETE"], endpoint='delete_stock')(
        requires_auth("delete:stocks")(delete_stock)
    )
