import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Para quickstart: SQLite; para seed massivo, use Postgres do compose
    "sqlite:///./social.db"
)

API_PREFIX = "/v1"
PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100
