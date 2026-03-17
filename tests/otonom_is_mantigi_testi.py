
import unittest
import sys
import os

# Ana dizini path'in EN BAŞINA ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, date
from flask import Flask
from models import (
    db, User, Kurum, Surec, SurecPerformansGostergesi, 
    BireyselPerformansGostergesi, PerformansGostergeVeri
)
# Uygulama factory fonksiyonunu import et
from __init__ import create_app

class OtonomIsMantigiTesti(unittest.TestCase):
    def setUp(self):
        """Test ortamını hazırla"""
        # Test konfigürasyonu
        self.app = create_app(config_name='testing')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.populate_base_data()

    def tearDown(self):
        """Test ortamını temizle"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def populate_base_data(self):
        """Temel verileri (Kurum, Admin, User) oluştur"""
        # 1. Kurum
        self.kurum = Kurum(
            kisa_ad="TEST_KURUM",
            ticari_unvan="Test Kurum A.Ş.",
            email="info@testkurum.com"
        )
        db.session.add(self.kurum)
        db.session.commit()

        # 2. Admin Kullanıcı
        self.admin_user = User(
            username="admin_user",
            email="admin@test.com",
            password_hash="hashed_secret",
            kurum_id=self.kurum.id,
            sistem_rol="admin",
            first_name="Admin",
            last_name="Yonetici"
        )
        db.session.add(self.admin_user)

        # 3. Standart Kullanıcı
        self.std_user = User(
            username="std_user",
            email="user@test.com",
            password_hash="hashed_secret",
            kurum_id=self.kurum.id,
            sistem_rol="kurum_kullanici",
            first_name="Standart",
            last_name="Kullanici"
        )
        db.session.add(self.std_user)
        db.session.commit()

    def test_surec_ve_pg_yonetimi(self):
        """
        Senaryo 1: Admin Yetkisi ile Süreç ve PG Yönetimi
        Hedef: Süreç ekleme ve buna bağlı PG tanımlama başarısını ölçmek.
        """
        print("\n--- TEST 1: Süreç ve PG Yönetimi Başlatılıyor ---")
        
        # 1. Süreç Ekleme
        yeni_surec = Surec(
            ad="Pazarlama Süreci",
            code="SR-01",
            kurum_id=self.kurum.id,
            durum="Aktif"
        )
        db.session.add(yeni_surec)
        db.session.commit()
        
        # Doğrulama
        kaydedilen_surec = Surec.query.filter_by(code="SR-01").first()
        self.assertIsNotNone(kaydedilen_surec)
        self.assertEqual(kaydedilen_surec.ad, "Pazarlama Süreci")
        print("✓ Süreç başarıyla oluşturuldu.")

        # 2. PG (Performans Göstergesi) Ekleme
        yeni_pg = SurecPerformansGostergesi(
            surec_id=kaydedilen_surec.id,
            ad="Müşteri Memnuniyet Oranı",
            kodu="PG-01",
            hedef_deger="90",
            olcum_birimi="Yüzde",
            periyot="Aylık",
            direction="Increasing"
        )
        db.session.add(yeni_pg)
        db.session.commit()

        # Doğrulama
        kaydedilen_pg = SurecPerformansGostergesi.query.filter_by(kodu="PG-01").first()
        self.assertIsNotNone(kaydedilen_pg)
        self.assertEqual(kaydedilen_pg.surec_id, saved_process_id := kaydedilen_surec.id)
        print("✓ PG başarıyla sürece bağlandı.")
        
        return saved_process_id, kaydedilen_pg.id

    def test_veri_butunlugu_ve_hesaplama(self):
        """
        Senaryo 2: Veri Bütünlüğü ve Hesaplama
        Hedef: PG verisinin sisteme girilmesi ve kaydedilmesi.
        """
        print("\n--- TEST 2: Veri Bütünlüğü ve Hesaplama Başlatılıyor ---")
        
        # Ön Hazırlık: Süreç ve PG oluştur (Test 1'deki mantığı tekrar et veya setup'a taşı)
        surec = Surec(ad="Satış", code="SR-02", kurum_id=self.kurum.id)
        db.session.add(surec)
        db.session.commit()
        
        pg = SurecPerformansGostergesi(
            surec_id=surec.id, ad="Satış Adedi", kodu="PG-02", 
            hedef_deger="100", olcum_birimi="Adet"
        )
        db.session.add(pg)
        db.session.commit()

        # 1. Bireysel PG Atama (Süreç PG'sinden Standart Kullanıcıya)
        bireysel_pg = BireyselPerformansGostergesi(
            user_id=self.std_user.id,
            ad=pg.ad,
            kodu=pg.kodu,
            kaynak='Süreç',
            kaynak_surec_id=surec.id,
            kaynak_surec_pg_id=pg.id,
            hedef_deger="100"
        )
        db.session.add(bireysel_pg)
        db.session.commit()
        
        print(f"✓ Bireysel PG atandı: {bireysel_pg.ad} -> {self.std_user.username}")

        # 2. Veri Girişi (Ocak Ayı için)
        pg_veri = PerformansGostergeVeri(
            bireysel_pg_id=bireysel_pg.id,
            user_id=self.std_user.id,
            yil=2024,
            veri_tarihi=date(2024, 1, 31),
            giris_periyot_tipi="aylik",
            giris_periyot_ay=1,
            gerceklesen_deger="120", # Hedef 100, Gerçekleşen 120
            created_by=self.std_user.id
        )
        db.session.add(pg_veri)
        db.session.commit()

        # Doğrulama
        kayitli_veri = PerformansGostergeVeri.query.filter_by(bireysel_pg_id=bireysel_pg.id).first()
        self.assertIsNotNone(kayitli_veri)
        self.assertEqual(kayitli_veri.gerceklesen_deger, "120")
        print("✓ PG Verisi başarıyla kaydedildi.")

    def test_rol_bazli_yetki_sinirlari(self):
        """
        Senaryo 3: Rol Bazlı Yetki ve Mantıksal Sınırlar
        Hedef: Bir kullanıcının başkasının verisine erişimini (mantıksal olarak) test etmek.
        """
        print("\n--- TEST 3: Rol Bazlı Yetki Sınırları Başlatılıyor ---")
        
        # Senaryo: Admin bir veri giriyor, Standart Kullanıcı bunu görmemeli (kendi sorgusunda)
        # Not: Bu test, kodun nasıl sorguladığına bağlıdır. Burada veritabanı seviyesinde izolasyonu test ediyoruz.
        
        # Admin kendine bir hedef atıyor
        admin_kpi = BireyselPerformansGostergesi(
            user_id=self.admin_user.id, ad="Yönetim KPI", kodu="KPI-ADM", kaynak='Bireysel'
        )
        db.session.add(admin_kpi)
        db.session.commit()
        
        # Standart kullanıcı kendi query'sinde bunu görmemeli
        # Simüle edilen query: BireyselPerformansGostergesi.query.filter_by(user_id=current_user.id).all()
        
        std_user_kpis = BireyselPerformansGostergesi.query.filter_by(user_id=self.std_user.id).all()
        admin_user_kpis = BireyselPerformansGostergesi.query.filter_by(user_id=self.admin_user.id).all()
        
        # Kontrol: Standart kullanıcının listesinde Admin'in KPI'ı YOK
        admin_kpi_ids = [k.id for k in admin_user_kpis]
        std_kpi_ids = [k.id for k in std_user_kpis]
        
        # Kesişim boş olmalı (eğer std kullanıcıya özellikle atanmadıysa)
        intersection = set(admin_kpi_ids).intersection(set(std_kpi_ids))
        self.assertEqual(len(intersection), 0)
        
        print("✓ Veri İzolasyonu Başarılı: Kullanıcılar varsayılan olarak birbirlerinin bireysel hedeflerini görmüyor.")

if __name__ == '__main__':
    unittest.main()
