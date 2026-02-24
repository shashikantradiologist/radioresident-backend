from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import check_password_hash
from flask_login import login_user
from flask_dance.contrib.google import google

from app.models.user import db, User

auth_bp = Blueprint("auth", __name__)

# -------------------------
# Email/Password Login
# -------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    # POST
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    remember = bool(request.form.get("remember"))

    user = User.query.filter_by(email=email).first()

    # If user doesn't exist OR is a Google-only user (password_hash is None) OR wrong password
    if (not user) or (not getattr(user, "password_hash", None)) or (not check_password_hash(user.password_hash, password)):
        flash("Invalid email or password", "error")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)
    flash("Logged in!", "success")
    return redirect(url_for("public.home"))


# -------------------------
# Google OAuth Finalize Login (Flask-Dance)
# -------------------------
@auth_bp.route("/auth/after-login")
def after_login():
    # If token not present, start Google login
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        current_app.logger.warning("Google userinfo failed: %s %s", resp.status_code, resp.text)
        flash("Failed to fetch Google profile.", "error")
        return redirect(url_for("auth.login"))

    info = resp.json()
    email = (info.get("email") or "").strip().lower()
    full_name = (info.get("name") or "").strip() or email
    google_id = info.get("id") or info.get("sub")  # depends on endpoint

    if not email:
        flash("Google account missing email.", "error")
        return redirect(url_for("auth.login"))

    try:
        user = None

        # Prefer google_sub match if your model supports it
        if google_id and hasattr(User, "google_sub"):
            user = User.query.filter_by(google_sub=google_id).first()

        # Fallback to email
        if not user:
            user = User.query.filter_by(email=email).first()

        if not user:
            # Create user (Google-only user typically has password_hash = NULL)
            user = User(full_name=full_name, email=email)

            if hasattr(user, "google_sub") and google_id:
                user.google_sub = google_id

            if hasattr(user, "auth_provider"):
                user.auth_provider = "google"

            db.session.add(user)
        else:
            # Keep profile updated
            if hasattr(user, "full_name"):
                user.full_name = full_name

            if hasattr(user, "google_sub") and google_id and not getattr(user, "google_sub", None):
                user.google_sub = google_id

            if hasattr(user, "auth_provider") and not getattr(user, "auth_provider", None):
                user.auth_provider = "google"

        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Could not create/update user from Google account.")
        flash("Could not login with Google. Please try again.", "error")
        return redirect(url_for("auth.login"))

    login_user(user)
    flash("Logged in with Google!", "success")
    return redirect(url_for("public.home"))