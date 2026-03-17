"""
Şu an dashboard'da giriş yapmış kullanıcının görevlerini kontrol et
"""
from app import app
from models import Task
from datetime import date, timedelta

with app.app_context():
    # Tüm görevleri listele (hangi kullanıcıya ait olursa olsun)
    all_tasks = Task.query.filter_by(is_archived=False).all()
    
    print(f"\n{'='*70}")
    print(f"VERİTABANINDAKİ TÜM AKTİF GÖREVLER")
    print(f"{'='*70}\n")
    
    if not all_tasks:
        print("❌ Veritabanında hiç aktif görev yok!")
        print("\nÇözüm: Önce bir görev oluşturun:")
        print("1. Ana sayfaya gidin")
        print("2. Bir proje oluşturun")
        print("3. O projeye görev ekleyin")
        print("4. Görevi kendinize atayın")
    else:
        print(f"Toplam {len(all_tasks)} aktif görev bulundu:\n")
        
        # Kullanıcılara göre grupla
        user_tasks = {}
        for task in all_tasks:
            user_id = task.assigned_to_id
            if user_id not in user_tasks:
                user_tasks[user_id] = []
            user_tasks[user_id].append(task)
        
        today = date.today()
        
        for user_id, tasks in user_tasks.items():
            from models import User
            user = User.query.get(user_id)
            username = user.username if user else "Bilinmeyen"
            
            print(f"\n👤 Kullanıcı: {username} (ID: {user_id})")
            print(f"   📋 Görev Sayısı: {len(tasks)}\n")
            
            for task in tasks[:10]:  # İlk 10 görevi göster
                if not task.due_date:
                    print(f"   ❌ {task.title}: TARİH YOK")
                    continue
                    
                due = task.due_date if isinstance(task.due_date, date) else task.due_date.date()
                status_icon = "✅" if task.status in ['Tamamlandı', 'Completed'] else "⏳"
                
                # Kategori belirle
                if due < today:
                    category = "GEÇMIŞ"
                elif due == today:
                    category = "BUGÜN"
                elif due <= today + timedelta(days=7):
                    category = "BU HAFTA"
                elif due <= today + timedelta(days=30):
                    category = "BU AY"
                else:
                    category = "BU YIL"
                
                print(f"   {status_icon} {task.title}")
                print(f"      📅 {due} | 📂 {category} | Durum: {task.status}")
            
            if len(tasks) > 10:
                print(f"   ... ve {len(tasks) - 10} görev daha")
