from app.models.candle import Candle

def get_candles(symbol, interval):
    
    # SELECT *
    # FROM candle
    # WHERE symbol = :symbol
    # AND interval = :interval
    # ORDER BY timestamp DESC
    # LIMIT 500;

    candles = (
        Candle.query # this does not query a table, rather the table is created already. this is sqlAlchaemy interface to query the candle table which is defined inside candle model.
        .filter_by(symbol=symbol, interval=interval)
        .order_by(Candle.timestamp.desc())
        .limit(500) # pulls last 500 candles
        .all()
    )

    
    # convert to list of dicts for JSON
    return [
        {
            "timestamp": c.timestamp.isoformat(),
            "open": float(c.open),
            "high": float(c.high),
            "low": float(c.low),
            "close": float(c.close),
            "volume": float(c.volume),
        }
        for c in candles # returns json object for every candle in the specified window to price api
    ]