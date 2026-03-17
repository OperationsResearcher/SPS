# -*- coding: utf-8 -*-
"""
Stratejik Planlama Veri Aktarım Scripti (V3.1.0)
Excel/CSV dosyalarındaki kurumsal verileri veritabanına aktarır.

KURULUM:
    pip install pandas openpyxl

KULLANIM:
    python import_strategic_data.py [--reset]
    
    --reset: Mevcut verileri temizler (isteğe bağlı)
"""

import sys
import argparse
from datetime import datetime
import pandas as pd
import json
import os

# Windows konsol encoding sorununu çöz
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Flask app context için
from __init__ import create_app
from extensions import db
from models import (
    CorporateIdentity, AnaStrateji, AltStrateji, Surec, User,
    strategy_process_matrix, process_owners
)

# Excel dosya yolu
EXCEL_FILE = 'SP VE SÜREÇ YAPISI.xlsx'


def reset_data():
    """Mevcut stratejik planlama verilerini temizle"""
    print("🧹 Mevcut veriler temizleniyor...")
    
    try:
        # Association table'ları temizle
        db.session.execute(strategy_process_matrix.delete())
        db.session.execute(process_owners.delete())
        
        # Ana tabloları temizle
        AltStrateji.query.delete()
        AnaStrateji.query.delete()
        Surec.query.delete()
        CorporateIdentity.query.delete()
        
        db.session.commit()
        print("[OK] Temizlik tamamlandi")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"[HATA] Temizlik hatasi: {e}")
        return False


def import_corporate_identity(df, kurum_id):
    """Kurumsal Kimlik verilerini import et"""
    print("\n[KURUMSAL KIMLIK] Import ediliyor...")
    
    try:
        # Excel'den veri çek (Misyon Vizyon SWOT sayfası veya ilgili sayfa)
        # Örnek: Vizyon, Misyon, Değerler sütunlarını al
        vizyon = None
        misyon = None
        degerler = None
        kalite_politikasi = None
        
        # Excel yapısına göre sütun isimlerini ayarla
        if 'Vizyon' in df.columns:
            vizyon = df['Vizyon'].iloc[0] if not df['Vizyon'].isna().iloc[0] else None
        if 'Misyon' in df.columns:
            misyon = df['Misyon'].iloc[0] if not df['Misyon'].isna().iloc[0] else None
        if 'Değerler' in df.columns:
            degerler_str = df['Değerler'].iloc[0] if not df['Değerler'].isna().iloc[0] else None
            if degerler_str:
                # Eğer string ise JSON'a çevir
                try:
                    degerler = json.dumps(degerler_str.split(',') if isinstance(degerler_str, str) else degerler_str)
                except:
                    degerler = json.dumps([degerler_str])
        if 'Kalite Politikası' in df.columns:
            kalite_politikasi = df['Kalite Politikası'].iloc[0] if not df['Kalite Politikası'].isna().iloc[0] else None
        
        # Mevcut kaydı kontrol et
        existing = CorporateIdentity.query.filter_by(kurum_id=kurum_id).first()
        if existing:
            existing.vizyon = vizyon
            existing.misyon = misyon
            existing.degerler = degerler
            existing.kalite_politikasi = kalite_politikasi
            existing.updated_at = datetime.utcnow()
            print(f"  [OK] Kurumsal kimlik guncellendi (Kurum ID: {kurum_id})")
        else:
            new_identity = CorporateIdentity(
                kurum_id=kurum_id,
                vizyon=vizyon,
                misyon=misyon,
                degerler=degerler,
                kalite_politikasi=kalite_politikasi
            )
            db.session.add(new_identity)
            print(f"  [OK] Kurumsal kimlik olusturuldu (Kurum ID: {kurum_id})")
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"  [HATA] Kurumsal kimlik import hatasi: {e}")
        return False


