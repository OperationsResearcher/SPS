# -*- coding: utf-8 -*-
"""Proje kontrol listesi iş kuralları (şablon → proje kopyası, çift onay, kilitli kapanış).

Yetki kararları burada tek yerde toplanır; route'lar yalnızca bu fonksiyonları çağırır.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from flask_babel import gettext as _

from extensions import db
from app.models.project_checklist import (
    ChecklistTemplate,
    ChecklistTemplateItem,
    ProjectChecklistAssignment,
    ProjectChecklistItem,
    STATUS_APPROVED,
    TARGET_PROCESS,
    TARGET_TYPES,
    TARGET_PROJECT,
    TARGET_USER,
    STATUS_DONE,
    STATUS_PENDING,
)


class ChecklistError(Exception):
    """İş kuralı ihlali — mesaj kullanıcıya gösterilir."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _naive_now() -> datetime:
    # Süreç faaliyeti tablolarıyla aynı: DB'de naive TR yerel saati tutulur
    from app.utils.tr_time import now_tr
    return now_tr().replace(tzinfo=None)


# ── Yıl / şablon ─────────────────────────────────────────────────────────────
def project_year(project) -> int:
    """Projenin yılı: bağlı plan yılı → başlangıç tarihi yılı → bugünün yılı."""
    if getattr(project, "plan_year_id", None):
        from app.models.plan_year import PlanYear
        py = db.session.get(PlanYear, project.plan_year_id)
        if py:
            return int(py.year)
    if project.start_date:
        return int(project.start_date.year)
    return date.today().year


def get_template(tenant_id: int, year: int, *, create: bool = False) -> ChecklistTemplate | None:
    tpl = ChecklistTemplate.query.filter_by(tenant_id=tenant_id, year=year).first()
    if tpl is None and create:
        tpl = ChecklistTemplate(tenant_id=tenant_id, year=year, name="Kontrol Listesi")  # gettext yok: betiklerden (istek bağlamı olmadan) da çağrılır
        db.session.add(tpl)
        db.session.flush()
    return tpl


def copy_template_to_project(project, *, template: ChecklistTemplate | None = None) -> int:
    """Kurumun projenin yılındaki şablonunu projeye kopyalar. Zaten maddesi varsa dokunmaz.

    Döner: eklenen madde sayısı. Şablon yoksa 0 (proje yine de oluşur).
    """
    existing = ProjectChecklistItem.query.filter_by(project_id=project.id).count()
    if existing:
        return 0
    tpl = template or get_template(project.kurum_id, project_year(project))
    if tpl is None or not tpl.is_active:
        return 0
    base = project.start_date or date.today()
    added = 0
    for it in (i for i in tpl.items if i.is_active):
        nxt = None
        if it.period_days:
            nxt = datetime.combine(base, datetime.min.time()) + timedelta(days=int(it.period_days))
        db.session.add(ProjectChecklistItem(
            project_id=project.id,
            source_item_id=it.id,
            stage=it.stage,
            item_group=it.item_group,
            text=it.text,
            period_days=it.period_days,
            evidence_required=bool(it.evidence_required),
            sort_order=it.sort_order,
            next_reminder_at=nxt,
        ))
        added += 1
    db.session.flush()
    return added


# ── Okuma ────────────────────────────────────────────────────────────────────
def active_items(project_id: int) -> list[ProjectChecklistItem]:
    return (
        ProjectChecklistItem.query
        .filter_by(project_id=project_id, is_active=True)
        .order_by(ProjectChecklistItem.sort_order, ProjectChecklistItem.id)
        .all()
    )


def _pct(approved: int, total: int) -> int:
    return int(round(100 * approved / total)) if total else 0


def progress(project_id: int) -> dict:
    """Genel ve aşama bazlı ilerleme (onaylı / toplam)."""
    items = active_items(project_id)
    total = len(items)
    approved = sum(1 for i in items if i.status == STATUS_APPROVED)
    done = sum(1 for i in items if i.status == STATUS_DONE)
    stages: dict[str, dict] = {}
    for i in items:
        s = stages.setdefault(i.stage, {"stage": i.stage, "total": 0, "approved": 0, "done": 0})
        s["total"] += 1
        if i.status == STATUS_APPROVED:
            s["approved"] += 1
        elif i.status == STATUS_DONE:
            s["done"] += 1
    stage_list = list(stages.values())
    for s in stage_list:
        s["pct"] = _pct(s["approved"], s["total"])
    return {
        "total": total,
        "approved": approved,
        "done": done,
        "pending": total - approved - done,
        "pct": _pct(approved, total),
        "stages": stage_list,
    }


