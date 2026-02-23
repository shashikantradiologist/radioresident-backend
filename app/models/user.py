from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # Local identity
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(255), nullable=True)

    # Google identity
    google_sub = db.Column(db.String(255), unique=True, nullable=True, index=True)
    avatar_url = db.Column(db.String(512), nullable=True)

    # Authorization / roles
    role = db.Column(db.String(50), default="resident")  # resident/faculty/admin

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)