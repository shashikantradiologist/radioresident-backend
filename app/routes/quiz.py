# app/routes/quiz.py
import random
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import login_required, current_user

from app.models.user import db
from app.models.quiz import Quiz, Question, QuizAttempt, AttemptAnswer

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@quiz_bp.post("/start")
@login_required
def start():
    # For MVP: start the first active quiz
    quiz = Quiz.query.filter_by(is_active=True).order_by(Quiz.id.asc()).first()
    if not quiz:
        flash("No active quiz available yet.", "error")
        return redirect(url_for("protected.dashboard"))

    questions = Question.query.filter_by(quiz_id=quiz.id, is_active=True).all()
    if len(questions) < 10:
        flash("Not enough questions (need 10). Seed the quiz first.", "error")
        return redirect(url_for("protected.dashboard"))

    chosen = random.sample(questions, 10)
    order = [q.id for q in chosen]

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        total=10,
        score=0,
        started_at=datetime.utcnow(),
    )
    db.session.add(attempt)
    db.session.commit()

    session["quiz_attempt_id"] = attempt.id
    session["quiz_order"] = order
    session["quiz_index"] = 0

    return redirect(url_for("quiz.question"))


@quiz_bp.get("/question")
@login_required
def question():
    attempt_id = session.get("quiz_attempt_id")
    order = session.get("quiz_order")
    idx = session.get("quiz_index")

    if not attempt_id or not order or idx is None:
        flash("Start a quiz first.", "error")
        return redirect(url_for("protected.dashboard"))

    if idx >= len(order):
        return redirect(url_for("quiz.results"))

    q = Question.query.get_or_404(order[idx])

    return render_template(
        "quiz/question.html",
        q=q,
        idx=idx + 1,
        total=len(order),
    )


@quiz_bp.post("/answer")
@login_required
def answer():
    attempt_id = session.get("quiz_attempt_id")
    order = session.get("quiz_order")
    idx = session.get("quiz_index")

    if not attempt_id or not order or idx is None:
        flash("No active quiz.", "error")
        return redirect(url_for("protected.dashboard"))

    if idx >= len(order):
        return redirect(url_for("quiz.results"))

    selected = request.form.get("selected")
    if selected not in {"A", "B", "C", "D"}:
        flash("Please select an option.", "error")
        return redirect(url_for("quiz.question"))

    attempt = QuizAttempt.query.get_or_404(attempt_id)
    question_id = order[idx]
    q = Question.query.get_or_404(question_id)

    # prevent double submission for same question
    existing = AttemptAnswer.query.filter_by(attempt_id=attempt.id, question_id=q.id).first()
    if not existing:
        is_correct = (selected == q.correct)

        db.session.add(AttemptAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected=selected,
            is_correct=is_correct,
        ))

        if is_correct:
            attempt.score += 1

        db.session.commit()

    session["quiz_index"] = idx + 1
    return redirect(url_for("quiz.question"))


@quiz_bp.get("/results")
@login_required
def results():
    attempt_id = session.get("quiz_attempt_id")
    if not attempt_id:
        return redirect(url_for("protected.dashboard"))

    attempt = QuizAttempt.query.get_or_404(attempt_id)

    if attempt.finished_at is None:
        attempt.finished_at = datetime.utcnow()
        attempt.duration_seconds = int((attempt.finished_at - attempt.started_at).total_seconds())
        db.session.commit()

    answers = (AttemptAnswer.query
               .filter_by(attempt_id=attempt.id)
               .all())

    # clear session so a new quiz can start
    session.pop("quiz_attempt_id", None)
    session.pop("quiz_order", None)
    session.pop("quiz_index", None)

    return render_template("quiz/results.html", attempt=attempt, answers=answers)