"""Dashboard Blueprint - main landing page after login."""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.models.core import User, Ticket

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="")


@dashboard_bp.route("/")
@login_required
def index():
    """Dashboard home - redirect based on role."""
    if current_user.role and current_user.role.name == "tenant_admin":
        return redirect(url_for("dashboard_bp.tenant_dashboard"))
        
    view = request.args.get("view", "classic")
    template = "dashboard/sideview.html" if view == "sideview" else "dashboard/classic.html"
    return render_template(template)


@dashboard_bp.route("/tenant-dashboard")
@login_required
def tenant_dashboard():
    """Tenant Administrator Dashboard."""
    tenant_id = current_user.tenant_id
    
    # 1. Kullanıcı Sayısı
    user_count = User.query.filter_by(tenant_id=tenant_id).count() if tenant_id else 0
    
    # 2. Aktif Destek Talepleri
    active_tickets = Ticket.query.filter_by(tenant_id=tenant_id, status="Bekliyor").count() if tenant_id else 0
    
    # 3. Paket Kullanım Limitleri
    package_limit = current_user.tenant.max_user_count if current_user.tenant else 0
    package_name = current_user.tenant.package.name if current_user.tenant and current_user.tenant.package else "Bilinmiyor"
    usage_percent = int((user_count / package_limit) * 100) if package_limit and package_limit > 0 else 0
    
    # 4. Son Aktiviteler (Son Talepler üzerinden simüle ediyoruz)
    recent_activities = []
    if tenant_id:
        recent_tickets = Ticket.query.filter_by(tenant_id=tenant_id).order_by(Ticket.created_at.desc()).limit(5).all()
        for t in recent_tickets:
            recent_activities.append({
                "source": "Destek Talebi",
                "subject": t.subject,
                "status": t.status,
                "date": t.created_at.strftime("%Y-%m-%d") if t.created_at else "",
                "priority": "Normal",
                "project": "İletişim"
            })
            
    stats = {
        "user_count": user_count,
        "active_tickets": active_tickets,
        "package_limit": package_limit,
        "package_name": package_name,
        "usage_percent": usage_percent
    }
    
    return render_template("dashboard/tenant_panel.html",
                           stats=stats,
                           recent_activities=recent_activities)

from flask import jsonify
from flask_babel import gettext as _

@dashboard_bp.route("/tenant-dashboard/update-strategy", methods=["POST"])
@login_required
def update_tenant_strategy():
    """Update tenant strategic identity."""
    if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
        
    tenant = current_user.tenant
    if not tenant:
        return jsonify({"success": False, "message": _("Kurum bulunamadı.")}), 404
        
    data = request.json
    tenant.purpose = data.get("purpose", tenant.purpose)
    tenant.vision = data.get("vision", tenant.vision)
    tenant.core_values = data.get("core_values", tenant.core_values)
    tenant.code_of_ethics = data.get("code_of_ethics", tenant.code_of_ethics)
    tenant.quality_policy = data.get("quality_policy", tenant.quality_policy)
    
    try:
        from app.models import db
        db.session.commit()
        return jsonify({"success": True, "message": _("Stratejik kimlik başarıyla güncellendi.")})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
