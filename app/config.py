from dotenv import load_dotenv
import os

load_dotenv()

# imported when app is created
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False