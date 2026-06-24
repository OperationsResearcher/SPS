"""Admin Araçları — Loglar servisi.

Kurum (tenant) bazında ve genel olarak:
  1. Son giriş (kim, ne zaman) + toplam giriş sayısı  → AuditLog (action="OTURUM AÇMA")
  2. Son veri hareketi (ne değişti, kim, ne zaman)     → AuditLog (CRUD) ∪ KpiData (PG verisi)
  3. Hiç giriş yapmamış kullanıcılar (sayı + liste)    → login audit'i olmayan User'lar
  4. Son hareketler akışı (genel, son ~25)             → AuditLog ∪ KpiData

NOT: PG verisi girişi AuditLog'a yazılmaz (yalnız KpiData/KpiDataAudit). Bu yüzden "son
veri hareketi" iki kaynağın birleşimidir. Tüm zaman damgaları UTC ISO döner; ekranda
admin'in tarayıcı saat dilimine JS ile çevrilir. Salt-okuma; veri değiştirmez.
"""
from __future__ import annotations

from datetime import datetime, timezone

from flask_babel import gettext as _

from sqlalchemy import func, and_, or_

from extensions import db
from app.models.core import Tenant, User
from app.models.audit import AuditLog
from app.models.process import Process, ProcessKpi, KpiData

# Başarılı giriş aksiyonları (başarısız "LOGIN_FAILED" hariç).
_LOGIN_ACTIONS = ("OTURUM AÇMA", "LOGIN")
# Veri değişikliği sayılmayan (güvenlik) audit kayıtları.
_SECURITY_RESOURCE = "GÜVENLİK"
# İzole test kurumu — gerçek loglardan tamamen hariç tutulur.
_TOMOFILTEST_NAME = "tomofiltest"


_EPOCH = datetime.min.replace(tzinfo=timezone.utc)


def _iso(dt) -> str | None:
    """DateTime'ı UTC ISO 8601'e çevirir (naive ise UTC varsayar)."""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _cmp(dt) -> datetime:
    """Sıralama/karşılaştırma için tz-aware UTC anahtarı (naive→UTC, None→epoch).

    Aware ve naive kayıtların karışmasından doğan TypeError'ı önler.
    """
    if not dt:
        return _EPOCH
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def _uname(u: User | None) -> str:
    if not u:
        return "—"
    full = f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}".strip()
    return full or (u.email or f"#{u.id}")