def import_strategies(df, kurum_id):
    """Stratejileri import et (Main ve Sub)"""
    print("\n[STRATEJILER] Import ediliyor...")
    print(f"  [DEBUG] Sutunlar: {list(df.columns)}")
    print(f"  [DEBUG] Ilk 10 satir:")
    print(df.head(10))
    
    main_count = 0
    sub_count = 0
    
    try:
        # Excel başlık satırını bul (Unnamed sütunları varsa başlık farklı satırda olabilir)
        header_row = 0
        for idx in range(min(5, len(df))):
            row_values = df.iloc[idx].astype(str).tolist()
            if any('kod' in str(v).lower() or 'code' in str(v).lower() for v in row_values):
                header_row = idx
                # Başlık satırını sütun olarak ayarla
                df.columns = df.iloc[header_row]
                df = df.iloc[header_row+1:].reset_index(drop=True)
                print(f"  [DEBUG] Baslik satiri bulundu: {header_row}")
                print(f"  [DEBUG] Yeni sutunlar: {list(df.columns)}")
                break
        
        # Excel'den strateji kodlarını al
        code_col = None
        name_col = None
        target_method_col = None
        
        # Sütun isimlerini bul
        for col in df.columns:
            col_str = str(col).lower()
            if 'kod' in col_str or 'code' in col_str:
                code_col = col
            if 'ad' in col_str or 'name' in col_str or 'tanım' in col_str or 'tanim' in col_str or 'strateji' in col_str:
                name_col = col
            if 'hedef' in col_str or 'target' in col_str or 'yöntem' in col_str or 'yontem' in col_str:
                target_method_col = col
        
        if not code_col:
            print("  [UYARI] Kod sutunu bulunamadi, mevcut sutunlar:")
            for col in df.columns:
                print(f"    - {col}")
            return False
        
        # Ana stratejileri ve alt stratejileri ayır
        main_strategies = {}  # {code: AnaStrateji}
        
        for idx, row in df.iterrows():
            code = str(row[code_col]).strip() if pd.notna(row[code_col]) else None
            if not code or code == 'nan':
                continue
            
            name = row[name_col] if name_col and pd.notna(row.get(name_col, None)) else None
            target_method = row[target_method_col] if target_method_col and pd.notna(row.get(target_method_col, None)) else None
            
            # ST1, ST2 formatı -> Ana Strateji
            if code.startswith('ST') and '.' not in code:
                # Ana strateji
                existing = AnaStrateji.query.filter_by(code=code, kurum_id=kurum_id).first()
                if existing:
                    existing.name = name
                    existing.ad = name or code
                    existing.updated_at = datetime.utcnow()
                else:
                    existing = AnaStrateji(
                        kurum_id=kurum_id,
                        code=code,
                        ad=name or code,
                        name=name
                    )
                    db.session.add(existing)
                    db.session.flush()
                
                main_strategies[code] = existing
                main_count += 1
                print(f"  [OK] Ana Strateji: {code} - {name or code}")
            
            # ST1.1, ST1.2 formatı -> Alt Strateji
            elif code.startswith('ST') and '.' in code:
                # Alt strateji
                parent_code = code.split('.')[0]  # ST1
                parent = main_strategies.get(parent_code)
                
                if not parent:
                    # Ana stratejiyi bul
                    parent = AnaStrateji.query.filter_by(code=parent_code, kurum_id=kurum_id).first()
                    if not parent:
                        print(f"  [UYARI] Ana strateji bulunamadi: {parent_code}, atlaniyor...")
                        continue
                
                existing = AltStrateji.query.filter_by(code=code, ana_strateji_id=parent.id).first()
                if existing:
                    existing.name = name
                    existing.ad = name or code
                    existing.target_method = target_method
                    existing.updated_at = datetime.utcnow()
                else:
                    existing = AltStrateji(
                        ana_strateji_id=parent.id,
                        code=code,
                        ad=name or code,
                        name=name,
                        target_method=target_method
                    )
                    db.session.add(existing)
                
                sub_count += 1
                print(f"  [OK] Alt Strateji: {code} - {name or code} (Hedef: {target_method or 'Belirtilmemis'})")
        
        db.session.commit()
        print(f"\n  [OZET] {main_count} Ana Strateji, {sub_count} Alt Strateji")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"  [HATA] Strateji import hatasi: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_processes(df, kurum_id):
    """Süreçleri import et (Sahiplik ile)"""
    print("\n[SURECLER] Import ediliyor...")
    
    process_count = 0
    owner_count = 0
    
    try:
        # Excel başlık satırını bul (Unnamed sütunları varsa başlık farklı satırda olabilir)
        header_row = None
        for idx in range(min(10, len(df))):
            row_values = df.iloc[idx].astype(str).tolist()
            # "Kod", "Süreç Kodu", "SR1" gibi değerler içeren satırı bul
            if any('kod' in str(v).lower() or 'code' in str(v).lower() or str(v).strip().startswith('SR') for v in row_values if pd.notna(v) and str(v) != 'nan'):
                header_row = idx
                # Başlık satırını sütun olarak ayarla
                new_columns = [str(v).strip() if pd.notna(v) and str(v) != 'nan' else f'Unnamed_{i}' for i, v in enumerate(df.iloc[idx])]
                df.columns = new_columns
                df = df.iloc[header_row+1:].reset_index(drop=True)
                print(f"  [DEBUG] Baslik satiri bulundu: {header_row}")
                print(f"  [DEBUG] Yeni sutunlar: {list(df.columns)}")
                break
        
        if header_row is None:
            print("  [UYARI] Baslik satiri bulunamadi, mevcut sutunlar:")
            for col in df.columns:
                print(f"    - {col}")
            print("  [DEBUG] Ilk 10 satir:")
            print(df.head(10))
            return False
        
        # Excel'den süreç kodlarını al
        code_col = None
        name_col = None
        weight_col = None
        owner_col = None
        
        # Sütun isimlerini bul
        for col in df.columns:
            col_str = str(col).lower()
            if 'kod' in col_str or 'code' in col_str:
                code_col = col
            if 'ad' in col_str or 'name' in col_str or 'süreç' in col_str or 'surec' in col_str:
                name_col = col
            if 'ağırlık' in col_str or 'agirlik' in col_str or 'weight' in col_str or 'puan' in col_str:
                weight_col = col
            if 'sahip' in col_str or 'owner' in col_str or 'sorumlu' in col_str:
                owner_col = col
        
        if not code_col:
            print("  [UYARI] Kod sutunu bulunamadi, mevcut sutunlar:")
            for col in df.columns:
                print(f"    - {col}")
            return False
        
        for idx, row in df.iterrows():
            code = str(row[code_col]).strip() if pd.notna(row[code_col]) else None
            if not code or code == 'nan' or not code.startswith('SR'):
                continue
            
            name = row[name_col] if name_col and pd.notna(row.get(name_col, None)) else None
            weight = None
            if weight_col and pd.notna(row.get(weight_col, None)):
                try:
                    weight = float(row[weight_col])
                except:
                    weight = 0.0
            
            owner_name = row[owner_col] if owner_col and pd.notna(row.get(owner_col, None)) else None
            
            # Süreç oluştur/güncelle
            existing = Surec.query.filter_by(code=code, kurum_id=kurum_id).first()
            if existing:
                existing.name = name
                existing.ad = name or code
                existing.weight = weight or 0.0
                existing.updated_at = datetime.utcnow()
                process = existing
            else:
                process = Surec(
                    kurum_id=kurum_id,
                    code=code,
                    ad=name or code,
                    name=name,
                    weight=weight or 0.0
                )
                db.session.add(process)
                db.session.flush()
            
            process_count += 1
            print(f"  [OK] Surec: {code} - {name or code} (Agirlik: {weight or 0.0})")
            
            # Sahiplik atama
            if owner_name:
                # Kullanıcıyı bul (isim veya username ile)
                owner_name_clean = str(owner_name).strip()
                
                # İsim formatını parse et (Örn: "Duygu LAZOĞLU" -> first_name="Duygu", last_name="LAZOĞLU")
                name_parts = owner_name_clean.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                    
                    # Kullanıcıyı bul
                    user = User.query.filter_by(
                        first_name=first_name,
                        last_name=last_name,
                        kurum_id=kurum_id
                    ).first()
                    
                    if not user:
                        # Username ile dene
                        username_lower = owner_name_clean.lower().replace(' ', '')
                        user = User.query.filter_by(username=username_lower, kurum_id=kurum_id).first()
                    
                    if user:
                        # Mevcut sahiplik kontrolü
                        from sqlalchemy import select
                        existing_owner = db.session.execute(
                            select(process_owners).where(
                                process_owners.c.process_id == process.id,
                                process_owners.c.user_id == user.id
                            )
                        ).first()
                        
                        if not existing_owner:
                            db.session.execute(
                                process_owners.insert().values(
                                    process_id=process.id,
                                    user_id=user.id
                                )
                            )
                            owner_count += 1
                            print(f"    [SAHIP] Sahip atandi: {owner_name_clean}")
                        else:
                            print(f"    [INFO] Sahip zaten mevcut: {owner_name_clean}")
                    else:
                        print(f"    [UYARI] Kullanici bulunamadi: {owner_name_clean}")
        
        db.session.commit()
        print(f"\n  [OZET] {process_count} Surec, {owner_count} Sahiplik Atamasi")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"  [HATA] Surec import hatasi: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_matrix(df):
    """Strateji-Süreç Matrisini import et"""
    print("\n[MATRIS] Strateji-Surec Matrisi import ediliyor...")
    
    matrix_count = 0
    
    try:
        # Excel'deki matris yapısını oku
        # İlk satır: Süreç kodları (SR1, SR2, ...)
        # İlk sütun: Strateji kodları (ST1.1, ST1.2, ...)
        # Kesişim hücreleri: A, B veya boş
        
        # İlk satırı süreç kodları olarak al
        process_codes = []
        for col_idx, col_name in enumerate(df.columns[1:], start=1):  # İlk sütunu atla (strateji kodları için)
            code = str(col_name).strip() if pd.notna(col_name) else None
            if code and (code.startswith('SR') or 'süreç' in code.lower()):
                process_codes.append((col_idx, code))
        
        # İlk sütunu strateji kodları olarak al
        strategy_col = df.columns[0]
        
        for idx, row in df.iterrows():
            strategy_code = str(row[strategy_col]).strip() if pd.notna(row[strategy_col]) else None
            if not strategy_code or not strategy_code.startswith('ST'):
                continue
            
            # Alt stratejiyi bul
            alt_strategy = AltStrateji.query.filter_by(code=strategy_code).first()
            if not alt_strategy:
                print(f"  [UYARI] Alt strateji bulunamadi: {strategy_code}, atlaniyor...")
                continue
            
            # Her süreç için matris değerini kontrol et
            for col_idx, process_code in process_codes:
                cell_value = row.iloc[col_idx] if col_idx < len(row) else None
                
                if pd.isna(cell_value) or str(cell_value).strip() == '':
                    continue
                
                cell_value = str(cell_value).strip().upper()
                
                # Süreç kodunu bul
                process = Surec.query.filter_by(code=process_code).first()
                if not process:
                    print(f"  [UYARI] Surec bulunamadi: {process_code}, atlaniyor...")
                    continue
                
                # Puan hesapla
                score = 0
                if cell_value == 'A':
                    score = 9
                elif cell_value == 'B':
                    score = 3
                else:
                    # Sayısal değer olabilir
                    try:
                        score = int(cell_value)
                    except:
                        continue
                
                # Mevcut ilişkiyi kontrol et
                from sqlalchemy import select
                existing = db.session.execute(
                    select(strategy_process_matrix).where(
                        strategy_process_matrix.c.sub_strategy_id == alt_strategy.id,
                        strategy_process_matrix.c.process_id == process.id
                    )
                ).first()
                
                if existing:
                    # Güncelle
                    db.session.execute(
                        strategy_process_matrix.update().where(
                            strategy_process_matrix.c.sub_strategy_id == alt_strategy.id,
                            strategy_process_matrix.c.process_id == process.id
                        ).values(
                            relationship_strength=score,
                            relationship_score=score
                        )
                    )
                else:
                    # Yeni ekle
                    db.session.execute(
                        strategy_process_matrix.insert().values(
                            sub_strategy_id=alt_strategy.id,
                            process_id=process.id,
                            relationship_strength=score,
                            relationship_score=score
                        )
                    )
                
                matrix_count += 1
                print(f"  [OK] Matris: {strategy_code} <-> {process_code} = {score} ({'A' if score == 9 else 'B' if score == 3 else 'Sayisal'})")
        
        db.session.commit()
        print(f"\n  [OZET] {matrix_count} Matris Baglantisi")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"  [HATA] Matris import hatasi: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ana import fonksiyonu"""
    parser = argparse.ArgumentParser(description='Stratejik Planlama Veri Aktarım Scripti')
    parser.add_argument('--reset', action='store_true', help='Mevcut verileri temizle')
    parser.add_argument('--excel', default=EXCEL_FILE, help='Excel dosya yolu')
    parser.add_argument('--kurum-id', type=int, default=1, help='Kurum ID (varsayılan: 1)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("STRATEJİK PLANLAMA VERİ AKTARIMI (V3.1.0)")
    print("=" * 60)
    print(f"Excel Dosyası: {args.excel}")
    print(f"Kurum ID: {args.kurum_id}")
    print("=" * 60)
    
    # Flask app oluştur
    app = create_app()
    
    with app.app_context():
        # Temizlik (isteğe bağlı)
        if args.reset:
            if not reset_data():
                print("[HATA] Temizlik basarisiz, islem durduruldu")
                return
        
        # Excel dosyasını oku
        try:
            excel_file = pd.ExcelFile(args.excel)
            print(f"\n[EXCEL] Excel sayfalari: {excel_file.sheet_names}")
        except Exception as e:
            print(f"[HATA] Excel dosyasi okunamadi: {e}")
            return
        
        # Sayfa isimlerini bul (öncelik sırasına göre)
        sheet_mapping = {}
        for sheet in excel_file.sheet_names:
            sheet_lower = sheet.lower()
            # Matris sayfasını önce kontrol et (çünkü "SP - Süreç Matrisi" hem matris hem süreç içeriyor)
            if ('matris' in sheet_lower or 'matrix' in sheet_lower) and 'matrix' not in sheet_mapping:
                sheet_mapping['matrix'] = sheet
            elif ('misyon' in sheet_lower or 'vizyon' in sheet_lower or 'swot' in sheet_lower) and 'corporate_identity' not in sheet_mapping:
                sheet_mapping['corporate_identity'] = sheet
            elif 'strateji' in sheet_lower and 'strategies' not in sheet_mapping:
                sheet_mapping['strategies'] = sheet
            elif ('süreç' in sheet_lower or 'process' in sheet_lower) and 'processes' not in sheet_mapping and 'matris' not in sheet_lower:
                # Matris içermeyen süreç sayfası
                sheet_mapping['processes'] = sheet
        
        print(f"\n[SAYFA ESLESTIRME]")
        for key, sheet in sheet_mapping.items():
            print(f"  {key}: {sheet}")
        
        # Import işlemleri
        results = {
            'corporate_identity': False,
            'strategies': False,
            'processes': False,
            'matrix': False
        }
        
        # 1. Kurumsal Kimlik
        if 'corporate_identity' in sheet_mapping:
            df_ci = pd.read_excel(args.excel, sheet_name=sheet_mapping['corporate_identity'])
            results['corporate_identity'] = import_corporate_identity(df_ci, args.kurum_id)
        else:
            print("\n[UYARI] Kurumsal Kimlik sayfasi bulunamadi, atlaniyor...")
        
        # 2. Stratejiler
        if 'strategies' in sheet_mapping:
            df_strategies = pd.read_excel(args.excel, sheet_name=sheet_mapping['strategies'])
            results['strategies'] = import_strategies(df_strategies, args.kurum_id)
        else:
            print("\n[UYARI] Stratejiler sayfasi bulunamadi, atlaniyor...")
        
        # 3. Süreçler
        if 'processes' in sheet_mapping:
            df_processes = pd.read_excel(args.excel, sheet_name=sheet_mapping['processes'])
            results['processes'] = import_processes(df_processes, args.kurum_id)
        else:
            print("\n[UYARI] Surecler sayfasi bulunamadi, atlaniyor...")
        
        # 4. Matris
        if 'matrix' in sheet_mapping:
            df_matrix = pd.read_excel(args.excel, sheet_name=sheet_mapping['matrix'])
            results['matrix'] = import_matrix(df_matrix)
        else:
            print("\n[UYARI] Matris sayfasi bulunamadi, atlaniyor...")
        
        # Sonuç özeti
        print("\n" + "=" * 60)
        print("[IMPORT SONUC OZETI]")
        print("=" * 60)
        
        # Sayıları al (migration kontrolü ile)
        try:
            strategy_count = AnaStrateji.query.filter_by(kurum_id=args.kurum_id).count()
        except Exception as e:
            print(f"[UYARI] Ana strateji sayisi alinamadi (migration gerekli olabilir): {e}")
            strategy_count = 0
        
        try:
            sub_strategy_count = db.session.query(AltStrateji).join(AnaStrateji).filter(AnaStrateji.kurum_id == args.kurum_id).count()
        except Exception as e:
            print(f"[UYARI] Alt strateji sayisi alinamadi: {e}")
            sub_strategy_count = 0
        
        try:
            process_count = Surec.query.filter_by(kurum_id=args.kurum_id).count()
        except Exception as e:
            print(f"[UYARI] Surec sayisi alinamadi: {e}")
            process_count = 0
        
        try:
            from sqlalchemy import select, func
            matrix_count = db.session.execute(select(func.count()).select_from(strategy_process_matrix)).scalar()
        except Exception as e:
            print(f"[UYARI] Matris sayisi alinamadi: {e}")
            matrix_count = 0
        
        print(f"[OK] Basariyla Aktarilan:")
        print(f"  - {strategy_count} Ana Strateji")
        print(f"  - {sub_strategy_count} Alt Strateji")
        print(f"  - {process_count} Surec")
        print(f"  - {matrix_count} Matris Baglantisi")
        
        if strategy_count == 0 and sub_strategy_count == 0 and process_count == 0:
            print("\n[UYARI] Veritabani migration gerekli olabilir!")
            print("  /debug/init_strategy_v3 route'unu calistirin veya ALTER TABLE komutlarini uygulayin.")
            print("  Gerekli kolonlar: ana_strateji.code, alt_strateji.code, surec.code, vb.")
        
        print("\n" + "=" * 60)
        print("[OK] IMPORT TAMAMLANDI!")
        print("=" * 60)


if __name__ == '__main__':
    main()

