from flask import Flask
from app.extensions import db
from app.api.prices import prices_bp

# main part of app -> register blueprints for the whole app etc...
# creates the app to then be triggered by run.py
def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config") # get the config which has database url for SQLAlchemy

    # connects to flask app and tells sqlalchemy that the database url is in this apps config.
    db.init_app(app) # attaches SQLAlchemy database instance to this Flask app. Models can now query the database (all the db.session queries, etc..)

    app.register_blueprint(prices_bp, url_prefix="/api")

    return app