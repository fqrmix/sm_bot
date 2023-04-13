import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """
        Config class for PostgreSQL
    """
    HOST = os.environ.get("POSTGRESQL_HOST")
    USER = os.environ.get("POSTGRESQL_USER")
    PASSWORD = os.environ.get("POSTGRESQL_PASSWORD")
    DATABASE_NAME = os.environ.get("POSTGRESQL_DATABASE")
