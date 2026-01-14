# -*- coding: utf-8 -*-
"""
Raporlama Özellikli Uçtan Uca (E2E) Sistem Test Scripti
SQLite altyapısına taşınmış sistemin tüm modüllerinin entegrasyonunu doğrular.
"""
import sys
import traceback
from datetime import datetime, date, timedelta
from flask import Flask
from werkzeug.security import generate_password_hash

# Uygulama ve modelleri import et
from __init__ import create_app
from models import (
    db, User, Kurum, Surec, SurecPerformansGostergesi,
    PerformansGostergeVeri, BireyselPerformansGostergesi, BireyselFaaliyet,
    Project, Task, TaskSubtask, ProjectRisk, surec_liderleri, surec_uyeleri
)

# Test sonuçları için global değişkenler
TEST_RESULTS = {
    'total_steps': 0,
    'successful': 0,
    'failed': 0,
    'errors': []
}

# Test verileri için ID'ler
TEST_DATA_IDS = {
    'kurum_id': None,
    'user_id': None,
    'surec_id': None,
    'pg_id': None,
    'project_id': None,
    'task_id': None,
    'subtask_id': None,
    'risk_id': None
}


def log(message, status="INFO"):
    """
    Mesajı hem terminale hem de test_results.txt dosyasına yazar.
    
    Args:
        message: Log mesajı
        status: Mesaj durumu (INFO, SUCCESS, ERROR)
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Durum ikonları
    status_icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌"
    }
    
    icon = status_icons.get(status, "ℹ️")
    status_text = {
        "INFO": "BİLGİ",
        "SUCCESS": "BAŞARILI",
        "ERROR": "HATA"
    }.get(status, "BİLGİ")
    
    log_line = f"[{timestamp}] [{icon} {status_text}] {message}"
    
    # Terminale yazdır
    print(log_line)
    
    # Dosyaya yazdır
    try:
        with open('test_results.txt', 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
            
            # Hata durumunda traceback ekle
            if status == "ERROR" and sys.exc_info()[0] is not None:
                f.write(traceback.format_exc() + '\n')
    except Exception as e:
        print(f"Log dosyasına yazma hatası: {e}")


def reset_log_file():
    """Test başlangıcında log dosyasını sıfırla"""
    try:
        with open('test_results.txt', 'w', encoding='utf-8') as f:
            f.write(f"=== TEST BAŞLANGIÇ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    except Exception as e:
        print(f"Log dosyası sıfırlama hatası: {e}")


def test_step(step_name, test_func):
    """
    Test adımını çalıştırır ve sonucu kaydeder.
    
    Args:
        step_name: Test adımının adı
        test_func: Test fonksiyonu (True dönerse başarılı)
    """
    TEST_RESULTS['total_steps'] += 1
    log(f"Test Adımı: {step_name}", "INFO")
    
    try:
        result = test_func()
        if result:
            TEST_RESULTS['successful'] += 1
            log(f"✓ {step_name} - BAŞARILI", "SUCCESS")
            return True
        else:
            TEST_RESULTS['failed'] += 1
            log(f"✗ {step_name} - BAŞARISIZ", "ERROR")
            return False
    except Exception as e:
        TEST_RESULTS['failed'] += 1
        TEST_RESULTS['errors'].append({
            'step': step_name,
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        log(f"✗ {step_name} - HATA: {str(e)}", "ERROR")
        return False


def setup_test_environment(app):
    """Test ortamını hazırla"""
    log("Test ortamı hazırlanıyor...", "INFO")
    
    # CSRF korumasını kapat
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Test client oluştur
    client = app.test_client()
    
    # Admin kullanıcısını bul veya oluştur
    admin_user = User.query.filter_by(username='Admin').first()
    if not admin_user:
        # Admin kullanıcısı yoksa, ilk admin kullanıcısını bul
        admin_user = User.query.filter_by(sistem_rol='admin').first()
    
    if not admin_user:
        log("Admin kullanıcısı bulunamadı! Test için bir admin kullanıcısı gerekli.", "ERROR")
        return None, None
    
    log(f"Admin kullanıcısı bulundu: {admin_user.username} (ID: {admin_user.id})", "SUCCESS")
    
    # Session ile oturum aç
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_user.id)
        sess['_fresh'] = True
    
    return client, admin_user


def test_kurum_ekle(client, admin_user):
    """A. KURUM YÖNETİMİ: Test kurumu oluştur"""
    def _test():
        # Önce aynı isimde kurum var mı kontrol et
        existing = Kurum.query.filter_by(kisa_ad='Test Otomasyon Holding').first()
        if existing:
            log(f"Mevcut kurum bulundu, siliniyor: ID={existing.id}", "INFO")
            db.session.delete(existing)
            db.session.commit()
        
        # Kurum oluştur (doğrudan DB'ye yaz)
        kurum = Kurum(
            kisa_ad='Test Otomasyon Holding',
            ticari_unvan='Test Otomasyon Holding A.Ş.',
            faaliyet_alani='Yazılım Test Otomasyonu',
            sektor='Teknoloji',
            calisan_sayisi=50
        )
        db.session.add(kurum)
        db.session.commit()
        
        # DB'den kurumu kontrol et
        kurum_check = Kurum.query.filter_by(kisa_ad='Test Otomasyon Holding').first()
        if not kurum_check:
            log("Kurum veritabanında bulunamadı!", "ERROR")
            return False
        
        TEST_DATA_IDS['kurum_id'] = kurum_check.id
        log(f"Kurum oluşturuldu: ID={kurum_check.id}", "SUCCESS")
        return True
    
    return test_step("A. Kurum Yönetimi - Kurum Ekleme", _test)


def test_kullanici_ekle(client, admin_user):
    """B. KULLANICI YÖNETİMİ: Test kullanıcısı oluştur"""
    def _test():
        if not TEST_DATA_IDS['kurum_id']:
            log("Kurum ID bulunamadı!", "ERROR")
            return False
        
        # Önce aynı kullanıcı var mı kontrol et
        existing = User.query.filter_by(username='test_mudur').first()
        if existing:
            log(f"Mevcut kullanıcı bulundu, siliniyor: ID={existing.id}", "INFO")
            db.session.delete(existing)
            db.session.commit()
        
        # Kullanıcı oluştur (doğrudan DB'ye yaz)
        user = User(
            username='test_mudur',
            email='test_mudur@test.com',
            password_hash=generate_password_hash('Test123!'),
            first_name='Test',
            last_name='Müdür',
            sistem_rol='kurum_yoneticisi',
            kurum_id=TEST_DATA_IDS['kurum_id']
        )
        db.session.add(user)
        db.session.commit()
        
        # DB'den kullanıcıyı kontrol et
        user_check = User.query.filter_by(username='test_mudur').first()
        if not user_check:
            log("Kullanıcı veritabanında bulunamadı!", "ERROR")
            return False
        
        TEST_DATA_IDS['user_id'] = user_check.id
        log(f"Kullanıcı oluşturuldu: ID={user_check.id}", "SUCCESS")
        return True
    
    return test_step("B. Kullanıcı Yönetimi - Kullanıcı Ekleme", _test)


def test_surec_ekle(client, admin_user):
    """C. STRATEJİK PLANLAMA: Süreç oluştur"""
    def _test():
        if not TEST_DATA_IDS['kurum_id'] or not TEST_DATA_IDS['user_id']:
            log("Kurum veya Kullanıcı ID bulunamadı!", "ERROR")
            return False
        
        # Önce aynı süreç var mı kontrol et
        existing = Surec.query.filter_by(ad='Bilgi İşlem Süreci').first()
        if existing:
            log(f"Mevcut süreç bulundu, siliniyor: ID={existing.id}", "INFO")
            # İlişkileri temizle
            existing.liderler.clear()
            existing.uyeler.clear()
            db.session.delete(existing)
            db.session.commit()
        
        # Süreç oluştur (doğrudan DB'ye yaz)
        surec = Surec(
            ad='Bilgi İşlem Süreci',
            kurum_id=TEST_DATA_IDS['kurum_id'],
            durum='Aktif',
            ilerleme=0
        )
        db.session.add(surec)
        db.session.flush()  # ID'yi almak için
        
        # Lider ilişkisini ekle
        lider = User.query.get(TEST_DATA_IDS['user_id'])
        if lider:
            surec.liderler.append(lider)
        
        db.session.commit()
        
        # DB'den süreci kontrol et
        surec_check = Surec.query.filter_by(ad='Bilgi İşlem Süreci').first()
        if not surec_check:
            log("Süreç veritabanında bulunamadı!", "ERROR")
            return False
        
        # Lider ilişkisini kontrol et
        liderler = [u.id for u in surec_check.liderler]
        if TEST_DATA_IDS['user_id'] not in liderler:
            log("Süreç lider ilişkisi kurulamadı!", "ERROR")
            return False
        
        TEST_DATA_IDS['surec_id'] = surec_check.id
        log(f"Süreç oluşturuldu: ID={surec_check.id}, Liderler: {liderler}", "SUCCESS")
        return True
    
    return test_step("C. Stratejik Planlama - Süreç Ekleme", _test)


def test_performans_gostergesi_ekle(client, admin_user):
    """C. STRATEJİK PLANLAMA: Performans göstergesi ekle"""
    def _test():
        if not TEST_DATA_IDS['surec_id']:
            log("Süreç ID bulunamadı!", "ERROR")
            return False
        
        # Önce aynı PG var mı kontrol et
        existing = SurecPerformansGostergesi.query.filter_by(
            surec_id=TEST_DATA_IDS['surec_id'],
            ad='Test Performans Göstergesi'
        ).first()
        if existing:
            log(f"Mevcut PG bulundu, siliniyor: ID={existing.id}", "INFO")
            db.session.delete(existing)
            db.session.commit()
        
        # Performans göstergesi oluştur (doğrudan DB'ye yaz)
        pg = SurecPerformansGostergesi(
            surec_id=TEST_DATA_IDS['surec_id'],
            ad='Test Performans Göstergesi',
            aciklama='Test için oluşturuldu',
            hedef_deger='100',
            olcum_birimi='Adet',
            periyot='Aylik',
            veri_toplama_yontemi='Toplam'
        )
        db.session.add(pg)
        db.session.commit()
        
        # DB'den PG'yi kontrol et
        pg_check = SurecPerformansGostergesi.query.filter_by(
            surec_id=TEST_DATA_IDS['surec_id'],
            ad='Test Performans Göstergesi'
        ).first()
        
        if not pg_check:
            log("Performans göstergesi veritabanında bulunamadı!", "ERROR")
            return False
        
        TEST_DATA_IDS['pg_id'] = pg_check.id
        log(f"Performans göstergesi oluşturuldu: ID={pg_check.id}", "SUCCESS")
        return True
    
    return test_step("C. Stratejik Planlama - Performans Göstergesi Ekleme", _test)


def test_pg_veri_girisi(client, admin_user):
    """C. STRATEJİK PLANLAMA: PG veri girişi"""
    def _test():
        if not TEST_DATA_IDS['pg_id'] or not TEST_DATA_IDS['user_id']:
            log("PG veya Kullanıcı ID bulunamadı!", "ERROR")
            return False
        
        # Önce bireysel PG oluştur (süreç PG'sinden türetilmiş)
        bireysel_pg = BireyselPerformansGostergesi(
            user_id=TEST_DATA_IDS['user_id'],
            ad='Test Performans Göstergesi',
            kaynak='Süreç',
            kaynak_surec_id=TEST_DATA_IDS['surec_id'],
            kaynak_surec_pg_id=TEST_DATA_IDS['pg_id'],
            hedef_deger='100',
            olcum_birimi='Adet',
            periyot='Aylik'
        )
        db.session.add(bireysel_pg)
        db.session.commit()
        
        # Ocak ayı için veri girişi
        yil = datetime.now().year
        ocak_tarihi = date(yil, 1, 31)  # Ocak ayının son Cuması yaklaşık
        
        pg_veri = PerformansGostergeVeri(
            bireysel_pg_id=bireysel_pg.id,
            user_id=TEST_DATA_IDS['user_id'],
            yil=yil,
            veri_tarihi=ocak_tarihi,
            giris_periyot_tipi='aylik',
            giris_periyot_no=1,
            giris_periyot_ay=1,
            ay=1,
            gerceklesen_deger='100',
            aciklama='Test veri girişi'
        )
        db.session.add(pg_veri)
        db.session.commit()
        
        # DB'den veriyi kontrol et
        veri = PerformansGostergeVeri.query.filter_by(
            bireysel_pg_id=bireysel_pg.id,
            yil=yil,
            ay=1
        ).first()
        
        if not veri:
            log("PG verisi veritabanında bulunamadı!", "ERROR")
            return False
        
        log(f"PG veri girişi yapıldı: ID={veri.id}, Değer={veri.gerceklesen_deger}", "SUCCESS")
        return True
    
    return test_step("C. Stratejik Planlama - PG Veri Girişi", _test)


def test_proje_ekle(client, admin_user):
    """D. PROJE YÖNETİMİ: Proje oluştur"""
    def _test():
        if not TEST_DATA_IDS['kurum_id'] or not TEST_DATA_IDS['user_id'] or not TEST_DATA_IDS['surec_id']:
            log("Gerekli ID'ler bulunamadı!", "ERROR")
            return False
        
        # Önce aynı isimde proje var mı kontrol et ve sil
        existing = Project.query.filter_by(name='Test Projesi').first()
        if existing:
            log(f"Mevcut proje bulundu, siliniyor: ID={existing.id}", "INFO")
            # İlişkileri temizle
            existing.related_processes.clear()
            existing.members.clear()
            existing.observers.clear()
            db.session.delete(existing)
            db.session.commit()
        
        # Proje oluştur (doğrudan DB'ye yaz)
        project = Project(
            kurum_id=TEST_DATA_IDS['kurum_id'],
            name='Test Projesi',
            manager_id=TEST_DATA_IDS['user_id'],
            description='Test için oluşturuldu',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            priority='Orta'
        )
        db.session.add(project)
        db.session.flush()  # ID'yi almak için
        
        # Süreç ilişkisini ekle (mükerrer kontrolü ile)
        surec = Surec.query.get(TEST_DATA_IDS['surec_id'])
        if surec:
            # İlişki zaten var mı kontrol et
            if surec not in project.related_processes:
                project.related_processes.append(surec)
        
        db.session.commit()
        
        # DB'den projeyi kontrol et
        proje = Project.query.filter_by(name='Test Projesi').first()
        if not proje:
            log("Proje veritabanında bulunamadı!", "ERROR")
            return False
        
        # İlişkiyi kontrol et
        related_surec_ids = [s.id for s in proje.related_processes]
        if TEST_DATA_IDS['surec_id'] not in related_surec_ids:
            log("Süreç ilişkisi kurulamadı!", "ERROR")
            return False
        
        TEST_DATA_IDS['project_id'] = proje.id
        log(f"Proje oluşturuldu: ID={proje.id}, İlişkili Süreçler: {related_surec_ids}", "SUCCESS")
        return True
    
    return test_step("D. Proje Yönetimi - Proje Ekleme", _test)


def test_gorev_ekle(client, admin_user):
    """D. PROJE YÖNETİMİ: Görev ekle"""
    def _test():
        if not TEST_DATA_IDS['project_id'] or not TEST_DATA_IDS['user_id']:
            log("Proje veya Kullanıcı ID bulunamadı!", "ERROR")
            return False
        
        # Görev oluştur
        task = Task(
            project_id=TEST_DATA_IDS['project_id'],
            assigned_to_id=TEST_DATA_IDS['user_id'],
            title='Test Görevi',
            description='Test için oluşturuldu',
            due_date=date.today() + timedelta(days=7),
            priority='Orta',
            status='Yapılacak'
        )
        db.session.add(task)
        db.session.commit()
        
        # DB'den görevi kontrol et
        gorev = Task.query.filter_by(
            project_id=TEST_DATA_IDS['project_id'],
            title='Test Görevi'
        ).first()
        
        if not gorev:
            log("Görev veritabanında bulunamadı!", "ERROR")
            return False
        
        TEST_DATA_IDS['task_id'] = gorev.id
        log(f"Görev oluşturuldu: ID={gorev.id}", "SUCCESS")
        return True
    
    return test_step("D. Proje Yönetimi - Görev Ekleme", _test)


def test_alt_gorev_ekle(client, admin_user):
    """D. PROJE YÖNETİMİ: Alt görev ekle"""
    def _test():
        if not TEST_DATA_IDS['task_id']:
            log("Görev ID bulunamadı!", "ERROR")
            return False
        
        # Alt görev oluştur
        subtask = TaskSubtask(
            task_id=TEST_DATA_IDS['task_id'],
            title='Test Alt Görev',
            is_completed=False,
            order=0
        )
        db.session.add(subtask)
        db.session.commit()
        
        # DB'den alt görevi kontrol et
        alt_gorev = TaskSubtask.query.filter_by(
            task_id=TEST_DATA_IDS['task_id'],
            title='Test Alt Görev'
        ).first()
        
        if not alt_gorev:
            log("Alt görev veritabanında bulunamadı!", "ERROR")
            return False
        
        TEST_DATA_IDS['subtask_id'] = alt_gorev.id
        log(f"Alt görev oluşturuldu: ID={alt_gorev.id}", "SUCCESS")
        return True
    
    return test_step("D. Proje Yönetimi - Alt Görev Ekleme", _test)


def test_risk_ekle(client, admin_user):
    """D. PROJE YÖNETİMİ: Risk ekle"""
    def _test():
        if not TEST_DATA_IDS['project_id'] or not TEST_DATA_IDS['user_id']:
            log("Proje veya Kullanıcı ID bulunamadı!", "ERROR")
            return False
        
        # Risk oluştur
        risk = ProjectRisk(
            project_id=TEST_DATA_IDS['project_id'],
            created_by_id=TEST_DATA_IDS['user_id'],
            title='Test Risk',
            description='Test için oluşturuldu',
            impact=3,
            probability=2,
            mitigation_plan='Test azaltma planı',
            status='Aktif'
        )
        db.session.add(risk)
        db.session.commit()
        
        # DB'den riski kontrol et
        proje_riski = ProjectRisk.query.filter_by(
            project_id=TEST_DATA_IDS['project_id'],
            title='Test Risk'
        ).first()
        
        if not proje_riski:
            log("Risk veritabanında bulunamadı!", "ERROR")
            return False
        
        TEST_DATA_IDS['risk_id'] = proje_riski.id
        log(f"Risk oluşturuldu: ID={proje_riski.id}", "SUCCESS")
        return True
    
    return test_step("D. Proje Yönetimi - Risk Ekleme", _test)


def cleanup_test_data():
    """Test verilerini temizle - Güvenli Silme: Çocuktan Ebeveyne (Child -> Parent) sırasıyla"""
    log("Test verileri temizleniyor (Güvenli Silme)...", "INFO")
    
    try:
        # Önce rollback yap (varsa pending transaction)
        try:
            db.session.rollback()
        except:
            pass
        
        # ============================================================
        # 1. ADIM: PerformansGostergeVeri (Veri Girişleri) - EN ALT SEVİYE
        # ============================================================
        if TEST_DATA_IDS['user_id']:
            log("1. PerformansGostergeVeri kayıtları siliniyor...", "INFO")
            # Kullanıcıya ait tüm PG verilerini sil
            PerformansGostergeVeri.query.filter_by(user_id=TEST_DATA_IDS['user_id']).delete()
            # Ayrıca bireysel PG'lere bağlı verileri de sil
            if TEST_DATA_IDS['pg_id']:
                bireysel_pg_ids = [pg.id for pg in BireyselPerformansGostergesi.query.filter_by(
                    kaynak_surec_pg_id=TEST_DATA_IDS['pg_id']
                ).all()]
                if bireysel_pg_ids:
                    PerformansGostergeVeri.query.filter(
                        PerformansGostergeVeri.bireysel_pg_id.in_(bireysel_pg_ids)
                    ).delete()
        
        # ============================================================
        # 2. ADIM: BireyselPerformansGostergesi (Kullanıcının Hedefleri)
        # ============================================================
        if TEST_DATA_IDS['user_id']:
            log("2. BireyselPerformansGostergesi kayıtları siliniyor...", "INFO")
            BireyselPerformansGostergesi.query.filter_by(user_id=TEST_DATA_IDS['user_id']).delete()
        
        # Ayrıca test PG'sine bağlı bireysel PG'leri de sil
        if TEST_DATA_IDS['pg_id']:
            BireyselPerformansGostergesi.query.filter_by(
                kaynak_surec_pg_id=TEST_DATA_IDS['pg_id']
            ).delete()
        
        # ============================================================
        # 3. ADIM: BireyselFaaliyet (Kullanıcının Faaliyetleri)
        # ============================================================
        if TEST_DATA_IDS['user_id']:
            log("3. BireyselFaaliyet kayıtları siliniyor...", "INFO")
            BireyselFaaliyet.query.filter_by(user_id=TEST_DATA_IDS['user_id']).delete()
        
        # ============================================================
        # 4. ADIM: TaskSubtask (Alt Görevler)
        # ============================================================
        if TEST_DATA_IDS['subtask_id']:
            log("4. TaskSubtask kayıtları siliniyor...", "INFO")
            subtask = TaskSubtask.query.get(TEST_DATA_IDS['subtask_id'])
            if subtask:
                db.session.delete(subtask)
        
        # ============================================================
        # 5. ADIM: Task (Görevler)
        # ============================================================
        if TEST_DATA_IDS['task_id']:
            log("5. Task kayıtları siliniyor...", "INFO")
            task = Task.query.get(TEST_DATA_IDS['task_id'])
            if task:
                db.session.delete(task)
        
        # ============================================================
        # 6. ADIM: ProjectRisk (Proje Riskleri)
        # ============================================================
        if TEST_DATA_IDS['risk_id']:
            log("6. ProjectRisk kayıtları siliniyor...", "INFO")
            risk = ProjectRisk.query.get(TEST_DATA_IDS['risk_id'])
            if risk:
                db.session.delete(risk)
        
        # ============================================================
        # 7. ADIM: Project (Projeler) - İlişkileri önce temizle
        # ============================================================
        if TEST_DATA_IDS['project_id']:
            log("7. Project kayıtları siliniyor...", "INFO")
            project = Project.query.get(TEST_DATA_IDS['project_id'])
            if project:
                # İlişki tablolarını temizle
                project.related_processes.clear()
                project.members.clear()
                project.observers.clear()
                db.session.flush()
                db.session.delete(project)
        
        # İlişki tablosundaki mükerrer kayıtları temizle (güvenlik için)
        try:
            from sqlalchemy import text
            if TEST_DATA_IDS['project_id']:
                db.session.execute(
                    text("DELETE FROM project_related_processes WHERE project_id = :project_id"),
                    {"project_id": TEST_DATA_IDS['project_id']}
                )
        except Exception as cleanup_error:
            log(f"İlişki tablosu temizleme uyarısı: {str(cleanup_error)}", "INFO")
        
        # ============================================================
        # 8. ADIM: SurecPerformansGostergesi (Süreç PG'leri)
        # ============================================================
        if TEST_DATA_IDS['pg_id']:
            log("8. SurecPerformansGostergesi kayıtları siliniyor...", "INFO")
            surec_pg = SurecPerformansGostergesi.query.get(TEST_DATA_IDS['pg_id'])
            if surec_pg:
                db.session.delete(surec_pg)
        
        # ============================================================
        # 9. ADIM: Surec (Süreçler) - İlişkileri önce temizle
        # ============================================================
        if TEST_DATA_IDS['surec_id']:
            log("9. Surec kayıtları siliniyor...", "INFO")
            surec = Surec.query.get(TEST_DATA_IDS['surec_id'])
            if surec:
                # İlişkileri temizle
                surec.liderler.clear()
                surec.uyeler.clear()
                db.session.flush()
                db.session.delete(surec)
        
        # ============================================================
        # 10. ADIM: User (Kullanıcılar) - EN SON
        # ============================================================
        if TEST_DATA_IDS['user_id']:
            log("10. User kayıtları siliniyor...", "INFO")
            user = User.query.get(TEST_DATA_IDS['user_id'])
            if user:
                db.session.delete(user)
        
        # ============================================================
        # 11. ADIM: Kurum (Kurumlar) - EN SON
        # ============================================================
        if TEST_DATA_IDS['kurum_id']:
            log("11. Kurum kayıtları siliniyor...", "INFO")
            kurum = Kurum.query.get(TEST_DATA_IDS['kurum_id'])
            if kurum:
                db.session.delete(kurum)
        
        db.session.commit()
        log("Test verileri başarıyla temizlendi (Güvenli Silme tamamlandı)", "SUCCESS")
        
    except Exception as e:
        try:
            db.session.rollback()
        except:
            pass
        log(f"Temizlik hatası: {str(e)}", "ERROR")
        import traceback
        log(f"Traceback: {traceback.format_exc()}", "ERROR")
        
        # Hata durumunda da ilişki tablosunu temizlemeyi dene
        try:
            from sqlalchemy import text
            if TEST_DATA_IDS.get('project_id'):
                db.session.execute(
                    text("DELETE FROM project_related_processes WHERE project_id = :project_id"),
                    {"project_id": TEST_DATA_IDS['project_id']}
                )
                db.session.commit()
        except:
            pass


def print_summary():
    """Test özetini yazdır"""
    summary = f"""
