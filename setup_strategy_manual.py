# -*- coding: utf-8 -*-
import sys
import os

# Windows konsol encoding sorununu çöz
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from app import app
from sqlalchemy import text
import time

# Model ve DB bağlantısını güvenli şekilde al
try:
    from app import db
except ImportError:
    from models import db

from models import CorporateIdentity, MainStrategy, SubStrategy, Process, StrategyProcessMatrix, User, PerformanceIndicator

# ----------------------------------------------------------------
# YARDIMCI: DUMMY KURUM OLUŞTURUCU (ID: 87)
# ----------------------------------------------------------------
def ensure_dummy_institution(target_id):
    print(f"[KURUM] Kurum ID ({target_id}) Kontrolu Yapiliyor...")
    try:
        # Önce mevcut kurumu kontrol et
        from models import Kurum
        existing_kurum = Kurum.query.get(target_id)
        if existing_kurum:
            print(f"   [OK] Kurum (ID:{target_id}) zaten mevcut: {existing_kurum.kisa_ad}")
            return existing_kurum
        
        # Yoksa oluştur
        new_kurum = Kurum(
            id=target_id,
            kisa_ad='KMF Demo Kurum',
            ticari_unvan='KMF Demo Kurum A.S.',
            faaliyet_alani='Model Fabrika'
        )
        db.session.add(new_kurum)
        db.session.commit()
        print(f"   [OK] Kurum (ID:{target_id}) olusturuldu.")
        return new_kurum
    except Exception as e:
        db.session.rollback()
        print(f"   [HATA] Kurum olusturma hatasi: {e}")
        import traceback
        traceback.print_exc()
        raise

def force_reset_schema():
    print("[BALYOZ MODU] Tablolar Zorla Siliniyor...")
    
    engine = db.engine
    
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF;"))
        
        tables_to_drop = [
            'strategy_process_matrix',
            'sub_strategy', 'alt_strateji', 
            'main_strategy', 'ana_strateji', 
            'process_owners', 'surec_sahipleri',
            'process', 'surec',
            'corporate_identity', 'kurumsal_kimlik',
            'project_processes', 'project_related_processes'
        ]
        
        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"   [SILINDI] {table}")
            except Exception as e:
                print(f"   [HATA] ({table}): {e}")
        
        conn.execute(text("PRAGMA foreign_keys=ON;"))
        conn.commit()
    
    print("[OLUSTURMA] Tablolar Yeniden Olusturuluyor (db.create_all)...")
    db.create_all()
    print("[OK] Sema tertemiz bir sekilde kuruldu.")

