# -*- coding: utf-8 -*-
"""
KalDer Kurulum ve BSC Stratejik Plan Veri Import Scripti

Tenant: KalDer (Kurum), User: KalDerAdmin (Şifre: Kalder123!)
Veriler: StrategicGoal -> AnaStrateji/AltStrateji, KPI -> SurecPerformansGostergesi/BireyselPerformansGostergesi,
         ActualValue -> PerformansGostergeVeri. Tüm kayıtlar KalDer kurum_id ile ilişkilendirilir.

Yapılanlar:
  1. "KalDer" kurumu oluşturulur (yoksa); varsa mevcut ID kullanılır.
  2. KalDerAdmin kullanıcısı oluşturulur (şifre: Kalder123!).
  3. temp_data içindeki CSV/Excel dosyalarından (BSC_Paydas, BSC_Finansal vb.):
     - Stratejik Hedef -> AnaStrateji/AltStrateji (StrategicGoal)
     - Gösterge Adı, Birim -> KPI tabloları
     - Aylık Hedef/Gerçekleşen -> PerformansGostergeVeri (ActualValue), uygun yıl/ay ile

Kullanım (yerel):
  python scripts/setup_kalder_and_import_bsc.py
  python scripts/setup_kalder_and_import_bsc.py --data-dir temp_data
  python scripts/setup_kalder_and_import_bsc.py --year 2025

Docker (sps-web konteyneri içinde):
  docker exec -it sps-web python scripts/setup_kalder_and_import_bsc.py --data-dir /app/temp_data
  docker exec -it sps-web python scripts/setup_kalder_and_import_bsc.py --data-dir /app/temp_data --year 2025
"""
import os
import re
import sys
from datetime import date
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from werkzeug.security import generate_password_hash
from __init__ import create_app
from extensions import db
from models import (
    Kurum,
    User,
    AnaStrateji,
    AltStrateji,
    Surec,
    SurecPerformansGostergesi,
    BireyselPerformansGostergesi,
    PerformansGostergeVeri,
)

# Sabitler
KALDER_KURUM_AD = "KalDer"
KALDER_ADMIN_USERNAME = "KalDerAdmin"
KALDER_ADMIN_PASSWORD = "KalDer_4660"
KALDER_ADMIN_EMAIL = "kalderadmin@kalder.org"
BSC_SUREÇ_ADI = "KalDer BSC Göstergeleri"

# CSV sütun eşleştirmeleri (farklı yazımlar kabul edilir)
STRATEJIK_HEDEF_ALIASES = ["stratejik hedef", "stratejik hedefler", "hedef", "ana hedef", "perspektif"]
GOSTERGE_ADI_ALIASES = ["gösterge adı", "gosterge adi", "gösterge", "kpi", "gösterge adi"]
BIRIM_ALIASES = ["birim", "ölçüm birimi", "olcum birimi", "unit"]

# Türkçe ay adları -> ay numarası (sütun başlığı veya Dönem hücresi için)
AY_ADLARI = {
    "oca": 1, "şub": 2, "sub": 2, "mar": 3, "nis": 4, "may": 5, "haz": 6,
    "tem": 7, "ağu": 8, "agu": 8, "eyl": 9, "eki": 10, "kas": 11, "ara": 12,
    "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5,
    "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9,
    "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12,
}

# Dönem (ay adı) sütunu için
DONEM_ALIASES = ["dönem", "donem", "period", "ay", "month"]
HEDEF_ALIASES = ["hedef", "target"]
GERCEKLESEN_ALIASES = ["gerçekleşen", "gerceklesen", "actual", "gerceklenen"]


def _donem_to_ay_no(val):
    """Dönem hücresini (Ocak, Şubat...) ay numarasına çevirir."""
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return None
    s = _norm_col(str(val).strip())
    for ay_ad, no in AY_ADLARI.items():
        if ay_ad in s or s in ay_ad:
            return no
    return None