def progress_map(project_ids: list[int]) -> dict[int, dict]:
    """Liste/portföy için toplu ilerleme (tek sorgu): {project_id: {total, approved, pct}}."""
    out = {pid: {"total": 0, "approved": 0, "pct": 0} for pid in project_ids}
    if not project_ids:
        return out
    rows = (
        db.session.query(ProjectChecklistItem.project_id, ProjectChecklistItem.status, db.func.count())
        .filter(ProjectChecklistItem.project_id.in_(project_ids), ProjectChecklistItem.is_active.is_(True))
        .group_by(ProjectChecklistItem.project_id, ProjectChecklistItem.status)
        .all()
    )
    for pid, st, n in rows:
        out[pid]["total"] += n
        if st == STATUS_APPROVED:
            out[pid]["approved"] += n
    for v in out.values():
        v["pct"] = _pct(v["approved"], v["total"])
    return out


# ── Yetki ────────────────────────────────────────────────────────────────────
def can_manage(user, project) -> bool:
    """Madde ekleme/silme/atama/onay: proje lideri, kurum yöneticisi, platform admini."""
    from app_platform.modules.proje.permissions import user_is_project_leader
    return bool(user_is_project_leader(user, project))


def can_work(user, project, item: ProjectChecklistItem) -> bool:
    """'Yapıldı' işaretleyebilir: maddeye atanmış (kişi / süreç üyesi / proje ekibi) veya yönetici/lider."""
    if can_manage(user, project):
        return True
    return user_is_assigned(user, project, item)


# ── Atamalar: kullanıcı / süreç (tüm üyeleri) / proje (proje ekibi) ───────────
def project_team_ids(project) -> set[int]:
    ids = {int(u.id) for u in (list(project.leaders or []) + list(project.members or [])) if u}
    if project.manager_id:
        ids.add(int(project.manager_id))
    return ids


def process_member_ids(process) -> set[int]:
    return {int(u.id) for u in (list(process.leaders or []) + list(process.members or []) + list(process.owners or []))
            if u and getattr(u, "is_active", True)}


def expand_assignees(project, item: ProjectChecklistItem) -> set[int]:
    """Atamaları kullanıcı kimliklerine açar (süreç → üyeleri, proje → ekip)."""
    from app.models.process import Process
    ids: set[int] = set()
    for a in item.assignments:
        if a.target_type == TARGET_USER:
            ids.add(int(a.target_id))
        elif a.target_type == TARGET_PROJECT:
            ids |= project_team_ids(project)
        elif a.target_type == TARGET_PROCESS:
            proc = db.session.get(Process, int(a.target_id))
            if proc and proc.tenant_id == project.kurum_id and proc.is_active:
                ids |= process_member_ids(proc)
    return ids


def user_is_assigned(user, project, item: ProjectChecklistItem) -> bool:
    uid = int(user.id)
    for a in item.assignments:
        if a.target_type == TARGET_USER and int(a.target_id) == uid:
            return True
        if a.target_type == TARGET_PROJECT and uid in project_team_ids(project):
            return True
        if a.target_type == TARGET_PROCESS:
            from app.models.process import Process
            proc = db.session.get(Process, int(a.target_id))
            if proc and proc.tenant_id == project.kurum_id and proc.is_active and uid in process_member_ids(proc):
                return True
    return False


def assignment_labels(project, item: ProjectChecklistItem) -> list[dict]:
    """Arayüz için: [{type, id, label}] — kullanıcı adı, süreç adı veya 'Proje ekibi'."""
    from app.models.core import User
    from app.models.process import Process
    out = []
    for a in item.assignments:
        if a.target_type == TARGET_PROJECT:
            label = "Proje ekibi"
        elif a.target_type == TARGET_PROCESS:
            proc = db.session.get(Process, int(a.target_id))
            label = f"[{proc.code}] {proc.name}" if proc and proc.code else (proc.name if proc else f"#{a.target_id}")
        else:
            u = db.session.get(User, int(a.target_id))
            label = (f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}".strip() or u.email) if u else f"#{a.target_id}"
        out.append({"type": a.target_type, "id": int(a.target_id), "label": label})
    return out


