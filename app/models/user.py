from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# db will be initialized in app/__init__.py
db = SQLAlchemy()

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	full_name = db.Column(db.String(120), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)
	# Add more fields as needed

	def __repr__(self):
		return f"<User {self.email}>"