def _norm_col(s):
    if s is None or (isinstance(s, float) and str(s) == "nan"):
        return ""
    s = str(s).strip().lower()
    s = s.replace("ı", "i").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c")
    return s


def _find_column(df, aliases):
    for col in df.columns:
        n = _norm_col(col)
        for a in aliases:
            if a in n or n in a:
                return col
    return None


def _parse_year_from_filename(filename):
    """Dosya adından yıl çıkar. Örn: BSC_2025_2027 -> 2025."""
    m = re.search(r"20\d{2}", str(filename))
    return int(m.group(0)) if m else date.today().year


def _parse_month_from_header(header):
    """Sütun başlığından ay ve hedef/gerçekleşen bilgisini çıkar. Örn: 'Oca Hedef', 'Şub Gerçekleşen'."""
    if header is None or (isinstance(header, float) and str(header) == "nan"):
        return None, None
    h = _norm_col(str(header))
    is_hedef = "hedef" in h
    is_gercek = "gercek" in h or "gerçek" in h or "gerceklesen" in h
    if not (is_hedef or is_gercek):
        return None, None
    for ay_ad, no in AY_ADLARI.items():
        if ay_ad in h and len(ay_ad) >= 2:
            return no, "hedef" if is_hedef else "gerceklesen"
    # Sayısal ay: 01, 02, ... 12
    m = re.search(r"(?:^|[\s_-])(\d{1,2})(?:[\s_-]|$)", h)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 12:
            return num, "hedef" if is_hedef else "gerceklesen"
    return None, None


def get_or_create_kalder(app):
    with app.app_context():
        kurum = Kurum.query.filter(Kurum.kisa_ad.ilike(KALDER_KURUM_AD)).first()
        if kurum:
            print(f"  [OK] KalDer kurumu zaten mevcut (ID: {kurum.id})")
            return kurum.id
        kurum = Kurum(
            kisa_ad=KALDER_KURUM_AD,
            ticari_unvan="Kalite Derneği",
            faaliyet_alani="Kalite ve Kurumsal Performans",
            sektor="Sivil Toplum",
            email="info@kalder.org",
            web_adresi="https://www.kalder.org",
        )
        db.session.add(kurum)
        db.session.commit()
        print(f"  [OK] KalDer kurumu oluşturuldu (ID: {kurum.id})")
        return kurum.id


def get_or_create_kalder_admin(app, kurum_id):
    with app.app_context():
        user = User.query.filter(User.username == KALDER_ADMIN_USERNAME).first()
        if user:
            if user.kurum_id != kurum_id:
                user.kurum_id = kurum_id
                db.session.commit()
            user.password_hash = generate_password_hash(KALDER_ADMIN_PASSWORD)
            user.sistem_rol = "kurum_yoneticisi"
            db.session.commit()
            print(f"  [OK] KalDerAdmin kullanıcısı güncellendi (ID: {user.id})")
            return user.id
        user = User(
            username=KALDER_ADMIN_USERNAME,
            email=KALDER_ADMIN_EMAIL,
            password_hash=generate_password_hash(KALDER_ADMIN_PASSWORD),
            first_name="KalDer",
            last_name="Admin",
            sistem_rol="kurum_yoneticisi",
            kurum_id=kurum_id,
        )
        db.session.add(user)
        db.session.commit()
        print(f"  [OK] KalDerAdmin kullanıcısı oluşturuldu (ID: {user.id})")
        return user.id


def get_or_create_bsc_surec(app, kurum_id):
    with app.app_context():
        surec = Surec.query.filter(
            Surec.kurum_id == kurum_id,
            Surec.ad.ilike(BSC_SUREÇ_ADI),
        ).first()
        if surec:
            return surec.id
        surec = Surec(
            kurum_id=kurum_id,
            ad=BSC_SUREÇ_ADI,
            code="BSC",
            durum="Aktif",
        )
        db.session.add(surec)
        db.session.commit()
        print(f"  [OK] BSC süreci oluşturuldu (ID: {surec.id})")
        return surec.id


