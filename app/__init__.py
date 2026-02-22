from flask import Flask
from config import Config


from flask_login import LoginManager
from app.models.user import db, User
from flask_dance.contrib.google import make_google_blueprint, google

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Google OAuth config (replace with real client ID/secret in production)
    app.config["GOOGLE_OAUTH_CLIENT_ID"] = app.config.get("GOOGLE_OAUTH_CLIENT_ID", "your-google-client-id")
    app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = app.config.get("GOOGLE_OAUTH_CLIENT_SECRET", "your-google-client-secret")

    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Google OAuth blueprint
    google_bp = make_google_blueprint(
        client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
        client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
        scope=["profile", "email"],
        redirect_url="/login/google/authorized"
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.public import public_bp
    from app.routes.protected import protected_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(protected_bp)

    return app