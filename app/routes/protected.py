from flask import Blueprint, render_template
from flask_login import login_required

protected_bp = Blueprint("protected", __name__)

@protected_bp.get("/dashboard")
@login_required
def dashboard():
    return render_template("protected/dashboard.html")

@protected_bp.get("/courses")
@login_required
def courses():
    # Later: role-based gating (premium)
    return render_template("protected/courses.html")

@protected_bp.get("/notes")
@login_required
def notes():
    # Later: role-based gating (premium)
    return render_template("protected/notes.html")

@protected_bp.get("/leaderboard")
@login_required
def leaderboard():
    return render_template("protected/leaderboard.html")