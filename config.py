"""Database config."""
from os import getenv, path,curdir

from dotenv.main import load_dotenv
# import sentry_sdk

# Load variables from .env from the base folder of the project

load_dotenv(".env")


# Database connection variables
DATABASE_USERNAME = getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")
DATABASE_HOST = getenv("DATABASE_HOST")
DATABASE_NAME = getenv("DATABASE_NAME")


SERPER_TOKEN = getenv("SERPER_TOKEN")

SERPER_ON = getenv("SERPER_ON")

SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server"