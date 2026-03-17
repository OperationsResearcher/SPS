
# -*- coding: utf-8 -*-
"""
seed_technova_full.py
---------------------
Massive, all-in-one data seeding script for 'TechNova Solutions'.
Simulates a fully operational company with rich, interconnected data.
Usage: python seed_technova_full.py
"""

import sys
import random
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash
import services.audit_service

# NUCLEAR FIX: Disable Audit Logging during seeding
# This prevents "IntegrityError: NOT NULL constraint failed: audit_log.user_id"
# because we run outside of a request context with no real user session.
services.audit_service._create_log = lambda mapper, connection, target, action, changes: None
services.audit_service._register_model = lambda model_cls: None
print("🛡️ Audit Logging Disabled for Seeding.")

# Initialize Flask App
app = create_app()

# ENCODING FIX FOR WINDOWS CONSOLE
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Helper functions for colored output
def print_section(title):
    print(f"\n{'-'*60}")
    print(f">> {title}")
    print(f"{'-'*60}")

def print_success(msg):
    print(f"[OK] {msg}")

def print_error(msg):
    print(f"[ERROR] {msg}")

def print_info(msg):
    print(f"[INFO] {msg}")

def log_phase(phase_num, title):
    print(f"\n{'='*70}")
    print(f"PHASE {phase_num}: {title}")
    print(f"{'='*70}")

def log_item(msg):
    print(f"   -> {msg}")

# Models
from models import (
    User, Kurum, AnaStrateji, StrategyMapLink,
    Surec, SurecPerformansGostergesi, BireyselPerformansGostergesi,
    PerformansGostergeVeri, AnalysisItem, TowsMatrix,
    Project, Task, UserActivityLog, AuditLog, Notification
)
import models # For lazy getattr usage

