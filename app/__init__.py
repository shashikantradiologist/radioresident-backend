from flask import Flask
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

    # ---- Google OAuth (Flask-Dance) ----
    client_id = app.config.get("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = app.config.get("GOOGLE_OAUTH_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Missing GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET in environment")

    google_bp = make_google_blueprint(
        client_id=client_id,
        client_secret=client_secret,
        scope=["profile", "email"],
        # after OAuth success, redirect to YOUR route that creates/logs-in user
        redirect_to="auth.google_callback",
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    # blueprints
    from app.routes.auth import auth_bp
    from app.routes.public import public_bp
    from app.routes.protected import protected_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(protected_bp)

    return app