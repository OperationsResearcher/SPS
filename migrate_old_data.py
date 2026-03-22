#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kokpitim — Eski SQLite yedeğinden (docs/kokpitim_yedek.db) aktif DB'ye veri taşıma.

Çalıştırma:
  python migrate_old_data.py [--dry-run] [--skip-notifications] [--skip-audit] [--old-db PATH]

Önkoşul: Ortam değişkenleri / config ile hedef DB bağlantısı (Flask app) tanımlı olmalı.

Altın kurallar (docs/cursor_migration_prompt.md):
  - Hard delete yok; silindi -> is_active tersine.
  - Şifre hash'leri aynen taşınır.
  - Tablo bazında transaction; hata olursa rollback.
  - Duplicate kontrolü; ID eşlemesi (eski id -> yeni id).

Not: Hedef kodda modeli olmayan tablolar (project, task, pestle, strategy_map_link, ...)
     istatistikte "unmapped" olarak raporlanır ve atlanır.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import sqlite3

from sqlalchemy import inspect, select, text

# Proje kökü
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.models import db
from app.models.core import Notification as CoreNotification
from app.models.core import Role, Strategy, SubStrategy, Tenant, User
from app.models.process import (
    FavoriteKpi,
    IndividualKpiData,
    IndividualPerformanceIndicator,
    Process,
    ProcessKpi,
    ProcessSubStrategyLink,
    process_leaders,
    process_members,
    process_owners_table,
)
from app.models.strategy import SwotAnalysis

DEFAULT_OLD_DB = os.path.join(ROOT, "docs", "kokpitim_yedek.db")

# Eski sistem_rol -> hedef Role.name (seed.py ile uyumlu)
SISTEM_ROL_TO_ROLE_NAME = {
    "admin": "Admin",
    "kurum_yoneticisi": "tenant_admin",
    "ust_yonetim": "executive_manager",
    "kurum_kullanici": "standard_user",
    "surec_lideri": "User",
}

# SWOT kategori normalizasyonu
SWOT_CAT_MAP = {
    "strengths": "strength",
    "weaknesses": "weakness",
    "opportunities": "opportunity",
    "threats": "threat",
    "strength": "strength",
    "weakness": "weakness",
    "opportunity": "opportunity",
    "threat": "threat",
}


def _stat() -> Dict[str, int]:
    return {"migrated": 0, "skipped": 0, "error": 0}


