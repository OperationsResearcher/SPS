"""Admin backup scheduler service (daily/weekly)."""

from __future__ import annotations

import datetime
import json
import logging
import os
import shutil
import tempfile
from functools import partial

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from services import admin_backup_service as backup_service

logger = logging.getLogger(__name__)
_scheduler = None
_job_id = "admin_backup_auto_job"

_default_cfg = {
    "enabled": False,
    "backup_type": "data",  # data | full
    "frequency": "daily",  # daily | weekly
    "time": "02:00",
    "day_of_week": "sun",
    "keep_last": 7,
}


def _cfg_path(app) -> str:
    os.makedirs(app.instance_path, exist_ok=True)
    return os.path.join(app.instance_path, "backup_schedule.json")


def _output_dir(app) -> str:
    root = os.path.abspath(os.path.join(app.root_path, os.pardir))
    out = os.path.join(root, "Yedekler", "otomatik")
    os.makedirs(out, exist_ok=True)
    return out


def _normalize(cfg: dict | None) -> dict:
    out = dict(_default_cfg)
    if isinstance(cfg, dict):
        out.update(cfg)
    out["enabled"] = bool(out.get("enabled"))
    out["backup_type"] = "full" if str(out.get("backup_type", "data")).lower() == "full" else "data"
    out["frequency"] = "weekly" if str(out.get("frequency", "daily")).lower() == "weekly" else "daily"

    time_raw = str(out.get("time", "02:00")).strip()
    try:
        hh, mm = time_raw.split(":", 1)
        hh_i = max(0, min(23, int(hh)))
        mm_i = max(0, min(59, int(mm)))
    except Exception:
        hh_i, mm_i = 2, 0
    out["time"] = f"{hh_i:02d}:{mm_i:02d}"

    dow = str(out.get("day_of_week", "sun")).strip().lower()
    if dow not in {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}:
        dow = "sun"
    out["day_of_week"] = dow

    try:
        keep_last = int(out.get("keep_last", 7))
    except Exception:
        keep_last = 7
    out["keep_last"] = max(1, min(120, keep_last))
    return out


def load_schedule(app) -> dict:
    p = _cfg_path(app)
    if not os.path.isfile(p):
        return dict(_default_cfg)
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _normalize(data)
    except Exception as e:
        logger.warning("backup schedule okunamadi: %s", e)
        return dict(_default_cfg)


def save_schedule(app, cfg: dict) -> dict:
    norm = _normalize(cfg)
    with open(_cfg_path(app), "w", encoding="utf-8") as f:
        json.dump(norm, f, ensure_ascii=False, indent=2)
    return norm


def _rotate_backups(out_dir: str, prefix: str, keep_last: int) -> None:
    items = []
    for name in os.listdir(out_dir):
        if not name.startswith(prefix):
            continue
        full = os.path.join(out_dir, name)
        if os.path.isfile(full):
            items.append((os.path.getmtime(full), full))
    items.sort(reverse=True)
    for _, old in items[keep_last:]:
        try:
            os.unlink(old)
        except OSError:
            logger.warning("Eski yedek silinemedi: %s", old)


def _run_job(app) -> None:
    cfg = load_schedule(app)
    if not cfg.get("enabled"):
        return
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    out_dir = _output_dir(app)
    with app.app_context():
        try:
            backup_service.require_postgres_uri()
            if cfg["backup_type"] == "full":
                src = backup_service.build_full_system_zip_path()
                dst_name = f"auto_full_{now}.zip"
                dst = os.path.join(out_dir, dst_name)
                shutil.move(src, dst)
                _rotate_backups(out_dir, "auto_full_", cfg["keep_last"])
            else:
                fd, temp_sql = tempfile.mkstemp(prefix="auto_data_", suffix=".sql")
                os.close(fd)
                try:
                    backup_service.dump_data_only_sql(temp_sql)
                    dst_name = f"auto_data_{now}.sql"
                    dst = os.path.join(out_dir, dst_name)
                    shutil.move(temp_sql, dst)
                finally:
                    if os.path.exists(temp_sql):
                        os.unlink(temp_sql)
                _rotate_backups(out_dir, "auto_data_", cfg["keep_last"])
            logger.info("Otomatik yedek tamamlandi: %s", dst_name)
        except Exception as e:
            logger.exception("Otomatik yedek hatasi: %s", e)


def apply_schedule(app) -> dict:
    global _scheduler
    cfg = load_schedule(app)
    if _scheduler is None:
        _scheduler = BackgroundScheduler(daemon=True)
        _scheduler.start()
    if _scheduler.get_job(_job_id):
        _scheduler.remove_job(_job_id)
    if not cfg.get("enabled"):
        return cfg

    hh, mm = cfg["time"].split(":")
    if cfg["frequency"] == "weekly":
        trigger = CronTrigger(day_of_week=cfg["day_of_week"], hour=int(hh), minute=int(mm))
    else:
        trigger = CronTrigger(hour=int(hh), minute=int(mm))

    _scheduler.add_job(
        func=partial(_run_job, app),
        trigger=trigger,
        id=_job_id,
        name="Admin otomatik yedek",
        replace_existing=True,
    )
    return cfg


def init_backup_scheduler(app) -> dict:
    """App startup hook: load persisted schedule and register job."""
    return apply_schedule(app)


def list_recent_backups(app, limit: int = 20) -> list[dict]:
    out = _output_dir(app)
    rows = []
    for name in os.listdir(out):
        full = os.path.join(out, name)
        if not os.path.isfile(full):
            continue
        if not (name.startswith("auto_data_") or name.startswith("auto_full_")):
            continue
        size = os.path.getsize(full)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(full))
        rows.append(
            {
                "name": name,
                "size_mb": round(size / (1024 * 1024), 2),
                "modified_at": mtime.strftime("%Y-%m-%d %H:%M"),
                "kind": "Tam Sistem" if name.startswith("auto_full_") else "Veri",
            }
        )
    rows.sort(key=lambda x: x["modified_at"], reverse=True)
    return rows[: max(1, min(limit, 100))]
