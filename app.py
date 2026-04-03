# -*- coding: utf-8 -*-
"""
Flask Uygulama Giriş Noktası
"""
import os
import sys
from pathlib import Path


def _ensure_project_venv_python():
    """Yanlış interpreter ile çalıştırılıyorsa proje venv python'a geç."""
    if os.environ.get("KOKPITIM_VENV_BOOTSTRAPPED") == "1":
        return
    venv_python = Path(__file__).resolve().parent / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        return
    try:
        current = Path(sys.executable).resolve()
    except Exception:
        current = Path(sys.executable)
    if current == venv_python.resolve():
        return
    os.environ["KOKPITIM_VENV_BOOTSTRAPPED"] = "1"
    os.execv(str(venv_python), [str(venv_python), *sys.argv])


_ensure_project_venv_python()

try:
    from dotenv import load_dotenv
except ModuleNotFoundError as e:
    raise SystemExit(
        "Modül 'python-dotenv' yüklü değil (venv boş veya yanlış Python).\n"
        "  .venv\\Scripts\\activate\n"
        "  pip install -r requirements.txt\n"
        "Sonra tekrar: py app.py"
    ) from e

load_dotenv()

from app import create_app
import atexit

app = create_app()

# Uygulama kapanırken scheduler'ı temiz şekilde kapat
def cleanup():
    from services.task_reminder_scheduler import shutdown_scheduler
    from services.process_activity_scheduler import shutdown_process_activity_scheduler
    shutdown_scheduler()
    shutdown_process_activity_scheduler()

atexit.register(cleanup)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)