def get_or_create_ana_strateji(app, kurum_id, hedef_metni, dosya_adi=""):
    """Stratejik hedef metninden AnaStrateji oluşturur veya mevcut olanı döner."""
    with app.app_context():
        ad = (hedef_metni or "").strip() or "Genel Hedef"
        existing = AnaStrateji.query.filter(
            AnaStrateji.kurum_id == kurum_id,
            AnaStrateji.ad == ad,
        ).first()
        if existing:
            return existing.id
        # Dosya adından perspektif tahmin et (BSC_Finansal -> FINANSAL)
        perspective = None
        if dosya_adi:
            u = dosya_adi.upper()
            if "FİNANS" in u or "FINANS" in u:
                perspective = "FINANSAL"
            elif "PAYDA" in u or "MÜŞTER" in u or "MUSTER" in u:
                perspective = "MUSTERI"
            elif "SÜREÇ" in u or "SUREÇ" in u or "SUREC" in u:
                perspective = "SUREC"
            elif "ÖĞREN" in u or "OGREN" in u:
                perspective = "OGRENME"
        ana = AnaStrateji(
            kurum_id=kurum_id,
            ad=ad,
            perspective=perspective,
        )
        db.session.add(ana)
        db.session.commit()
        return ana.id


def get_or_create_alt_strateji(app, ana_strateji_id, ad):
    with app.app_context():
        ad = (ad or "").strip() or "Alt Hedef"
        existing = AltStrateji.query.filter(
            AltStrateji.ana_strateji_id == ana_strateji_id,
            AltStrateji.ad == ad,
        ).first()
        if existing:
            return existing.id
        alt = AltStrateji(ana_strateji_id=ana_strateji_id, ad=ad)
        db.session.add(alt)
        db.session.commit()
        return alt.id


def _load_dataframe(path):
    """CSV veya Excel dosyasından DataFrame yükler."""
    import pandas as pd
    path = Path(path)
    if not path.exists():
        return None, path.stem if path else ""
    if path.suffix.lower() == ".csv":
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(path, encoding="latin-1")
        return ([(df, path.stem)], path.stem)
    if path.suffix.lower() in (".xlsx", ".xls"):
        try:
            xl = pd.ExcelFile(path)
            dfs = []
            for sheet in xl.sheet_names:
                # KalDer Excel: başlık 2. satırda (Gösterge Adı, Birim, Dönem, Hedef, Gerçekleşen)
                d = pd.read_excel(path, sheet_name=sheet, header=2)
                if d.empty or len(d.columns) < 3:
                    d = pd.read_excel(path, sheet_name=sheet, header=0)
                if not d.empty and len(d.columns) > 0:
                    dfs.append((d, sheet))
            if not dfs:
                return (None, path.stem)
            return (dfs, path.stem)
        except Exception as e:
            print(f"  [HATA] Excel okunamadı {path.name}: {e}")
            return (None, path.stem)
    return (None, path.stem)