def set_assignments(project, user, item_ids: list[int], targets: list[dict], *, replace: bool = True) -> list[int]:
    """Seçili maddelere atama hedeflerini yazar (yönetici/lider).

    targets: [{type: user|process|project, id}]. replace=True maddelerin mevcut atamalarını değiştirir,
    False mevcutlara ekler. Döner: yeni atanan kullanıcı kimlikleri (bildirim için).
    """
    from app.models.core import User
    from app.models.process import Process

    if not can_manage(user, project):
        raise ChecklistError(_("Bu işlem için yetkiniz yok."), 403)
    _ensure_open(project)
    clean: list[tuple[str, int]] = []
    for t in targets or []:
        ttype = (t.get("type") or "").strip()
        if ttype not in TARGET_TYPES:
            raise ChecklistError(_("Geçersiz atama hedefi."), 400)
        if ttype == TARGET_PROJECT:
            tid = 0
        else:
            try:
                tid = int(t.get("id"))
            except (TypeError, ValueError):
                raise ChecklistError(_("Geçersiz atama hedefi."), 400)
            if ttype == TARGET_USER:
                u = db.session.get(User, tid)
                if not u or not u.is_active or u.tenant_id != project.kurum_id:
                    raise ChecklistError(_("Geçerli bir kullanıcı seçin."), 400)
            else:
                p = db.session.get(Process, tid)
                if not p or not p.is_active or p.tenant_id != project.kurum_id:
                    raise ChecklistError(_("Geçerli bir süreç seçin."), 400)
        if (ttype, tid) not in clean:
            clean.append((ttype, tid))
    items = (
        ProjectChecklistItem.query
        .filter(ProjectChecklistItem.project_id == project.id, ProjectChecklistItem.is_active.is_(True),
                ProjectChecklistItem.id.in_([int(i) for i in item_ids or []]))
        .all()
    )
    if not items:
        raise ChecklistError(_("Madde seçilmedi."), 400)
    newly: set[int] = set()
    for it in items:
        before = expand_assignees(project, it)
        if replace:
            for a in list(it.assignments):
                db.session.delete(a)
            db.session.flush()
            db.session.refresh(it)
        have = {(a.target_type, int(a.target_id)) for a in it.assignments}
        for ttype, tid in clean:
            if (ttype, tid) not in have:
                db.session.add(ProjectChecklistAssignment(
                    item_id=it.id, target_type=ttype, target_id=tid, assigned_by=user.id))
        db.session.flush()
        db.session.refresh(it)
        newly |= expand_assignees(project, it) - before
    return sorted(newly)


def _ensure_open(project) -> None:
    if project.completed_at is not None:
        raise ChecklistError(_("Proje tamamlandı; kontrol listesi kilitli. Değişiklik için önce projeyi yeniden açın."), 423)


def _ensure_item_in_project(project, item) -> None:
    if item is None or item.project_id != project.id or not item.is_active:
        raise ChecklistError(_("Madde bulunamadı."), 404)


# ── Durum geçişleri ──────────────────────────────────────────────────────────
def mark_done(project, item: ProjectChecklistItem, user) -> ProjectChecklistItem:
    _ensure_item_in_project(project, item)
    _ensure_open(project)
    if not can_work(user, project, item):
        raise ChecklistError(_("Bu maddeyi işaretleme yetkiniz yok."), 403)
    if item.status != STATUS_PENDING:
        raise ChecklistError(_("Madde zaten işaretlenmiş."), 409)
    if item.evidence_required and not any(e.is_active for e in item.evidences):
        raise ChecklistError(_("Bu madde için kanıt (dosya veya bağlantı) eklemeden işaretlenemez."), 422)
    item.status = STATUS_DONE
    item.done_by = user.id
    item.done_at = _naive_now()
    item.approved_by = None
    item.approved_at = None
    return item


