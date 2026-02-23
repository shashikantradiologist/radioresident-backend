from flask import Flask
# Load environment variables from a .env file if python-dotenv is available.
# This must run before importing Config so os.environ values are populated.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from config import Config

from flask_login import LoginManager
from app.models.user import db, User
from flask_dance.contrib.google import make_google_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # init extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Google OAuth (Flask-Dance) ---
    client_id = app.config.get("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = app.config.get("GOOGLE_OAUTH_CLIENT_SECRET")

    if client_id and client_secret:
        google_bp = make_google_blueprint(
            client_id=client_id,
            client_secret=client_secret,
            scope=["profile", "email"],
            redirect_to="auth.google_callback",
        )
        app.register_blueprint(google_bp, url_prefix="/login")
    else:
        app.logger.warning(
            "Google OAuth disabled (missing GOOGLE_OAUTH_CLIENT_ID/SECRET)."
        )

    # blueprints
    from app.routes.auth import auth_bp
    from app.routes.public import public_bp
    from app.routes.protected import protected_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(protected_bp)

    return app