"""
1salih kullanıcısının görevlerini detaylı kontrol et
"""
from app import app
from models import Task, User
from datetime import date, timedelta

with app.app_context():
    # 1salih kullanıcısını bul
    user = User.query.filter_by(username='1salih').first()
    
    if not user:
        print("❌ '1salih' kullanıcısı bulunamadı!")
        print("\nMevcut kullanıcılar:")
        for u in User.query.all():
            print(f"  - {u.username} (ID: {u.id})")
    else:
        print(f"\n{'='*70}")
        print(f"👤 Kullanıcı: {user.username} (ID: {user.id})")
        print(f"{'='*70}\n")
        
        today = date.today()
        week_end = today + timedelta(days=7)
        month_end = today + timedelta(days=30)
        year_end = date(today.year, 12, 31)
        
        print(f"📅 BUGÜN: {today}")
        print(f"📅 HAFTA SONU: {week_end} (7 gün sonra)")
        print(f"📅 AY SONU: {month_end} (30 gün sonra)")
        print(f"📅 YIL SONU: {year_end}\n")
        
        # Görevleri çek
        tasks = Task.query.filter_by(
            assigned_to_id=user.id,
            is_archived=False
        ).order_by(Task.due_date.asc()).all()
        
        if not tasks:
            print("❌ Bu kullanıcıya atanmış hiç görev yok!")
        else:
            print(f"📋 Toplam {len(tasks)} görev bulundu:\n")
            
            # Kategorilere ayır
            categories = {
                'overdue': [],
                'today': [],
                'week': [],
                'month': [],
                'year': [],
                'no_date': []
            }
            
            for task in tasks:
                if not task.due_date:
                    categories['no_date'].append(task)
                    continue
                
                due = task.due_date if isinstance(task.due_date, date) else task.due_date.date()
                
                # Kapsayıcı mantık
                if due < today:
                    categories['overdue'].append(task)
                elif due == today:
                    categories['today'].append(task)
                    categories['week'].append(task)
                    categories['month'].append(task)
                    categories['year'].append(task)
                elif due <= week_end:
                    categories['week'].append(task)
                    categories['month'].append(task)
                    categories['year'].append(task)
                elif due <= month_end:
                    categories['month'].append(task)
                    categories['year'].append(task)
                elif due <= year_end:
                    categories['year'].append(task)
            
            # Sonuçları göster
            print(f"📊 KATEGORİ DAĞILIMI:")
            print(f"   🔴 Geçmiş: {len(categories['overdue'])} görev")
            print(f"   🟢 Bugün: {len(categories['today'])} görev")
            print(f"   🔵 Bu Hafta: {len(categories['week'])} görev")
            print(f"   🟡 Bu Ay: {len(categories['month'])} görev")
            print(f"   🟣 Bu Yıl: {len(categories['year'])} görev")
            print(f"   ⚪ Tarihsiz: {len(categories['no_date'])} görev\n")
            
            # Detaylı liste
            print(f"{'='*70}")
            print("DETAYLI GÖREV LİSTESİ")
            print(f"{'='*70}\n")
            
            for task in tasks:
                status_icon = "✅" if task.status in ['Tamamlandı', 'Completed'] else "⏳"
                
                if not task.due_date:
                    print(f"{status_icon} {task.title}")
                    print(f"   📅 TARİH YOK | Durum: {task.status}\n")
                    continue
                
                due = task.due_date if isinstance(task.due_date, date) else task.due_date.date()
                days_diff = (due - today).days
                
                # Hangi kategorilere dahil
                cats = []
                if due < today:
                    cats.append("GEÇMIŞ")
                elif due == today:
                    cats.append("BUGÜN+HAFTA+AY+YIL")
                elif due <= week_end:
                    cats.append("HAFTA+AY+YIL")
                elif due <= month_end:
                    cats.append("AY+YIL")
                elif due <= year_end:
                    cats.append("YIL")
                
                print(f"{status_icon} {task.title}")
                print(f"   📅 {due} ({days_diff:+d} gün) | Durum: {task.status}")
                print(f"   📂 Kategori: {', '.join(cats)}\n")
