import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-123")

    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Production: Render Postgres via DATABASE_URL
    # Local fallback: SQLite inside instance/
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///instance/radioresident.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")