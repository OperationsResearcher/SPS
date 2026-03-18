"""Admin modülü — kullanıcı, kurum, paket, bileşen yönetimi."""

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from micro import micro_bp
from app.models import db
from app.models.core import User, Role, Tenant

_ADMIN_ROLES   = ("Admin",)
_MANAGER_ROLES = ("Admin", "tenant_admin", "executive_manager")


def _is_admin():
    return current_user.role and current_user.role.name in _ADMIN_ROLES


def _is_manager():
    return current_user.role and current_user.role.name in _MANAGER_ROLES


def _403():
    return jsonify({"success": False, "message": "Bu işlem için yetkiniz yok."}), 403


# ── Kullanıcı Yönetimi ────────────────────────────────────────────────────────

@micro_bp.route("/admin/users")
@login_required
def admin_users():
    if not _is_manager():
        return render_template("micro/errors/403.html"), 403

    if _is_admin():
        users = User.query.order_by(User.tenant_id, User.first_name).all()
    else:
        users = User.query.filter_by(tenant_id=current_user.tenant_id).order_by(User.first_name).all()

    roles   = Role.query.all()
    tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.name).all() if _is_admin() else []
    return render_template("micro/admin/users.html", users=users, roles=roles, tenants=tenants)


@micro_bp.route("/admin/users/add", methods=["POST"])
@login_required
def admin_users_add():
    if not _is_manager():
        return _403()

    data  = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"success": False, "message": "E-posta zorunludur."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Bu e-posta zaten kayıtlı."}), 400

    # tenant_admin tekil kontrolü
    role = Role.query.get(data.get("role_id"))
    tid  = int(data.get("tenant_id") or current_user.tenant_id or 0)
    if role and role.name == "tenant_admin":
        existing = User.query.join(Role).filter(
            User.tenant_id == tid, Role.name == "tenant_admin", User.is_active == True
        ).first()
        if existing:
            return jsonify({"success": False, "message": "Bu kurumda zaten aktif bir Kurum Yöneticisi var."}), 400

    try:
        u = User(
            email=email,
            password_hash=generate_password_hash(data.get("password") or "Changeme123!"),
            first_name=data.get("first_name", "").strip(),
            last_name=data.get("last_name", "").strip(),
            tenant_id=tid or None,
            role_id=data.get("role_id"),
            job_title=data.get("job_title", "").strip() or None,
            department=data.get("department", "").strip() or None,
        )
        db.session.add(u)
        db.session.commit()
        return jsonify({"success": True, "message": "Kullanıcı oluşturuldu.", "id": u.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_users_add] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/admin/users/edit/<int:user_id>", methods=["POST"])
@login_required
def admin_users_edit(user_id):
    if not _is_manager():
        return _403()

    u = User.query.get_or_404(user_id)
    if not _is_admin() and u.tenant_id != current_user.tenant_id:
        return _403()

    data = request.get_json() or {}
    try:
        u.first_name  = data.get("first_name", u.first_name or "").strip()
        u.last_name   = data.get("last_name",  u.last_name  or "").strip()
        u.job_title   = data.get("job_title",  u.job_title)
        u.department  = data.get("department", u.department)
        if data.get("role_id"):
            u.role_id = int(data["role_id"])
        if data.get("password"):
            u.password_hash = generate_password_hash(data["password"])
        db.session.commit()
        return jsonify({"success": True, "message": "Kullanıcı güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_users_edit] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@micro_bp.route("/admin/users/toggle/<int:user_id>", methods=["POST"])
@login_required
def admin_users_toggle(user_id):
    if not _is_manager():
        return _403()

    u = User.query.get_or_404(user_id)
    if not _is_admin() and u.tenant_id != current_user.tenant_id:
        return _403()
    if u.id == current_user.id:
        return jsonify({"success": False, "message": "Kendi hesabınızı pasife alamazsınız."}), 400

    try:
        u.is_active = not u.is_active
        db.session.commit()
        state = "aktifleştirildi" if u.is_active else "pasife alındı"
        return jsonify({"success": True, "message": f"Kullanıcı {state}.", "is_active": u.is_active})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_users_toggle] {e}")
        return jsonify({"success": False, "message": "İşlem sırasında hata oluştu."}), 500


# ── Toplu Kullanıcı İçe Aktarma ───────────────────────────────────────────────

@micro_bp.route("/admin/users/bulk-import", methods=["POST"])
@login_required
def admin_users_bulk_import():
    if not _is_manager():
        return _403()

    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "message": "Dosya seçilmedi."}), 400

    try:
        import io, csv
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        reader = csv.DictReader(stream)
        standard_role = Role.query.filter_by(name="standard_user").first()
        tid = current_user.tenant_id

        created, skipped = 0, 0
        for row in reader:
            email = (row.get("email") or row.get("E-posta") or "").strip().lower()
            if not email:
                skipped += 1
                continue
            if User.query.filter_by(email=email).first():
                skipped += 1
                continue
            u = User(
                email=email,
                password_hash=generate_password_hash("Changeme123!"),
                first_name=(row.get("first_name") or row.get("Ad") or "").strip(),
                last_name=(row.get("last_name") or row.get("Soyad") or "").strip(),
                tenant_id=tid,
                role_id=standard_role.id if standard_role else None,
            )
            db.session.add(u)
            created += 1

        db.session.commit()
        return jsonify({"success": True, "message": f"{created} kullanıcı oluşturuldu, {skipped} atlandı."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_users_bulk_import] {e}")
        return jsonify({"success": False, "message": "İçe aktarma sırasında hata oluştu."}), 500


@micro_bp.route("/admin/users/sample-excel")
@login_required
def admin_users_sample_excel():
    """Toplu kullanıcı içe aktarma için örnek Excel dosyası indir."""
    import io
    import openpyxl
    from flask import send_file

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Kullanicilar"
    ws.append(["email", "first_name", "last_name"])
    ws.append(["ornek1@kurum.com", "Ahmet", "Yilmaz"])
    ws.append(["ornek2@kurum.com", "Ayse", "Kaya"])
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 15

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="kullanici_sablonu.xlsx",
    )


