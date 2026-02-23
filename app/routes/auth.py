from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from app.models.user import db, User
from flask_dance.contrib.google import google

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/google/callback")
def google_callback():
    if not google.authorized:
        flash("Google authorization required.", "error")
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        current_app.logger.warning("Google userinfo failed: %s %s", resp.status_code, resp.text)
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for("auth.login"))

    info = resp.json()
    email = (info.get("email") or "").strip().lower()
    full_name = (info.get("name") or "").strip() or email
    google_id = info.get("id") or info.get("sub")  # depending on endpoint

    if not email:
        flash("Google account missing email.", "error")
        return redirect(url_for("auth.login"))

    try:
        # Prefer google_id match if your model supports it
        user = None
        if google_id and hasattr(User, "google_sub"):
            user = User.query.filter_by(google_sub=google_id).first()

        if not user:
            user = User.query.filter_by(email=email).first()

        if not user:
            # For google users, password_hash should be NULL ideally
            user = User(full_name=full_name, email=email)
            if hasattr(user, "google_sub") and google_id:
                user.google_sub = google_id
            if hasattr(user, "auth_provider"):
                user.auth_provider = "google"
            db.session.add(user)
        else:
            # keep profile updated
            user.full_name = full_name
            if hasattr(user, "google_sub") and google_id and not user.google_sub:
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