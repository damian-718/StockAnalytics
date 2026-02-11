from flask import Blueprint, request, jsonify
from app.services.price_service import get_candles

prices_bp = Blueprint("prices", __name__)
# Client → Flask API → price_service.get_candles() → Candle.query(...) → Python objects → jsonify() → Client
@prices_bp.route("/prices")
def prices():
    symbol = request.args.get("symbol", "BTC-USD")
    interval = request.args.get("interval", "1m")
    data = get_candles(symbol, interval)
    return jsonify(data)