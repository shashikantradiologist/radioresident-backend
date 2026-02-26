from flask import Flask

# Load environment variables early
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from config import Config
from flask_login import LoginManager
from app.models.user import db, User
from flask_dance.contrib.google import make_google_blueprint
from flask_migrate import Migrate
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Dev-only safety net (optional)
    # Better: fix scopes (we are doing that) and then you can remove this later.
    app.config.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", True)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
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
            scope=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            # Do NOT redirect to the callback. Let Flask-Dance handle /authorized.
            redirect_to="auth.after_login",  # (optional: create this route)
        )
        app.register_blueprint(google_bp, url_prefix="/login")
    else:
        app.logger.warning("Google OAuth disabled (missing GOOGLE_OAUTH_CLIENT_ID/SECRET).")

    # blueprints (adjust imports to match your actual folders)
    from app.routes.auth import auth_bp
    from app.routes.public import public_bp
    from app.routes.protected import protected_bp
    from app.routes.quiz import quiz_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(protected_bp)
    app.register_blueprint(quiz_bp)

    return app