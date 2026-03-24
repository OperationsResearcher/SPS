"""Admin Blueprint - SaaS management (packages, modules, tenants)."""

import io
import re
from datetime import datetime

import pandas as pd
from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from sqlalchemy.orm import joinedload, selectinload

from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User, Ticket, Strategy, SubStrategy
from app.models.saas import ModuleComponentSlug, RouteRegistry, SystemModule, SubscriptionPackage
from app.models.process import Process, ProcessKpi, ProcessSubStrategyLink
from app.utils.process_utils import validate_process_parent_id, validate_same_tenant_user_ids, validate_same_tenant_sub_strategies, ensure_int_list, parse_optional_date

admin_bp = Blueprint("admin_bp", __name__)


def _require_admin():
    """Ensure current user has Admin role."""
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.role or current_user.role.name != "Admin":
        abort(403)


def _require_process_admin():
    """Ensure current user can manage processes (Admin, tenant_admin, executive_manager)."""
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.role or current_user.role.name not in ("Admin", "tenant_admin", "executive_manager"):
        abort(403)


def _slugify(text):
    """Convert name to code (snake_case)."""
    if not text:
        return ""
    tr_map = {"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u", "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u"}
    s = str(text).strip()
    for tr, en in tr_map.items():
        s = s.replace(tr, en)
    s = re.sub(r"[^\w]+", "_", s.lower()).strip("_")
    return s or "unnamed"


@admin_bp.route("/")
@login_required
def index():
    """Admin dashboard - summary stats and tenants overview."""
    _require_admin()
    tenants_list = (
        Tenant.query.options(joinedload(Tenant.package))
        .order_by(Tenant.name)
        .all()
    )
    users_count = User.query.filter_by(is_active=True).count()
    packages_count = SubscriptionPackage.query.filter_by(is_active=True).count()
    modules_count = SystemModule.query.filter_by(is_active=True).count()
    return render_template(
        "admin/index.html",
        tenants_list=tenants_list,
        tenants_count=len(tenants_list),
        users_count=users_count,
        packages_count=packages_count,
        modules_count=modules_count,
    )


@admin_bp.route("/packages", methods=["GET", "POST"])
@login_required
def packages():
    """Manage packages and modules."""
    _require_admin()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_module":
            name = (request.form.get("module_name") or "").strip()
            if name:
                code = _slugify(name)
                if SystemModule.query.filter_by(code=code).first():
                    flash("Bu modül kodu zaten mevcut.", "danger")
                else:
                    mod = SystemModule(name=name, code=code, is_active=True)
                    db.session.add(mod)
                    db.session.flush()
                    for slug in request.form.getlist("module_component_slugs"):
                        slug = (slug or "").strip()
                        if slug:
                            db.session.add(ModuleComponentSlug(module_id=mod.id, component_slug=slug))
                    db.session.commit()
                    flash("Modül eklendi.", "success")
            else:
                flash("Modül adı gerekli.", "danger")
        elif action == "edit_module":
            mod_id = request.form.get("module_id")
            mod = SystemModule.query.get(mod_id) if mod_id else None
            if mod:
                name = (request.form.get("module_name") or "").strip()
                if name:
                    mod.name = name
                    mod.code = _slugify(name)
                    ModuleComponentSlug.query.filter_by(module_id=mod.id).delete()
                    for slug in request.form.getlist("module_component_slugs"):
                        slug = (slug or "").strip()
                        if slug:
                            db.session.add(ModuleComponentSlug(module_id=mod.id, component_slug=slug))
                    db.session.commit()
                    flash("Modül güncellendi.", "success")
            else:
                flash("Modül bulunamadı.", "danger")
        elif action == "delete_module":
            mod_id = request.form.get("module_id")
            mod = SystemModule.query.get(mod_id) if mod_id else None
            if mod:
                # Kural 4: Hard delete yasağı — soft delete uygulanıyor
                for pkg in mod.packages:
                    pkg.modules.remove(mod)
                mod.is_active = False
                db.session.commit()
                flash("Modül devre dışı bırakıldı.", "success")
            else:
                flash("Modül bulunamadı.", "danger")
        elif action == "add_package":
            name = (request.form.get("package_name") or "").strip()
            if name:
                code = _slugify(name)
                if SubscriptionPackage.query.filter_by(code=code).first():
                    flash("Bu paket kodu zaten mevcut.", "danger")
                else:
                    pkg = SubscriptionPackage(name=name, code=code, is_active=True)
                    db.session.add(pkg)
                    mod_ids = request.form.getlist("package_modules")
                    db.session.flush()
                    for mid in mod_ids:
                        m = SystemModule.query.get(int(mid))
                        if m:
                            pkg.modules.append(m)
                    db.session.commit()
                    flash("Paket eklendi.", "success")
            else:
                flash("Paket adı gerekli.", "danger")
        elif action == "edit_package":
            pkg_id = request.form.get("package_id")
            pkg = SubscriptionPackage.query.get(pkg_id) if pkg_id else None
            if pkg:
                name = (request.form.get("package_name") or "").strip()
                if name:
                    pkg.name = name
                    pkg.code = _slugify(name)
                    pkg.modules = []
                    mod_ids = request.form.getlist("package_modules")
                    for mid in mod_ids:
                        m = SystemModule.query.get(int(mid))
                        if m:
                            pkg.modules.append(m)
                    db.session.commit()
                    flash("Paket güncellendi.", "success")
            else:
                flash("Paket bulunamadı.", "danger")
        elif action == "delete_package":
            pkg_id = request.form.get("package_id")
            pkg = SubscriptionPackage.query.get(pkg_id) if pkg_id else None
            if pkg:
                if pkg.tenants:
                    flash("Bu pakete bağlı kurumlar var, önce kurumların paketini değiştirin.", "danger")
                else:
                    # Kural 4: Hard delete yasağı — soft delete uygulanıyor
                    pkg.modules = []
                    pkg.is_active = False
                    db.session.commit()
                    flash("Paket devre dışı bırakıldı.", "success")
            else:
                flash("Paket bulunamadı.", "danger")
        return redirect(url_for("admin_bp.packages"))

    modules = SystemModule.query.filter_by(is_active=True).order_by(SystemModule.name).all()
    packages_list = SubscriptionPackage.query.filter_by(is_active=True).order_by(SubscriptionPackage.name).all()
    routes = RouteRegistry.query.order_by(RouteRegistry.endpoint).all()
    component_slugs = sorted(
        {r.component_slug for r in RouteRegistry.query.filter(RouteRegistry.component_slug.isnot(None), RouteRegistry.component_slug != "").all()},
        key=str.lower,
    )
    # Modül başına bileşen slug listesi (şablon için önceden hesapla)
    module_slugs_map = {m.id: [mcs.component_slug for mcs in m.component_slugs] for m in modules}
    return render_template(
        "admin/packages.html",
        component_slugs=component_slugs,
        module_slugs_map=module_slugs_map,
        modules=modules,
        packages_list=packages_list,
        routes=routes,
        active_tab="packages"
    )


