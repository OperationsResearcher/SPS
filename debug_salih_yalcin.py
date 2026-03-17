"""
salih.yalcin kullanıcısının görevlerini kontrol et
"""
from app import app
from models import Task, User
from datetime import date, timedelta

with app.app_context():
    user = User.query.filter_by(username='salih.yalcin').first()
    
    if not user:
        print("❌ Kullanıcı bulunamadı!")
    else:
        print(f"\n{'='*80}")
        print(f"👤 Kullanıcı: {user.username} (ID: {user.id})")
        print(f"{'='*80}\n")
        
        tasks = Task.query.filter_by(assigned_to_id=user.id, is_archived=False).all()
        
        print(f"📋 Toplam {len(tasks)} aktif görev\n")
        
        today = date.today()
        week_end = today + timedelta(days=7)
        month_end = today + timedelta(days=30)
        
        print(f"📅 BUGÜN: {today}")
        print(f"📅 HAFTA SONU: {week_end}")
        print(f"📅 AY SONU: {month_end}\n")
        print(f"{'='*80}\n")
        
        for task in tasks:
            if not task.due_date:
                print(f"❌ {task.title}: TARİH YOK\n")
                continue
            
            due = task.due_date if isinstance(task.due_date, date) else task.due_date.date()
            days_diff = (due - today).days
            
            # Kategorileri belirle
            cats = []
            if due < today:
                cats.append("🔴 GEÇMIŞ")
            elif due == today:
                cats.append("🟢 BUGÜN → HAFTA → AY → YIL")
            elif due <= week_end:
                cats.append("🔵 HAFTA → AY → YIL")
            elif due <= month_end:
                cats.append("🟡 AY → YIL")
            else:
                cats.append("🟣 YIL")
            
            status_icon = "✅" if task.status in ['Tamamlandı', 'Completed'] else "⏳"
            
            print(f"{status_icon} {task.title}")
            print(f"   📅 {due} ({days_diff:+d} gün)")
            print(f"   📂 {', '.join(cats)}")
            print(f"   📊 Durum: {task.status}\n")
