import os
from sqlalchemy.engine.url import URL

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
db_uri = {
    'drivername': 'postgres',
    'username': 'horizon',
    'password': '0105415595',
    'host': 'localhost',
    'port': 5432,
    'database': 'fyyur'
}

# TODO IMPLEMENT DATABASE URL (Done!)
SQLALCHEMY_DATABASE_URI = URL(**db_uri)

# Modification tracking
SQLALCHEMY_TRACK_MODIFICATIONS = False