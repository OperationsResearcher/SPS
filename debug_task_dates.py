"""
V3 Dashboard görev tarihlerini debug et
"""
from app import app
from models import Task
from datetime import date, timedelta

with app.app_context():
    # Kullanıcı ID'sini buraya girin (örneğin 1)
    user_id = 1  # ← Kendi kullanıcı ID'nizi buraya yazın
    
    today = date.today()
    week_end = today + timedelta(days=7)
    month_end = today + timedelta(days=30)
    year_end = date(today.year, 12, 31)
    
    print(f"\n{'='*60}")
    print(f"BUGÜN: {today}")
    print(f"HAFTA SONU: {week_end}")
    print(f"AY SONU: {month_end}")
    print(f"YIL SONU: {year_end}")
    print(f"{'='*60}\n")
    
    tasks = Task.query.filter_by(assigned_to_id=user_id, is_archived=False).all()
    
    print(f"Toplam {len(tasks)} görev bulundu:\n")
    
    for task in tasks:
        if not task.due_date:
            print(f"❌ {task.title}: TARİH YOK (Status: {task.status})")
            continue
            
        due = task.due_date if isinstance(task.due_date, date) else task.due_date.date()
        
        # Kategorileri belirle
        categories = []
        
        if due < today:
            categories.append("GEÇMIŞ")
        elif due == today:
            categories.append("BUGÜN → HAFTA → AY → YIL")
        elif due <= week_end:
            categories.append("HAFTA → AY → YIL")
        elif due <= month_end:
            categories.append("AY → YIL")
        elif due <= year_end:
            categories.append("YIL")
        else:
            categories.append("GELECEK YIL")
        
        status_icon = "✅" if task.status in ['Tamamlandı', 'Completed'] else "⏳"
        
        print(f"{status_icon} {task.title}")
        print(f"   📅 Bitiş: {due} | Durum: {task.status}")
        print(f"   📂 Kategori: {', '.join(categories)}")
        print()
