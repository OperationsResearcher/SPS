"""
Audit Logger Service
Sprint 5-6: Güvenlik ve Stabilite
Kullanıcı aktivitelerini loglama
"""

from flask import request
from flask_login import current_user
from app.models.audit import AuditLog
from app.extensions import db
from functools import wraps
import json

class AuditLogger:
    """Audit logging servisi"""
    
    @staticmethod
    def log(action, resource_type=None, resource_id=None, description=None, 
            old_values=None, new_values=None):
        """
        Audit log kaydı oluştur
        
        Args:
            action: CREATE, UPDATE, DELETE, LOGIN, LOGOUT, VIEW
            resource_type: Process, KPI, User, etc.
            resource_id: Resource ID
            description: Açıklama
            old_values: Eski değerler (dict)
            new_values: Yeni değerler (dict)
        """
        try:
            audit_log = AuditLog(
                user_id=current_user.id if current_user.is_authenticated else None,
                username=current_user.email if current_user.is_authenticated else 'Anonymous',
                tenant_id=current_user.tenant_id if current_user.is_authenticated else None,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                old_values=old_values,
                new_values=new_values,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string[:500] if request.user_agent else None,
                request_method=request.method,
                request_path=request.path[:500]
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
        except Exception as e:
            print(f"Audit log error: {e}")
            db.session.rollback()
    
    @staticmethod
    def log_create(resource_type, resource_id, new_values, description=None):
        """CREATE aksiyonu logla"""
        AuditLogger.log(
            action='CREATE',
            resource_type=resource_type,
            resource_id=resource_id,
            description=description or f'{resource_type} created',
            new_values=new_values
        )
    
    @staticmethod
    def log_update(resource_type, resource_id, old_values, new_values, description=None):
        """UPDATE aksiyonu logla"""
        AuditLogger.log(
            action='UPDATE',
            resource_type=resource_type,
            resource_id=resource_id,
            description=description or f'{resource_type} updated',
            old_values=old_values,
            new_values=new_values
        )
    
    @staticmethod
    def log_delete(resource_type, resource_id, old_values, description=None):
        """DELETE aksiyonu logla"""
        AuditLogger.log(
            action='DELETE',
            resource_type=resource_type,
            resource_id=resource_id,
            description=description or f'{resource_type} deleted',
            old_values=old_values
        )

    
    @staticmethod
    def log_login(user_id, username, success=True):
        """LOGIN aksiyonu logla"""
        AuditLogger.log(
            action='LOGIN_SUCCESS' if success else 'LOGIN_FAILED',
            resource_type='User',
            resource_id=user_id,
            description=f'User {username} logged {"in" if success else "in failed"}'
        )
    
    @staticmethod
    def log_logout(user_id, username):
        """LOGOUT aksiyonu logla"""
        AuditLogger.log(
            action='LOGOUT',
            resource_type='User',
            resource_id=user_id,
            description=f'User {username} logged out'
        )


def audit_log(action, resource_type=None):
    """
    Audit log decorator
    
    Usage:
        @app.route('/api/kpi-data/<int:kpi_id>', methods=['DELETE'])
        @audit_log('DELETE', 'KPI')
        def delete_kpi(kpi_id):
            # Function içeriği
            return jsonify({'success': True})
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Resource ID'yi kwargs'dan al
            resource_id = kwargs.get('id') or kwargs.get('kpi_id') or kwargs.get('process_id')
            
            # Function'ı çalıştır
            result = f(*args, **kwargs)
            
            # Başarılı ise logla
            if result and (isinstance(result, tuple) and result[1] < 400) or not isinstance(result, tuple):
                AuditLogger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    description=f'{action} {resource_type} {resource_id}'
                )
            
            return result
        
        return wrapper
    return decorator


# Export
__all__ = ['AuditLogger', 'audit_log']
