import os

# Set SECRET_KEY from .env file. If not set, default SECRET_KEY from flaskr/__init__ will be used. Using the default
#  SECRET_KEY is NOT suitable for a production environment
if os.environ.get('SECRET_KEY'):
    SECRET_KEY = os.environ['SECRET_KEY']

# STATIC_DATA_PATH is set relative to the root of the project. If not set in .env, it will be set at ./static_data
STATIC_DATA_PATH = os.environ.get('STATIC_DATA_PATH') or 'static_data'

# Define employees api url in EMPLOYEES_API_URL
EMPLOYEES_API_URL = os.environ.get('EMPLOYEES_API_URL')
