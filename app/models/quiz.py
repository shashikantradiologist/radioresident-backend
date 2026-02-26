# app/models/quiz.py
from datetime import datetime
from app.models.user import db

class Quiz(db.Model):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    questions = db.relationship("Question", backref="quiz", lazy=True, cascade="all, delete-orphan")


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)

    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)

    prompt = db.Column(db.Text, nullable=False)

    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)

    correct = db.Column(db.String(1), nullable=False)  # "A"/"B"/"C"/"D"
    explanation = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # table name default: user
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)

    score = db.Column(db.Integer, default=0, nullable=False)
    total = db.Column(db.Integer, default=10, nullable=False)

    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    finished_at = db.Column(db.DateTime, nullable=True)

    # make leaderboard tie-break easy + DB-agnostic
    duration_seconds = db.Column(db.Integer, nullable=True)

    quiz = db.relationship("Quiz", lazy=True)
    answers = db.relationship("AttemptAnswer", backref="attempt", lazy=True, cascade="all, delete-orphan")


class AttemptAnswer(db.Model):
    __tablename__ = "attempt_answers"
    id = db.Column(db.Integer, primary_key=True)

    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)

    selected = db.Column(db.String(1), nullable=False)  # "A"/"B"/"C"/"D"
    is_correct = db.Column(db.Boolean, default=False, nullable=False)

    question = db.relationship("Question", lazy=True)