def approve(project, item: ProjectChecklistItem, user) -> ProjectChecklistItem:
    """İkinci onay: yönetici/lider ve maddeyi 'Yapıldı' yapandan FARKLI kişi."""
    _ensure_item_in_project(project, item)
    _ensure_open(project)
    if not can_manage(user, project):
        raise ChecklistError(_("Onay yetkisi yalnızca proje lideri ve yöneticisindedir."), 403)
    if item.status != STATUS_DONE:
        raise ChecklistError(_("Yalnızca 'Yapıldı' durumundaki madde onaylanabilir."), 409)
    if item.done_by is not None and int(item.done_by) == int(user.id):
        raise ChecklistError(_("Maddeyi işaretleyen kişi onaylayamaz; ikinci bir yetkili onaylamalıdır."), 403)
    item.status = STATUS_APPROVED
    item.approved_by = user.id
    item.approved_at = _naive_now()
    item.next_reminder_at = None
    return item


def reopen_item(project, item: ProjectChecklistItem, user) -> ProjectChecklistItem:
    """Maddeyi 'Bekliyor'a döndürür (yalnız yönetici/lider)."""
    _ensure_item_in_project(project, item)
    _ensure_open(project)
    if not can_manage(user, project):
        raise ChecklistError(_("Bu işlem için yetkiniz yok."), 403)
    if item.status == STATUS_PENDING:
        return item
    item.status = STATUS_PENDING
    item.done_by = item.done_at = item.approved_by = item.approved_at = None
    if item.period_days:
        item.next_reminder_at = _naive_now() + timedelta(days=int(item.period_days))
    return item


# ── Kilitli kapanış ──────────────────────────────────────────────────────────
def completion_state(project_id: int) -> dict:
    items = active_items(project_id)
    remaining = [i for i in items if i.status != STATUS_APPROVED]
    return {
        "has_items": bool(items),
        "can_complete": not remaining,
        "remaining": len(remaining),
        "total": len(items),
    }


def complete_project(project, user) -> None:
    if not can_manage(user, project):
        raise ChecklistError(_("Projeyi tamamlama yetkiniz yok."), 403)
    if project.completed_at is not None:
        raise ChecklistError(_("Proje zaten tamamlandı."), 409)
    st = completion_state(project.id)
    if not st["can_complete"]:
        raise ChecklistError(
            _("Kontrol listesinde onaylanmamış %(n)s madde var; proje tamamlanamaz.", n=st["remaining"]), 422
        )
    project.completed_at = _naive_now()
    project.completed_by = user.id


def reopen_project(project, user) -> None:
    if not can_manage(user, project):
        raise ChecklistError(_("Projeyi yeniden açma yetkiniz yok."), 403)
    project.completed_at = None
    project.completed_by = None


# ── Maddeyi proje içinde yönetme (yönetici) ──────────────────────────────────
def add_item(project, user, *, stage: str, text: str, item_group: str | None = None,
             period_days: int | None = None, evidence_required: bool = False) -> ProjectChecklistItem:
    if not can_manage(user, project):
        raise ChecklistError(_("Bu işlem için yetkiniz yok."), 403)
    _ensure_open(project)
    stage, text = (stage or "").strip(), (text or "").strip()
    if not stage or not text:
        raise ChecklistError(_("Aşama ve madde metni zorunludur."), 400)
    last = (
        db.session.query(db.func.max(ProjectChecklistItem.sort_order))
        .filter_by(project_id=project.id).scalar()
    ) or 0
    item = ProjectChecklistItem(
        project_id=project.id, stage=stage, item_group=(item_group or None), text=text,
        period_days=period_days or None,
        evidence_required=bool(evidence_required), sort_order=last + 1,
        next_reminder_at=(_naive_now() + timedelta(days=int(period_days))) if period_days else None,
    )
    db.session.add(item)
    db.session.flush()
    return item