@admin_bp.route("/components/sync", methods=["POST"])
@login_required
def components_sync():
    """Rota keşfi - url_map'teki tüm rotaları RouteRegistry'ye ekler (static hariç)."""
    _require_admin()
    added_count = 0
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        
        try:
            valid_methods = [m for m in rule.methods if m not in ['OPTIONS', 'HEAD']]
            methods_str = ", ".join(valid_methods) if valid_methods else "GET"

            existing = RouteRegistry.query.filter_by(endpoint=rule.endpoint).first()
            if not existing:
                new_route = RouteRegistry(
                    endpoint=rule.endpoint,
                    url_rule=str(rule),
                    methods=methods_str
                )
                db.session.add(new_route)
                db.session.commit() # Her başarılı kayıtta commit yap
                added_count += 1
            else:
                existing.methods = methods_str
                existing.url_rule = str(rule)
                db.session.commit()
        except Exception as e:
            db.session.rollback() # Hata varsa geri al ve diğer rotaya geç
            continue
            
    return jsonify({"success": True, "message": f"{added_count} yeni rota eklendi.", "added": added_count})


@admin_bp.route("/components/update", methods=["POST"])
@login_required
def components_update():
    """AJAX ile bileşen slug güncelleme."""
    _require_admin()
    data = request.get_json() or {}
    rid = data.get("id")
    slug = (data.get("component_slug") or "").strip() or None
    if not rid:
        return jsonify({"success": False, "message": "Geçersiz rota ID."}), 400
    rec = RouteRegistry.query.get(rid)
    if not rec:
        return jsonify({"success": False, "message": "Rota bulunamadı."}), 404
    rec.component_slug = slug
    db.session.commit()
    return jsonify({"success": True, "message": "Bileşen adı kaydedildi."})


def _require_admin_or_tenant_admin():
    """Admin, tenant_admin veya executive_manager erişebilir."""
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.role or current_user.role.name not in ("Admin", "tenant_admin", "executive_manager"):
        abort(403)


