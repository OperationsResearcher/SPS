"""Dashboard Blueprint - main landing page after login."""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload, selectinload
from app.models.core import User, Ticket, Strategy

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="")


@dashboard_bp.route("/performans-kartim")
@login_required
def performans_kartim():
    """Performans Kartım - Bireysel performans göstergeleri ve faaliyetler."""
    return render_template("bireysel_panel.html")


@dashboard_bp.route("/")
@login_required
def index():
    """Dashboard home - redirect based on role."""
    if current_user.role and current_user.role.name == "tenant_admin":
        return redirect(url_for("dashboard_bp.tenant_dashboard"))
        
    view = request.args.get("view", "classic")
    template = "dashboard/sideview.html" if view == "sideview" else "dashboard/classic.html"
    return render_template(template)


@dashboard_bp.route("/kurum-paneli")
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
                "date": t.created_at.strftime("%d.%m.%Y %H:%M") if t.created_at else "",
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
    
    # 5. Stratejiler (sadece aktif)
    strategies = []
    if tenant_id:
        strategies = Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).options(
            selectinload(Strategy.sub_strategies)
        ).all()
    
    return render_template("dashboard/tenant_panel.html",
                           stats=stats,
                           recent_activities=recent_activities,
                           strategies=strategies)

from flask import jsonify

@dashboard_bp.route("/kurum-paneli/update-strategy", methods=["POST"])
@login_required
def update_tenant_strategy():
    """Update tenant strategic identity."""
    if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        
    tenant = current_user.tenant
    if not tenant:
        return jsonify({"success": False, "message": "Kurum bulunamadı."}), 404
        
    data = request.json
    field_name = data.get("field_name")
    field_value = data.get("field_value")
    
    if field_name in ["purpose", "vision", "core_values", "code_of_ethics", "quality_policy"]:
        setattr(tenant, field_name, field_value)
    else:
        # Fallback for old multi-field form, if any
        tenant.purpose = data.get("purpose", tenant.purpose)
        tenant.vision = data.get("vision", tenant.vision)
        tenant.core_values = data.get("core_values", tenant.core_values)
        tenant.code_of_ethics = data.get("code_of_ethics", tenant.code_of_ethics)
        tenant.quality_policy = data.get("quality_policy", tenant.quality_policy)
    
    try:
        from app.models import db
        db.session.commit()
        return jsonify({"success": True, "message": "Başarıyla güncellendi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@dashboard_bp.route("/kurum-paneli/add-strategy", methods=["POST"])
@login_required
def add_strategy():
    """Add a new Main Strategy."""
    if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        
    tenant_id = current_user.tenant_id
    data = request.json
    
    title = data.get("title")
    if not title:
        return jsonify({"success": False, "message": "Strateji adı zorunludur."}), 400
        
    from app.models.core import Strategy
    from app.models import db
    
    new_strategy = Strategy(
        tenant_id=tenant_id,
        title=title,
        description=data.get("description", "")
    )
    
    try:
        db.session.add(new_strategy)
        db.session.commit()
        return jsonify({"success": True, "message": "Ana strateji başarıyla eklendi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@dashboard_bp.route("/kurum-paneli/add-sub-strategy", methods=["POST"])
@login_required
def add_sub_strategy():
    """Add a new Sub Strategy."""
    if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        
    data = request.json
    strategy_id = data.get("strategy_id")
    title = data.get("title")
    
    if not strategy_id or not title:
        return jsonify({"success": False, "message": "Ana strateji ID ve Alt strateji adı zorunludur."}), 400
        
    from app.models.core import SubStrategy
    from app.models import db
    
    new_sub = SubStrategy(
        strategy_id=strategy_id,
        title=title,
        description=data.get("description", "")
    )
    
    try:
        db.session.add(new_sub)
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji başarıyla eklendi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@dashboard_bp.route("/kurum-paneli/update-main-strategy/<int:strategy_id>", methods=["POST"])
@login_required
def update_main_strategy(strategy_id):
    """Ana stratejiyi güncelle."""
    if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
    st = Strategy.query.filter_by(id=strategy_id, tenant_id=current_user.tenant_id).first_or_404()
    data = request.json or {}
    title = data.get("title")
    if not title or not str(title).strip():
        return jsonify({"success": False, "message": "Strateji adı zorunludur."}), 400
    st.title = str(title).strip()
    st.description = data.get("description", st.description) or ""
    try:
        from app.models import db
        db.session.commit()
        return jsonify({"success": True, "message": "Ana strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@dashboard_bp.route("/kurum-paneli/delete-main-strategy/<int:strategy_id>", methods=["POST"])
@login_required
def delete_main_strategy(strategy_id):
    """Ana stratejiyi sil (soft: is_active=False)."""
    if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
    st = Strategy.query.filter_by(id=strategy_id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        from app.models import db
        st.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Ana strateji silindi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@dashboard_bp.route("/kurum-paneli/update-sub-strategy/<int:sub_id>", methods=["POST"])
@login_required
def update_sub_strategy(sub_id):
    """Alt stratejiyi güncelle."""
    if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
    from app.models.core import SubStrategy
    sub = SubStrategy.query.join(Strategy).filter(
        SubStrategy.id == sub_id,
        Strategy.tenant_id == current_user.tenant_id
    ).first_or_404()
    data = request.json or {}
    title = data.get("title")
    if not title or not str(title).strip():
        return jsonify({"success": False, "message": "Alt strateji adı zorunludur."}), 400
    sub.title = str(title).strip()
    sub.description = data.get("description", sub.description) or ""
    try:
        from app.models import db
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@dashboard_bp.route("/kurum-paneli/delete-sub-strategy/<int:sub_id>", methods=["POST"])
@login_required
def delete_sub_strategy(sub_id):
    """Alt stratejiyi sil (soft: is_active=False)."""
    if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
    from app.models.core import SubStrategy
    sub = SubStrategy.query.join(Strategy).filter(
        SubStrategy.id == sub_id,
        Strategy.tenant_id == current_user.tenant_id
    ).first_or_404()
    try:
        from app.models import db
        sub.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji silindi."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