def update_item(project, item, user, **fields) -> ProjectChecklistItem:
    _ensure_item_in_project(project, item)
    if not can_manage(user, project):
        raise ChecklistError(_("Bu işlem için yetkiniz yok."), 403)
    _ensure_open(project)
    for key in ("stage", "item_group", "text", "note"):
        if key in fields and fields[key] is not None:
            val = str(fields[key]).strip()
            if key in ("stage", "text") and not val:
                raise ChecklistError(_("Aşama ve madde metni zorunludur."), 400)
            setattr(item, key, val or None)
    if "period_days" in fields:
        pd = fields["period_days"] or None
        item.period_days = int(pd) if pd else None
        item.next_reminder_at = (
            _naive_now() + timedelta(days=item.period_days)
            if item.period_days and item.status != STATUS_APPROVED else None
        )
    if "evidence_required" in fields and fields["evidence_required"] is not None:
        item.evidence_required = bool(fields["evidence_required"])
    return item


def remove_item(project, item, user) -> None:
    """Soft delete — yönetici çıkarır (denetim kaydı route'ta yazılır)."""
    _ensure_item_in_project(project, item)
    if not can_manage(user, project):
        raise ChecklistError(_("Bu işlem için yetkiniz yok."), 403)
    _ensure_open(project)
    item.is_active = False
    item.next_reminder_at = None


# ── Şablon yönetimi (kurum yöneticisi) ───────────────────────────────────────
def template_active_items(tpl: ChecklistTemplate) -> list[ChecklistTemplateItem]:
    return [i for i in tpl.items if i.is_active]


def _template_item_from_fields(tpl, fields: dict, sort_order: int) -> ChecklistTemplateItem:
    stage = (fields.get("stage") or "").strip()
    text = (fields.get("text") or "").strip()
    if not stage or not text:
        raise ChecklistError(_("Aşama ve madde metni zorunludur."), 400)
    pd = fields.get("period_days")
    try:
        pd = int(pd) if pd not in (None, "") else None
    except (TypeError, ValueError):
        raise ChecklistError(_("Periyot gün sayısı geçersiz."), 400)
    if pd is not None and not (1 <= pd <= 366):
        raise ChecklistError(_("Periyot 1 ile 366 gün arasında olmalıdır."), 400)
    return ChecklistTemplateItem(
        template_id=tpl.id, stage=stage[:100],
        item_group=((fields.get("item_group") or "").strip()[:60] or None),
        text=text,
        period_days=pd,
        evidence_required=bool(fields.get("evidence_required")),
        sort_order=sort_order,
    )


def template_save_item(tpl: ChecklistTemplate, fields: dict, item_id: int | None = None) -> ChecklistTemplateItem:
    """Şablona madde ekler veya (item_id verilirse) günceller."""
    if item_id:
        it = db.session.get(ChecklistTemplateItem, int(item_id))
        if not it or it.template_id != tpl.id or not it.is_active:
            raise ChecklistError(_("Madde bulunamadı."), 404)
        new = _template_item_from_fields(tpl, fields, it.sort_order)
        for k in ("stage", "item_group", "text", "period_days", "evidence_required"):
            setattr(it, k, getattr(new, k))
        return it
    last = max((i.sort_order for i in tpl.items), default=0)
    it = _template_item_from_fields(tpl, fields, last + 1)
    db.session.add(it)
    db.session.flush()
    return it


def template_delete_item(tpl: ChecklistTemplate, item_id: int) -> None:
    it = db.session.get(ChecklistTemplateItem, int(item_id))
    if not it or it.template_id != tpl.id or not it.is_active:
        raise ChecklistError(_("Madde bulunamadı."), 404)
    it.is_active = False  # soft delete; mevcut projelere kopyalanmış maddeler etkilenmez


def template_reorder(tpl: ChecklistTemplate, ids: list[int]) -> None:
    by_id = {i.id: i for i in tpl.items if i.is_active}
    order = [int(x) for x in ids if int(x) in by_id]
    for n, iid in enumerate(order, start=1):
        by_id[iid].sort_order = n
    base = len(order)
    for it in by_id.values():  # listede olmayanlar sona
        if it.id not in order:
            base += 1
            it.sort_order = base


def template_import(tpl: ChecklistTemplate, rows: list[dict], *, replace: bool) -> int:
    """Excel satırlarını şablona yazar. replace=True: mevcut maddeler pasife alınır."""
    if replace:
        for it in tpl.items:
            it.is_active = False
    last = 0 if replace else max((i.sort_order for i in tpl.items), default=0)
    for n, r in enumerate(rows, start=1):
        db.session.add(_template_item_from_fields(tpl, r, last + n))
    db.session.flush()
    db.session.refresh(tpl)
    return len(rows)


