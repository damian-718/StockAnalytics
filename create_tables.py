# run just once before starting app to create the tables ingestion will populate

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()  # this creates all tables defined in models. the models are part of SQLAlchemy.
    print("Tables created successfully!")