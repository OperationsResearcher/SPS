import logging as _sio_log
"""
WebSocket Events
Sprint 7-9: Real-Time ve Bildirimler
Flask-SocketIO event handlers
"""

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, rooms
from app.extensions import socketio
from app.services.notification_service import NotificationService

# Aktif kullanıcılar (room tracking)
active_users = {}


def _process_room(process_id) -> str:
    return f'process_{process_id}'


def _can_access_process(process_id) -> bool:
    """GUV-16: süreç odasına yalnız aynı kurumun kullanıcısı (platform Admin: hepsi) girebilir."""
    from app.constants.roles import PLATFORM_ADMIN_ROLES
    from app.models.process import Process
    try:
        pid = int(process_id)
    except (TypeError, ValueError):
        return False
    role = getattr(getattr(current_user, "role", None), "name", None)
    q = Process.query.filter_by(id=pid)
    if role not in PLATFORM_ADMIN_ROLES:
        q = q.filter_by(tenant_id=current_user.tenant_id)
    return q.first() is not None


def _in_process_room(process_id) -> bool:
    """Oda yayınları için: kullanıcı odaya yetkili girişle katılmış olmalı."""
    return _process_room(process_id) in rooms()


def _display_name():
    """Yayınlanan olaylarda e-posta yerine görünen ad (D-012)."""
    name = " ".join(p for p in (getattr(current_user, "first_name", None),
                                getattr(current_user, "last_name", None)) if p)
    return name or None


def _payload(data) -> dict:
    """İstemci verisi dict değilse (None, liste, sayı) boş sözlük say."""
    return data if isinstance(data, dict) else {}

@socketio.on('connect')
def handle_connect():
    """Kullanıcı bağlandı"""
    if current_user.is_authenticated:
        user_id = current_user.id
        room = f'user_{user_id}'
        
        # Kullanıcıyı kendi room'una ekle
        join_room(room)
        
        # Aktif kullanıcılar listesine ekle
        active_users[request.sid] = {
            'user_id': user_id,
            'username': _display_name(),
            'connected_at': None
        }
        
        # Okunmamış bildirim sayısını gönder
        unread_count = NotificationService.get_unread_count(user_id)
        emit('unread_count', {'count': unread_count})
        
        _sio_log.getLogger(__name__).debug(f"User {user_id} connected to room {room}")


@socketio.on('disconnect')
def handle_disconnect():
    """Kullanıcı bağlantıyı kesti"""
    if request.sid in active_users:
        user_info = active_users.pop(request.sid)
        _sio_log.getLogger(__name__).debug(f"User {user_info['user_id']} disconnected")


@socketio.on('join_process')
def handle_join_process(data):
    """Süreç room'una katıl (collaboration için)"""
    if current_user.is_authenticated:
        data = _payload(data)
        process_id = data.get('process_id')
        if not _can_access_process(process_id):
            emit('error', {'message': 'forbidden'})
            return
        room = _process_room(process_id)

        join_room(room)
        
        # Diğer kullanıcılara bildir
        emit('user_joined', {
            'user_id': current_user.id,
            'username': _display_name(),
            'process_id': process_id
        }, room=room, skip_sid=request.sid)
        
        _sio_log.getLogger(__name__).debug(f"User {current_user.id} joined process {process_id}")


@socketio.on('leave_process')
def handle_leave_process(data):
    """Süreç room'undan ayrıl"""
    if current_user.is_authenticated:
        data = _payload(data)
        process_id = data.get('process_id')
        # D-012: yalnız yetkili girişle odaya katılmış kullanıcı ayrılma olayı yayınlayabilir
        if not _in_process_room(process_id):
            return
        room = _process_room(process_id)

        leave_room(room)

        # Diğer kullanıcılara bildir (e-posta yok)
        emit('user_left', {
            'user_id': current_user.id,
            'username': _display_name(),
            'process_id': process_id
        }, room=room)
        
        _sio_log.getLogger(__name__).debug(f"User {current_user.id} left process {process_id}")