def template_copy_year(tenant_id: int, from_year: int, to_year: int) -> int:
    """Bir yılın şablonunu başka bir yıla kopyalar (hedefte aktif madde yoksa)."""
    if from_year == to_year:
        raise ChecklistError(_("Kaynak ve hedef yıl aynı olamaz."), 400)
    src = get_template(tenant_id, from_year)
    if not src or not template_active_items(src):
        raise ChecklistError(_("Kaynak yılın şablonu boş."), 404)
    dst = get_template(tenant_id, to_year, create=True)
    if template_active_items(dst):
        raise ChecklistError(_("Hedef yılın şablonunda zaten madde var."), 409)
    rows = [
        {"stage": i.stage, "item_group": i.item_group, "text": i.text,
         "period_days": i.period_days, "evidence_required": i.evidence_required}
        for i in template_active_items(src)
    ]
    return template_import(dst, rows, replace=False)


# ── Not ve kanıt ─────────────────────────────────────────────────────────────
EVIDENCE_ALLOWED_EXT = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".txt", ".csv", ".mp4", ".mov", ".zip",
}
EVIDENCE_MAX_BYTES = 10 * 1024 * 1024


def set_note(project, item, user, note: str | None) -> None:
    _ensure_item_in_project(project, item)
    _ensure_open(project)
    if not can_work(user, project, item):
        raise ChecklistError(_("Bu işlem için yetkiniz yok."), 403)
    item.note = (note or "").strip()[:2000] or None


def _evidence_dir(project_id: int) -> str:
    import os
    from flask import current_app
    path = os.path.join(current_app.instance_path, "checklist_evidence", str(int(project_id)))
    os.makedirs(path, exist_ok=True)
    return path


def add_evidence(project, item, user, *, link_url: str | None = None, title: str | None = None, file_storage=None):
    """Maddeye bağlantı veya dosya kanıtı ekler (atanan kişi ya da yönetici)."""
    import os
    import uuid
    from werkzeug.utils import secure_filename
    from app.models.project_checklist import ProjectChecklistEvidence

    _ensure_item_in_project(project, item)
    _ensure_open(project)
    if not can_work(user, project, item):
        raise ChecklistError(_("Bu işlem için yetkiniz yok."), 403)
    if file_storage is not None and file_storage.filename:
        original = secure_filename(file_storage.filename) or "dosya"
        ext = os.path.splitext(original)[1].lower()
        if ext not in EVIDENCE_ALLOWED_EXT:
            raise ChecklistError(_("Bu dosya türü kabul edilmiyor."), 400)
        data = file_storage.read(EVIDENCE_MAX_BYTES + 1)
        if len(data) > EVIDENCE_MAX_BYTES:
            raise ChecklistError(_("Dosya en çok 10 MB olabilir."), 413)
        if not data:
            raise ChecklistError(_("Dosya boş."), 400)
        stored = f"{uuid.uuid4().hex}{ext}"
        with open(os.path.join(_evidence_dir(project.id), stored), "wb") as fh:
            fh.write(data)
        ev = ProjectChecklistEvidence(
            item_id=item.id, uploader_id=user.id, kind="file",
            title=((title or "").strip() or original)[:255], file_path=f"{int(project.id)}/{stored}",
        )
    else:
        url = (link_url or "").strip()
        if not url.lower().startswith(("http://", "https://")) or len(url) > 1000:
            raise ChecklistError(_("Geçerli bir bağlantı (http/https) girin."), 400)
        ev = ProjectChecklistEvidence(
            item_id=item.id, uploader_id=user.id, kind="link",
            title=((title or "").strip() or url)[:255], url=url,
        )
    db.session.add(ev)
    db.session.flush()
    return ev


