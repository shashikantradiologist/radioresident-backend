from app.models.user import db
from dotenv import load_dotenv
load_dotenv()
print("Starting RadioResident...")

from app import create_app

app = create_app()
with app.app_context():
    db.create_all()

print("Flask app created successfully")

if __name__ == "__main__":
    print("Running Flask server")
    app.run(debug=True)