def _parse_dt(val: Any) -> Optional[datetime]:
    if val is None:
        return None
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return None
        for fmt in (
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(val[:26], fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def _parse_date(val: Any) -> Optional[date]:
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        s = val.strip()[:10]
        if len(s) >= 10:
            try:
                return date(int(s[0:4]), int(s[5:7]), int(s[8:10]))
            except ValueError:
                return None
    return None


def _as_bool(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "t")
    return bool(val)


def _str_or_none(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _role_id_for_sistem_rol(sistem_rol: Optional[str], roles_by_name: Dict[str, Role]) -> Optional[int]:
    if not sistem_rol:
        r = roles_by_name.get("standard_user")
        return r.id if r else None
    key = (sistem_rol or "").strip().lower()
    name = SISTEM_ROL_TO_ROLE_NAME.get(key)
    if name and name in roles_by_name:
        return roles_by_name[name].id
    # Bilinmeyen: standard_user
    r = roles_by_name.get("standard_user")
    return r.id if r else None


def _order_process_rows(rows: List[sqlite3.Row]) -> List[sqlite3.Row]:
    """parent_id ilişkisine göre kökten yapraklara sıra (ormanda DFS)."""
    by_id = {int(r["id"]): r for r in rows}
    children: Dict[int, List[int]] = defaultdict(list)
    roots: List[int] = []
    for r in rows:
        oid = int(r["id"])
        pid = r["parent_id"]
        if pid is not None and int(pid) in by_id:
            children[int(pid)].append(oid)
        else:
            roots.append(oid)
    ordered: List[sqlite3.Row] = []
    seen = set()

    def visit(oid: int) -> None:
        if oid in seen:
            return
        seen.add(oid)
        row = by_id.get(oid)
        if row is not None:
            ordered.append(row)
        for cid in sorted(children.get(oid, [])):
            visit(cid)

    for rid in sorted(roots):
        visit(rid)
    for r in rows:
        oid = int(r["id"])
        if oid not in seen:
            ordered.append(r)
            seen.add(oid)
    return ordered


def migrate(
    old_db_path: str,
    dry_run: bool = False,
    skip_notifications: bool = False,
    skip_audit: bool = False,
) -> Dict[str, Dict[str, int]]:
    if not os.path.isfile(old_db_path):
        raise FileNotFoundError(f"Yedek DB bulunamadı: {old_db_path}")

    stats: Dict[str, Dict[str, int]] = {}
    unmapped_tables = [
        "pestle_analizi",
        "analysis_item",
        "tows_matrix",
        "deger",
        "etik_kural",
        "kalite_politikasi",
        "strategic_plan",
        "project",
        "task",
        "activity",
        "raid_item",
        "strategy_map_link",
        "note",
        "feedback",
        "user_dashboard_settings",
        "user_activity_log",
    ]

    kurum_map: Dict[int, int] = {}
    user_map: Dict[int, int] = {}
    ana_strateji_map: Dict[int, int] = {}
    alt_strateji_map: Dict[int, int] = {}
    surec_map: Dict[int, int] = {}
    surec_pg_map: Dict[int, int] = {}
    bireysel_pg_map: Dict[int, int] = {}

    app = create_app()
    old_conn = sqlite3.connect(old_db_path)
    old_conn.row_factory = sqlite3.Row

    def run_table(name: str, fn: Callable[[], None]) -> None:
        stats[name] = _stat()
        s = stats[name]
        try:
            fn()
            if dry_run:
                db.session.rollback()
            else:
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            s["error"] += 1
            print(f"[HATA] {name}: {e}")
            traceback.print_exc()

    with app.app_context():
        roles_by_name = {r.name: r for r in Role.query.all()}
        if not roles_by_name:
            print("UYARI: roles tablosu boş — seed çalıştırmanız önerilir.")

        # --- 1. kurum -> tenants ---
        def step_kurum() -> None:
            s = stats["kurum"]
            for row in old_conn.execute("SELECT * FROM kurum ORDER BY id"):
                try:
                    kisa = _str_or_none(row["kisa_ad"])
                    if not kisa:
                        s["error"] += 1
                        continue
                    existing = Tenant.query.filter_by(short_name=kisa).first()
                    if existing:
                        kurum_map[int(row["id"])] = existing.id
                        s["skipped"] += 1
                        continue
                    t = Tenant(
                        name=_str_or_none(row["ticari_unvan"]) or kisa,
                        short_name=kisa,
                        is_active=not _as_bool(row["silindi"]),
                        activity_area=_str_or_none(row["faaliyet_alani"]),
                        sector=_str_or_none(row["sektor"]),
                        employee_count=row["calisan_sayisi"],
                        contact_email=_str_or_none(row["email"]),
                        phone_number=_str_or_none(row["telefon"]),
                        website_url=_str_or_none(row["web_adresi"]),
                        tax_office=_str_or_none(row["vergi_dairesi"]),
                        tax_number=_str_or_none(row["vergi_numarasi"]),
                        purpose=_str_or_none(row["amac"]),
                        vision=_str_or_none(row["vizyon"]),
                        core_values=_str_or_none(row["stratejik_profil"]),
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                    )
                    db.session.add(t)
                    db.session.flush()
                    kurum_map[int(row["id"])] = t.id
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("kurum", step_kurum)

        # --- 2. user -> users ---
        def step_user() -> None:
            s = stats["user"]
            for row in old_conn.execute("SELECT * FROM user ORDER BY id"):
                try:
                    email = (_str_or_none(row["email"]) or "").lower()
                    if not email:
                        s["error"] += 1
                        continue
                    existing = User.query.filter_by(email=email).first()
                    if existing:
                        user_map[int(row["id"])] = existing.id
                        s["skipped"] += 1
                        continue
                    kid = int(row["kurum_id"])
                    tenant_id = kurum_map.get(kid)
                    if tenant_id is None:
                        s["error"] += 1
                        print(f"  user id={row['id']}: kurum_id={kid} eşlemesi yok")
                        continue
                    u = User(
                        email=email,
                        password_hash=_str_or_none(row["password_hash"]) or "!invalid!",
                        first_name=_str_or_none(row["first_name"]),
                        last_name=_str_or_none(row["last_name"]),
                        is_active=not _as_bool(row["silindi"]),
                        tenant_id=tenant_id,
                        role_id=_role_id_for_sistem_rol(_str_or_none(row["sistem_rol"]), roles_by_name),
                        phone_number=_str_or_none(row["phone"]),
                        job_title=_str_or_none(row["title"]),
                        department=_str_or_none(row["department"]),
                        profile_picture=_str_or_none(row["profile_photo"]),
                        theme_preferences=_str_or_none(row["theme_preferences"]),
                        layout_preference=_str_or_none(row["layout_preference"]) or "classic",
                        show_page_guides=bool(row["show_page_guides"]) if row["show_page_guides"] is not None else True,
                        guide_character_style=_str_or_none(row["guide_character_style"]) or "professional",
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                    )
                    db.session.add(u)
                    db.session.flush()
                    user_map[int(row["id"])] = u.id
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("user", step_user)

        # --- 3. ana_strateji -> strategies ---
        def step_ana_strateji() -> None:
            s = stats["ana_strateji"]
            for row in old_conn.execute("SELECT * FROM ana_strateji ORDER BY id"):
                try:
                    tid = kurum_map.get(int(row["kurum_id"]))
                    if tid is None:
                        s["error"] += 1
                        continue
                    code = _str_or_none(row["code"])
                    title = _str_or_none(row["ad"]) or _str_or_none(row["name"]) or "Strateji"
                    q = Strategy.query.filter_by(tenant_id=tid)
                    ex = q.filter_by(code=code).first() if code else q.filter(Strategy.code.is_(None), Strategy.title == title).first()
                    if ex:
                        ana_strateji_map[int(row["id"])] = ex.id
                        s["skipped"] += 1
                        continue
                    st = Strategy(
                        tenant_id=tid,
                        code=code,
                        title=title,
                        description=_str_or_none(row["aciklama"]),
                        is_active=True,
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                        updated_at=_parse_dt(row["updated_at"]) or datetime.now(timezone.utc),
                    )
                    db.session.add(st)
                    db.session.flush()
                    ana_strateji_map[int(row["id"])] = st.id
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("ana_strateji", step_ana_strateji)

        # --- 4. alt_strateji -> sub_strategies ---
        def step_alt_strateji() -> None:
            s = stats["alt_strateji"]
            for row in old_conn.execute("SELECT * FROM alt_strateji ORDER BY id"):
                try:
                    sid = ana_strateji_map.get(int(row["ana_strateji_id"]))
                    if sid is None:
                        s["error"] += 1
                        continue
                    code = _str_or_none(row["code"])
                    title = _str_or_none(row["ad"]) or _str_or_none(row["name"]) or "Alt strateji"
                    q = SubStrategy.query.filter_by(strategy_id=sid)
                    ex = q.filter_by(code=code).first() if code else q.filter(SubStrategy.code.is_(None), SubStrategy.title == title).first()
                    if ex:
                        alt_strateji_map[int(row["id"])] = ex.id
                        s["skipped"] += 1
                        continue
                    ss = SubStrategy(
                        strategy_id=sid,
                        code=code,
                        title=title,
                        description=_str_or_none(row["aciklama"]),
                        is_active=True,
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                        updated_at=_parse_dt(row["updated_at"]) or datetime.now(timezone.utc),
                    )
                    db.session.add(ss)
                    db.session.flush()
                    alt_strateji_map[int(row["id"])] = ss.id
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("alt_strateji", step_alt_strateji)

        # --- 5. surec -> processes ---
        def step_surec() -> None:
            s = stats["surec"]
            rows = list(old_conn.execute("SELECT * FROM surec"))
            for row in _order_process_rows(rows):
                try:
                    tid = kurum_map.get(int(row["kurum_id"]))
                    if tid is None:
                        s["error"] += 1
                        continue
                    code = _str_or_none(row["code"])
                    name = _str_or_none(row["ad"]) or _str_or_none(row["name"]) or "Süreç"
                    q = Process.query.filter_by(tenant_id=tid)
                    ex = q.filter_by(code=code).first() if code else q.filter(Process.code.is_(None), Process.name == name).first()
                    if ex:
                        surec_map[int(row["id"])] = ex.id
                        s["skipped"] += 1
                        continue
                    parent_old = row["parent_id"]
                    parent_new = surec_map.get(int(parent_old)) if parent_old is not None else None
                    p = Process(
                        tenant_id=tid,
                        parent_id=parent_new,
                        code=code,
                        name=name,
                        english_name=_str_or_none(row["name"]),
                        weight=row["weight"],
                        document_no=_str_or_none(row["dokuman_no"]),
                        revision_no=_str_or_none(row["rev_no"]),
                        revision_date=_parse_date(row["rev_tarihi"]),
                        first_publish_date=_parse_date(row["ilk_yayin_tarihi"]),
                        status=_str_or_none(row["durum"]) or "Aktif",
                        progress=int(row["ilerleme"] or 0),
                        start_boundary=_str_or_none(row["baslangic_siniri"]),
                        end_boundary=_str_or_none(row["bitis_siniri"]),
                        start_date=_parse_date(row["baslangic_tarihi"]),
                        end_date=_parse_date(row["bitis_tarihi"]),
                        description=_str_or_none(row["aciklama"]),
                        is_active=not _as_bool(row["silindi"]),
                        deleted_at=_parse_dt(row["deleted_at"]),
                        deleted_by=user_map.get(int(row["deleted_by"])) if row["deleted_by"] else None,
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                    )
                    db.session.add(p)
                    db.session.flush()
                    surec_map[int(row["id"])] = p.id
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("surec", step_surec)

        # parent_id ikinci geçiş: eski parent hâlâ yanlışsa güncelle
        def fix_process_parents() -> None:
            for row in old_conn.execute("SELECT id, parent_id FROM surec WHERE parent_id IS NOT NULL"):
                pid_new = surec_map.get(int(row["id"]))
                p_old_parent = row["parent_id"]
                if pid_new is None or p_old_parent is None:
                    continue
                new_parent = surec_map.get(int(p_old_parent))
                proc = db.session.get(Process, pid_new)
                if proc and new_parent and proc.parent_id != new_parent:
                    proc.parent_id = new_parent

        try:
            fix_process_parents()
            if dry_run:
                db.session.rollback()
            else:
                db.session.commit()
        except Exception:
            db.session.rollback()
            print("[HATA] surec_parent_fix")
            traceback.print_exc()

        # --- 6. surec_performans_gostergesi -> process_kpis ---
        def step_surec_pg() -> None:
            s = stats["surec_performans_gostergesi"]
            for row in old_conn.execute("SELECT * FROM surec_performans_gostergesi ORDER BY id"):
                try:
                    proc_id = surec_map.get(int(row["surec_id"]))
                    if proc_id is None:
                        s["error"] += 1
                        continue
                    kodu = _str_or_none(row["kodu"])
                    ad = _str_or_none(row["ad"]) or "PG"
                    q = ProcessKpi.query.filter_by(process_id=proc_id)
                    ex = q.filter_by(code=kodu).first() if kodu else None
                    if ex is None:
                        ex = q.filter_by(name=ad).first()
                    if ex:
                        surec_pg_map[int(row["id"])] = ex.id
                        s["skipped"] += 1
                        continue
                    alt_id = row["alt_strateji_id"]
                    sub_id = alt_strateji_map.get(int(alt_id)) if alt_id is not None else None
                    pk = ProcessKpi(
                        process_id=proc_id,
                        name=ad,
                        description=_str_or_none(row["aciklama"]),
                        code=kodu,
                        target_value=_str_or_none(row["hedef_deger"]),
                        unit=_str_or_none(row["olcum_birimi"]) or _str_or_none(row["unit"]),
                        period=_str_or_none(row["periyot"]),
                        data_source=_str_or_none(row["veri_alinacak_yer"]),
                        target_setting_method=_str_or_none(row["hedef_belirleme_yontemi"]),
                        data_collection_method=_str_or_none(row["veri_toplama_yontemi"]) or "Ortalama",
                        gosterge_turu=_str_or_none(row["gosterge_turu"]),
                        target_method=_str_or_none(row["target_method"]),
                        basari_puani_araliklari=_str_or_none(row["basari_puani_araliklari"]),
                        onceki_yil_ortalamasi=row["onceki_yil_ortalamasi"],
                        weight=(
                            row["weight"]
                            if row["weight"] is not None
                            else row["agirlik"]
                        ),
                        direction=_str_or_none(row["direction"]) or "Increasing",
                        calculated_score=row["calculated_score"] if row["calculated_score"] is not None else row["agirlikli_basari_puani"],
                        is_active=True,
                        sub_strategy_id=sub_id,
                        start_date=_parse_date(row["baslangic_tarihi"]),
                        end_date=_parse_date(row["bitis_tarihi"]),
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                    )
                    db.session.add(pk)
                    db.session.flush()
                    surec_pg_map[int(row["id"])] = pk.id
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("surec_performans_gostergesi", step_surec_pg)

        # --- 7. bireysel_performans_gostergesi ---
        def step_bireysel_pg() -> None:
            s = stats["bireysel_performans_gostergesi"]
            for row in old_conn.execute("SELECT * FROM bireysel_performans_gostergesi ORDER BY id"):
                try:
                    uid = user_map.get(int(row["user_id"]))
                    if uid is None:
                        s["error"] += 1
                        continue
                    kodu = _str_or_none(row["kodu"])
                    ad = _str_or_none(row["ad"]) or "Bireysel PG"
                    q = IndividualPerformanceIndicator.query.filter_by(user_id=uid)
                    ex = q.filter_by(code=kodu).first() if kodu else q.filter_by(name=ad).first()
                    if ex:
                        bireysel_pg_map[int(row["id"])] = ex.id
                        s["skipped"] += 1
                        continue
                    ksid = row["kaynak_surec_id"]
                    kpgid = row["kaynak_surec_pg_id"]
                    ind = IndividualPerformanceIndicator(
                        user_id=uid,
                        name=ad,
                        description=_str_or_none(row["aciklama"]),
                        code=kodu,
                        target_value=_str_or_none(row["hedef_deger"]),
                        actual_value=_str_or_none(row["gerceklesen_deger"]),
                        unit=_str_or_none(row["olcum_birimi"]),
                        period=_str_or_none(row["periyot"]),
                        weight=float(row["agirlik"]) if row["agirlik"] is not None else 0,
                        is_important=bool(row["onemli"]) if row["onemli"] is not None else False,
                        start_date=_parse_date(row["baslangic_tarihi"]),
                        end_date=_parse_date(row["bitis_tarihi"]),
                        status=_str_or_none(row["durum"]) or "Devam Ediyor",
                        source=_str_or_none(row["kaynak"]) or "Bireysel",
                        source_process_id=surec_map.get(int(ksid)) if ksid is not None else None,
                        source_process_kpi_id=surec_pg_map.get(int(kpgid)) if kpgid is not None else None,
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                    )
                    db.session.add(ind)
                    db.session.flush()
                    bireysel_pg_map[int(row["id"])] = ind.id
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("bireysel_performans_gostergesi", step_bireysel_pg)

        # --- 8. performans_gosterge_veri -> individual_kpi_data (batch flush) ---
        def step_pg_veri() -> None:
            s = stats["performans_gosterge_veri"]
            BATCH = 100
            for n, row in enumerate(
                old_conn.execute("SELECT * FROM performans_gosterge_veri ORDER BY id"), start=1
            ):
                try:
                    pg_new = bireysel_pg_map.get(int(row["bireysel_pg_id"]))
                    if pg_new is None:
                        s["error"] += 1
                        continue
                    uid = user_map.get(int(row["user_id"]))
                    if uid is None:
                        s["error"] += 1
                        continue
                    yil = int(row["yil"])
                    d = _parse_date(row["veri_tarihi"])
                    if d is None:
                        s["error"] += 1
                        continue
                    ex = (
                        IndividualKpiData.query.filter_by(
                            individual_pg_id=pg_new,
                            year=yil,
                            data_date=d,
                            user_id=uid,
                        ).first()
                    )
                    if ex:
                        s["skipped"] += 1
                        continue
                    gercek = _str_or_none(row["gerceklesen_deger"]) or "0"
                    pt = _str_or_none(row["giris_periyot_tipi"])
                    if not pt:
                        if row["ceyrek"]:
                            pt = "ceyrek"
                        elif row["ay"]:
                            pt = "aylik"
                    pn = row["giris_periyot_no"]
                    if pn is None and row["ceyrek"]:
                        pn = int(row["ceyrek"])
                    pm = row["giris_periyot_ay"]
                    if pm is None and row["ay"]:
                        pm = int(row["ay"])
                    kd = IndividualKpiData(
                        individual_pg_id=pg_new,
                        year=yil,
                        data_date=d,
                        period_type=pt,
                        period_no=pn,
                        period_month=pm,
                        target_value=_str_or_none(row["hedef_deger"]),
                        actual_value=gercek,
                        status=_str_or_none(row["durum"]),
                        status_percentage=row["durum_yuzdesi"],
                        description=_str_or_none(row["aciklama"]),
                        user_id=uid,
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                    )
                    db.session.add(kd)
                    if n % BATCH == 0:
                        db.session.flush()
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()
            db.session.flush()

        stats["performans_gosterge_veri"] = _stat()
        try:
            step_pg_veri()
            if dry_run:
                db.session.rollback()
            else:
                db.session.commit()
        except Exception as e:
            stats["performans_gosterge_veri"]["error"] += 1
            db.session.rollback()
            print(f"[HATA] performans_gosterge_veri: {e}")
            traceback.print_exc()

        # --- 9. swot_analizi ---
        def step_swot() -> None:
            s = stats["swot_analizi"]
            for row in old_conn.execute("SELECT * FROM swot_analizi ORDER BY id"):
                try:
                    tid = kurum_map.get(int(row["kurum_id"]))
                    if tid is None:
                        s["error"] += 1
                        continue
                    raw_cat = (_str_or_none(row["kategori"]) or "").lower()
                    cat = SWOT_CAT_MAP.get(raw_cat, raw_cat[:32] if raw_cat else "strength")
                    baslik = _str_or_none(row["baslik"]) or ""
                    acik = _str_or_none(row["aciklama"]) or ""
                    content = (baslik + ("\n" + acik if acik else "")).strip() or baslik or "SWOT"
                    ex = SwotAnalysis.query.filter_by(tenant_id=tid, category=cat, content=content).first()
                    if ex:
                        s["skipped"] += 1
                        continue
                    sa = SwotAnalysis(
                        tenant_id=tid,
                        category=cat,
                        content=content,
                        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                        is_active=True,
                    )
                    db.session.add(sa)
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("swot_analizi", step_swot)

        # --- 10. İlişki tabloları ---
        def step_surec_alt_stratejiler() -> None:
            s = stats["surec_alt_stratejiler"]
            for row in old_conn.execute("SELECT * FROM surec_alt_stratejiler"):
                try:
                    pid = surec_map.get(int(row["surec_id"]))
                    sid = alt_strateji_map.get(int(row["alt_strateji_id"]))
                    if pid is None or sid is None:
                        s["error"] += 1
                        continue
                    ex = ProcessSubStrategyLink.query.filter_by(process_id=pid, sub_strategy_id=sid).first()
                    if ex:
                        s["skipped"] += 1
                        continue
                    db.session.add(ProcessSubStrategyLink(process_id=pid, sub_strategy_id=sid, contribution_pct=None))
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("surec_alt_stratejiler", step_surec_alt_stratejiler)

        def step_strategy_process_matrix() -> None:
            s = stats["strategy_process_matrix"]
            for row in old_conn.execute("SELECT * FROM strategy_process_matrix ORDER BY id"):
                try:
                    pid = surec_map.get(int(row["process_id"]))
                    sid = alt_strateji_map.get(int(row["sub_strategy_id"]))
                    if pid is None or sid is None:
                        s["error"] += 1
                        continue
                    pct = row["relationship_score"]
                    if pct is None:
                        pct = row["relationship_strength"]
                    if pct is not None:
                        try:
                            pct = float(pct)
                        except (TypeError, ValueError):
                            pct = None
                    link = ProcessSubStrategyLink.query.filter_by(process_id=pid, sub_strategy_id=sid).first()
                    if link:
                        if pct is not None and link.contribution_pct is None:
                            link.contribution_pct = pct
                        s["skipped"] += 1
                        continue
                    db.session.add(ProcessSubStrategyLink(process_id=pid, sub_strategy_id=sid, contribution_pct=pct))
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("strategy_process_matrix", step_strategy_process_matrix)

        def insert_assoc(
            table,
            proc_col: str,
            user_col: str,
            old_process_col: str,
            step_name: str,
        ) -> None:
            st = stats[step_name]
            for row in old_conn.execute(f"SELECT * FROM {step_name}"):
                try:
                    p_new = surec_map.get(int(row[old_process_col]))
                    u_new = user_map.get(int(row["user_id"]))
                    if p_new is None or u_new is None:
                        st["error"] += 1
                        continue
                    stmt = select(table).where(
                        table.c[proc_col] == p_new,
                        table.c[user_col] == u_new,
                    )
                    if db.session.execute(stmt).first():
                        st["skipped"] += 1
                        continue
                    db.session.execute(
                        table.insert().values(**{proc_col: p_new, user_col: u_new})
                    )
                    st["migrated"] += 1
                except Exception:
                    st["error"] += 1
                    traceback.print_exc()

        for name, tbl, old_col in (
            ("surec_uyeleri", process_members, "surec_id"),
            ("surec_liderleri", process_leaders, "surec_id"),
            ("process_owners", process_owners_table, "process_id"),
        ):
            stats[name] = _stat()
            try:
                insert_assoc(tbl, "process_id", "user_id", old_col, name)
                if dry_run:
                    db.session.rollback()
                else:
                    db.session.commit()
            except Exception:
                db.session.rollback()
                stats[name]["error"] += 1
                traceback.print_exc()

        # --- 11. favori_kpi ---
        def step_favori() -> None:
            s = stats["favori_kpi"]
            for row in old_conn.execute("SELECT * FROM favori_kpi ORDER BY id"):
                try:
                    uid = user_map.get(int(row["user_id"]))
                    kpi_id = surec_pg_map.get(int(row["surec_pg_id"]))
                    if uid is None or kpi_id is None:
                        s["error"] += 1
                        continue
                    ex = FavoriteKpi.query.filter_by(user_id=uid, process_kpi_id=kpi_id).first()
                    if ex:
                        s["skipped"] += 1
                        continue
                    db.session.add(
                        FavoriteKpi(
                            user_id=uid,
                            process_kpi_id=kpi_id,
                            sort_order=int(row["sira"] or 0),
                        )
                    )
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        run_table("favori_kpi", step_favori)

        # --- 12. notification -> core.notifications ---
        def step_notification() -> None:
            s = stats["notification"]
            for row in old_conn.execute("SELECT * FROM notification ORDER BY id"):
                try:
                    uid = user_map.get(int(row["user_id"]))
                    if uid is None:
                        s["error"] += 1
                        continue
                    u = db.session.get(User, uid)
                    tenant_id = u.tenant_id if u else None
                    title = _str_or_none(row["baslik"]) or "Bildirim"
                    msg = _str_or_none(row["mesaj"]) or ""
                    created = _parse_dt(row["created_at"]) or datetime.now(timezone.utc)
                    tip = _str_or_none(row["tip"]) or "legacy"
                    ex = CoreNotification.query.filter_by(
                        user_id=uid,
                        title=title,
                        notification_type=tip,
                        message=msg,
                    ).first()
                    if ex:
                        s["skipped"] += 1
                        continue
                    proc_id = row["surec_id"]
                    n = CoreNotification(
                        user_id=uid,
                        tenant_id=tenant_id,
                        notification_type=_str_or_none(row["tip"]) or "legacy",
                        title=title,
                        message=msg,
                        link=_str_or_none(row["link"]),
                        is_read=_as_bool(row["okundu"]),
                        process_id=surec_map.get(int(proc_id)) if proc_id else None,
                        related_user_id=user_map.get(int(row["ilgili_user_id"])) if row["ilgili_user_id"] else None,
                        created_at=created,
                    )
                    db.session.add(n)
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        if not skip_notifications:
            run_table("notification", step_notification)
        else:
            stats["notification"] = _stat()
            print("Bildirimler atlandı (--skip-notifications).")

        # --- 13. audit_log ---
        # Hedef DB şeması eski olabilir (ör. username/description yok); ORM tüm sütunları
        # gönderdiği için sqlite hata verir. Gerçek sütunlara göre INSERT kullan.
        def step_audit() -> None:
            s = stats["audit_log"]
            insp = inspect(db.engine)
            try:
                aud_cols = {c["name"] for c in insp.get_columns("audit_logs")}
            except Exception:
                aud_cols = set()

            for row in old_conn.execute("SELECT * FROM audit_log ORDER BY id"):
                try:
                    uid = user_map.get(int(row["user_id"])) if row["user_id"] else None
                    tid = None
                    if uid:
                        u = db.session.get(User, uid)
                        if u is not None:
                            tid = u.tenant_id
                    changes = row["changes"]
                    if isinstance(changes, str):
                        try:
                            changes = json.loads(changes)
                        except json.JSONDecodeError:
                            changes = None
                    new_values: Dict[str, Any] = {}
                    if isinstance(changes, dict):
                        new_values.update(changes)
                    un = _str_or_none(row["user_name"])
                    rn = _str_or_none(row["record_name"])
                    if un:
                        new_values.setdefault("_migration_username", un)
                    if rn:
                        new_values.setdefault("_migration_record_name", rn)

                    action = _str_or_none(row["action"]) or "UNKNOWN"
                    rtype = _str_or_none(row["module"]) or "legacy"
                    rid = int(row["record_id"]) if row["record_id"] is not None else None
                    created = _parse_dt(row["timestamp"]) or datetime.now(timezone.utc)

                    nv_out: Any = new_values if new_values else None
                    if isinstance(nv_out, dict):
                        nv_out = json.dumps(nv_out, ensure_ascii=False)

                    row_payload = {
                        "user_id": uid,
                        "tenant_id": tid,
                        "username": un or "",
                        "action": action,
                        "resource_type": rtype,
                        "resource_id": rid,
                        "description": rn,
                        "old_values": None,
                        "new_values": nv_out,
                        "ip_address": None,
                        "user_agent": None,
                        "request_method": None,
                        "request_path": None,
                        "created_at": created,
                    }

                    keys = [k for k in row_payload if k in aud_cols]
                    if not keys:
                        s["error"] += 1
                        continue
                    stmt = text(
                        "INSERT INTO audit_logs ("
                        + ", ".join(keys)
                        + ") VALUES ("
                        + ", ".join(f":{k}" for k in keys)
                        + ")"
                    )
                    db.session.execute(stmt, {k: row_payload[k] for k in keys})
                    s["migrated"] += 1
                except Exception:
                    s["error"] += 1
                    traceback.print_exc()

        if not skip_audit:
            run_table("audit_log", step_audit)
        else:
            stats["audit_log"] = _stat()
            print("Audit log atlandı (--skip-audit).")

    old_conn.close()

    stats["_unmapped_tables"] = {
        "skipped_by_design": len(unmapped_tables),
    }

    print("\n=== MİGRASYON RAPORU ===")
    for tablo, s in sorted(stats.items()):
        if tablo.startswith("_"):
            continue
        print(f"{tablo}: {s['migrated']} taşındı, {s['skipped']} atlandı, {s['error']} hata")
    print(
        "\nModeli olmayan / bu scriptte işlenmeyen tablolar:",
        ", ".join(unmapped_tables),
    )

    with app.app_context():
        print("\n=== HEDEF DB SAYAÇLARI (migration sonrası) ===")
        print("Tenant:", Tenant.query.count())
        print("User:", User.query.count())
        print("Strategy:", Strategy.query.count())
        print("SubStrategy:", SubStrategy.query.count())
        print("Process:", Process.query.count())
        print("ProcessKpi:", ProcessKpi.query.count())
        print("IndividualPerformanceIndicator:", IndividualPerformanceIndicator.query.count())
        print("IndividualKpiData:", IndividualKpiData.query.count())

    return stats


def main() -> None:
    p = argparse.ArgumentParser(description="Kokpitim eski SQLite -> aktif DB migration")
    p.add_argument("--old-db", default=DEFAULT_OLD_DB, help="Yedek SQLite dosyası")
    p.add_argument("--dry-run", action="store_true", help="Commit etmeden dene (çoğu adımda rollback)")
    p.add_argument("--skip-notifications", action="store_true", help="notification tablosunu atla")
    p.add_argument("--skip-audit", action="store_true", help="audit_log tablosunu atla")
    args = p.parse_args()
    migrate(
        old_db_path=args.old_db,
        dry_run=args.dry_run,
        skip_notifications=args.skip_notifications,
        skip_audit=args.skip_audit,
    )


if __name__ == "__main__":
    main()
