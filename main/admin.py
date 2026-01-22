
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from models import AuditLog
from sqlalchemy import desc
from datetime import datetime
from extensions import db
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    # Sadece admin ve kurum yöneticileri erişebilir
    if not current_user.is_authenticated or current_user.sistem_rol not in ['admin', 'kurum_yoneticisi']:
        abort(403)

@admin_bp.route('/activity-stream')
@login_required
def activity_stream():
    page = request.args.get('page', type=int, default=1)

    query = AuditLog.query.filter(
        AuditLog.user_id.isnot(None),
        AuditLog.module.isnot(None)
    )

    query = query.order_by(desc(AuditLog.timestamp))

    pagination = query.paginate(page=page, per_page=20, error_out=False)

    now = datetime.now()
    for log in pagination.items:
        if log.timestamp:
            delta = now - log.timestamp
            seconds = int(delta.total_seconds())
            if seconds < 60:
                log.time_ago = 'Az önce'
            elif seconds < 3600:
                log.time_ago = f"{seconds // 60} dakika önce"
            elif seconds < 86400:
                log.time_ago = f"{seconds // 3600} saat önce"
            else:
                log.time_ago = f"{seconds // 86400} gün önce"
        else:
            log.time_ago = '-'

    return render_template(
        'admin/activity_stream.html',
        logs=pagination.items,
        pagination=pagination
    )


@admin_bp.route('/fix-db-schema')
@login_required
def fix_db_schema():
    """
    AuditLog tablosunu drop edip yeniden oluşturur.
    """
    try:
        with db.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS audit_log"))
            conn.commit()
    except Exception as e:
        return f"Drop failed: {e}", 500

    try:
        db.create_all()
    except Exception as e:
        return f"Create failed: {e}", 500

    return "Database Schema Repaired! <a href='/admin/activity-stream'>Go to Logs</a>"
