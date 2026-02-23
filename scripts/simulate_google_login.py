import os
import sys
from unittest.mock import patch, MagicMock

# Ensure project root is on sys.path so `app` package can be imported when
# running this script directly from the scripts/ folder.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.user import db, User

app = create_app()
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

with app.app_context():
    db.create_all()

    with app.test_client() as client:
        # Avoid importing LocalProxy directly via patch() because that triggers
        # attribute access; instead replace the attribute on the module.
        import importlib
        gd = importlib.import_module('flask_dance.contrib.google')
        mock_google = MagicMock()
        mock_google.authorized = True
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            'email': 'simulated@example.com',
            'name': 'Simulated User'
        }
        mock_google.get.return_value = mock_resp
        # Replace the `google` symbol in the auth routes module so the
        # callback uses our mock instead of the LocalProxy (which requires
        # a flask request context).
        import app.routes.auth as auth_mod
        setattr(auth_mod, 'google', mock_google)

        resp = client.get('/auth/google/callback', follow_redirects=True)
        print('Status code:', resp.status_code)
        data = resp.get_data(as_text=True)
        # Print a short snippet of the response
        print('Response snippet:')
        print(data[:1000])

        user = User.query.filter_by(email='simulated@example.com').first()
        print('User created:', bool(user))
