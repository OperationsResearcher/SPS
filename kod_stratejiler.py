# -*- coding: utf-8 -*-
"""
Ana ve Alt Stratejilere Kod Atama Scripti
Ana stratejilere: S1, S2, S3...
Alt stratejilere: S1.1, S1.2, S2.1...
"""
import sys
import io

# Windows console için UTF-8 encoding ayarla
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from app import create_app
from extensions import db
from models import AnaStrateji, AltStrateji, Kurum

app = create_app()

def kodlari_ata(kurum_id=None):
    """
    Ana ve alt stratejilere kod atar
    
    Args:
        kurum_id: Belirli bir kurum için kodlama yapmak için (None ise tüm kurumlar)
    """
    with app.app_context():
        try:
            # Kurum filtresi
            if kurum_id:
                kurumlar = [Kurum.query.get(kurum_id)]
                if not kurumlar[0]:
                    print(f"Hata: Kurum ID {kurum_id} bulunamadı!")
                    return
            else:
                kurumlar = Kurum.query.all()
            
            toplam_ana = 0
            toplam_alt = 0
            
            for kurum in kurumlar:
                print(f"\n{'='*60}")
                print(f"Kurum: {kurum.kisa_ad} (ID: {kurum.id})")
                print(f"{'='*60}")
                
                # Ana stratejileri getir (sıralı - id'ye göre)
                ana_stratejiler = AnaStrateji.query.filter_by(kurum_id=kurum.id).order_by(AnaStrateji.id).all()
                
                if not ana_stratejiler:
                    print(f"  Bu kurumda ana strateji bulunamadı.")
                    continue
                
                print(f"  Bulunan ana strateji sayısı: {len(ana_stratejiler)}")
                
                # Ana stratejilere kod ata
                # Önce tüm kodları geçici olarak temizle (unique constraint için)
                for ana_strateji in ana_stratejiler:
                    if ana_strateji.code:
                        ana_strateji.code = None
                db.session.flush()  # Değişiklikleri flush et
                
                # Şimdi yeni kodları ata
                for index, ana_strateji in enumerate(ana_stratejiler, start=1):
                    kod = f"S{index}"
                    ana_strateji.code = kod
                    print(f"  [OK] Ana Strateji: {ana_strateji.ad[:50]:<50} | Kod: -> {kod}")
                    toplam_ana += 1
                    
                    # Bu ana stratejinin alt stratejilerini getir (sıralı - id'ye göre)
                    alt_stratejiler = AltStrateji.query.filter_by(ana_strateji_id=ana_strateji.id).order_by(AltStrateji.id).all()
                    
                    if alt_stratejiler:
                        # Alt stratejilere kod ata
                        for alt_index, alt_strateji in enumerate(alt_stratejiler, start=1):
                            alt_kod = f"{kod}.{alt_index}"
                            eski_alt_kod = alt_strateji.code or "(kod yok)"
                            alt_strateji.code = alt_kod
                            print(f"    [OK] Alt Strateji: {alt_strateji.ad[:45]:<45} | Kod: {eski_alt_kod:>10} -> {alt_kod}")
                            toplam_alt += 1
                
                # Değişiklikleri kaydet
                db.session.commit()
                print(f"\n  [OK] Kurum '{kurum.kisa_ad}' için kodlar basariyla atandi ve kaydedildi!")
            
            print(f"\n{'='*60}")
            print(f"ÖZET:")
            print(f"  Toplam Ana Strateji: {toplam_ana}")
            print(f"  Toplam Alt Strateji: {toplam_alt}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[HATA] Hata olustu: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    import sys
    
    # Komut satırı argümanı varsa (kurum_id)
    if len(sys.argv) > 1:
        try:
            kurum_id = int(sys.argv[1])
            print(f"Belirtilen kurum (ID: {kurum_id}) için kodlama yapılıyor...\n")
            kodlari_ata(kurum_id=kurum_id)
        except ValueError:
            print("Hata: Kurum ID bir sayı olmalıdır!")
            print("Kullanım: python kod_stratejiler.py [kurum_id]")
    else:
        print("Tüm kurumlar için kodlama yapılıyor...\n")
        kodlari_ata()

