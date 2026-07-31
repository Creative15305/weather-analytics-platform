import os
from dotenv import load_dotenv

# Loads variables from a local .env file (never commit .env to GitHub)
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

API_KEY = os.getenv("API_KEY")
