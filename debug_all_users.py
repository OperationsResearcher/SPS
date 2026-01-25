"""
Tüm kullanıcıları ve görevlerini listele
"""
from app import app
from models import Task, User

with app.app_context():
    print("\n" + "="*60)
    print("TÜM KULLANICILAR VE GÖREVLERİ")
    print("="*60 + "\n")
    
    users = User.query.all()
    
    for user in users:
        task_count = Task.query.filter_by(assigned_to_id=user.id, is_archived=False).count()
        print(f"👤 ID: {user.id} | {user.username} ({user.email})")
        print(f"   📋 Görev Sayısı: {task_count}")
        
        if task_count > 0:
            tasks = Task.query.filter_by(assigned_to_id=user.id, is_archived=False).limit(5).all()
            for task in tasks:
                status_icon = "✅" if task.status in ['Tamamlandı', 'Completed'] else "⏳"
                print(f"      {status_icon} {task.title} (Bitiş: {task.due_date})")
        print()
