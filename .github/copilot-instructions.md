<!-- Brief, actionable guidance for AI coding agents working on this repo -->
# Copilot instructions for radioresident-backend

Purpose
- Short: small Flask app that serves public pages and has placeholder auth routes.

Big picture
- Entry points: `run.py` (development runner) and `wsgi.py` (WSGI callable). `run.py` calls `create_app()` in `app/__init__.py` and runs Flask with `debug=True`.
- App factory: `create_app()` is in `app/__init__.py`. It registers `auth` and `public` blueprints there.
- Blueprints: `app/routes/auth.py` (login/register placeholders), `app/routes/public.py` (public pages), `app/routes/protected.py` (views guarded by `login_required` but not registered in `create_app()`).

What to know about structure and conventions
- Templates live under `templates/` with subfolders `auth/` and `public/` matching route blueprints.
- Static assets are under `static/`.
- `config.py` contains SECRET_KEY and SQLAlchemy connection (`sqlite:///radioresident.db`) but SQLAlchemy and Flask-Login are not currently wired into `create_app()`.
- `app/models/user.py` exists but is empty — implement models here using SQLAlchemy when adding persistence.

Developer workflows & commands
- Quick dev run (local):

    python run.py

- Production WSGI (example):

    gunicorn wsgi:app -w 4 -b 0.0.0.0:8000

- Expected dependency file: `requirements.txt`. If adding packages, update it accordingly.

Patterns and examples to follow
- Route handlers: use Flask `Blueprint` patterns as in `app/routes/*.py`. Example: `auth_bp = Blueprint("auth", __name__)` and `@auth_bp.route('/login', methods=['GET','POST'])`.
- Form handling: request values are read via `request.form.get(...)` and flash messages are used for feedback — mirror this style when adding new forms.
- Protected routes use `@login_required` in `app/routes/protected.py`. If enabling these routes, register the `protected` blueprint and wire up `Flask-Login` and a `User` model.

Integration points & TODOs an agent may be asked to implement
- Persisted users: implement `User` model in `app/models/user.py` using `Flask-SQLAlchemy` and register `SQLAlchemy()` in `create_app()`.
- Authentication wiring: configure `Flask-Login` in `create_app()` (login manager, `user_loader`) and use the existing `login_required` imports in `protected.py`.
- Database migrations: none present. If adding migrations, prefer `Flask-Migrate` and document commands in `README.md`.

Checks before creating PRs
- Ensure `create_app()` registers any new blueprints you add.
- Keep template paths aligned with blueprint names (`templates/auth/`, `templates/public/`, etc.).
- Update `requirements.txt` when adding libs and keep `config.py` secret values out of source (replace hardcoded `SECRET_KEY` in production).

Where to look for examples in this repo
- `app/__init__.py` — app factory and blueprint registration.
- `app/routes/auth.py` — form handling pattern for login/register.
- `app/routes/public.py` — simple page endpoints returning templates.
- `config.py` — config keys and DB URI placeholder.

If anything is unclear or you want examples implemented (user model, login wiring, migrations), tell me which piece to add and I will implement it and run a quick validation.
