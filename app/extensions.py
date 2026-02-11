from flask_sqlalchemy import SQLAlchemy

# initialize session, but not yet hooked up to postgres untill init.py is loaded and sqlalchemy sees the config url
db = SQLAlchemy()