--- TEST SONUCU ---
Toplam Adım: {TEST_RESULTS['total_steps']}
Başarılı: {TEST_RESULTS['successful']}
Hatalı: {TEST_RESULTS['failed']}
Başarı Oranı: {(TEST_RESULTS['successful'] / TEST_RESULTS['total_steps'] * 100) if TEST_RESULTS['total_steps'] > 0 else 0:.1f}%
"""
    
    print(summary)
    
    # Dosyaya da yaz
    try:
        with open('test_results.txt', 'a', encoding='utf-8') as f:
            f.write(summary + '\n')
            
            if TEST_RESULTS['errors']:
                f.write("\n--- HATA DETAYLARI ---\n")
                for error in TEST_RESULTS['errors']:
                    f.write(f"\nAdım: {error['step']}\n")
                    f.write(f"Hata: {error['error']}\n")
                    f.write(f"Traceback:\n{error['traceback']}\n")
    except Exception as e:
        print(f"Özet yazma hatası: {e}")


def main():
    """Ana test fonksiyonu"""
    reset_log_file()
    log("=== FULL SYSTEM TEST BAŞLATILIYOR ===", "INFO")
    
    # Uygulamayı oluştur
    app = create_app()
    
    with app.app_context():
        try:
            # Test ortamını hazırla
            client, admin_user = setup_test_environment(app)
            if not client or not admin_user:
                log("Test ortamı hazırlanamadı!", "ERROR")
                return
            
            # Test senaryosunu çalıştır
            test_kurum_ekle(client, admin_user)
            test_kullanici_ekle(client, admin_user)
            test_surec_ekle(client, admin_user)
            test_performans_gostergesi_ekle(client, admin_user)
            test_pg_veri_girisi(client, admin_user)
            test_proje_ekle(client, admin_user)
            test_gorev_ekle(client, admin_user)
            test_alt_gorev_ekle(client, admin_user)
            test_risk_ekle(client, admin_user)
            
        except Exception as e:
            log(f"Test sırasında beklenmeyen hata: {str(e)}", "ERROR")
            log(traceback.format_exc(), "ERROR")
        
        finally:
            # Temizlik
            cleanup_test_data()
            
            # Özet
            print_summary()
            
            log("=== TEST TAMAMLANDI ===", "INFO")


if __name__ == '__main__':
    main()

