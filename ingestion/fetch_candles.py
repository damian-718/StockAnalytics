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
    for row in raw_candles:
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