"""
1salih kullanıcısının GERÇEK görevlerini VERİTABANINDAN çek
"""
from app import app
from models import Task, User
from datetime import date, timedelta
from sqlalchemy import inspect

with app.app_context():
    user = User.query.filter_by(username='1salih').first()
    
    if not user:
        print("❌ '1salih' kullanıcısı bulunamadı!")
    else:
        print(f"\n{'='*80}")
        print(f"👤 Kullanıcı: {user.username} (ID: {user.id})")
        print(f"{'='*80}\n")
        
        # RAW SQL ile görevleri çek
        from extensions import db
        
        query = """
        SELECT id, title, due_date, status, is_archived, project_id
        FROM task
        WHERE assigned_to_id = :user_id
        ORDER BY due_date ASC
        """
        
        result = db.session.execute(db.text(query), {'user_id': user.id})
        rows = result.fetchall()
        
        print(f"📋 Veritabanında {len(rows)} görev bulundu:\n")
        
        today = date.today()
        week_end = today + timedelta(days=7)
        month_end = today + timedelta(days=30)
        
        print(f"📅 BUGÜN: {today}")
        print(f"📅 HAFTA SONU: {week_end}")
        print(f"📅 AY SONU: {month_end}\n")
        print(f"{'='*80}\n")
        
        for row in rows:
            task_id, title, due_date, status, is_archived, project_id = row
            
            print(f"🔍 GÖREV ID: {task_id}")
            print(f"   📝 Başlık: {title}")
            print(f"   📅 due_date (RAW): {due_date} (Tip: {type(due_date).__name__})")
            print(f"   📊 Status: {status}")
            print(f"   📦 is_archived: {is_archived}")
            print(f"   🏢 project_id: {project_id}")
            
            if due_date:
                # Tarihi parse et
                if isinstance(due_date, str):
                    from datetime import datetime
                    try:
                        due = datetime.strptime(due_date, '%Y-%m-%d').date()
                    except:
                        try:
                            due = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S').date()
                        except:
                            print(f"   ❌ TARİH PARSE EDİLEMEDİ!")
                            continue
                elif isinstance(due_date, date):
                    due = due_date
                else:
                    due = due_date.date() if hasattr(due_date, 'date') else None
                
                if due:
                    days_diff = (due - today).days
                    
                    # Kategorileri belirle
                    cats = []
                    if due < today:
                        cats.append("GEÇMIŞ")
                    elif due == today:
                        cats.append("BUGÜN → HAFTA → AY → YIL")
                    elif due <= week_end:
                        cats.append("HAFTA → AY → YIL")
                    elif due <= month_end:
                        cats.append("AY → YIL")
                    else:
                        cats.append("YIL")
                    
                    print(f"   🗓️  Parse edilmiş: {due} ({days_diff:+d} gün)")
                    print(f"   📂 Kategori: {', '.join(cats)}")
            
            print()
