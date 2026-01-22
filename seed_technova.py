
# -*- coding: utf-8 -*-
"""
seed_technova.py
----------------
Failsafe data seeding script for 'TechNova Solutions'.
Usage: python seed_technova.py
"""

import sys
import random
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash
# from models import (
#     User, Kurum, AnaStrateji, StrategyMapLink,
#     Surec, SurecPerformansGostergesi, BireyselPerformansGostergesi,
#     PerformansGostergeVeri, AnalysisItem
# )

# Initialize Flask App
app = create_app()

# Encoding fix for Windows Console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def print_section(title):
    print(f"\n{'-'*60}")
    print(f">> {title}")
    print(f"{'-'*60}")

def print_success(msg):
    print(f"[OK] {msg}")

def print_error(msg):
    print(f"[ERROR] {msg}")

def seed_technova():
    with app.app_context():
        # Import models here to ensure app context and db are ready
        from models import (
            User, Kurum, AnaStrateji, StrategyMapLink,
            Surec, SurecPerformansGostergesi, BireyselPerformansGostergesi,
            PerformansGostergeVeri, AnalysisItem
        )
        
        try:
            print_section("SAFETY CHECK & CLEANUP")
            
            # Global cleanup for clean slate
            # We search by name to find the old one
            target_name = "TechNova Solutions"
            existing_kurums = Kurum.query.filter_by(kisa_ad=target_name).all()
            
            if existing_kurums:
                print(f"Found {len(existing_kurums)} existing institutions with name '{target_name}'. Cleaning up...")
                for k in existing_kurums:
                    # Generic cleanup helper or specific deletions
                    # 1. Users
                    User.query.filter_by(kurum_id=k.id).delete()
                    # 2. Strategies
                    AnaStrateji.query.filter_by(kurum_id=k.id).delete()
                    # 3. Analysis
                    AnalysisItem.query.filter_by(kurum_id=k.id).delete()
                    # 4. Processes
                    Surec.query.filter_by(kurum_id=k.id).delete()
                    # 5. Delete Kurum
                    db.session.delete(k)
                
                db.session.commit()
                print_success(f"Cleanup complete.")
            else:
                print(f"No existing '{target_name}' found.")

            # 2. Phase 1: Foundation (Kurum & Users)
            print_section("PHASE 1: FOUNDATION")
            
            technova = Kurum(
                kisa_ad=target_name,
                ticari_unvan="TechNova Bilişim Çözümleri A.Ş.",
                faaliyet_alani="Yazılım & Teknoloji",
                logo_url="https://ui-avatars.com/api/?name=TN&background=0D8ABC&color=fff&size=128",
                show_guide_system=True
            )
            db.session.add(technova)
            db.session.commit()
            
            # FORCE REFRESH TO GET ID
            db.session.refresh(technova)
            
            if not technova.id:
                raise ValueError("Failed to get ID for new Kurum!")
                
            print_success(f"Institution '{target_name}' created with ID: {technova.id}")
            
            # Users
            pw_hash = generate_password_hash('123456')
            
            users_data = [
                {"role": "ust_yonetim", "u": "can_ceo", "f": "Can", "l": "Yılmaz", "title": "CEO"},
                {"role": "kurum_yoneticisi", "u": "leyla_cto", "f": "Leyla", "l": "Kaya", "title": "CTO"},
                {"role": "kurum_kullanici", "u": "zeynep_hr", "f": "Zeynep", "l": "Demir", "title": "HR Manager"}
            ]
            
            created_users = {}
            
            for u_data in users_data:
                # Check duplicate user
                exists = User.query.filter_by(username=u_data['u']).first()
                if exists:
                    print(f"User {u_data['u']} exists, updating...")
                    exists.kurum_id = technova.id
                    exists.password_hash = pw_hash
                    created_users[u_data['role']] = exists
                else:
                    user = User(
                        username=u_data['u'],
                        email=f"{u_data['u']}@technova.com",
                        first_name=u_data['f'],
                        last_name=u_data['l'],
                        title=u_data['title'],
                        sistem_rol=u_data['role'],
                        password_hash=pw_hash,
                        kurum_id=technova.id
                    )
                    db.session.add(user)
                    created_users[u_data['role']] = user
            
            db.session.commit()
            print_success("Users (CEO, CTO, HR) created/linked.")

            # 3. Phase 2: Strategic Analysis (SWOT/PESTLE)
            print_section("PHASE 2: STRATEGIC ANALYSIS")
            
            swot_items = [
                ("SWOT", "STRENGTH", "Güçlü Ar-Ge Ekibi", 5),
                ("SWOT", "WEAKNESS", "Yetersiz Pazarlama Bütçesi", 3),
                ("SWOT", "OPPORTUNITY", "Yapay Zeka Pazarının Büyümesi", 4),
                ("SWOT", "THREAT", "Ekonomik Dalgalanmalar", 2),
                ("PESTLE", "TECHNOLOGICAL", "5G Teknolojileri", 4),
                ("PESTLE", "ECONOMIC", "Kur Artışı", 3)
            ]
            
            for atype, cat, content, score in swot_items:
                item = AnalysisItem(
                    kurum_id=technova.id,
                    analysis_type=atype,
                    category=cat,
                    content=content,
                    score=score
                )
                db.session.add(item)
            
            db.session.commit()
            print_success(f"Added {len(swot_items)} SWOT/PESTLE items.")

            # 4. Phase 3: The Scorecard (Strategies)
            print_section("PHASE 3: THE SCORECARD (STRATEGIES)")
            
            # Define strategies in a way we can track them
            strategies_def = [
                {"code": "F1", "ad": "Gelirleri Artır", "pers": "FINANSAL"},
                {"code": "F2", "ad": "Maliyetleri Düşür", "pers": "FINANSAL"},
                {"code": "M1", "ad": "Müşteri Memnuniyetini Yükselt", "pers": "MUSTERI"},
                {"code": "S1", "ad": "Operasyonel Mükemmellik", "pers": "SUREC"},
                {"code": "O1", "ad": "Yetenek Yönetimi", "pers": "OGRENME"}
            ]
            
            for s_def in strategies_def:
                strat = AnaStrateji(
                    kurum_id=technova.id,
                    code=s_def['code'],
                    bsc_code=s_def['code'],
                    ad=s_def['ad'],
                    perspective=s_def['pers']
                )
                db.session.add(strat)
            
            db.session.commit()
            print_success("Strategies created. Fetching IDs for reliable wiring...")

            # 5. Phase 4: The Wiring (Links) - The "Anti-Error" Part
            print_section("PHASE 4: THE WIRING (LINKS)")
            
            # Fetch real objects with IDs
            f1 = AnaStrateji.query.filter_by(code='F1', kurum_id=technova.id).first()
            f2 = AnaStrateji.query.filter_by(code='F2', kurum_id=technova.id).first()
            m1 = AnaStrateji.query.filter_by(code='M1', kurum_id=technova.id).first()
            s1 = AnaStrateji.query.filter_by(code='S1', kurum_id=technova.id).first()
            o1 = AnaStrateji.query.filter_by(code='O1', kurum_id=technova.id).first()
            
            # Wiring Logic: Bottom-up or Cause-Effect
            # O1 -> S1 -> M1 -> F1
            links = [
                (o1, s1),
                (s1, m1),
                (m1, f1),
                (m1, f2) # Example: Customer sat. leads to lower churn cost too? or maybe just revenue
            ]
            
            link_count = 0
            for source, target in links:
                if source and target:
                    # Check if link exists
                    exists = StrategyMapLink.query.filter_by(source_id=source.id, target_id=target.id).first()
                    if not exists:
                        link = StrategyMapLink(source_id=source.id, target_id=target.id)
                        db.session.add(link)
                        link_count += 1
            
            db.session.commit()
            print_success(f"[LINK] {link_count} Strategy Links Wired successfully.")

            # 6. Phase 5: Process Data (Charts)
            print_section("PHASE 5: PROCESS DATA (CHARTS)")
            
            # Create Process
            surec = Surec(
                kurum_id=technova.id,
                ad="Yazılım Geliştirme",
                code="SR-MAIN",
                durum="Aktif",
                weight=1.0
            )
            # Check existing? No we deleted kurum so it should be clean.
            db.session.add(surec)
            db.session.commit()
            
            # Create KPI
            kpi = SurecPerformansGostergesi(
                surec_id=surec.id,
                ad="Sprint Velocity",
                hedef_deger="50",
                olcum_birimi="Story Points",
                periyot="Aylık",
                direction="Increasing"
            )
            db.session.add(kpi)
            db.session.commit()
            
            # Assign to User (CTO Leyla generally fits role)
            leyla = User.query.filter_by(username='leyla_cto').first()
            
            bpg = BireyselPerformansGostergesi(
                user_id=leyla.id,
                kaynak_surec_pg_id=kpi.id,
                ad=kpi.ad, # Explicitly adding 'ad' as it is non-nullable
                hedef_deger=kpi.hedef_deger,
                olcum_birimi=kpi.olcum_birimi,
                kaynak='Süreç',
                baslangic_tarihi=datetime.now().date().replace(day=1, month=1),
                bitis_tarihi=datetime.now().date().replace(day=31, month=12)
            )
            db.session.add(bpg)
            db.session.commit()
            
            # Insert 6 months of data
            print("Injecting 6 months of dummy data...")
            base_month = datetime.now().replace(day=1)
            
            data_points = [42, 45, 40, 48, 52, 55] # Increasing trend
            
            for i, val in enumerate(data_points):
                # Go back i months
                # Simple month subtraction logic
                month_offset = 6 - i
                 # Calculate date: basically (now - offset months)
                # A simple approximation
                d = base_month
                for _ in range(month_offset):
                    # Go to first of previous month
                    first_of_month = d.replace(day=1)
                    d = first_of_month - timedelta(days=1)
                
                # d is now end of previous month.
                # Let's say we want data for specific months regardless of exact day
                # We can just iterate linearly from 6 months ago.
                
                # Better approach:
                # Start 6 months ago
                start_date = base_month
                # Go back 6 months approx
                start_date = start_date - timedelta(days=180) 
                
                # Let's just create dates manually for robustness
                target_date = datetime.now() - timedelta(days=30 * (6-i))
                
                pg_veri = PerformansGostergeVeri(
                    bireysel_pg_id=bpg.id,
                    user_id=leyla.id,
                    yil=target_date.year,
                    veri_tarihi=target_date,
                    gerceklesen_deger=str(val),
                    giris_periyot_tipi="Aylık",
                    giris_periyot_ay=target_date.month
                )
                db.session.add(pg_veri)
                
            db.session.commit()
            print_success(f"Inserted 6 data points for '{kpi.ad}'.")
            
            print_section("SEEDING COMPLETE")
            print("TechNova Solutions is ready for demo!")
            
        except Exception as e:
            db.session.rollback()
            print_error(f"Seeding Failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seed_technova()