@admin_bp.route("/tenants")
@login_required
def tenants():
    """List tenants - Admin tümünü, tenant_admin/executive_manager sadece kendi kurumunu görür."""
    _require_admin_or_tenant_admin()
    q = Tenant.query.options(joinedload(Tenant.package)).order_by(Tenant.name)
    if current_user.role.name == "Admin":
        tenants_list = q.all()
    else:
        if not current_user.tenant_id:
            abort(403)
        tenants_list = q.filter_by(id=current_user.tenant_id).all()
    packages_list = SubscriptionPackage.query.filter_by(is_active=True).order_by(SubscriptionPackage.name).all()
    is_platform_admin = current_user.role and current_user.role.name == "Admin"
    return render_template(
        "admin/tenants.html",
        tenants_list=tenants_list,
        packages_list=packages_list,
        active_tab="tenants",
        is_platform_admin=is_platform_admin
    )


@admin_bp.route("/strategy-management")
@login_required
def strategy_management():
    """Stratejik planlama akış yapısı - Admin tüm kurumları, tenant_admin/executive_manager sadece kendi kurumunu görür."""
    _require_admin_or_tenant_admin()
    tenant_id = request.args.get("tenant_id", type=int)
    tenants_q = Tenant.query.filter_by(is_active=True).order_by(Tenant.name)
    if current_user.role and current_user.role.name != "Admin":
        if not current_user.tenant_id:
            abort(403)
        tenants_q = tenants_q.filter_by(id=current_user.tenant_id)
    tenants_list = tenants_q.all()
    selected_tenant = None
    strategies = []
    processes = []
    if current_user.role and current_user.role.name != "Admin" and current_user.tenant_id:
        tenant_id = current_user.tenant_id
    if tenant_id:
        selected_tenant = Tenant.query.get(tenant_id)
        if selected_tenant:
            strategies = (
                Strategy.query.filter_by(tenant_id=tenant_id, is_active=True)
                .options(selectinload(Strategy.sub_strategies))
                .order_by(Strategy.code)
                .all()
            )
            processes = (
                Process.query.filter_by(tenant_id=tenant_id, is_active=True)
                .order_by(Process.code)
                .all()
            )
    return render_template(
        "admin/strategy_mgmt.html",
        tenants_list=tenants_list,
        selected_tenant=selected_tenant,
        strategies=strategies,
        processes=processes,
        active_tab="strategy_mgmt"
    )


def _parse_tenant_form():
    """Ortak form alanlarını parse et."""
    return {
        "name": (request.form.get("name") or "").strip(),
        "short_name": (request.form.get("short_name") or "").strip(),
        "activity_area": (request.form.get("activity_area") or "").strip() or None,
        "sector": (request.form.get("sector") or "").strip() or None,
        "employee_count": int(x) if (x := request.form.get("employee_count")) and x.strip().isdigit() else None,
        "contact_email": (request.form.get("contact_email") or "").strip() or None,
        "phone_number": (request.form.get("phone_number") or "").strip() or None,
        "website_url": (request.form.get("website_url") or "").strip() or None,
        "tax_office": (request.form.get("tax_office") or "").strip() or None,
        "tax_number": (request.form.get("tax_number") or "").strip() or None,
        "package_id": request.form.get("package_id") or None,
        "max_user_count": int(x) if (x := request.form.get("max_user_count")) and x.strip().isdigit() else 5,
        "license_end_date": _parse_date(request.form.get("license_end_date")),
    }