# ── Kurum Yönetimi ────────────────────────────────────────────────────────────

@micro_bp.route("/admin/tenants")
@login_required
def admin_tenants():
    if not _is_manager():
        return render_template("micro/errors/403.html"), 403

    if _is_admin():
        tenants = Tenant.query.order_by(Tenant.name).all()
    else:
        tenants = Tenant.query.filter_by(id=current_user.tenant_id).all()

    try:
        from app.models.saas import SubscriptionPackage
        packages = SubscriptionPackage.query.filter_by(is_active=True).order_by(SubscriptionPackage.name).all()
    except Exception:
        packages = []

    total_users = sum(len(t.users) for t in tenants)
    return render_template("micro/admin/tenants.html", tenants=tenants, packages=packages, total_users=total_users)


@micro_bp.route("/admin/tenants/add", methods=["POST"])
@login_required
def admin_tenants_add():
    if not _is_admin():
        return _403()

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"success": False, "message": "Kurum adı zorunludur."}), 400

    try:
        t = Tenant(
            name=name,
            short_name=data.get("short_name", "").strip() or None,
            sector=data.get("sector") or None,
            activity_area=data.get("activity_area") or None,
            employee_count=int(data["employee_count"]) if data.get("employee_count") else None,
            contact_email=data.get("contact_email") or None,
            phone_number=data.get("phone_number") or None,
            website_url=data.get("website_url") or None,
            tax_office=data.get("tax_office") or None,
            tax_number=data.get("tax_number") or None,
            max_user_count=int(data["max_user_count"]) if data.get("max_user_count") else 5,
            package_id=int(data["package_id"]) if data.get("package_id") else None,
        )
        if data.get("license_end_date"):
            from datetime import date
            t.license_end_date = date.fromisoformat(data["license_end_date"])
        db.session.add(t)
        db.session.commit()
        return jsonify({"success": True, "message": "Kurum oluşturuldu.", "id": t.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_tenants_add] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/admin/tenants/edit/<int:tenant_id>", methods=["POST"])
@login_required
def admin_tenants_edit(tenant_id):
    if not _is_manager():
        return _403()
    if not _is_admin() and tenant_id != current_user.tenant_id:
        return _403()

    t    = Tenant.query.get_or_404(tenant_id)
    data = request.get_json() or {}
    try:
        t.name            = (data.get("name") or t.name).strip()
        t.short_name      = data.get("short_name", t.short_name) or None
        t.sector          = data.get("sector") or None
        t.activity_area   = data.get("activity_area") or None
        t.employee_count  = int(data["employee_count"]) if data.get("employee_count") else None
        t.contact_email   = data.get("contact_email") or None
        t.phone_number    = data.get("phone_number") or None
        t.website_url     = data.get("website_url") or None
        t.tax_office      = data.get("tax_office") or None
        t.tax_number      = data.get("tax_number") or None
        t.max_user_count  = int(data["max_user_count"]) if data.get("max_user_count") else t.max_user_count
        if data.get("license_end_date"):
            from datetime import date
            t.license_end_date = date.fromisoformat(data["license_end_date"])
        if data.get("package_id"):
            t.package_id = int(data["package_id"])
        db.session.commit()
        return jsonify({"success": True, "message": "Kurum güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_tenants_edit] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@micro_bp.route("/admin/tenants/toggle/<int:tenant_id>", methods=["POST"])
@login_required
def admin_tenants_toggle(tenant_id):
    if not _is_admin():
        return _403()

    t = Tenant.query.get_or_404(tenant_id)
    try:
        t.is_active = not t.is_active
        db.session.commit()
        state = "aktifleştirildi" if t.is_active else "arşivlendi"
        return jsonify({"success": True, "message": f"Kurum {state}.", "is_active": t.is_active})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_tenants_toggle] {e}")
        return jsonify({"success": False, "message": "İşlem sırasında hata oluştu."}), 500


# ── Paket Yönetimi ────────────────────────────────────────────────────────────

@micro_bp.route("/admin/packages")
@login_required
def admin_packages():
    if not _is_admin():
        return render_template("micro/errors/403.html"), 403

    try:
        from app.models.saas import SubscriptionPackage, SystemModule
        packages = SubscriptionPackage.query.order_by(SubscriptionPackage.name).all()
        modules  = SystemModule.query.order_by(SystemModule.name).all()
    except Exception:
        packages, modules = [], []

    return render_template("micro/admin/packages.html", packages=packages, modules=modules)


# ── Bileşen Senkronizasyonu ───────────────────────────────────────────────────

@micro_bp.route("/admin/components/sync", methods=["POST"])
@login_required
def admin_components_sync():
    if not _is_admin():
        return _403()

    try:
        from app.models.saas import RouteRegistry
        from flask import current_app as app

        synced = 0
        for rule in app.url_map.iter_rules():
            slug = rule.endpoint
            if not RouteRegistry.query.filter_by(endpoint=slug).first():
                db.session.add(RouteRegistry(
                    endpoint=slug,
                    url_pattern=str(rule),
                    methods=",".join(sorted(rule.methods or [])),
                ))
                synced += 1
        db.session.commit()
        return jsonify({"success": True, "message": f"{synced} yeni bileşen kaydedildi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_components_sync] {e}")
        return jsonify({"success": False, "message": "Senkronizasyon sırasında hata oluştu."}), 500


@micro_bp.route("/admin/components/update", methods=["POST"])
@login_required
def admin_components_update():
    if not _is_admin():
        return _403()

    data = request.get_json() or {}
    try:
        from app.models.saas import RouteRegistry
        for item in data.get("items", []):
            rec = RouteRegistry.query.filter_by(endpoint=item.get("endpoint")).first()
            if rec and item.get("component_slug"):
                rec.component_slug = item["component_slug"]
        db.session.commit()
        return jsonify({"success": True, "message": "Bileşen slug'ları güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_components_update] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


# ── Bildirim Merkezi Yönetimi ─────────────────────────────────────────────────

@micro_bp.route("/admin/notifications")
@login_required
def admin_notifications():
    if not _is_manager():
        return render_template("micro/errors/403.html"), 403

    from app.models.core import Notification
    from sqlalchemy.orm import joinedload
    if _is_admin():
        notifications = (Notification.query
                         .options(joinedload(Notification.user))
                         .order_by(Notification.created_at.desc()).limit(500).all())
        tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.name).all()
    else:
        notifications = (Notification.query
                         .options(joinedload(Notification.user))
                         .filter_by(tenant_id=current_user.tenant_id)
                         .order_by(Notification.created_at.desc()).limit(200).all())
        tenants = []

    return render_template("micro/admin/notifications.html",
                           notifications=notifications, tenants=tenants)


@micro_bp.route("/admin/notifications/delete/<int:notif_id>", methods=["POST"])
@login_required
def admin_notifications_delete(notif_id):
    if not _is_manager():
        return _403()

    from app.models.core import Notification
    n = Notification.query.get_or_404(notif_id)
    if not _is_admin() and n.tenant_id != current_user.tenant_id:
        return _403()

    try:
        # Soft delete: is_read=True ile işaretle
        n.is_read = True
        db.session.commit()
        return jsonify({"success": True, "message": "Bildirim silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_notifications_delete] {e}")
        return jsonify({"success": False, "message": "İşlem sırasında hata oluştu."}), 500


@micro_bp.route("/admin/notifications/broadcast", methods=["POST"])
@login_required
def admin_notifications_broadcast():
    if not _is_manager():
        return _403()

    data    = request.get_json() or {}
    title   = (data.get("title") or "").strip()
    message = (data.get("message") or "").strip()
    notif_type = data.get("type", "system_broadcast")

    if not title or not message:
        return jsonify({"success": False, "message": "Başlık ve mesaj zorunludur."}), 400

    try:
        from app.models.core import Notification
        if _is_admin():
            target_users = User.query.filter_by(is_active=True).all()
            if data.get("tenant_id"):
                target_users = User.query.filter_by(
                    is_active=True, tenant_id=int(data["tenant_id"])
                ).all()
        else:
            target_users = User.query.filter_by(
                is_active=True, tenant_id=current_user.tenant_id
            ).all()

        count = 0
        for u in target_users:
            n = Notification(
                user_id=u.id,
                tenant_id=u.tenant_id,
                notification_type=notif_type,
                title=title,
                message=message,
                link=data.get("link") or None,
            )
            db.session.add(n)
            count += 1

        db.session.commit()
        return jsonify({"success": True, "message": f"{count} kullanıcıya bildirim gönderildi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_notifications_broadcast] {e}")
        return jsonify({"success": False, "message": "Bildirim gönderilemedi."}), 500


@micro_bp.route("/admin/notifications/stats")
@login_required
def admin_notifications_stats():
    if not _is_manager():
        return _403()

    from app.models.core import Notification
    from sqlalchemy import func
    try:
        q = Notification.query
        if not _is_admin():
            q = q.filter_by(tenant_id=current_user.tenant_id)

        total   = q.count()
        unread  = q.filter_by(is_read=False).count()
        by_type = db.session.query(
            Notification.notification_type, func.count(Notification.id)
        )
        if not _is_admin():
            by_type = by_type.filter(Notification.tenant_id == current_user.tenant_id)
        by_type = by_type.group_by(Notification.notification_type).all()

        return jsonify({
            "success": True,
            "total": total,
            "unread": unread,
            "by_type": {t: c for t, c in by_type},
        })
    except Exception as e:
        current_app.logger.error(f"[admin_notifications_stats] {e}")
        return jsonify({"success": False, "message": "İstatistik alınamadı."}), 500


# ── SaaS Paket / Modül CRUD ───────────────────────────────────────────────────

@micro_bp.route("/admin/packages/add", methods=["POST"])
@login_required
def admin_packages_add():
    if not _is_admin():
        return _403()

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    code = (data.get("code") or "").strip().lower().replace(" ", "_")
    if not name or not code:
        return jsonify({"success": False, "message": "Ad ve kod zorunludur."}), 400

    try:
        from app.models.saas import SubscriptionPackage
        if SubscriptionPackage.query.filter_by(code=code).first():
            return jsonify({"success": False, "message": "Bu kod zaten kullanılıyor."}), 400
        pkg = SubscriptionPackage(name=name, code=code, description=data.get("description") or None)
        db.session.add(pkg)
        db.session.commit()
        return jsonify({"success": True, "message": "Paket oluşturuldu.", "id": pkg.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_packages_add] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/admin/packages/edit/<int:pkg_id>", methods=["POST"])
@login_required
def admin_packages_edit(pkg_id):
    if not _is_admin():
        return _403()

    from app.models.saas import SubscriptionPackage
    pkg  = SubscriptionPackage.query.get_or_404(pkg_id)
    data = request.get_json() or {}
    try:
        pkg.name        = (data.get("name") or pkg.name).strip()
        pkg.description = data.get("description") or pkg.description
        db.session.commit()
        return jsonify({"success": True, "message": "Paket güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_packages_edit] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@micro_bp.route("/admin/packages/toggle/<int:pkg_id>", methods=["POST"])
@login_required
def admin_packages_toggle(pkg_id):
    if not _is_admin():
        return _403()

    from app.models.saas import SubscriptionPackage
    pkg = SubscriptionPackage.query.get_or_404(pkg_id)
    try:
        pkg.is_active = not pkg.is_active
        db.session.commit()
        state = "aktifleştirildi" if pkg.is_active else "pasife alındı"
        return jsonify({"success": True, "message": f"Paket {state}.", "is_active": pkg.is_active})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_packages_toggle] {e}")
        return jsonify({"success": False, "message": "İşlem sırasında hata oluştu."}), 500


@micro_bp.route("/admin/modules/add", methods=["POST"])
@login_required
def admin_modules_add():
    if not _is_admin():
        return _403()

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    code = (data.get("code") or "").strip().lower().replace(" ", "_")
    if not name or not code:
        return jsonify({"success": False, "message": "Ad ve kod zorunludur."}), 400

    try:
        from app.models.saas import SystemModule
        if SystemModule.query.filter_by(code=code).first():
            return jsonify({"success": False, "message": "Bu kod zaten kullanılıyor."}), 400
        mod = SystemModule(name=name, code=code, description=data.get("description") or None)
        db.session.add(mod)
        db.session.commit()
        return jsonify({"success": True, "message": "Modül oluşturuldu.", "id": mod.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_modules_add] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/admin/modules/toggle/<int:mod_id>", methods=["POST"])
@login_required
def admin_modules_toggle(mod_id):
    if not _is_admin():
        return _403()

    from app.models.saas import SystemModule
    mod = SystemModule.query.get_or_404(mod_id)
    try:
        mod.is_active = not mod.is_active
        db.session.commit()
        state = "aktifleştirildi" if mod.is_active else "pasife alındı"
        return jsonify({"success": True, "message": f"Modül {state}.", "is_active": mod.is_active})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_modules_toggle] {e}")
        return jsonify({"success": False, "message": "İşlem sırasında hata oluştu."}), 500
