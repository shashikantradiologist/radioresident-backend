from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
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

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    remember = bool(request.form.get("remember"))

    user = User.query.filter_by(email=email).first()

    # Invalid if:
    # - no user
    # - Google-only user (no password_hash)
    # - wrong password
    if (
        not user
        or not getattr(user, "password_hash", None)
        or not check_password_hash(user.password_hash, password)
    ):
        flash("Invalid email or password", "error")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)
    flash("Logged in!", "success")
    return redirect(url_for("public.home"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("public.home"))


# -------------------------
# Google OAuth Finalize Login (Flask-Dance)
# -------------------------
@auth_bp.route("/auth/after-login")
def after_login():
    # If token not present, start Google login flow
    if not google.authorized:
        return redirect(url_for("google.login"))

    # Fetch Google profile
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        current_app.logger.warning(
            "Google userinfo failed: status=%s body=%s",
            resp.status_code,
            resp.text,
        )
        flash("Failed to fetch Google profile.", "error")
        return redirect(url_for("auth.login"))

    info = resp.json()
    email = (info.get("email") or "").strip().lower()
    full_name = (info.get("name") or "").strip() or email
    google_id = info.get("id") or info.get("sub")  # endpoint-dependent
    avatar_url = info.get("picture")

    if not email:
        flash("Google account missing email.", "error")
        return redirect(url_for("auth.login"))

    try:
        # 1) Prefer Google subject ID if model supports it
        user = None
        if google_id and hasattr(User, "google_sub"):
            user = User.query.filter_by(google_sub=google_id).first()

        # 2) Fallback to email
        if not user:
            user = User.query.filter_by(email=email).first()

        # 3) Create if not exists
        is_new_user = user is None
        if is_new_user:
            # Only pass fields that definitely exist in constructor
            user = User(email=email)
            if hasattr(user, "full_name"):
                user.full_name = full_name

        # 4) Keep user profile updated safely
        if hasattr(user, "full_name") and full_name:
            user.full_name = full_name

        if hasattr(user, "google_sub") and google_id:
            user.google_sub = google_id

        if hasattr(user, "avatar_url") and avatar_url:
            user.avatar_url = avatar_url

        if hasattr(user, "auth_provider"):
            user.auth_provider = "google"

        # 5) Persist once
        db.session.add(user)
        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Could not create/update user from Google account.")
        flash("Could not login with Google. Please try again.", "error")
        return redirect(url_for("auth.login"))

    # 6) Login after successful commit
    login_user(user)
    flash("Logged in with Google!", "success")
    return redirect(url_for("public.home"))