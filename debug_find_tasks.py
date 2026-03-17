"""
Ekranda görünen görevleri bul (v3-test başlıklı görevler)
"""
from app import app
from models import Task, User

with app.app_context():
    print(f"\n{'='*80}")
    print("EKRANDA GÖRÜNEN GÖREVLERİ ARIYORUM...")
    print(f"{'='*80}\n")
    
    # Ekran görüntüsündeki görev başlıkları
    search_titles = ['v3-test-final', 'v3 test bu ay', 'v3-test']
    
    for title in search_titles:
        # Benzer başlıklı görevleri ara
        tasks = Task.query.filter(Task.title.like(f'%{title}%')).all()
        
        if tasks:
            print(f"🔍 '{title}' içeren görevler:\n")
            for task in tasks:
                user = User.query.get(task.assigned_to_id) if task.assigned_to_id else None
                username = user.username if user else "Atanmamış"
                
                print(f"   📝 {task.title}")
                print(f"   👤 Atanan: {username} (ID: {task.assigned_to_id})")
                print(f"   📅 Bitiş: {task.due_date}")
                print(f"   📊 Durum: {task.status}")
                print(f"   📦 Arşiv: {task.is_archived}")
                print()
    
    # Tüm aktif görevleri listele
    print(f"\n{'='*80}")
    print("TÜM AKTİF GÖREVLER (is_archived=False)")
    print(f"{'='*80}\n")
    
    all_active = Task.query.filter_by(is_archived=False).order_by(Task.created_at.desc()).limit(20).all()
    
    for task in all_active:
        user = User.query.get(task.assigned_to_id) if task.assigned_to_id else None
        username = user.username if user else "Atanmamış"
        
        print(f"📝 {task.title}")
        print(f"   👤 {username} (ID: {task.assigned_to_id})")
        print(f"   📅 {task.due_date}")
        print()
