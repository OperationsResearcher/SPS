"""
1salih kullanıcısının görevlerini ORM ile kontrol et
"""
from app import app
from models import Task, User
from datetime import date, timedelta

with app.app_context():
    user = User.query.filter_by(username='1salih').first()
    
    if not user:
        print("❌ Kullanıcı bulunamadı!")
        # Tüm kullanıcıları listele
        print("\nMevcut kullanıcılar:")
        for u in User.query.limit(10).all():
            print(f"  - {u.username} (ID: {u.id})")
    else:
        print(f"\n{'='*80}")
        print(f"👤 Kullanıcı: {user.username} (ID: {user.id})")
        print(f"{'='*80}\n")
        
        # Tüm görevleri çek (arşivlenmemiş)
        tasks = Task.query.filter_by(assigned_to_id=user.id).all()
        
        print(f"📋 TOPLAM {len(tasks)} GÖREV BULUNDU\n")
        
        # Arşivlenmiş ve arşivlenmemiş ayır
        active_tasks = [t for t in tasks if not t.is_archived]
        archived_tasks = [t for t in tasks if t.is_archived]
        
        print(f"   ✅ Aktif: {len(active_tasks)}")
        print(f"   📦 Arşivlenmiş: {len(archived_tasks)}\n")
        
        if not active_tasks:
            print("❌ Aktif görev yok! (Belki hepsi arşivlenmiş?)")
        else:
            today = date.today()
            week_end = today + timedelta(days=7)
            month_end = today + timedelta(days=30)
            
            print(f"📅 BUGÜN: {today}")
            print(f"📅 HAFTA SONU: {week_end}")
            print(f"📅 AY SONU: {month_end}\n")
            print(f"{'='*80}\n")
            
            for task in active_tasks:
                print(f"🔍 ID: {task.id} | {task.title}")
                print(f"   📅 due_date: {task.due_date} (Tip: {type(task.due_date).__name__})")
                print(f"   📊 status: {task.status}")
                print(f"   📦 is_archived: {task.is_archived}")
                
                if task.due_date:
                    # Tarihi date objesine çevir
                    due = task.due_date if isinstance(task.due_date, date) else task.due_date.date()
                    days_diff = (due - today).days
                    
                    # Kategorileri belirle (matematiksel kapsayıcılık)
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
                    
                    print(f"   🗓️  {due} ({days_diff:+d} gün)")
                    print(f"   📂 {', '.join(cats)}")
                else:
                    print(f"   ❌ TARİH YOK")
                
                print()
