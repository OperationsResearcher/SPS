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
            'username': current_user.email,
            'connected_at': None
        }
        
        # Okunmamış bildirim sayısını gönder
        unread_count = NotificationService.get_unread_count(user_id)
        emit('unread_count', {'count': unread_count})
        
        print(f"User {user_id} connected to room {room}")


@socketio.on('disconnect')
def handle_disconnect():
    """Kullanıcı bağlantıyı kesti"""
    if request.sid in active_users:
        user_info = active_users.pop(request.sid)
        print(f"User {user_info['user_id']} disconnected")


@socketio.on('join_process')
def handle_join_process(data):
    """Süreç room'una katıl (collaboration için)"""
    if current_user.is_authenticated:
        process_id = data.get('process_id')
        room = f'process_{process_id}'
        
        join_room(room)
        
        # Diğer kullanıcılara bildir
        emit('user_joined', {
            'user_id': current_user.id,
            'username': current_user.email,
            'process_id': process_id
        }, room=room, skip_sid=request.sid)
        
        print(f"User {current_user.id} joined process {process_id}")


@socketio.on('leave_process')
def handle_leave_process(data):
    """Süreç room'undan ayrıl"""
    if current_user.is_authenticated:
        process_id = data.get('process_id')
        room = f'process_{process_id}'
        
        leave_room(room)
        
        # Diğer kullanıcılara bildir
        emit('user_left', {
            'user_id': current_user.id,
            'username': current_user.email,
            'process_id': process_id
        }, room=room)
        
        print(f"User {current_user.id} left process {process_id}")


@socketio.on('kpi_data_update')
def handle_kpi_data_update(data):
    """KPI veri güncellemesi (real-time collaboration)"""
    if current_user.is_authenticated:
        process_id = data.get('process_id')
        kpi_id = data.get('kpi_id')
        field = data.get('field')
        value = data.get('value')
        
        # Diğer kullanıcılara broadcast et
        emit('kpi_updated', {
            'kpi_id': kpi_id,
            'field': field,
            'value': value,
            'updated_by': current_user.email,
            'timestamp': None
        }, room=f'process_{process_id}', skip_sid=request.sid)
        
        print(f"KPI {kpi_id} updated by user {current_user.id}")


@socketio.on('typing')
def handle_typing(data):
    """Kullanıcı yazıyor göstergesi"""
    if current_user.is_authenticated:
        process_id = data.get('process_id')
        field = data.get('field')
        
        emit('user_typing', {
            'user_id': current_user.id,
            'username': current_user.email,
            'field': field
        }, room=f'process_{process_id}', skip_sid=request.sid)


@socketio.on('mark_notification_read')
def handle_mark_notification_read(data):
    """Bildirimi okundu olarak işaretle"""
    if current_user.is_authenticated:
        notification_id = data.get('notification_id')
        NotificationService.mark_as_read(notification_id)
        
        # Güncel okunmamış sayıyı gönder
        unread_count = NotificationService.get_unread_count(current_user.id)
        emit('unread_count', {'count': unread_count})


@socketio.on('get_active_users')
def handle_get_active_users(data):
    """Aktif kullanıcıları getir"""
    if current_user.is_authenticated:
        process_id = data.get('process_id')
        room = f'process_{process_id}'
        
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
