# AGENTS.md

## Cursor Cloud specific instructions

### Overview
This is **Stratejik Planlama Sistemi (SPS)** — a monolithic Python/Flask web application for strategic planning, performance tracking, and process management. All UI is server-rendered via Jinja2 (no separate frontend build step).

### Running the application
```bash
cd /workspace && python3 app.py
```
The app starts on **port 5001** in debug mode with hot-reloading enabled. The database is **SQLite** (`instance/spsv2.db`) — no external DB services needed.

### Key gotchas

- **Windows-only packages**: `requirements.txt` includes `pywin32`, `pywinpty`, `windows-curses`, and `tkcalendar` which fail on Linux. Filter them out when installing:
  ```
  grep -v -E "^(pywin32|pywinpty|windows-curses|tkcalendar)" requirements.txt > /tmp/req_linux.txt
  pip install -r /tmp/req_linux.txt
  ```
- **Missing dependency**: `apscheduler` is used by `services/task_reminder_scheduler.py` but is not listed in `requirements.txt`. Install separately: `pip install apscheduler`.
- **`.env` file**: Copy `.env.example` to `.env` before running. The default uses SQLite — no changes needed for development.
- **Demo data**: Run `python3 scripts/setup_db.py` to seed the database with 5 organizations and ~27 users. All demo users have password `123456`. There is also an easy-login page at `/auth/easy-login`.
- **Database location**: SQLite DB is stored at `instance/spsv2.db` (Flask's instance folder), not at the project root.
- **Flask-Caching warning**: A harmless `CACHE_TYPE is set to null` warning appears on startup — this is expected and does not affect functionality.

### Lint / Test / Build
- **Lint**: No formal linter is configured. Use `flake8` for basic checks: `python3 -m flake8 app.py config.py extensions.py --max-line-length=120`
- **Tests**: `python3 -m pytest tests/ -v` — some pre-existing test failures exist (health endpoint 404, model field mismatches in fixtures).
- **Build**: No build step required — it's a server-rendered Flask app.
