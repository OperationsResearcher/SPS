# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from flask import has_request_context, request
from flask_login import current_user, user_logged_in, user_logged_out
from sqlalchemy import event, inspect
from sqlalchemy.orm.attributes import get_history

from models import (
    AuditLog,
    User,
    Project,
    Task,
    AnaStrateji,
    Surec,
    SurecPerformansGostergesi,
    PerformansGostergeVeri
)

logger = logging.getLogger(__name__)


WHITELIST_MODELS = [
    User,
    Project,
    Task,
    AnaStrateji,
    Surec,
    SurecPerformansGostergesi,
    PerformansGostergeVeri
]


MODULE_NAME_MAP = {
    'User': 'Kullanıcı Yönetimi',
    'Project': 'Proje Yönetimi',
    'Task': 'Görev Yönetimi',
    'AnaStrateji': 'Strateji Yönetimi',
    'Surec': 'Süreç Yönetimi',
    'SurecPerformansGostergesi': 'KPI Yönetimi',
    'PerformansGostergeVeri': 'KPI Veri Girişi'
}


IGNORE_FIELDS = {
    'id', 'created_at', 'updated_at', 'deleted_at', 'deleted_by',
    'last_login', 'last_seen', 'modified_at', 'silindi'
}


FIELD_LABELS = {
    'status': 'Durum',
    'durum': 'Durum',
    'title': 'Başlık',
    'name': 'Ad',
    'ad': 'Ad',
    'baslik': 'Başlık',
    'konu': 'Konu',
    'description': 'Açıklama',
    'aciklama': 'Açıklama',
    'priority': 'Öncelik',
    'hedef_yil': 'Hedef Yıl',
    'hedef': 'Hedef',
    'value': 'Değer'
}


def _get_current_user():
    if not has_request_context():
        return None
    try:
        if current_user and current_user.is_authenticated:
            return current_user
    except Exception:
        return None
    return None


def _get_model_name(target, mapper):
    try:
        return mapper.class_.__name__
    except Exception:
        return getattr(target.__class__, '__name__', None)


def _get_module_name(model_name):
    return MODULE_NAME_MAP.get(model_name, model_name)


def _get_record_id(target):
    try:
        mapper = inspect(target).mapper
        pk_keys = [key.name for key in mapper.primary_key]
        pk_values = [getattr(target, k) for k in pk_keys]
        if len(pk_values) == 1:
            return pk_values[0]
    except Exception:
        return None
    return None


def _get_record_name(target):
    for attr in ['baslik', 'ad', 'name', 'title', 'konu']:
        value = getattr(target, attr, None)
        if value:
            return str(value)
    return None


def _label_field(field_name):
    return FIELD_LABELS.get(field_name, field_name.replace('_', ' ').title())


def _format_change(old_val, new_val):
    old_str = '' if old_val is None else str(old_val)
    new_str = '' if new_val is None else str(new_val)
    return f"{old_str} -> {new_str}".strip()


def _collect_update_changes(target):
    mapper = inspect(target).mapper
    changes = {}
    for column in mapper.columns:
        prop = column.key
        if prop in IGNORE_FIELDS:
            continue
        history = get_history(target, prop)
        if history.has_changes():
            old_val = history.deleted[0] if history.deleted else None
            new_val = history.added[0] if history.added else getattr(target, prop)
            label = _label_field(prop)
            changes[label] = _format_change(old_val, new_val)
    return changes


def _collect_insert_changes(target):
    return {'Kayıt': 'Oluşturuldu'}


def _collect_delete_changes(target):
    return {'Kayıt': 'Silindi'}


def _should_log(user):
    return user is not None


def _create_log(mapper, connection, target, action, changes):
    user = _get_current_user()
    if not _should_log(user):
        return
    if not changes:
        return

    model_name = _get_model_name(target, mapper)
    if not model_name or model_name in ['Session', 'AuditLog']:
        return

    record_id = _get_record_id(target)
    if record_id is None:
        return
    record_name = _get_record_name(target) or f"{model_name} #{record_id}"
    module_name = _get_module_name(model_name)
    if not module_name:
        return

    connection.execute(
        AuditLog.__table__.insert(),
        {
            'user_id': user.id,
            'user_name': getattr(user, 'username', None) or getattr(user, 'email', None) or str(user.id),
            'action': action,
            'module': module_name,
            'record_id': record_id or 0,
            'record_name': record_name,
            'changes': changes,
            'timestamp': datetime.now()
        }
    )


def _register_model(model_cls):
    @event.listens_for(model_cls, 'after_insert')
    def after_insert(mapper, connection, target):
        try:
            _create_log(mapper, connection, target, 'CREATE', _collect_insert_changes(target))
        except Exception as exc:
            logger.error(f'Audit after_insert error: {exc}')

    @event.listens_for(model_cls, 'after_update')
    def after_update(mapper, connection, target):
        try:
            changes = _collect_update_changes(target)
            if not changes:
                return
            _create_log(mapper, connection, target, 'UPDATE', changes)
        except Exception as exc:
            logger.error(f'Audit after_update error: {exc}')

    @event.listens_for(model_cls, 'after_delete')
    def after_delete(mapper, connection, target):
        try:
            _create_log(mapper, connection, target, 'DELETE', _collect_delete_changes(target))
        except Exception as exc:
            logger.error(f'Audit after_delete error: {exc}')


def register_audit_listeners(app):
    for model_cls in WHITELIST_MODELS:
        _register_model(model_cls)


def _get_user_display_name(user):
    return getattr(user, 'username', None) or getattr(user, 'ad_soyad', None) or getattr(user, 'email', None) or str(user.id)


def _get_request_ip():
    if has_request_context():
        return request.remote_addr
    return None


def register_auth_audit_signals(app):
    """
    Login / Logout audit kayıtlarını bağlar.
    """
    @user_logged_in.connect_via(app)
    def log_login(sender, user, **extra):
        try:
            ip_addr = _get_request_ip()
            AuditLog.query.session.execute(
                AuditLog.__table__.insert(),
                {
                    'user_id': user.id,
                    'user_name': _get_user_display_name(user),
                    'action': 'OTURUM AÇMA',
                    'module': 'GÜVENLİK',
                    'record_id': user.id,
                    'record_name': _get_user_display_name(user),
                    'changes': {'ip': ip_addr},
                    'timestamp': datetime.now()
                }
            )
            AuditLog.query.session.commit()
        except Exception as exc:
            logger.error(f'Audit login error: {exc}')

    @user_logged_out.connect_via(app)
    def log_logout(sender, user, **extra):
        try:
            ip_addr = _get_request_ip()
            AuditLog.query.session.execute(
                AuditLog.__table__.insert(),
                {
                    'user_id': user.id,
                    'user_name': _get_user_display_name(user),
                    'action': 'OTURUM KAPATMA',
                    'module': 'GÜVENLİK',
                    'record_id': user.id,
                    'record_name': _get_user_display_name(user),
                    'changes': {'ip': ip_addr},
                    'timestamp': datetime.now()
                }
            )
            AuditLog.query.session.commit()
        except Exception as exc:
            logger.error(f'Audit logout error: {exc}')
