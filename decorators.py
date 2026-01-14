# -*- coding: utf-8 -*-
"""
Access Control Decorators
Proje Yönetimi için RBAC (Role-Based Access Control) decorator'ları
"""
from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from models import Project, db
from sqlalchemy import and_


def project_access_required(allowed_roles=None):
    """
    Proje erişim kontrolü decorator'ı
    
    Args:
        allowed_roles: İzin verilen roller listesi
            - 'manager': Proje yöneticisi
            - 'member': Proje üyesi
            - 'observer': Gözlemci
            - None: Herhangi bir rol (sadece projeye erişim)
    
    Usage:
        @project_access_required(allowed_roles=['manager', 'member'])
        def api_endpoint(project_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # project_id'yi args veya kwargs'tan al
            project_id = kwargs.get('project_id') or (args[0] if args else None)
            
            if not project_id:
                return jsonify({'success': False, 'message': 'Proje ID bulunamadı'}), 400
            
            try:
                project = Project.query.get_or_404(project_id)
                
                # Kurum kontrolü
                if project.kurum_id != current_user.kurum_id:
                    return jsonify({'success': False, 'message': 'Bu projeye erişim yetkiniz yok'}), 403
                
                # Kullanıcının rolünü belirle
                user_role = _get_user_project_role(project, current_user.id)
                
                if user_role is None:
                    return jsonify({'success': False, 'message': 'Bu projede yetkiniz yok'}), 403
                
                # Rol kontrolü (eğer allowed_roles belirtilmişse)
                if allowed_roles and user_role not in allowed_roles:
                    role_names = {
                        'manager': 'Proje Yöneticisi',
                        'member': 'Proje Üyesi',
                        'observer': 'Gözlemci'
                    }
                    return jsonify({
                        'success': False, 
                        'message': f'Bu işlem için {role_names.get(user_role, user_role)} yetkisi gereklidir'
                    }), 403
                
                # Rol bilgisini kwargs'a ekle
                kwargs['user_project_role'] = user_role
                kwargs['project'] = project
                
                return f(*args, **kwargs)
            except Exception as e:
                from flask import current_app
                current_app.logger.error(f'Proje erişim kontrolü hatası: {e}')
                return jsonify({'success': False, 'message': str(e)}), 500
        
        return decorated_function
    return decorator


def _get_user_project_role(project, user_id):
    """
    Kullanıcının projedeki rolünü döndürür
    
    Returns:
        'manager': Proje yöneticisi
        'member': Proje üyesi
        'observer': Gözlemci
        None: Yetkisi yok
    """
    # Proje yöneticisi kontrolü
    if project.manager_id == user_id:
        return 'manager'
    
    # Üye kontrolü (association table üzerinden)
    from models import project_members
    member_exists = db.session.query(project_members).filter(
        and_(
            project_members.c.project_id == project.id,
            project_members.c.user_id == user_id
        )
    ).first() is not None
    
    if member_exists:
        return 'member'
    
    # Gözlemci kontrolü (association table üzerinden)
    from models import project_observers
    observer_exists = db.session.query(project_observers).filter(
        and_(
            project_observers.c.project_id == project.id,
            project_observers.c.user_id == user_id
        )
    ).first() is not None
    
    if observer_exists:
        return 'observer'
    
    # Sistem rolleri: kurum üst yönetimi de proje yöneticisi seviyesinde işlem yapabilsin
    if hasattr(current_user, 'sistem_rol') and current_user.sistem_rol in ['admin', 'kurum_yoneticisi', 'ust_yonetim']:
        return 'manager'

    # Projeye bağlı süreçlerin liderleri de (ilişkili süreçlerde) manager seviyesinde kabul edilir
    try:
        from models import surec_liderleri
        related_ids = [p.id for p in (project.related_processes or [])]
        if related_ids:
            is_leader = db.session.query(surec_liderleri).filter(
                and_(
                    surec_liderleri.c.surec_id.in_(related_ids),
                    surec_liderleri.c.user_id == user_id,
                )
            ).first() is not None
            if is_leader:
                return 'manager'
    except Exception:
        # Liderlik kontrolü opsiyoneldir; hata durumda rolü değiştirmeyiz
        pass
    
    return None


def project_manager_required(f):
    """Sadece proje yöneticisi yetkisi gerektirir"""
    return project_access_required(allowed_roles=['manager'])(f)


def project_member_required(f):
    """Proje yöneticisi veya üye yetkisi gerektirir"""
    return project_access_required(allowed_roles=['manager', 'member'])(f)


def project_observer_allowed(f):
    """Proje yöneticisi, üye veya gözlemci yetkisi gerektirir (en düşük yetki)"""
    return project_access_required(allowed_roles=['manager', 'member', 'observer'])(f)


























