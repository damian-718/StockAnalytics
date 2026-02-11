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

    return response.json()