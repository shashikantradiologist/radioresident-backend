# wsgi.py
import os

# Load environment variables early (local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from app import create_app

app = create_app()

# ---- Auto-run migrations on startup (Render free plan friendly) ----
# This prevents: "no such table: user"
# It is safe to run every boot; Alembic will no-op if already up-to-date.
if os.environ.get("AUTO_MIGRATE", "1") == "1":
    try:
        from flask_migrate import upgrade

        with app.app_context():
            upgrade()
            print("✅ DB migration applied (upgrade).")
    except Exception as e:
        # Don't crash the app if migration fails; log it so you can see in Render logs
        print("⚠️ Migration skipped/failed:", repr(e))