def _process_one_df(app, df, dosya_adi, path_name, kurum_id, kalder_admin_id, surec_id, yil):
    """Tek bir DataFrame'i işler. Uzun format (Dönem sütunu) veya geniş format (aylık sütunlar) desteklenir."""
    import pandas as pd

    # Sütun adlarını normalize et (Unnamed veya Türkçe karakter farkları)
    col_hedef = _find_column(df, STRATEJIK_HEDEF_ALIASES) or _find_column(df, ["unnamed: 1"])
    col_gosterge = _find_column(df, GOSTERGE_ADI_ALIASES) or _find_column(df, ["gosterge bilesenleri", "gösterge bileşenleri"])
    col_birim = _find_column(df, BIRIM_ALIASES)
    col_donem = _find_column(df, DONEM_ALIASES)
    col_hedef_val = _find_column(df, HEDEF_ALIASES)
    col_gerceklesen = _find_column(df, GERCEKLESEN_ALIASES)

    # İlk iki sütun genelde Stratejik Hedef / Gösterge (Unnamed: 0, Unnamed: 1)
    if not col_hedef and len(df.columns) >= 2:
        for c in df.columns:
            if "1" in str(c) or "stratejik" in _norm_col(str(c)):
                col_hedef = c
                break
        if not col_hedef:
            col_hedef = df.columns[1]
    if not col_gosterge and len(df.columns) >= 3:
        for c in df.columns:
            if "gosterge" in _norm_col(str(c)) or "gösterge" in str(c).lower():
                col_gosterge = c
                break
        if not col_gosterge:
            col_gosterge = df.columns[2]
    if not col_birim:
        col_birim = None
    # Hedef/Gerçekleşen: "Hedef ", "Gerçekleşen " veya "Hedef", "Gerçekleşen .1" gibi
    if not col_hedef_val:
        for c in df.columns:
            if _norm_col(str(c)).startswith("hedef"):
                col_hedef_val = c
                break
    if not col_gerceklesen:
        for c in df.columns:
            if "gercek" in _norm_col(str(c)) or "gerçek" in str(c).lower():
                col_gerceklesen = c
                break

    # Uzun format: Dönem sütunu var, her satır = bir ay
    long_format = col_donem is not None and col_hedef_val and col_gerceklesen
    if long_format:
        df = df.copy()
        df["_hedef_ff"] = df[col_hedef].ffill() if col_hedef in df.columns else ""
        df["_gosterge_ff"] = df[col_gosterge].ffill() if col_gosterge in df.columns else ""

    # Geniş format: aylık sütunlar (Oca Hedef, Şub Gerçekleşen...)
    month_columns = []
    if not long_format:
        for c in df.columns:
            ay_no, tip = _parse_month_from_header(c)
            if ay_no is not None:
                month_columns.append((c, ay_no, tip))

    stats = {"strateji": 0, "kpi": 0, "veri": 0}

    with app.app_context():
        for idx, row in df.iterrows():
            if long_format:
                hedef_metni = row.get("_hedef_ff") or row.get(col_hedef)
                gosterge_adi = row.get("_gosterge_ff") or row.get(col_gosterge)
                donem_val = row.get(col_donem)
                ay_no = _donem_to_ay_no(donem_val)
                hedef_val = row.get(col_hedef_val)
                gercek_val = row.get(col_gerceklesen)
                if pd.isna(gosterge_adi) or (pd.isna(ay_no) and pd.isna(hedef_val) and pd.isna(gercek_val)):
                    continue
                birim = row.get(col_birim) if col_birim else ""
            else:
                hedef_metni = row.get(col_hedef)
                gosterge_adi = row.get(col_gosterge)
                birim = row.get(col_birim) if col_birim else ""
                ay_no = None
                hedef_val = gercek_val = None

            if pd.isna(hedef_metni):
                hedef_metni = ""
            if pd.isna(gosterge_adi):
                gosterge_adi = ""
            hedef_metni = str(hedef_metni).strip()
            gosterge_adi = str(gosterge_adi).strip()
            if not gosterge_adi:
                continue

            # Ana strateji (Stratejik Hedef)
            ana_id = get_or_create_ana_strateji(app, kurum_id, hedef_metni or "Genel Hedef", dosya_adi)
            alt_id = get_or_create_alt_strateji(app, ana_id, hedef_metni or gosterge_adi)
            stats["strateji"] += 1

            # Süreç KPI (SurecPerformansGostergesi)
            surec_pg = SurecPerformansGostergesi.query.filter(
                SurecPerformansGostergesi.surec_id == surec_id,
                SurecPerformansGostergesi.ad == gosterge_adi,
            ).first()
            if not surec_pg:
                birim_str = str(birim).strip() if not pd.isna(birim) else ""
                surec_pg = SurecPerformansGostergesi(
                    surec_id=surec_id,
                    ad=gosterge_adi,
                    olcum_birimi=birim_str,
                    alt_strateji_id=alt_id,
                )
                db.session.add(surec_pg)
                db.session.commit()
            stats["kpi"] += 1

            # Bireysel PG (KalDerAdmin adına)
            bireysel_pg = BireyselPerformansGostergesi.query.filter(
                BireyselPerformansGostergesi.user_id == kalder_admin_id,
                BireyselPerformansGostergesi.kaynak_surec_pg_id == surec_pg.id,
            ).first()
            if not bireysel_pg:
                bireysel_pg = BireyselPerformansGostergesi(
                    user_id=kalder_admin_id,
                    ad=gosterge_adi,
                    olcum_birimi=surec_pg.olcum_birimi or "",
                    kaynak="Süreç",
                    kaynak_surec_id=surec_id,
                    kaynak_surec_pg_id=surec_pg.id,
                )
                db.session.add(bireysel_pg)
                db.session.commit()

            if long_format and ay_no is not None:
                # Uzun format: bu satır = bir ay, tek kayıt
                hedef_str = "" if pd.isna(hedef_val) else str(hedef_val).strip()
                gercek_str = "" if pd.isna(gercek_val) else str(gercek_val).strip()
                if not hedef_str and not gercek_str:
                    continue
                veri_tarihi = date(yil, ay_no, 1)
                existing = PerformansGostergeVeri.query.filter(
                    PerformansGostergeVeri.bireysel_pg_id == bireysel_pg.id,
                    PerformansGostergeVeri.veri_tarihi == veri_tarihi,
                ).first()
                if existing:
                    if hedef_str:
                        existing.hedef_deger = hedef_str
                    if gercek_str:
                        existing.gerceklesen_deger = gercek_str
                else:
                    pv = PerformansGostergeVeri(
                        bireysel_pg_id=bireysel_pg.id,
                        yil=yil,
                        veri_tarihi=veri_tarihi,
                        giris_periyot_tipi="aylik",
                        giris_periyot_ay=ay_no,
                        ay=ay_no,
                        user_id=kalder_admin_id,
                        hedef_deger=hedef_str,
                        gerceklesen_deger=gercek_str or "",
                    )
                    db.session.add(pv)
                stats["veri"] += 1
            else:
                # Geniş format: aylık sütunlardan topla
                ay_degerler = {}
                for col_name, ay_no, tip in month_columns:
                    val = row.get(col_name)
                    if pd.isna(val) or str(val).strip() in ("", "-", "—"):
                        continue
                    val_str = str(val).strip()
                    if ay_no not in ay_degerler:
                        ay_degerler[ay_no] = {"hedef": "", "gerceklesen": ""}
                    if tip == "hedef":
                        ay_degerler[ay_no]["hedef"] = val_str
                    else:
                        ay_degerler[ay_no]["gerceklesen"] = val_str
                for ay_no, degerler in ay_degerler.items():
                    if not degerler.get("hedef") and not degerler.get("gerceklesen"):
                        continue
                    veri_tarihi = date(yil, ay_no, 1)
                    existing = PerformansGostergeVeri.query.filter(
                        PerformansGostergeVeri.bireysel_pg_id == bireysel_pg.id,
                        PerformansGostergeVeri.veri_tarihi == veri_tarihi,
                    ).first()
                    if existing:
                        if degerler.get("hedef"):
                            existing.hedef_deger = degerler["hedef"]
                        if degerler.get("gerceklesen"):
                            existing.gerceklesen_deger = degerler["gerceklesen"]
                    else:
                        pv = PerformansGostergeVeri(
                            bireysel_pg_id=bireysel_pg.id,
                            yil=yil,
                            veri_tarihi=veri_tarihi,
                            giris_periyot_tipi="aylik",
                            giris_periyot_ay=ay_no,
                            ay=ay_no,
                            user_id=kalder_admin_id,
                            hedef_deger=degerler.get("hedef") or "",
                            gerceklesen_deger=degerler.get("gerceklesen") or "",
                        )
                        db.session.add(pv)
                    stats["veri"] += 1
            db.session.commit()

    print(f"  [OK] {path_name}: Strateji/KPI/Veri satır işlendi (yıl={yil}).")
    return stats.get("veri", 0) + stats.get("kpi", 0)