@socketio.on('kpi_data_update')
def handle_kpi_data_update(data):
    """KPI veri güncellemesi (real-time collaboration)"""
    if current_user.is_authenticated:
        data = _payload(data)
        process_id = data.get('process_id')
        kpi_id = data.get('kpi_id')
        field = data.get('field')
        value = data.get('value')
        if not _in_process_room(process_id):
            return  # GUV-16: yetkili katılım olmadan yayın yok

        # Diğer kullanıcılara broadcast et
        emit('kpi_updated', {
            'kpi_id': kpi_id,
            'field': field,
            'value': value,
            'updated_by': current_user.id,
            'timestamp': None
        }, room=f'process_{process_id}', skip_sid=request.sid)
        
        _sio_log.getLogger(__name__).debug(f"KPI {kpi_id} updated by user {current_user.id}")


@socketio.on('typing')
def handle_typing(data):
    """Kullanıcı yazıyor göstergesi"""
    if current_user.is_authenticated:
        data = _payload(data)
        process_id = data.get('process_id')
        field = data.get('field')
        if not _in_process_room(process_id):
            return

        emit('user_typing', {
            'user_id': current_user.id,
            'username': _display_name(),
            'field': field
        }, room=f'process_{process_id}', skip_sid=request.sid)


@socketio.on('mark_notification_read')
def handle_mark_notification_read(data):
    """Bildirimi okundu olarak işaretle"""
    if current_user.is_authenticated:
        notification_id = data.get('notification_id')
        NotificationService.mark_as_read(notification_id, current_user.id)  # GUV-16: sahiplik
        
        # Güncel okunmamış sayıyı gönder
        unread_count = NotificationService.get_unread_count(current_user.id)
        emit('unread_count', {'count': unread_count})


@socketio.on('get_active_users')
def handle_get_active_users(data):
    """Aktif kullanıcıları getir"""
    if current_user.is_authenticated:
        data = _payload(data)
        process_id = data.get('process_id')
        if not _in_process_room(process_id):
            return
        room = _process_room(process_id)

        # Bu room'daki aktif kullanıcıları bul
        room_users = []
        for sid, user_info in active_users.items():
            if room in rooms(sid=sid):
                room_users.append({
                    'user_id': user_info['user_id'],
                    'username': user_info['username']
                })
        
        emit('active_users', {'users': room_users})


# Utility functions
def broadcast_to_tenant(tenant_id, event, data):
    """Tenant'a broadcast"""
    socketio.emit(event, data, room=f'tenant_{tenant_id}')


def broadcast_to_process(process_id, event, data):
    """Süreç room'una broadcast"""
    socketio.emit(event, data, room=f'process_{process_id}')


def send_to_user(user_id, event, data):
    """Belirli kullanıcıya gönder"""
    socketio.emit(event, data, room=f'user_{user_id}')


# ── KPI Veri Girişi — Canlı Masaüstü Güncellemesi ────────────────────────────

@socketio.on("kpi_data_entered")
def handle_kpi_data_entered(data):
    """
    KPI veri girildiğinde tetiklenir.
    data: {"tenant_id": int, "process_id": int, "kpi_id": int}
    Aynı tenant'taki yöneticilerin masaüstü morning-summary widget'ını günceller.
    """
    if not current_user.is_authenticated:
        return
    tenant_id = current_user.tenant_id  # GUV-16: istemcinin verdiği tenant_id'ye güvenilmez
    data = _payload(data)
    socketio.emit(
        "morning_summary_refresh",
        {"reason": "kpi_data_entered", "process_id": data.get("process_id")},
        room=f"tenant_{tenant_id}",
    )


def notify_kpi_update(tenant_id: int, process_id: int, kpi_id: int) -> None:
    """
    Backend'den doğrudan çağrılabilir — KPI kaydından sonra tenant'a bildirim gönderir.
    Kullanım: routes_kpi_data.py içindeki kayıt endpoint'lerinden çağır.
    """
    from app.extensions import socketio as _sio
    _sio.emit(
        "morning_summary_refresh",
        {"reason": "kpi_data_updated", "process_id": process_id, "kpi_id": kpi_id},
        room=f"tenant_{tenant_id}",
    )
