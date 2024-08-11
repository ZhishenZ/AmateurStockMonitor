from config import app, setup_db, Stock, Indicator
from flask import render_template

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
    indicator_list = [indicator.indicator_type for indicator in indicators]
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

if __name__ == "__main__":
    app.run()