def _parse_date(val):
    """YYYY-MM-DD string'den date objesi."""
    if not val or not isinstance(val, str):
        return None
    try:
        return datetime.strptime(val.strip()[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@admin_bp.route("/tenants/add", methods=["POST"])
@login_required
def tenants_add():
    """Add new tenant."""
    _require_admin()
    data = _parse_tenant_form()
    name = data["name"] or data["short_name"]
    if not name:
        flash("Kısa ad veya ticari ünvan gerekli.", "danger")
        return redirect(url_for("admin_bp.tenants"))
    filters = [Tenant.name == name]
    if data["short_name"]:
        filters.append(Tenant.short_name == data["short_name"])
    existing = Tenant.query.filter(db.or_(*filters)).first()
    if existing:
        flash("Bu kurum adı veya kısa ad zaten mevcut.", "danger")
        return redirect(url_for("admin_bp.tenants"))
    t = Tenant(
        name=name,
        short_name=data["short_name"] or None,
        activity_area=data["activity_area"],
        sector=data["sector"],
        employee_count=data["employee_count"],
        contact_email=data["contact_email"],
        phone_number=data["phone_number"],
        website_url=data["website_url"],
        tax_office=data["tax_office"],
        tax_number=data["tax_number"],
        package_id=int(data["package_id"]) if data["package_id"] else None,
        max_user_count=data["max_user_count"] if data["max_user_count"] else 5,
        license_end_date=data["license_end_date"],
        is_active=True,
    )
    db.session.add(t)
    db.session.commit()
    flash("Kurum eklendi.", "success")
    return redirect(url_for("admin_bp.tenants"))


@admin_bp.route("/tenants/edit/<int:tenant_id>", methods=["POST"])
@login_required
def tenants_edit(tenant_id):
    """Edit tenant - Admin her kurumu, tenant_admin sadece kendi kurumunu düzenleyebilir."""
    _require_admin_or_tenant_admin()
    t = Tenant.query.get(tenant_id)
    if not t:
        flash("Kurum bulunamadı.", "danger")
        return redirect(url_for("admin_bp.tenants"))
    if current_user.role.name != "Admin" and t.id != current_user.tenant_id:
        abort(403)
    data = _parse_tenant_form()
    name = data["name"] or data["short_name"]
    if not name:
        flash("Kısa ad veya ticari ünvan gerekli.", "danger")
        return redirect(url_for("admin_bp.tenants"))
    t.name = name
    t.short_name = data["short_name"] or None
    t.activity_area = data["activity_area"]
    t.sector = data["sector"]
    t.employee_count = data["employee_count"]
    t.contact_email = data["contact_email"]
    t.phone_number = data["phone_number"]
    t.website_url = data["website_url"]
    t.tax_office = data["tax_office"]
    t.tax_number = data["tax_number"]
    t.package_id = int(data["package_id"]) if data["package_id"] else None
    t.max_user_count = data["max_user_count"] if data["max_user_count"] else 5
    t.license_end_date = data["license_end_date"]
    db.session.commit()
    flash("Kurum güncellendi.", "success")
    return redirect(url_for("admin_bp.tenants"))


@admin_bp.route("/tenants/archive/<int:tenant_id>", methods=["POST"])
@login_required
def tenants_archive(tenant_id):
    """Archive tenant (soft delete - set is_active=False)."""
    _require_admin()
    t = Tenant.query.get(tenant_id)
    if not t:
        flash("Kurum bulunamadı.", "danger")
        return redirect(url_for("admin_bp.tenants"))
    t.is_active = False
    db.session.commit()
    flash("Kurum arşivlendi.", "success")
    return redirect(url_for("admin_bp.tenants"))


# ---------------------------------------------------------------------------
# Users (Kullanıcı Yönetimi)
# ---------------------------------------------------------------------------

def _require_user_management():
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.role:
        abort(403)

@admin_bp.route("/users")
@login_required
def users():
    """List users - Admin sees all, tenants see theirs."""
    _require_user_management()
    if current_user.role.name == "Admin":
        users_list = (
            User.query.options(joinedload(User.tenant), joinedload(User.role))
            .order_by(User.first_name, User.email)
            .all()
        )
        tenants_list = Tenant.query.filter_by(is_active=True).order_by(Tenant.name).all()
        roles_list = Role.query.order_by(Role.name).all()
    else:
        users_list = (
            User.query.options(joinedload(User.tenant), joinedload(User.role))
            .filter_by(tenant_id=current_user.tenant_id)
            .order_by(User.first_name, User.email)
            .all()
        )
        tenants_list = Tenant.query.filter_by(id=current_user.tenant_id).all()
        # tenant_admin atama/değiştirme yalnızca Admin'de kalır.
        roles_list = Role.query.filter(Role.name.in_(["executive_manager", "standard_user"])).order_by(Role.name).all()

    return render_template(
        "admin/users.html",
        users_list=users_list,
        tenants_list=tenants_list,
        roles_list=roles_list,
        active_tab="users"
    )

def _parse_user_form():
    """Kullanıcı form alanlarını parse et."""
    return {
        "email": (request.form.get("email") or "").strip().lower(),
        "first_name": (request.form.get("first_name") or "").strip() or None,
        "last_name": (request.form.get("last_name") or "").strip() or None,
        "phone_number": (request.form.get("phone_number") or "").strip() or None,
        "job_title": (request.form.get("job_title") or "").strip() or None,
        "department": (request.form.get("department") or "").strip() or None,
        "profile_picture": (request.form.get("profile_picture") or "").strip() or None,
        "tenant_id": request.form.get("tenant_id") or None,
        "role_id": request.form.get("role_id") or None,
        "password": request.form.get("password") or "",
    }


@admin_bp.route("/users/add", methods=["POST"])
@login_required
def users_add():
    """Add new user."""
    _require_user_management()
    
    if current_user.role.name == "standard_user":
        abort(403)

    data = _parse_user_form()
    
    if current_user.role.name != "Admin":
        data["tenant_id"] = current_user.tenant_id
        
    if not data["email"]:
        flash("E-posta zorunludur.", "danger")
        return redirect(url_for("admin_bp.users"))
    if User.query.filter_by(email=data["email"]).first():
        flash("Bu e-posta adresi zaten kayıtlı.", "danger")
        return redirect(url_for("admin_bp.users"))
    if len(data["password"]) < 6:
        flash("Şifre en az 6 karakter olmalıdır.", "danger")
        return redirect(url_for("admin_bp.users"))
        
    target_role = Role.query.get(int(data["role_id"])) if data["role_id"] else None
    if current_user.role.name != "Admin" and target_role and target_role.name == "tenant_admin":
        flash("Kurum Yöneticisi atama işlemi sadece Admin tarafından yapılabilir.", "danger")
        return redirect(url_for("admin_bp.users"))
    if target_role and target_role.name == "tenant_admin":
        existing_admin = User.query.filter_by(tenant_id=data["tenant_id"], is_active=True).join(Role).filter(Role.name == "tenant_admin").first()
        if existing_admin:
            flash("Dikkat: Bu kurumda zaten aktif bir Kurum Yöneticisi var.", "danger")
            return redirect(url_for("admin_bp.users"))

    u = User(
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone_number=data["phone_number"],
        job_title=data["job_title"],
        department=data["department"],
        profile_picture=data["profile_picture"],
        tenant_id=int(data["tenant_id"]) if data["tenant_id"] else None,
        role_id=int(data["role_id"]) if data["role_id"] else None,
        is_active=True,
    )
    db.session.add(u)
    db.session.commit()
    flash("Kullanıcı eklendi.", "success")
    return redirect(url_for("admin_bp.users"))


@admin_bp.route("/users/edit/<int:user_id>", methods=["POST"])
@login_required
def users_edit(user_id):
    """Edit user."""
    _require_user_management()
    u = User.query.get(user_id)
    if not u:
        flash("Kullanıcı bulunamadı.", "danger")
        return redirect(url_for("admin_bp.users"))
        
    if current_user.role.name != "Admin" and u.tenant_id != current_user.tenant_id:
        abort(403)
        
    if current_user.role.name == "standard_user" and u.id != current_user.id:
        abort(403)
        
    if current_user.role.name != "Admin" and u.role and u.role.name == "tenant_admin":
        flash("Kurum Yöneticisi hesabını sadece Admin düzenleyebilir.", "danger")
        return redirect(url_for("admin_bp.users"))

    data = _parse_user_form()
    
    if current_user.role.name != "Admin":
        data["tenant_id"] = current_user.tenant_id
        
    if not data["email"]:
        flash("E-posta zorunludur.", "danger")
        return redirect(url_for("admin_bp.users"))
    existing = User.query.filter_by(email=data["email"]).first()
    if existing and existing.id != u.id:
        flash("Bu e-posta adresi başka bir kullanıcıya aittir.", "danger")
        return redirect(url_for("admin_bp.users"))
        
    target_role = Role.query.get(int(data["role_id"])) if data["role_id"] else None
    if current_user.role.name != "Admin" and target_role and target_role.name == "tenant_admin":
        flash("Kurum Yöneticisi rolü sadece Admin tarafından atanabilir/değiştirilebilir.", "danger")
        return redirect(url_for("admin_bp.users"))
    if target_role and target_role.name == "tenant_admin" and (not u.role or u.role.name != "tenant_admin"):
        existing_admin = User.query.filter_by(tenant_id=data["tenant_id"], is_active=True).join(Role).filter(Role.name == "tenant_admin").first()
        if existing_admin:
            flash("Dikkat: Bu kurumda zaten aktif bir Kurum Yöneticisi var.", "danger")
            return redirect(url_for("admin_bp.users"))

    u.email = data["email"]
    u.first_name = data["first_name"]
    u.last_name = data["last_name"]
    u.phone_number = data["phone_number"]
    u.job_title = data["job_title"]
    u.department = data["department"]
    u.profile_picture = data["profile_picture"]
    u.tenant_id = int(data["tenant_id"]) if data["tenant_id"] else None
    u.role_id = int(data["role_id"]) if data["role_id"] else None
    if data["password"]:
        u.password_hash = generate_password_hash(data["password"])
    db.session.commit()
    flash("Kullanıcı güncellendi.", "success")
    return redirect(url_for("admin_bp.users"))


@admin_bp.route("/users/toggle/<int:user_id>", methods=["POST"])
@login_required
def users_toggle(user_id):
    """Toggle user active status (soft delete)."""
    _require_user_management()
    u = User.query.get(user_id)
    if not u:
        flash("Kullanıcı bulunamadı.", "danger")
        return redirect(url_for("admin_bp.users"))
        
    if current_user.role.name != "Admin" and u.tenant_id != current_user.tenant_id:
        abort(403)
        
    if current_user.role.name == "standard_user":
        abort(403)
        
    if current_user.role.name != "Admin" and u.role and u.role.name == "tenant_admin":
        flash("Kurum Yöneticisi hesabını sadece Admin pasife/aktife alabilir.", "danger")
        return redirect(url_for("admin_bp.users"))
        
    if u.id == current_user.id:
        flash("Kendi hesabınızı devre dışı bırakamazsınız.", "danger")
        return redirect(url_for("admin_bp.users"))
    u.is_active = not u.is_active
    db.session.commit()
    flash("Kullanıcı durumu güncellendi.", "success")
    return redirect(url_for("admin_bp.users"))


@admin_bp.route("/users/bulk-template")
@login_required
def users_bulk_template():
    """Download template for bulk user import."""
    _require_user_management()
    
    if current_user.role.name == "standard_user":
        abort(403)
        
    output = io.BytesIO()
    data = [{
        "Ad": "Ahmet",
        "Soyad": "Yılmaz",
        "E-posta": "ahmet@ornek.com",
        "Şifre": "123456",
        "Unvan": "Mühendis",
        "Telefon": "5551234567"
    }]
    df = pd.DataFrame(data)
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    
    return send_file(
        output,
        download_name="kullanici_sablonu.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@admin_bp.route("/users/bulk-import", methods=["POST"])
@login_required
def users_bulk_import():
    """Handle bulk user import from Excel/CSV."""
    _require_user_management()
    
    if current_user.role.name == "standard_user":
        return jsonify({"status": "error", "message": "Yetkisiz işlem."}), 403

    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Dosya bulunamadı."}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Dosya seçilmedi."}), 400

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            return jsonify({"status": "error", "message": "Geçersiz dosya formatı. Lütfen Excel veya CSV yükleyin."}), 400

        # Replace NaN with None
        df = df.where(pd.notnull(df), None)
        
        # Mapping Turkish columns to English keys
        col_map = {
            "Ad": "first_name", "Soyad": "last_name", "E-posta": "email",
            "Şifre": "password", "Unvan": "job_title", "Telefon": "phone_number",
            "Departman": "department"
        }
        
        # Find matching columns
        actual_cols = df.columns.tolist()
        mapped_df = pd.DataFrame()
        
        email_col = next((c for c in actual_cols if "posta" in c.lower() or "mail" in c.lower()), None)
        if not email_col:
            return jsonify({"status": "error", "message": "Dosyada E-posta sütunu bulunamadı."}), 400
            
        success_count = 0
        duplicate_count = 0
        
        tenant_id = current_user.tenant_id
        default_role = Role.query.filter_by(name="standard_user").first()
        if not default_role:
             default_role = Role.query.first()
             
        for index, row in df.iterrows():
            email = str(row[email_col]).strip() if pd.notnull(row[email_col]) else ""
            if not email or email.lower() == "none" or email.lower() == "nan":
                continue
            
            # Check unique email
            if User.query.filter_by(email=email).first():
                duplicate_count += 1
                continue
            
            # Get fields based on column names or synonyms
            fn = str(row["Ad"]) if "Ad" in actual_cols and pd.notnull(row["Ad"]) else None
            ln = str(row["Soyad"]) if "Soyad" in actual_cols and pd.notnull(row["Soyad"]) else None
            pwd = str(row["Şifre"]) if "Şifre" in actual_cols and pd.notnull(row["Şifre"]) else "123456"
            jt = str(row["Unvan"]) if "Unvan" in actual_cols and pd.notnull(row["Unvan"]) else None
            ph = str(row["Telefon"]) if "Telefon" in actual_cols and pd.notnull(row["Telefon"]) else None
            dp = str(row["Departman"]) if "Departman" in actual_cols and pd.notnull(row["Departman"]) else None
            
            u = User(
                email=email,
                first_name=fn,
                last_name=ln,
                password_hash=generate_password_hash(pwd),
                job_title=jt,
                phone_number=ph,
                department=dp,
                tenant_id=tenant_id,
                role_id=default_role.id if default_role else None,
                is_active=True
            )
            db.session.add(u)
            success_count += 1
            
        db.session.commit()
        
        msg = f"{success_count} kullanıcı başarıyla eklendi."
        if duplicate_count > 0:
            msg += f" {duplicate_count} e-posta zaten mevcuttu."
            
        return jsonify({"status": "success", "message": msg})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Dosya okuma hatası: {str(e)}"}), 500


@admin_bp.route("/kule-iletisim")
@login_required
def kule_iletisim():
    """Kule İletişim yönetim paneli (Admin ve Yönetici erişimi)."""
    if current_user.role.name not in ['Admin', 'tenant_admin', 'executive_manager']:
        flash("Bu sayfayı görüntüleme yetkiniz yok.", "warning")
        return redirect(url_for('dashboard_bp.index'))
    
    # Filter by tenant if not Admin
    query = Ticket.query
    if current_user.role.name != 'Admin':
        query = query.filter_by(tenant_id=current_user.tenant_id)
        
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    total = len(tickets)
    pending = sum(1 for t in tickets if t.status == 'Bekliyor')
    in_progress = sum(1 for t in tickets if t.status == 'İnceleniyor')
    resolved = sum(1 for t in tickets if t.status == 'Çözüldü')
    
    return render_template(
        "admin/kule_iletisim.html",
        active_tab="kule",
        tickets=tickets,
        total_count=total,
        pending_count=pending,
        in_progress_count=in_progress,
        resolved_count=resolved
    )


@admin_bp.route("/kule-iletisim/<int:ticket_id>/detail")
@login_required
def kule_ticket_detail(ticket_id):
    if current_user.role.name not in ['Admin', 'tenant_admin', 'executive_manager']:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        
    ticket = Ticket.query.get_or_404(ticket_id)
    if current_user.role.name != 'Admin' and ticket.tenant_id != current_user.tenant_id:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        
    return jsonify({
        "success": True,
        "ticket": {
            "id": ticket.id,
            "user_name": f"{ticket.user.first_name or ''} {ticket.user.last_name or ''}".strip(),
            "tenant_name": ticket.tenant.name if ticket.tenant else 'Bireysel',
            "subject": ticket.subject,
            "message": ticket.message,
            "page_url": ticket.page_url,
            "screenshot_path": ticket.screenshot_path,
            "status": ticket.status,
            "admin_note": ticket.admin_note,
            "created_at": ticket.created_at.strftime('%d.%m.%Y %H:%M')
        }
    })


@admin_bp.route("/kule-iletisim/<int:ticket_id>/update", methods=["POST"])
@login_required
def kule_ticket_update(ticket_id):
    if current_user.role.name not in ['Admin', 'tenant_admin', 'executive_manager']:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        
    ticket = Ticket.query.get_or_404(ticket_id)
    if current_user.role.name != 'Admin' and ticket.tenant_id != current_user.tenant_id:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        
    data = request.get_json()
    new_status = data.get("status")
    admin_note = data.get("admin_note")
    
    if new_status:
        ticket.status = new_status
    if admin_note is not None:
        ticket.admin_note = admin_note
        
    db.session.commit()
    return jsonify({"success": True})


# ──────────────────────────────────────────────────
# Admin Süreç CRUD (Plan Faz 3)
# ──────────────────────────────────────────────────

@admin_bp.route("/get-process/<int:process_id>")
@login_required
def admin_get_process(process_id):
    """Süreç bilgilerini getir - admin/edit için."""
    _require_process_admin()
    p = Process.query.options(
        joinedload(Process.leaders),
        joinedload(Process.members),
        joinedload(Process.owners),
        selectinload(Process.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.sub_strategy)
    ).filter_by(id=process_id, is_active=True).first_or_404()
    if p.tenant_id != current_user.tenant_id and current_user.role.name != "Admin":
        abort(403)
    return jsonify({
        "success": True,
        "process": {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "english_name": p.english_name,
            "description": p.description,
            "document_no": p.document_no,
            "revision_no": p.revision_no,
            "revision_date": str(p.revision_date) if p.revision_date else "",
            "first_publish_date": str(p.first_publish_date) if p.first_publish_date else "",
            "start_date": str(p.start_date) if p.start_date else "",
            "end_date": str(p.end_date) if p.end_date else "",
            "status": p.status,
            "progress": p.progress,
            "parent_id": p.parent_id,
            "start_boundary": p.start_boundary,
            "end_boundary": p.end_boundary,
            "weight": p.weight,
            "leader_ids": [u.id for u in p.leaders],
            "member_ids": [u.id for u in p.members],
            "owner_ids": [u.id for u in p.owners],
            "sub_strategy_ids": [s.id for s in p.sub_strategies],
        }
    })


@admin_bp.route("/create-process", methods=["POST"])
@login_required
def admin_create_process():
    """Admin süreç oluştur."""
    _require_process_admin()
    if not request.is_json:
        return jsonify({"success": False, "message": "Content-Type application/json olmalı"}), 400
    data = request.get_json() or {}
    name = (data.get("name") or data.get("ad") or "").strip()
    if not name:
        return jsonify({"success": False, "message": "Süreç adı zorunludur"}), 400

    tenant_id = current_user.tenant_id
    parent_id_raw = data.get("parent_id")
    parent_id = validate_process_parent_id(None, parent_id_raw, tenant_id)

    new_process = Process(
        tenant_id=tenant_id,
        parent_id=parent_id,
        code=data.get("code") or None,
        name=name,
        english_name=data.get("english_name") or None,
        description=(data.get("description") or "").strip() or None,
        document_no=(data.get("document_no") or "").strip() or None,
        revision_no=(data.get("revision_no") or "").strip() or None,
        status=data.get("status", "Aktif"),
        progress=int(data.get("progress", 0) or 0),
        start_boundary=(data.get("start_boundary") or "").strip() or None,
        end_boundary=(data.get("end_boundary") or "").strip() or None,
    )
    for field, attr in [
        ("revision_date", "revision_date"),
        ("first_publish_date", "first_publish_date"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
    ]:
        if data.get(field):
            val = parse_optional_date(data.get(field))
            if val:
                setattr(new_process, attr, val)
    if data.get("weight") is not None and str(data.get("weight", "")).strip() != "":
        try:
            new_process.weight = min(100.0, max(0.0, float(data.get("weight"))))
        except (ValueError, TypeError):
            pass

    db.session.add(new_process)
    db.session.flush()

    leader_ids = ensure_int_list(data.get("leader_ids"))
    member_ids = ensure_int_list(data.get("member_ids"))
    sub_strategy_ids = ensure_int_list(data.get("sub_strategy_ids") or data.get("strateji_ids"))
    if leader_ids:
        new_process.leaders = validate_same_tenant_user_ids(tenant_id, leader_ids)
    if member_ids:
        new_process.members = validate_same_tenant_user_ids(tenant_id, member_ids)
    if sub_strategy_ids:
        new_process.sub_strategies = validate_same_tenant_sub_strategies(tenant_id, sub_strategy_ids)

    db.session.commit()
    return jsonify({"success": True, "message": "Süreç başarıyla oluşturuldu", "id": new_process.id})


@admin_bp.route("/add-process", methods=["POST"])
@login_required
def admin_add_process():
    """Admin panel hiyerarşik ekleme - create ile aynı."""
    return admin_create_process()


@admin_bp.route("/update-process/<int:process_id>", methods=["PUT", "POST"])
@login_required
def admin_update_process(process_id):
    """Admin süreç güncelle."""
    _require_process_admin()
    if not request.is_json:
        return jsonify({"success": False, "message": "Content-Type application/json olmalı"}), 400
    p = Process.query.filter_by(id=process_id, is_active=True).first_or_404()
    if p.tenant_id != current_user.tenant_id and current_user.role.name != "Admin":
        abort(403)

    data = request.get_json() or {}
    p.code = data.get("code", p.code)
    p.name = data.get("name", p.name)
    p.english_name = data.get("english_name", p.english_name)
    p.description = data.get("description", p.description)
    p.document_no = data.get("document_no", p.document_no)
    p.revision_no = data.get("revision_no", p.revision_no)
    p.status = data.get("status", p.status)
    p.progress = int(data.get("progress", p.progress) or 0)
    p.start_boundary = data.get("start_boundary", p.start_boundary)
    p.end_boundary = data.get("end_boundary", p.end_boundary)
    parent_id_raw = data.get("parent_id")
    p.parent_id = validate_process_parent_id(p.id, parent_id_raw, p.tenant_id)

    for field, attr in [
        ("revision_date", "revision_date"),
        ("first_publish_date", "first_publish_date"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
    ]:
        if data.get(field):
            val = parse_optional_date(data.get(field))
            if val:
                setattr(p, attr, val)
    if data.get("weight") is not None and str(data.get("weight", "")).strip() != "":
        try:
            p.weight = min(100.0, max(0.0, float(data.get("weight"))))
        except (ValueError, TypeError):
            pass

    if "leader_ids" in data:
        ids = ensure_int_list(data.get("leader_ids"))
        p.leaders = validate_same_tenant_user_ids(p.tenant_id, ids) if ids else []
    if "member_ids" in data:
        ids = ensure_int_list(data.get("member_ids"))
        p.members = validate_same_tenant_user_ids(p.tenant_id, ids) if ids else []
    if "sub_strategy_ids" in data or "strateji_ids" in data:
        ids = ensure_int_list(data.get("sub_strategy_ids") or data.get("strateji_ids"))
        p.sub_strategies = validate_same_tenant_sub_strategies(p.tenant_id, ids) if ids else []

    db.session.commit()
    return jsonify({"success": True, "message": "Süreç başarıyla güncellendi"})


@admin_bp.route("/delete-process/<int:process_id>", methods=["DELETE", "POST"])
@login_required
def admin_delete_process(process_id):
    """Admin süreç silme (soft delete)."""
    _require_process_admin()
    p = Process.query.filter_by(id=process_id, is_active=True).first_or_404()
    if p.tenant_id != current_user.tenant_id and current_user.role.name != "Admin":
        abort(403)
    from datetime import timezone as tz
    p.is_active = False
    p.deleted_at = datetime.now(tz.utc)
    p.deleted_by = current_user.id
    db.session.commit()
    return jsonify({"success": True, "message": "Süreç başarıyla silindi"})