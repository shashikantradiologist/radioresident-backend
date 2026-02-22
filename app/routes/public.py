from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)

@public_bp.get("/")
def home():
    return render_template("public/home.html")

@public_bp.get("/articles")
def articles():
    return render_template("public/articles.html")

@public_bp.get("/cases")
def cases():
    return render_template("public/cases.html")

@public_bp.get("/quizzes")
def quizzes():
    return render_template("public/quizzes.html")

@public_bp.get("/games")
def games():
    return render_template("public/games.html")