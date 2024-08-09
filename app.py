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


if __name__ == "__main__":
    app.run()
