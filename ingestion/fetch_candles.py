from datetime import datetime, timezone
from app.models.candle import Candle
from ingestion.coinbase_client import get_candles_raw

INTERVAL_MAP = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
}

def fetch_candles(symbol: str, interval: str):
    """
    Fetch candles from Coinbase and convert them into Candle models.
    """
    granularity = INTERVAL_MAP[interval]
    raw_candles = get_candles_raw(symbol, granularity)

    candles = []
    for row in raw_candles: # the raw candles are just numbers in row/col format like: row = [1677628800, 98.5, 101.2, 99.1, 100.3, 1250]. this will assign labels for each column based on the model. each append is a candle object which is converted to a database row by sqlalchemy.
        candles.append( # appends rows to the table defined inside of candle. sqlalchemy provides this.
            Candle(
                symbol=symbol,
                interval=interval,
                timestamp=datetime.fromtimestamp(row[0], tz=timezone.utc),
                low=row[1],
                high=row[2],
                open=row[3],
                close=row[4],
                volume=row[5],
            )
        )

    return candles