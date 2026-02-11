# not needed right now, eventually will have symbols table to track metadata for each symbol
# will let me query symbols without scanning entire market_candles table


# from app.extensions import db

# class Symbol(db.Model):
#     __tablename__ = "symbols"

#     id = db.Column(db.Integer, primary_key=True)
#     symbol = db.Column(db.String, unique=True, nullable=False)  # BTC-USD, ETH-USD
#     name = db.Column(db.String)  # Optional friendly name
#     active = db.Column(db.Boolean, default=True)

#     def __repr__(self):
#         return f"<Symbol {self.symbol}>"