def remove_evidence(project, evidence, user) -> None:
    _ensure_open(project)
    if evidence is None or not evidence.is_active or evidence.item.project_id != project.id:
        raise ChecklistError(_("Kanıt bulunamadı."), 404)
    own = evidence.uploader_id is not None and int(evidence.uploader_id) == int(user.id)
    if not (own or can_manage(user, project)):
        raise ChecklistError(_("Bu işlem için yetkiniz yok."), 403)
    # Kanıt zorunlu madde 'Yapıldı' iken son kanıt silinirse tutarsızlık olur → maddeyi geri al
    item = evidence.item
    evidence.is_active = False
    remaining = [e for e in item.evidences if e.is_active and e.id != evidence.id]
    if item.evidence_required and not remaining and item.status != STATUS_PENDING:
        item.status = STATUS_PENDING
        item.done_by = item.done_at = item.approved_by = item.approved_at = None


# ── Bildirimler (hata bildirimi akışı bozmaz) ────────────────────────────────
def _notify(user_id, tenant_id, ntype, title, message, link, actor_id=None) -> None:
    try:
        from micro.services.notification_triggers import _create
        _create(user_id=int(user_id), tenant_id=tenant_id, notification_type=ntype, title=title,
                message=message, link=link, related_user_id=actor_id)
    except Exception:  # bildirim başarısızlığı iş kuralını geri almamalı
        from flask import current_app
        current_app.logger.warning("[checklist] bildirim gönderilemedi", exc_info=True)


def _project_link(project) -> str:
    return f"/k-plan/project/{project.id}/views/checklist"


def notify_done(project, item, actor) -> None:
    """'Yapıldı' → proje liderlerine onay bekliyor bildirimi."""
    leader_ids = {int(u.id) for u in (project.leaders or [])}
    if project.manager_id:
        leader_ids.add(int(project.manager_id))
    leader_ids.discard(int(actor.id))
    for uid in leader_ids:
        _notify(uid, project.kurum_id, "checklist_approval",
                f"Onay bekleyen madde: {project.name}",
                f"'{item.text[:120]}' maddesi işaretlendi, onayınızı bekliyor.",
                _project_link(project), actor.id)


def notify_approved(project, item, actor) -> None:
    if item.done_by and int(item.done_by) != int(actor.id):
        _notify(item.done_by, project.kurum_id, "checklist_approved",
                f"Madde onaylandı: {project.name}", f"'{item.text[:120]}' maddesi onaylandı.",
                _project_link(project), actor.id)


def notify_assigned(project, user_ids, actor) -> None:
    """Yeni atanan kullanıcılara bildirim (atamayı yapan hariç)."""
    for uid in user_ids:
        if int(uid) != int(actor.id):
            _notify(uid, project.kurum_id, "checklist_assigned",
                    f"Kontrol listesi görevi: {project.name}",
                    "Size kontrol listesi maddeleri atandı.", _project_link(project), actor.id)


# ── Periyodik hatırlatma ─────────────────────────────────────────────────────
def run_due_reminders(now: datetime | None = None) -> int:
    """Zamanı gelen periyodik maddeler için sorumluya (yoksa proje liderlerine) bildirim gönderir.

    Döner: bildirim gönderilen madde sayısı. Onaylı, pasif ve tamamlanmış/arşivlenmiş
    projelerin maddeleri atlanır. Her madde için sonraki hatırlatma now + periyot.
    """
    from app.models.portfolio_project import Project

    now = now or _naive_now()
    due = (
        ProjectChecklistItem.query
        .join(Project, Project.id == ProjectChecklistItem.project_id)
        .filter(
            ProjectChecklistItem.is_active.is_(True),
            ProjectChecklistItem.status != STATUS_APPROVED,
            ProjectChecklistItem.period_days.isnot(None),
            ProjectChecklistItem.next_reminder_at.isnot(None),
            ProjectChecklistItem.next_reminder_at <= now,
            Project.is_active.is_(True),
            Project.is_archived.is_(False),
            Project.completed_at.is_(None),
        )
        .all()
    )
    sent = 0
    for it in due:
        project = it.project
        recipients = expand_assignees(project, it)
        if not recipients:
            recipients = project_team_ids(project)
        for uid in recipients:
            _notify(uid, project.kurum_id, "checklist_reminder",
                    f"Periyodik kontrol: {project.name}",
                    f"'{it.text[:120]}' maddesi için {it.period_days} günlük hatırlatma.",
                    _project_link(project))
        it.last_reminded_at = now
        it.next_reminder_at = now + timedelta(days=int(it.period_days))
        sent += 1
    return sent
