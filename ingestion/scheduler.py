from app import create_app
from app.extensions import db
from ingestion.fetch_candles import fetch_candles

# each process needs its own flask application instance
app = create_app()

# scheduler is its own process. hence the create app. need to ingest first, then hit flask endpoint for api/prices
# api is also its own flask app
#Coinbase API → fetch_candles() → Candle objects → db.session.add_all() → Postgres
def ingest(symbol="BTC-USD", interval="1m"): # right now hardcoded symbol and interval
    """
    Fetch candles and persist them to Postgres.
    Idempotency is enforced by the DB unique constraint.
    """
    with app.app_context():
        candles = fetch_candles(symbol, interval)

        try:
            db.session.add_all(candles) # adds all candles to the db, dupes are ignored due to candle model constraint with unique.
            db.session.commit()
            print(f"Ingested {len(candles)} candles for {symbol} {interval}")
        except Exception:
            # Duplicate rows are ignored via UNIQUE(symbol, interval, timestamp)
            db.session.rollback() # undo if error

if __name__ == "__main__":
    ingest()