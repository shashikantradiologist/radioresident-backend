print("Starting RadioResident...")

from app import create_app

app = create_app()

print("Flask app created successfully")

if __name__ == "__main__":
    print("Running Flask server")
    app.run(debug=True)
