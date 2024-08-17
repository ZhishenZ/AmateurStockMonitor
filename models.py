from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    indicators = db.relationship('Indicator', backref='stock', lazy=True)

class Indicator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    indicator_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    latest_trading_day = db.Column(db.String(50), nullable=False)