def seed_technova_full():
    with app.app_context():
        try:
            # ---------------------------------------------------------
            # PHASE 0: CLEAN SLATE PROTOCOL
            # ---------------------------------------------------------
            log_phase(0, "CLEAN SLATE PROTOCOL")
            
            target_name = "TechNova Solutions"
            existing_kurums = Kurum.query.filter_by(kisa_ad=target_name).all()
            
            if existing_kurums:
                log_item(f"Found {len(existing_kurums)} existing institutions. Wiping data...")
                for k in existing_kurums:
                    log_item(f"Deleting Institution ID: {k.id}")
                    
                    # 1. Project Portfolio
                    projects = Project.query.filter_by(kurum_id=k.id).all()
                    for p in projects:
                        Task.query.filter_by(project_id=p.id).delete()
                        db.session.delete(p)
                    
                    # 2. Process Management
                    processes = Surec.query.filter_by(kurum_id=k.id).all()
                    for p in processes:
                         # Manual cleanup if cascade misses
                         SurecPerformansGostergesi.query.filter_by(surec_id=p.id).delete()
                         db.session.delete(p)

                    # 3. Strategy & Analysis
                    StrategyMapLink.query.filter(StrategyMapLink.source.has(kurum_id=k.id)).delete()
                    AnaStrateji.query.filter_by(kurum_id=k.id).delete()
                    TowsMatrix.query.filter_by(kurum_id=k.id).delete()
                    AnalysisItem.query.filter_by(kurum_id=k.id).delete()
                    
                    # 4. Users (and their data like BPG)
                    users = User.query.filter_by(kurum_id=k.id).all()
                    app_notif_model = getattr(models, 'Notification', None) or Notification

                    for u in users:
                        PerformansGostergeVeri.query.filter_by(user_id=u.id).delete()
                        BireyselPerformansGostergesi.query.filter_by(user_id=u.id).delete()
                        UserActivityLog.query.filter_by(user_id=u.id).delete()
                        AuditLog.query.filter_by(user_id=u.id).delete()
                        if app_notif_model:
                             app_notif_model.query.filter_by(user_id=u.id).delete()
                        db.session.delete(u)

                    # 5. Kurum itself
                    db.session.delete(k)
                
                db.session.commit()
                print_success("Clean Slate Protocol Executed.")
            else:
                log_item("No existing data found. Starting fresh.")

            # ---------------------------------------------------------
            # PHASE 1: FOUNDATION (Institution & Users)
            # ---------------------------------------------------------
            log_phase(1, "FOUNDATION (Institution & Users)")
            
            technova = Kurum(
                kisa_ad=target_name,
                ticari_unvan="TechNova Bilişim Çözümleri A.Ş.",
                faaliyet_alani="Yazılım & Yapay Zeka",
                sektor="Teknoloji",
                logo_url="https://ui-avatars.com/api/?name=TN&background=0284c7&color=fff&size=128&font-size=0.5",
                show_guide_system=True,
                vizyon="Yapay zeka ile iş dünyasını dönüştüren global lider olmak.",
                amac="Yenilikçi, güvenilir ve sürdürülebilir teknoloji çözümleri sunmak."
            )
            db.session.add(technova)
            db.session.commit()
            db.session.refresh(technova)
            
            log_item(f"Created Institution: {technova.kisa_ad} (ID: {technova.id})")

            # Users
            pw_hash = generate_password_hash('123456')
            
            users_def = [
                {"u": "ceo", "role": "ust_yonetim", "f": "Can", "l": "Yılmaz", "t": "CEO"},
                {"u": "cto", "role": "kurum_yoneticisi", "f": "Leyla", "l": "Kaya", "t": "CTO"},
                {"u": "pm", "role": "surec_lideri", "f": "Murat", "l": "Demir", "t": "Proje Yöneticisi"},
                {"u": "hr", "role": "kurum_kullanici", "f": "Zeynep", "l": "Şahin", "t": "HR Specialist"}
            ]
            
            user_map = {}
            
            for u in users_def:
                chk = User.query.filter_by(username=u['u']).first()
                if chk:
                    # Update existing if somehow survived/exists
                    chk.kurum_id = technova.id
                    user_map[u['u']] = chk
                else:
                    new_u = User(
                        username=u['u'],
                        email=f"{u['u']}@technova.com",
                        first_name=u['f'],
                        last_name=u['l'],
                        title=u['t'],
                        sistem_rol=u['role'],
                        password_hash=pw_hash,
                        kurum_id=technova.id,
                        profile_photo=f"https://ui-avatars.com/api/?name={u['f']}+{u['l']}&background=random"
                    )
                    db.session.add(new_u)
                    user_map[u['u']] = new_u
            
            db.session.commit()
            print_success(f"Created {len(user_map)} Users.")

            # ---------------------------------------------------------
            # PHASE 2: ANALYTICS CENTER (SWOT/PESTLE)
            # ---------------------------------------------------------
            log_phase(2, "ANALYTICS CENTER")
            
            analysis_data = [
                # SWOT
                ("SWOT", "STRENGTH", "Patentli NLP Motoru", 5),
                ("SWOT", "STRENGTH", "Güçlü Ar-Ge Ekibi", 5),
                ("SWOT", "STRENGTH", "Yüksek Müşteri Sadakati", 4),
                ("SWOT", "STRENGTH", "Esnek Altyapı", 4),
                ("SWOT", "WEAKNESS", "Yüksek Sunucu Maliyetleri", 3),
                ("SWOT", "WEAKNESS", "Yetersiz Pazarlama Bütçesi", 4),
                ("SWOT", "WEAKNESS", "Uzun Satış Döngüsü", 2),
                ("SWOT", "WEAKNESS", "Personel Devir Hızı", 3),
                ("SWOT", "OPPORTUNITY", "Global SaaS Pazarı", 5),
                ("SWOT", "OPPORTUNITY", "Devlet Teşvikleri", 4),
                ("SWOT", "OPPORTUNITY", "Uzaktan Çalışma Araçları", 5),
                ("SWOT", "OPPORTUNITY", "Stratejik Ortaklıklar", 3),
                ("SWOT", "THREAT", "Agresif Rakipler", 4),
                ("SWOT", "THREAT", "Ekonomik Dalgalanmalar", 5),
                ("SWOT", "THREAT", "Veri Güvenliği Riskleri", 4),
                ("SWOT", "THREAT", "Teknoloji Bağımlılığı", 2),
                # PESTLE
                ("PESTLE", "POLITICAL", "Veri Koruma Yasaları (KVKK/GDPR)", 4),
                ("PESTLE", "ECONOMIC", "Döviz Kuru Oynaklığı", 5),
                ("PESTLE", "SOCIAL", "Hibrit Çalışma Kültürü", 3),
                ("PESTLE", "TECHNOLOGICAL", "Generative AI Devrimi", 5),
                ("PESTLE", "LEGAL", "Fikri Mülkiyet Hakları", 4),
                ("PESTLE", "ENVIRONMENTAL", "Yeşil Bilişim Gereksinimleri", 2),
            ]
            
            analysis_objs_s = []
            analysis_objs_o = []

            for atype, cat, content, score in analysis_data:
                item = AnalysisItem(
                    kurum_id=technova.id,
                    analysis_type=atype,
                    category=cat,
                    content=content,
                    score=score
                )
                db.session.add(item)
                if cat == "STRENGTH": analysis_objs_s.append(item)
                if cat == "OPPORTUNITY": analysis_objs_o.append(item)
            
            db.session.commit()
            print_success(f"Added {len(analysis_data)} Analysis Items.")
            
            # TOWS Generation
            # Need to fetch IDs after commit
            s_list = AnalysisItem.query.filter_by(kurum_id=technova.id, category="STRENGTH").all()
            o_list = AnalysisItem.query.filter_by(kurum_id=technova.id, category="OPPORTUNITY").all()

            if s_list and o_list:
                tows1 = TowsMatrix(
                    kurum_id=technova.id,
                    strength_id=s_list[0].id,
                    opportunity_threat_id=o_list[0].id,
                    strategy_text=f"Strateji: {s_list[0].content} gücünü kullanarak {o_list[0].content} fırsatını yakala.",
                    action_plan="Ar-Ge ekibini yeni pazara yönlendir."
                )
                tows2 = TowsMatrix(
                    kurum_id=technova.id,
                    strength_id=s_list[1].id if len(s_list)>1 else s_list[0].id,
                    opportunity_threat_id=o_list[1].id if len(o_list)>1 else o_list[0].id,
                    strategy_text=f"Büyüme: {s_list[1].content if len(s_list)>1 else s_list[0].content} ile {o_list[1].content if len(o_list)>1 else o_list[0].content} değerlendir.",
                    action_plan="Yatırımcı sunumlarını hazırla."
                )
                db.session.add_all([tows1, tows2])
                db.session.commit()
                log_item("Generated 2 TOWS Strategies.")

            # ---------------------------------------------------------
            # PHASE 3: PROCESS MANAGEMENT (Processes, KPIs, Data)
            # ---------------------------------------------------------
            log_phase(3, "PROCESS MANAGEMENT")
            
            processes_def = [
                {
                    "name": "Yazılım Geliştirme",
                    "code": "SR-01",
                    "desc": "Agile metodolojileri ile yazılım üretim süreci.",
                    "kpis": [
                        {"name": "Sprint Velocity", "target": "50", "unit": "SP", "dir": "Increasing", "trend": (40, 60)},
                        {"name": "Code Coverage", "target": "85", "unit": "%", "dir": "Increasing", "trend": (70, 90)}
                    ]
                },
                {
                    "name": "Müşteri Başarısı",
                    "code": "SR-02",
                    "desc": "Müşteri memnuniyeti ve desteği.",
                    "kpis": [
                        {"name": "NPS Skoru", "target": "70", "unit": "Puan", "dir": "Increasing", "trend": (50, 80)},
                        {"name": "Ortalama Yanıt Süresi", "target": "30", "unit": "Dk", "dir": "Decreasing", "trend": (60, 20)}
                    ]
                },
                 {
                    "name": "İnsan Kaynakları",
                    "code": "SR-03",
                    "desc": "Yetenek yönetimi ve işe alım.",
                    "kpis": [
                        {"name": "Çalışan Devir Hızı", "target": "10", "unit": "%", "dir": "Decreasing", "trend": (15, 5)},
                        {"name": "Eğitim Memnuniyeti", "target": "4.5", "unit": "5 Üzerinden", "dir": "Increasing", "trend": (3.5, 4.8)}
                    ]
                }
            ]
            
            cto_user = user_map.get("cto")
            total_data_points = 0

            for p_def in processes_def:
                proc = Surec(
                    kurum_id=technova.id,
                    ad=p_def["name"],
                    code=p_def["code"],
                    aciklama=p_def["desc"],
                    durum="Aktif",
                    weight=1.0
                )
                db.session.add(proc)
                db.session.flush() # get ID
                
                for k in p_def["kpis"]:
                    # Create KPI
                    pg = SurecPerformansGostergesi(
                        surec_id=proc.id,
                        ad=k["name"],
                        hedef_deger=k["target"],
                        olcum_birimi=k["unit"],
                        direction=k["dir"],
                        periyot="Aylık"
                    )
                    db.session.add(pg)
                    db.session.flush()

                    # Assign and Create BPG for CTO (as owner of data)
                    bpg = BireyselPerformansGostergesi(
                        user_id=cto_user.id,
                        kaynak_surec_pg_id=pg.id,
                        ad=k["name"],
                        hedef_deger=k["target"],
                        olcum_birimi=k["unit"],
                        kaynak='Süreç',
                        baslangic_tarihi=datetime(2025, 1, 1), # One year ago
                        bitis_tarihi=datetime(2025, 12, 31)
                    )
                    db.session.add(bpg)
                    db.session.flush()
                    
                    # Generate 12 months History
                    # Start from 12 months ago to now
                    today = datetime.now()
                    trend_min, trend_max = k["trend"]
                    
                    for i in range(12, 0, -1):
                        date_point = today - timedelta(days=30*i)
                        # Random val
                        val = random.uniform(trend_min, trend_max)
                        # Add some noise/trend
                        if k["dir"] == "Increasing":
                            val += (12-i) * 0.5 # Slight increase over time
                        else:
                            val -= (12-i) * 0.5 # Slight decrease
                            
                        # Format
                        val_str = f"{val:.1f}"
                        if k["unit"] == "%" or k["unit"] == "SP":
                             val_str = f"{int(val)}"

                        # Check existing
                        existing_data = PerformansGostergeVeri.query.filter_by(
                            bireysel_pg_id=bpg.id,
                            yil=date_point.year,
                            giris_periyot_ay=date_point.month
                        ).first()

                        if not existing_data:
                            entry = PerformansGostergeVeri(
                                bireysel_pg_id=bpg.id,
                                user_id=cto_user.id,
                                yil=date_point.year,
                                veri_tarihi=date_point,
                                giris_periyot_tipi="Aylık",
                                giris_periyot_ay=date_point.month,
                                gerceklesen_deger=val_str
                            )
                            db.session.add(entry)
                            total_data_points += 1
            
            db.session.commit()
            print_success(f"Created {len(processes_def)} Processes, {len(processes_def)*2} KPIs, {total_data_points} Data Points.")

            # ---------------------------------------------------------
            # PHASE 4: BALANCED SCORECARD (Strategies & Wiring)
            # ---------------------------------------------------------
            log_phase(4, "BALANCED SCORECARD")
            
            strategies_data = [
                # Finansal
                ("F1", "Ciro Artışı", "FINANSAL"),
                ("F2", "Maliyet Düşüşü", "FINANSAL"),
                ("F3", "Karlılık", "FINANSAL"),
                # Müşteri
                ("M1", "Global Pazar Genişlemesi", "MUSTERI"),
                ("M2", "Müşteri Sadakati", "MUSTERI"),
                ("M3", "Marka Bilinirliği", "MUSTERI"),
                ("M4", "Yeni Müşteri Kazanımı", "MUSTERI"),
                # Süreç
                ("S1", "AI Otomasyonu", "SUREC"),
                ("S2", "DevOps Dönüşümü", "SUREC"),
                ("S3", "Operasyonel Verimlilik", "SUREC"),
                ("S4", "Ar-Ge İnovasyon", "SUREC"),
                ("S5", "Veri Analitiği", "SUREC"),
                # Öğrenme
                ("G1", "Ar-Ge Yetkinliği", "OGRENME"),
                ("G2", "Liderlik Gelişimi", "OGRENME"),
                ("G3", "Kurumsal Hafıza", "OGRENME"),
            ]
            
            for code, name, pers in strategies_data:
                strat = AnaStrateji(
                    kurum_id=technova.id,
                    code=code,
                    bsc_code=code,
                    ad=name,
                    perspective=pers
                )
                db.session.add(strat)
            
            db.session.commit()
            
            # WIRING
            # Fetch all to map Code -> Object
            strats = AnaStrateji.query.filter_by(kurum_id=technova.id).all()
            s_map = {s.code: s for s in strats}
            
            links_def = [
                ("G1", "S4"), # Ar-Ge Yetkinliği -> Ar-Ge İnovasyon
                ("G1", "S1"),
                ("S1", "M2"), # AI Otomasyon -> Sadakat (Hızlı hizmet)
                ("S2", "S3"), # DevOps -> Verimlilik
                ("S3", "F2"), # Verimlilik -> Maliyet
                ("S4", "M1"), # İnovasyon -> Global Pazar
                ("M1", "F1"), # Global Pazar -> Ciro
                ("M2", "F3"), # Sadakat -> Karlılık
                ("G3", "S5"),
                ("S5", "M3")
            ]
            
            wired_count = 0
            for src_code, tgt_code in links_def:
                if src_code in s_map and tgt_code in s_map:
                    # Check existing
                    exists = StrategyMapLink.query.filter_by(
                        source_id=s_map[src_code].id,
                        target_id=s_map[tgt_code].id
                    ).first()
                    
                    if not exists:
                        link = StrategyMapLink(
                            source_id=s_map[src_code].id,
                            target_id=s_map[tgt_code].id
                        )
                        db.session.add(link)
                        wired_count += 1
                    
            db.session.commit()
            print_success(f"Implementation: 15 Strategies Created. {wired_count} Logical Links Wired.")

            # ---------------------------------------------------------
            # PHASE 5: PROJECT PORTFOLIO (PPM)
            # ---------------------------------------------------------
            log_phase(5, "PROJECT PORTFOLIO")
            
            projects_def = [
                "SPS V2.0 Geliştirme",
                "Bulut Migrasyonu",
                "Mobil App Yenileme",
                "AI Model Eğitimi",
                "Global Pazarlama Kampanyası"
            ]
            
            # Re-fetch users for assignment to ensure session attachment
            # Use query directly
            pm_user_obj = User.query.filter_by(username="pm").first()
            cto_user_obj = User.query.filter_by(username="cto").first()

            if not pm_user_obj: pm_user_obj = User.query.first()
            if not cto_user_obj: cto_user_obj = User.query.first()
            
            task_status_opts = ["Yapılacak", "Devam Ediyor", "Tamamlandı"]
            
            total_tasks = 0
            
            for p_name in projects_def:
                proj = Project(
                    kurum_id=technova.id,
                    name=p_name,
                    description=f"{p_name} projesi için detaylı planlama.",
                    manager_id=pm_user_obj.id,
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=180),
                    priority="Orta",
                    health_score=random.randint(70, 100)
                )
                db.session.add(proj)
                db.session.commit() # Commit to get ID safely
                db.session.refresh(proj)
                
                # Tasks
                for i in range(1, 6):
                    status = random.choice(task_status_opts)
                    progress = 100 if status == "Tamamlandı" else (random.randint(10, 80) if status == "Devam Ediyor" else 0)
                    
                    task = Task(
                        project_id=proj.id,
                        title=f"{p_name} - Faz {i}",
                        description=f"İş paketi detayları için dokümana bakınız.",
                        reporter_id=pm_user_obj.id,
                        assignee_id=cto_user_obj.id,
                        status=status,
                        progress=progress,
                        start_date=datetime.now(),
                        due_date=datetime.now() + timedelta(days=30),
                        priority=random.choice(["High", "Medium", "Low"])
                    )
                    db.session.add(task)
                    # Commit per task to isolate errors and avoid huge session buffer
                    db.session.commit()
                    total_tasks += 1
            
            print_success(f"Created 5 Projects and {total_tasks} Tasks.")
            
            # FINAL
            log_phase(6, "SEEDING COMPLETE")
            print("TechNova Solutions is FULLY OPERATIONAL.")
            print("   You may now log in as 'ceo', 'cto', 'pm' or 'hr' (Password: 123456)")
            
            # Count Verification
            print("\n----- DATA VERIFICATION -----")
            print(f"Users: {User.query.filter_by(kurum_id=technova.id).count()}")
            print(f"Strategies: {AnaStrateji.query.filter_by(kurum_id=technova.id).count()}")
            print(f"Processes: {Surec.query.filter_by(kurum_id=technova.id).count()}")
            print(f"KPIs: {SurecPerformansGostergesi.query.filter(SurecPerformansGostergesi.surec.has(kurum_id=technova.id)).count()}")
            print(f"Projects: {Project.query.filter_by(kurum_id=technova.id).count()}")
            print(f"Tasks: {Task.query.filter(Task.project.has(kurum_id=technova.id)).count()}")

        except Exception as e:
            db.session.rollback()
            print_error(f"Seeding Crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            # Write error to file for reading
            with open("seed_crash.log", "w", encoding="utf-8") as f:
                f.write(str(e))
                f.write("\n")
                traceback.print_exc(file=f)

if __name__ == "__main__":
    seed_technova_full()
