
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from flask_login import login_user
from app.models.user import db, User
from flask_dance.contrib.google import google
@auth_bp.route("/login/google")
def login_google():
    if not google.authorized:
        # Redirect to Google OAuth
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for("auth.login"))
    info = resp.json()
    email = info.get("email")
    full_name = info.get("name") or email
    if not email:
        flash("Google account missing email.", "error")
        return redirect(url_for("auth.login"))

    # Find or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(full_name=full_name, email=email, password_hash="google-oauth")
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Could not create user from Google account.", "error")
            return redirect(url_for("auth.login"))

    login_user(user)
    flash("Logged in with Google!", "success")
    return redirect(url_for("public.home"))

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Placeholder login logic
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""

        if not email or not password:
            flash("Please enter email and password.", "error")
            return redirect(url_for("auth.login"))

        flash("Login POST received (backend not implemented yet).", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        # Validate required fields
        if not full_name or not email or not password:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        # Check if user already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered.", "error")
            return redirect(url_for("auth.register"))

        # Hash password and create user
        pw_hash = generate_password_hash(password)
        user = User(full_name=full_name, email=email, password_hash=pw_hash)
        db.session.add(user)
        try:
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("Registration failed. Please try again.", "error")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html")