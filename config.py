import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-123")

    db_url = os.environ.get("DATABASE_URL")

    if db_url:
        # Render sometimes uses postgres://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        # If it already starts with postgresql://, still force psycopg v3
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # local fallback
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "radioresident.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")