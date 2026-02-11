from flask import Flask
from app.extensions import db
from app.api.prices import prices_bp

# main part of app -> register blueprints for the whole app etc...
# creates the app to then be triggered by run.py
def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)

    app.register_blueprint(prices_bp, url_prefix="/api")

    return app