def collect_logs() -> dict:
    # tomofiltest'i her sorgudan hariç tut. Reclone'da tenant id değişebildiği için
    # hem tenant id'leri hem sentetik admin kullanıcı adı (orphan kayıtlar) elenir.
    try:
        from app.services.tenant_clone_service import SYNTH_ADMIN_EMAIL
    except Exception:
        SYNTH_ADMIN_EMAIL = "admin@tomofiltest.local"
    excl_tids = [
        t.id for t in Tenant.query.filter(
            func.lower(Tenant.name) == _TOMOFILTEST_NAME).all()
    ]

    def audit_excl():
        """AuditLog sorgularına eklenecek tomofiltest hariç-tutma filtresi."""
        conds = [or_(AuditLog.username.is_(None), AuditLog.username != SYNTH_ADMIN_EMAIL)]
        if excl_tids:
            conds.append(or_(AuditLog.tenant_id.is_(None), AuditLog.tenant_id.notin_(excl_tids)))
        return and_(*conds)

    def kpi_excl():
        """KpiData sorgularına eklenecek tomofiltest hariç-tutma filtresi (Process.tenant_id)."""
        return Process.tenant_id.notin_(excl_tids) if excl_tids else True

    tenants = (
        Tenant.query.filter(
            Tenant.is_active.is_(True),
            func.lower(Tenant.name) != _TOMOFILTEST_NAME)
        .order_by(Tenant.name.asc()).all()
    )
    tenant_name = {t.id: t.name for t in tenants}

    # ── 1) Giriş sayısı (kurum bazlı) ──
    login_counts = dict(
        db.session.query(AuditLog.tenant_id, func.count(AuditLog.id))
        .filter(AuditLog.action.in_(_LOGIN_ACTIONS), audit_excl())
        .group_by(AuditLog.tenant_id).all()
    )
    login_total_global = (
        db.session.query(func.count(AuditLog.id))
        .filter(AuditLog.action.in_(_LOGIN_ACTIONS), audit_excl()).scalar() or 0
    )

    # ── 2) Son giriş (kurum bazlı): max(created_at) → o satır ──
    login_max_sq = (
        db.session.query(
            AuditLog.tenant_id.label("tid"),
            func.max(AuditLog.created_at).label("mx"))
        .filter(AuditLog.action.in_(_LOGIN_ACTIONS), audit_excl())
        .group_by(AuditLog.tenant_id).subquery()
    )
    last_login = {}  # tenant_id -> {"who","when"}
    for row in (
        db.session.query(AuditLog)
        .join(login_max_sq, and_(
            AuditLog.tenant_id == login_max_sq.c.tid,
            AuditLog.created_at == login_max_sq.c.mx))
        .filter(AuditLog.action.in_(_LOGIN_ACTIONS), audit_excl()).all()
    ):
        if row.tenant_id not in last_login:
            last_login[row.tenant_id] = {"who": row.username or "—", "when": _iso(row.created_at)}

    # ── 3) Son veri hareketi — kaynak A: AuditLog (CRUD, güvenlik dışı) ──
    change_filter = and_(
        AuditLog.resource_type.isnot(None),
        AuditLog.resource_type != _SECURITY_RESOURCE,
        AuditLog.action.notin_(_LOGIN_ACTIONS + ("OTURUM KAPATMA", "LOGOUT")),
        audit_excl(),
    )
    chg_max_sq = (
        db.session.query(
            AuditLog.tenant_id.label("tid"),
            func.max(AuditLog.created_at).label("mx"))
        .filter(change_filter)
        .group_by(AuditLog.tenant_id).subquery()
    )
    audit_change = {}  # tenant_id -> {"what","who","when","dt"}
    for row in (
        db.session.query(AuditLog)
        .join(chg_max_sq, and_(
            AuditLog.tenant_id == chg_max_sq.c.tid,
            AuditLog.created_at == chg_max_sq.c.mx))
        .filter(change_filter).all()
    ):
        if row.tenant_id not in audit_change:
            what = row.description or f"{row.action} · {row.resource_type}"
            audit_change[row.tenant_id] = {
                "what": what, "who": row.username or "—",
                "when": _iso(row.created_at), "dt": row.created_at,
            }

    # ── 3) kaynak B: KpiData (PG verisi) — coalesce(updated_at, created_at) ──
    kpi_time = func.coalesce(KpiData.updated_at, KpiData.created_at)
    kpi_max_sq = (
        db.session.query(
            Process.tenant_id.label("tid"),
            func.max(kpi_time).label("mx"))
        .select_from(KpiData)
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .filter(KpiData.is_active.is_(True), kpi_excl())
        .group_by(Process.tenant_id).subquery()
    )
    kpi_change = {}  # tenant_id -> {"what","who","when","dt"}
    for tid, kd, usr in (
        db.session.query(Process.tenant_id, KpiData, User)
        .select_from(KpiData)
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .join(kpi_max_sq, and_(
            kpi_max_sq.c.tid == Process.tenant_id,
            kpi_time == kpi_max_sq.c.mx))
        .outerjoin(User, KpiData.user_id == User.id)
        .filter(KpiData.is_active.is_(True), kpi_excl()).all()
    ):
        if tid not in kpi_change:
            dt = kd.updated_at or kd.created_at
            kpi_change[tid] = {
                "what": _("PG verisi: %(val)s") % {"val": kd.actual_value},
                "who": _uname(usr), "when": _iso(dt), "dt": dt,
            }

    def _latest_change(tid):
        a, b = audit_change.get(tid), kpi_change.get(tid)
        if a and b:
            return a if _cmp(a["dt"]) >= _cmp(b["dt"]) else b
        return a or b

    # ── 4) Hiç giriş yapmamış kullanıcılar ──
    logged_ids_sq = (
        db.session.query(AuditLog.user_id)
        .filter(AuditLog.action.in_(_LOGIN_ACTIONS), AuditLog.user_id.isnot(None), audit_excl())
        .distinct().subquery()
    )
    never_q = db.session.query(User).filter(
        User.is_active.is_(True),
        User.id.notin_(db.session.query(logged_ids_sq.c.user_id)),
    )
    if excl_tids:
        never_q = never_q.filter(or_(User.tenant_id.is_(None), User.tenant_id.notin_(excl_tids)))
    never_users = never_q.all()
    never_count_by_tenant: dict[int, int] = {}
    never_list = []
    for u in never_users:
        never_count_by_tenant[u.tenant_id] = never_count_by_tenant.get(u.tenant_id, 0) + 1
        never_list.append({
            "name": _uname(u), "email": u.email,
            "tenant": tenant_name.get(u.tenant_id, "—"),
            "role": getattr(getattr(u, "role", None), "name", "") or "",
        })
    never_list.sort(key=lambda r: (r["tenant"], r["name"].lower()))

    # ── Kurum bazlı satırlar ──
    rows = []
    for t in tenants:
        chg = _latest_change(t.id)
        rows.append({
            "id": t.id, "name": t.name,
            "login_total": login_counts.get(t.id, 0),
            "last_login": last_login.get(t.id),
            "last_change": ({"what": chg["what"], "who": chg["who"], "when": chg["when"]} if chg else None),
            "never_count": never_count_by_tenant.get(t.id, 0),
        })

    # ── Genel özet ──
    g_last_login_row = (
        db.session.query(AuditLog)
        .filter(AuditLog.action.in_(_LOGIN_ACTIONS), audit_excl())
        .order_by(AuditLog.created_at.desc()).first()
    )
    g_last_login = ({"who": g_last_login_row.username or "—",
                     "when": _iso(g_last_login_row.created_at),
                     "tenant": tenant_name.get(g_last_login_row.tenant_id, "—")}
                    if g_last_login_row else None)
    # genel son değişiklik = tüm kurum-bazlı son değişikliklerin en yenisi
    all_changes = [c for c in (_latest_change(t.id) for t in tenants) if c]
    g_last_change = None
    if all_changes:
        c = max(all_changes, key=lambda x: _cmp(x["dt"]))
        g_last_change = {"what": c["what"], "who": c["who"], "when": c["when"]}

    # ── Son hareketler akışı (AuditLog ∪ KpiData, son 25) ──
    feed = []
    for row in (
        db.session.query(AuditLog)
        .filter(audit_excl())
        .order_by(AuditLog.created_at.desc()).limit(25).all()
    ):
        is_login = row.action in _LOGIN_ACTIONS
        is_sec = (row.resource_type == _SECURITY_RESOURCE)
        feed.append({
            "when": _iso(row.created_at), "dt": row.created_at,
            "who": row.username or "—",
            "tenant": tenant_name.get(row.tenant_id, "—"),
            "what": (row.description or (f"{row.action} · {row.resource_type}" if row.resource_type else row.action)),
            "kind": ("login" if is_login else ("güvenlik" if is_sec else "değişiklik")),
        })
    for kd, usr, ptid in (
        db.session.query(KpiData, User, Process.tenant_id)
        .select_from(KpiData)
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .outerjoin(User, KpiData.user_id == User.id)
        .filter(KpiData.is_active.is_(True), kpi_excl())
        .order_by(kpi_time.desc()).limit(25).all()
    ):
        dt = kd.updated_at or kd.created_at
        feed.append({
            "when": _iso(dt), "dt": dt, "who": _uname(usr),
            "tenant": tenant_name.get(ptid, "—"),
            "what": _("PG verisi: %(val)s") % {"val": kd.actual_value}, "kind": "PG verisi",
        })
    feed.sort(key=lambda x: _cmp(x["dt"]), reverse=True)
    feed = [{k: v for k, v in f.items() if k != "dt"} for f in feed[:25]]

    return {
        "rows": rows,
        "tenant_count": len(rows),
        "global": {
            "login_total": login_total_global,
            "last_login": g_last_login,
            "last_change": g_last_change,
            "never_count": len(never_users),
        },
        "never_list": never_list,
        "feed": feed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Kurum bazlı DETAY logları (kategori bazlı zaman çizelgesi)
# ─────────────────────────────────────────────────────────────────────────────

# Kategori → AuditLog.resource_type eşlemesi. Tümü tek kaynaktan (AuditLog) gelir.
_CATEGORIES = [
    {"key": "strateji", "label": "Stratejik Plan", "icon": "fa-bullseye", "color": "#b45309",
     "rtypes": ["Strateji Yönetimi", "Kurum Yönetimi"]},
    {"key": "surec", "label": "Süreç", "icon": "fa-diagram-project", "color": "#0e7490",
     "rtypes": ["Süreç Yönetimi"]},
    {"key": "pg", "label": "PG (Gösterge)", "icon": "fa-gauge-high", "color": "#15803d",
     "rtypes": ["PG Yönetimi", "KPI Yönetimi"]},
    {"key": "pgveri", "label": "PG Verisi", "icon": "fa-database", "color": "#16a34a",
     "rtypes": ["PG Veri Girişi", "KPI Veri Girişi"]},
    {"key": "proje", "label": "Proje", "icon": "fa-folder-open", "color": "#9333ea",
     "rtypes": ["Proje Yönetimi"]},
    {"key": "gorev", "label": "Proje Görevi", "icon": "fa-list-check", "color": "#7c3aed",
     "rtypes": ["Proje Faaliyeti"]},
]

_ACTION_LABEL = {
    "CREATE": "Eklendi", "UPDATE": "Değiştirildi", "DELETE": "Silindi",
    "TENANT_TYPE_CHANGE": "Tip değişti",
}
# Kurumsal kimlik (/sp kartları) alan → etiket
_IDENTITY_FIELDS = {
    "vision": "Vizyon", "mission": "Misyon", "purpose": "Amaç",
    "core_values": "Değerler", "code_of_ethics": "Etik Kurallar",
    "quality_policy": "Kalite Politikası",
}


def _entity_label(row) -> str:
    """new_values/old_values'tan anlamlı bir varlık tanımı çıkarır."""
    nv = row.new_values if isinstance(row.new_values, dict) else {}
    ov = row.old_values if isinstance(row.old_values, dict) else {}
    src = nv or ov
    # Kurumsal kimlik: hangi kart(lar) değişti
    ident = [_(lbl) for key, lbl in _IDENTITY_FIELDS.items() if key in src]
    if ident:
        return ", ".join(ident)
    for k in ("name", "Ad", "title", "_migration_record_name", "code"):
        if src.get(k):
            return str(src[k])
    # PG verisi: kpi + dönem
    if src.get("kpi_id"):
        per = " ".join(str(src[k]) for k in ("year", "period_type", "period_no") if src.get(k))
        return f"PG #{src['kpi_id']}" + (f" · {per}" if per else "")
    return row.description or ""


def _event(row) -> dict:
    _raw_act = _ACTION_LABEL.get(row.action)
    act = _(_raw_act) if _raw_act else row.action
    return {
        "action": row.action, "action_label": act,
        "what": _entity_label(row),
        "who": row.username or "—",
        "when": _iso(row.created_at),
    }


def collect_tenant_logs(tenant_id: int, per_cat: int = 15) -> dict | None:
    """Tek kurum için kategori bazlı detaylı log zaman çizelgesi."""
    t = Tenant.query.get(tenant_id)
    if not t or (t.name or "").lower() == _TOMOFILTEST_NAME:
        return None

    categories = []
    for cat in _CATEGORIES:
        rows = (
            db.session.query(AuditLog)
            .filter(AuditLog.tenant_id == tenant_id,
                    AuditLog.resource_type.in_(cat["rtypes"]))
            .order_by(AuditLog.created_at.desc())
            .limit(per_cat).all()
        )
        total = (
            db.session.query(func.count(AuditLog.id))
            .filter(AuditLog.tenant_id == tenant_id,
                    AuditLog.resource_type.in_(cat["rtypes"])).scalar() or 0
        )
        events = [_event(r) for r in rows]
        categories.append({
            "key": cat["key"], "label": _(cat["label"]),
            "icon": cat["icon"], "color": cat["color"],
            "total": total,
            "last": events[0] if events else None,
            "events": events,
        })

    return {
        "tenant": {"id": t.id, "name": t.name},
        "categories": categories,
    }
