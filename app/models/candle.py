from app.extensions import db

# maps python object to postgres rows. the candle is a row in a table of candles.
# model is for storing data to db, this is a SQLAlchemy model
class Candle(db.Model): # this class is both a schema/model and also a mapping to the table to query.
    __tablename__ = "market_candles" # table to query

    # attributes that make up a candle, will be columns in postgres
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String, nullable=False)
    interval = db.Column(db.String, nullable=False)  # e.g., "1m", "5m"
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    open = db.Column(db.Numeric)
    high = db.Column(db.Numeric)
    low = db.Column(db.Numeric)
    close = db.Column(db.Numeric)
    volume = db.Column(db.Numeric)

    # uniqueconstraints prevents dupes (idempotency), UNIQUE(symbol, interval, timestamp) = natural idempotency key. why use interval? a time stamp has many intervals, 1m, 5m, etc...
    # typically for idempotency we create a uuid, but in this case symbol, interval, timestamp act as a unique key
    # so this will tell postgres, a combo of these column values cannot exist twice and wont do anything on repeated requests.
    __table_args__ = (db.UniqueConstraint("symbol", "interval", "timestamp", name="_symbol_interval_ts_uc"),)
    # this line runs just once when the table is created. now postgres knows how to check for uniquenes
    # postgres internally creates an index for that combination of columns, so when a row is inserted it can search for it