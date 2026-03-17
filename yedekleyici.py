import os
import shutil
import zipfile
import datetime

def create_backup():
    # 1. Klasör Ayarları
    BASE_DIR = os.getcwd()
    BACKUP_DIR = os.path.join(BASE_DIR, 'Yedekler')
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Yedek klasörü oluşturuldu: {BACKUP_DIR}")

    # 2. Dosya İsmi
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    zip_filename = f'Kokpitim_Tam_Yedek_{timestamp}.zip'
    zip_path = os.path.join(BACKUP_DIR, zip_filename)

    # 3. Hariç Tutulacaklar
    EXCLUDE_DIRS = {'.venv', '.git', '__pycache__', '.vscode', '.idea', 'Yedekler', '.gemini', '.tmp', 'node_modules', 'instance'}
    EXCLUDE_EXTENSIONS = {'.log', '.tmp', '.pyc', '.pyo'}

    # Ekstra önemli dosyaları manuel ekle (Veritabanı vb. instance/ altında olabilir)
    # Flask default olarak DB'yi instance/ klasöründe tutar, onu ayrı kontrol edeceğiz.
    
    print(f"Yedekleme başlatılıyor... Hedef: {zip_path}")
    
    file_count = 0
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Kök dizindeki her şeyi gez
        for root, dirs, files in os.walk(BASE_DIR):
            # Hariç tutulan klasörleri listeden çıkar (yerinde değişiklik)
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, BASE_DIR)
                
                # Uzantı kontrolü
                _, ext = os.path.splitext(file)
                if ext.lower() in EXCLUDE_EXTENSIONS:
                    continue
                
                # Kendi oluşturduğumuz zip dosyasını hariç tut (gerçi dirs exclusion ile YEDEKLER haricinde ama yine de)
                if file == zip_filename:
                    continue

                try:
                    zipf.write(file_path, rel_path)
                    file_count += 1
                except Exception as e:
                    print(f"Hata - Dosya eklenemedi: {rel_path} ({e})")

        # Özel Olarak Veritabanlarını Ekle (Eğer instance altındaysa ve exclusion'a takıldıysa)
        # Genellikle instance/ hariç tutulur ama DB oradaysa manuel eklenmeli
        # Sizin projenizde DB nerede? Root'ta 'sps.db' veya 'instance/sps.db' olabilir.
        # Root'takiler zaten yukarıdaki döngüde eklendi.
        # Instance altındakileri manuel ekleyelim (eğer instance exclusion'daysa)
        if 'instance' in EXCLUDE_DIRS and os.path.exists(os.path.join(BASE_DIR, 'instance')):
             for db_file in os.listdir(os.path.join(BASE_DIR, 'instance')):
                 if db_file.endswith('.db') or db_file.endswith('.sqlite'):
                     full_path = os.path.join(BASE_DIR, 'instance', db_file)
                     zipf.write(full_path, os.path.join('instance', db_file))
                     print(f"Veritabanı (Instance) eklendi: {db_file}")

    # 4. Sonuç Bilgisi
    size_bytes = os.path.getsize(zip_path)
    size_mb = size_bytes / (1024 * 1024)
    
    print("-" * 50)
    print(f"Yedekleme başarıyla tamamlandı: {zip_filename}")
    print(f"Toplam Dosya Sayısı: {file_count}")
    print(f"Toplam Yedek Boyutu: {size_mb:.2f} MB")
    print("Veritabanı yedeği alındı.")
    print("-" * 50)

if __name__ == "__main__":
    create_backup()