def import_one_file(app, file_path, kurum_id, kalder_admin_id, surec_id, yil=None):
    """Tek bir CSV veya Excel dosyasını işler (StrategicGoal, KPI, ActualValue)."""
    path = Path(file_path)
    result = _load_dataframe(path)
    if result is None:
        print(f"  [UYARI] Dosya okunamadı: {file_path}")
        return 0
    dfs_list, file_stem = result
    if not dfs_list:
        print(f"  [UYARI] Dosya boş: {file_path}")
        return 0
    if yil is None:
        yil = _parse_year_from_filename(path.stem)
    total = 0
    for item in dfs_list:
        df, sheet_name = item
        if df is None or df.empty:
            continue
        display_name = f"{path.name}({sheet_name})" if path.suffix.lower() in (".xlsx", ".xls") and sheet_name != file_stem else path.name
        total += _process_one_df(app, df, sheet_name, display_name, kurum_id, kalder_admin_id, surec_id, yil)
    return total


def main():
    import argparse
    parser = argparse.ArgumentParser(description="KalDer kurulumu ve BSC veri import (temp_data)")
    parser.add_argument("--data-dir", default="temp_data", help="Veri klasörü (varsayılan: temp_data)")
    parser.add_argument("--csv", nargs="*", help="Tek tek dosya yolları (CSV veya Excel)")
    parser.add_argument("--year", type=int, default=None, help="Veri yılı (yoksa dosya adından veya güncel yıl)")
    args = parser.parse_args()

    app = create_app()

    print("=" * 60)
    print("KALDER KURUM + KALDERADMIN + BSC VERİ IMPORT")
    print("=" * 60)

    # 1. Tenant: KalDer (Kurum)
    print("\n1. KalDer kurumu (Tenant)...")
    kurum_id = get_or_create_kalder(app)

    # 2. User: KalDerAdmin
    print("\n2. KalDerAdmin kullanıcısı...")
    kalder_admin_id = get_or_create_kalder_admin(app, kurum_id)

    # 3. BSC süreci (KPI'ların bağlanacağı süreç)
    print("\n3. BSC süreci...")
    surec_id = get_or_create_bsc_surec(app, kurum_id)

    # 4. temp_data içindeki CSV/Excel import
    data_files = []
    if args.csv:
        data_files = [Path(f) for f in args.csv]
    else:
        data_dir = Path(args.data_dir)
        if not data_dir.is_absolute():
            data_dir = PROJECT_ROOT / data_dir
        if data_dir.exists():
            for ext in ("*.csv", "*.xlsx", "*.xls"):
                for f in data_dir.glob(ext):
                    if "BSC" in f.name.upper() or "stratejik" in f.name.upper() or "bsc" in f.name.lower():
                        data_files.append(f)
            if not data_files:
                for ext in ("*.csv", "*.xlsx", "*.xls"):
                    data_files.extend(data_dir.glob(ext))
    data_files = sorted(set(data_files))

    if not data_files:
        print("\n4. temp_data içinde BSC/stratejik CSV veya Excel bulunamadı.")
        print("   --data-dir temp_data veya --csv dosya1.xlsx dosya2.csv ile verin.")
        print("   Örnek: python scripts/setup_kalder_and_import_bsc.py --data-dir temp_data")
    else:
        print(f"\n4. Veri import ({len(data_files)} dosya)...")
        for f in data_files:
            import_one_file(app, str(f), kurum_id, kalder_admin_id, surec_id, yil=args.year)

    print("\n" + "=" * 60)
    print("Tamamlandı.")
    print("  Tenant (KalDer) ID:", kurum_id)
    print("  User: KalDerAdmin, Şifre:", KALDER_ADMIN_PASSWORD)
    print("  Veriler bu Tenant ID ile ilişkilendirildi.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
