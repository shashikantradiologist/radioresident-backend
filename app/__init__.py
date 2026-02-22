from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes.auth import auth_bp
    from app.routes.public import public_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)

    return app