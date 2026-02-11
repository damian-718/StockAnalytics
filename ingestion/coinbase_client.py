import requests

COINBASE_API = "https://api.exchange.coinbase.com/products/{symbol}/candles"

def get_candles_raw(symbol: str, granularity: int):
    """
    Fetch raw candle data from Coinbase.

    Coinbase returns:
    [ time, low, high, open, close, volume ]
    """
    url = COINBASE_API.format(symbol=symbol)
    params = {"granularity": granularity}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json() # the raw candles are just numbers in row/col format like: row = [1677628800, 98.5, 101.2, 99.1, 100.3, 1250]. fetch candles labels it based on the model.