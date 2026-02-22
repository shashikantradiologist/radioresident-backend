from flask import Blueprint, render_template, request, redirect, url_for, flash

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
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        if not full_name or not email or not password:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        flash("Registration POST received (backend not implemented yet).", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")