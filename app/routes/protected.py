# app/routes/protected.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.models.quiz import QuizAttempt
from app.models.user import User
from app.models.user import db

protected_bp = Blueprint("protected", __name__)

@protected_bp.get("/dashboard")
@login_required
def dashboard():
    # Only count completed attempts
    base_q = QuizAttempt.query.filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.finished_at.isnot(None),
    )

    last_attempt = base_q.order_by(QuizAttempt.finished_at.desc()).first()
    last_score = last_attempt.score if last_attempt else None
    best_score = base_q.with_entities(func.max(QuizAttempt.score)).scalar() or None
    attempts_total = base_q.count()

    # streak placeholder for now (wire later)
    streak_days = 0

    # rank (simple MVP): last 30 days cumulative score
    since = datetime.utcnow() - timedelta(days=30)
    leaderboard_rows = (
        db.session.query(
            QuizAttempt.user_id.label("user_id"),
            func.sum(QuizAttempt.score).label("total_score"),
            func.avg(QuizAttempt.score).label("avg_score"),
            func.count(QuizAttempt.id).label("attempts"),
        )
        .filter(QuizAttempt.finished_at.isnot(None), QuizAttempt.finished_at >= since)
        .group_by(QuizAttempt.user_id)
        .order_by(desc("total_score"), desc("avg_score"), func.count(QuizAttempt.id))
        .all()
    )

    rank = None
    top3 = []
    for i, r in enumerate(leaderboard_rows, start=1):
        if r.user_id == current_user.id:
            rank = i
        if i <= 3:
            u = User.query.get(r.user_id)
            top3.append({
                "rank": i,
                "name": (u.full_name or u.email) if u else f"User {r.user_id}",
                "total_score": int(r.total_score or 0),
            })

    return render_template(
        "protected/dashboard.html",
        last_score=last_score,
        best_score=best_score,
        attempts_total=attempts_total,
        streak_days=streak_days,
        leaderboard_rank=rank,
        top3=top3,
    )

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