def seed_strategy_data():
    # 1. Şemayı Temizle
    force_reset_schema()
    
    # 2. SABİT KURUM ID: 87
    FIXED_KURUM_ID = 87
    ensure_dummy_institution(FIXED_KURUM_ID)
    
    print("\n[VERI YUKLEME] Veri Yukleme Basliyor...")

    # A. KURUMSAL KİMLİK
    try:
        import json
        # Önce mevcut kaydı kontrol et
        existing_identity = CorporateIdentity.query.filter_by(kurum_id=FIXED_KURUM_ID).first()
        if existing_identity:
            print("[OK] Kurumsal Kimlik zaten mevcut, guncelleniyor...")
            existing_identity.vizyon = "2026 yilina kadar uluslararasi projeler ustlenmek ve Turkiye'nin oncu Model Fabrikasi olmayi surdurmek."
            existing_identity.misyon = "Basta sanayicimiz olmak uzere ilgili paydaslarin yalin donusum, dijital donusum, yesil donusum basliklarini icermek uzere surdurulebilirliklerine katki saglayarak ulkemizin endustriyel kalkinmasina destek olmak."
            existing_identity.degerler = json.dumps(["Verimlilik", "Uretkenlik", "Paylasimcilik", "Seffaflik", "Ulkeye Adanmislik"])
            existing_identity.kalite_politikasi = "Model Fabrika Prensiplerine uygun, surdurulebilir kalite anlayisi."
        else:
            identity = CorporateIdentity(
                kurum_id=FIXED_KURUM_ID,
                vizyon="2026 yilina kadar uluslararasi projeler ustlenmek ve Turkiye'nin oncu Model Fabrikasi olmayi surdurmek.",
                misyon="Basta sanayicimiz olmak uzere ilgili paydaslarin yalin donusum, dijital donusum, yesil donusum basliklarini icermek uzere surdurulebilirliklerine katki saglayarak ulkemizin endustriyel kalkinmasina destek olmak.",
                degerler=json.dumps(["Verimlilik", "Uretkenlik", "Paylasimcilik", "Seffaflik", "Ulkeye Adanmislik"]),
                kalite_politikasi="Model Fabrika Prensiplerine uygun, surdurulebilir kalite anlayisi."
            )
            db.session.add(identity)
        db.session.commit()
        print("[OK] Kurumsal Kimlik eklendi/guncellendi.")
    except Exception as e:
        db.session.rollback()
        print(f"[HATA] Kurumsal Kimlik hatasi: {e}")
        import traceback
        traceback.print_exc()
        return  # Hata varsa devam etme

    # B. SÜREÇLER
    processes_data = [
        {"code": "SR1", "name": "Şirket Organları Yönetimi Süreci", "weight": 0.06},
        {"code": "SR2", "name": "Stratejik Planlama Süreci", "weight": 0.13},
        {"code": "SR3", "name": "Kurum İmajı ve Kültürü Yönetme Süreci", "weight": 0.09},
        {"code": "SR4", "name": "Pazarlama Stratejileri Yönetim Süreci", "weight": 0.13},
        {"code": "SR5", "name": "Eğitim Hizmetleri Yönetim Süreci", "weight": 0.08},
        {"code": "SR6", "name": "Danışmanlık Hizmetleri Yönetim Süreci", "weight": 0.15},
        {"code": "SR7", "name": "Başarıları Tanıma ve Ödüllendirme Süreci", "weight": 0.08},
        {"code": "SR8", "name": "İnsan Kaynakları Yönetim Süreci", "weight": 0.11},
        {"code": "SR9", "name": "Mali İşler Yönetim Süreci", "weight": 0.05},
        {"code": "SR10", "name": "Tedarik Yönetim Süreci", "weight": 0.05},
        {"code": "SR11", "name": "Makine, Teknoloji ve Bilgi Yönetim Süreci", "weight": 0.07}
    ]
    
    process_objects = {}
    for p_data in processes_data:
        try:
            # Önce mevcut süreci kontrol et
            existing_proc = Process.query.filter_by(code=p_data["code"], kurum_id=FIXED_KURUM_ID).first()
            if existing_proc:
                process_objects[p_data["code"]] = existing_proc
                continue
            
            # Surec modeli: code, ad (zorunlu), name (opsiyonel), weight, kurum_id
            proc = Process(
                code=p_data["code"], 
                ad=p_data["name"],  # ad zorunlu
                name=p_data["name"],  # name opsiyonel
                weight=p_data["weight"],
                kurum_id=FIXED_KURUM_ID 
            )
            db.session.add(proc)
            db.session.flush()  # ID'yi almak için
            process_objects[p_data["code"]] = proc
        except Exception as e:
            db.session.rollback()
            print(f"[HATA] Surec eklenirken hata ({p_data['code']}): {e}")
            import traceback
            traceback.print_exc()
            return  # Hata varsa devam etme
    
    db.session.commit()
    print(f"[OK] {len(process_objects)} Surec eklendi.")

    # C. STRATEJİLER
    strategies_data = [
        {"code": "ST1", "name": "KMF'nin stratejik yönünü belirlemek ve güncel tutmak", "subs": [{"code": "ST1.1", "name": "Stratejik plan hazırlamak...", "method": "HKY"}, {"code": "ST1.2", "name": "Farklı enstrümanlardan yararlanmak", "method": "SH"}]},
        {"code": "ST2", "name": "KMF'nin hukuki ve mali sürdürülebilirliğini sağlamak", "subs": [{"code": "ST2.1", "name": "Karlı büyümeye odaklanmak", "method": "HKY"}, {"code": "ST2.2", "name": "Mali kaynakları etkin yönetmek", "method": "DH"}]},
        {"code": "ST3", "name": "Sürdürülebilirliğe katkı sağlamak", "subs": [{"code": "ST3.1", "name": "Yalın dönüşüm hizmetlerini yaygınlaştırmak", "method": "HKY"}]},
        {"code": "ST4", "name": "Sürekli iyileştirme ve ödül süreci", "subs": [{"code": "ST4.1", "name": "Ödül sistematiği kurmak", "method": "SH"}]}
    ]

    sub_strategy_objects = {}
    
    for st_data in strategies_data:
        try:
            # Önce mevcut ana stratejiyi kontrol et
            existing_main = MainStrategy.query.filter_by(code=st_data["code"], kurum_id=FIXED_KURUM_ID).first()
            if existing_main:
                main_st = existing_main
            else:
                # MainStrategy (AnaStrateji): code, ad (zorunlu), name (opsiyonel), kurum_id
                main_st = MainStrategy(
                    code=st_data["code"], 
                    ad=st_data["name"],  # ad zorunlu
                    name=st_data["name"],  # name opsiyonel
                    kurum_id=FIXED_KURUM_ID 
                )
                db.session.add(main_st)
                db.session.flush()  # ID'yi almak için
            
            for sub_data in st_data["subs"]:
                try:
                    # Önce mevcut alt stratejiyi kontrol et
                    existing_sub = SubStrategy.query.filter_by(code=sub_data["code"], ana_strateji_id=main_st.id).first()
                    if existing_sub:
                        sub_strategy_objects[sub_data["code"]] = existing_sub
                        continue
                    
                    # SubStrategy (AltStrateji): code, ad (zorunlu), name (opsiyonel), target_method, ana_strateji_id (parent_id değil!)
                    sub_st = SubStrategy(
                        code=sub_data["code"], 
                        ad=sub_data["name"],  # ad zorunlu
                        name=sub_data["name"],  # name opsiyonel
                        target_method=sub_data["method"], 
                        ana_strateji_id=main_st.id  # parent_id değil, ana_strateji_id!
                    )
                    db.session.add(sub_st)
                    db.session.flush()  # ID'yi almak için
                    sub_strategy_objects[sub_data["code"]] = sub_st
                except Exception as e:
                    db.session.rollback()
                    print(f"[HATA] Alt Strateji eklenirken hata ({sub_data['code']}): {e}")
                    import traceback
                    traceback.print_exc()
                    return  # Hata varsa devam etme
        except Exception as e:
            db.session.rollback()
            print(f"[HATA] Ana Strateji eklenirken hata ({st_data['code']}): {e}")
            import traceback
            traceback.print_exc()
            return  # Hata varsa devam etme
            
    db.session.commit()
    print(f"[OK] {len(strategies_data)} Ana Strateji ve {len(sub_strategy_objects)} Alt Strateji eklendi.")

    # D. MATRİS İLİŞKİLERİ
    matrix_relations = [
        ("ST1.1", "SR2", 9), ("ST1.1", "SR1", 3), ("ST1.1", "SR3", 3), ("ST1.1", "SR4", 3),
        ("ST2.1", "SR1", 9), ("ST2.1", "SR2", 9), ("ST2.1", "SR4", 9), ("ST2.1", "SR9", 9),
        ("ST2.1", "SR5", 3), ("ST2.1", "SR6", 3),
        ("ST3.1", "SR4", 9), ("ST3.1", "SR2", 3), ("ST3.1", "SR3", 3), ("ST3.1", "SR5", 3)
    ]

    count_matrix = 0
    for st_code, sr_code, score in matrix_relations:
        if st_code in sub_strategy_objects and sr_code in process_objects:
            sub_st = sub_strategy_objects[st_code]
            proc = process_objects[sr_code]
            
            # Önce mevcut matris kaydını kontrol et
            existing_matrix = StrategyProcessMatrix.query.filter_by(
                sub_strategy_id=sub_st.id,
                process_id=proc.id
            ).first()
            
            if existing_matrix:
                existing_matrix.relationship_score = score
                count_matrix += 1
            else:
                matrix_entry = StrategyProcessMatrix(
                    sub_strategy_id=sub_st.id,
                    process_id=proc.id,
                    relationship_score=score
                )
                db.session.add(matrix_entry)
                count_matrix += 1

    db.session.commit()
    print(f"[OK] {count_matrix} Matris iliskisi kuruldu.")

    # Tüm işlemler zaten commit edildi, burada sadece mesaj ver
    print("[TAMAMLANDI] ISLEM TAMAM! Tum stratejik veriler veritabanina islendi.")

if __name__ == "__main__":
    with app.app_context():
        seed_strategy_data()