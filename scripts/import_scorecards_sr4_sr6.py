# -*- coding: utf-8 -*-
"""Import SR4/SR6 süreç karnesi Excel'lerinden KPI tanımı + veri girişlerini içe aktarır.

Mutabakat kuralları (son hali):
- (1) SR6 için periyot okuma kuralı:
  - 3 ay: 1.P..4.P = Q1..Q4 (31/03, 30/06, 30/09, 31/12)
  - 6 ay: 1.P = 30/06 (H1 sonu), 2.P = 31/12 (H2 sonu)
  - 1 yıl: 1.P doluysa 31/12 (yıl sonu) kabul edilir
- (2) Yıl sonu kuralı (d): satırda 'Yıl Sonu' doluysa onu kullan; değilse son dolu dönem değerini yıl sonu kabul et.

Veri saklama yaklaşımı:
- Süreç KPI verilerini yeni tablo açmadan mevcut mekanizmaya "köprü" ile yazar:
  - SurecPerformansGostergesi: KPI tanımı
  - BireyselPerformansGostergesi: süreç lideri adına kaynak='Süreç' KPI kaydı
  - PerformansGostergeVeri: dönem sonu tarihli (veri_tarihi) hedef + gerçekleşen

Notlar:
- Başarı puanı: eşik (Unnamed) kolonlarından okunur, kolon sırası 1..5 puanı temsil eder (Option B).
- 'basari_puani' ve 'agirlikli_basari_puani' alanları sadece en güncel yıl (max yıl) için güncellenir.

Run:
  C:/SPY_Cursor/SP_Code/.venv/Scripts/python.exe scripts/import_scorecards_sr4_sr6.py --dry-run
  C:/SPY_Cursor/SP_Code/.venv/Scripts/python.exe scripts/import_scorecards_sr4_sr6.py --apply

"""

from __future__ import annotations

import argparse
import binascii
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from models import (
    AnaStrateji,
    AltStrateji,
    BireyselPerformansGostergesi,
    Kurum,
    PerformansGostergeVeri,
    Surec,
    SurecPerformansGostergesi,
)


SR_FILES = {
    "SR4": "SR4 Pazarlama Stratejileri Yönetimi Süreç Karnesi.xlsx",
    "SR6": "SR6 Danışmanlık Hizmetleri Yönetimi Süreç Karnesi.xlsx",
}


@dataclass
class ImportStats:
    kpi_created: int = 0
    kpi_updated: int = 0
    bireysel_pg_created: int = 0
    bireysel_pg_updated: int = 0
    veri_created: int = 0
    veri_updated: int = 0
    warnings: int = 0


def _norm(s: str) -> str:
    s = " ".join(str(s).strip().split())
    s = s.casefold()
    s = s.replace("ı", "i")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def resolve_kmf_kurum_id(kurum_id: Optional[int]) -> int:
    if kurum_id is not None:
        return int(kurum_id)
    kmf = Kurum.query.filter(Kurum.kisa_ad.ilike("KMF")).first()
    if not kmf:
        raise SystemExit("KMF kurum not found. Pass --kurum-id explicitly or create kurum with kisa_ad='KMF'.")
    return int(kmf.id)


def safe_int_percent(value: Any) -> int:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    if isinstance(value, str):
        s = value.strip().replace("%", "")
        try:
            value = float(s.replace(",", "."))
        except Exception:
            return 0
    try:
        f = float(value)
    except Exception:
        return 0
    # Excel'de 0.25 gibi geldiği için <=1 ise 100 ile çarp.
    if f <= 1.0:
        return int(round(f * 100))
    return int(round(f))


def parse_float(value: Any) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s or s in {"-", "—"}:
        return None
    s = s.replace("TL", "").replace("%", "").strip()
    s = s.replace(" ", "")
    # 125.000,00 -> 125000.00
    if re.search(r"\d+\.\d{3}", s) and "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    m = re.search(r"\d+(?:\.\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None


def quarter_end_dates(year: int) -> dict[int, date]:
    return {
        1: date(year, 3, 31),
        2: date(year, 6, 30),
        3: date(year, 9, 30),
        4: date(year, 12, 31),
    }


def build_kpi_code(process_code: str, alt_code: str, gosterge: str) -> str:
    base = f"{process_code}:{alt_code}:{gosterge}".encode("utf-8")
    crc = binascii.crc32(base) & 0xFFFFFFFF
    return f"PG-{process_code}-{alt_code}-{crc:08X}"[:50]


def get_threshold_cols(df: pd.DataFrame) -> list[str]:
    unnamed = [c for c in df.columns if isinstance(c, str) and c.startswith("Unnamed:")]
    if "Ağırlıklı Başarı Puanı" in df.columns:
        cols = list(df.columns)
        i = cols.index("Ağırlıklı Başarı Puanı")
        unnamed = [c for c in unnamed if cols.index(c) > i]
    return unnamed


def parse_threshold_cell(cell: Any) -> tuple[Optional[float], Optional[float]]:
    if cell is None or (isinstance(cell, float) and pd.isna(cell)):
        return (None, None)
    s = str(cell).strip()
    if not s or s in {"-", "—"}:
        return (None, None)
    s = s.replace("TL", "").replace("%", "")
    s = " ".join(s.split())

    # +150.000 / 25+ / 61-
    if "+" in s:
        n = parse_float(s)
        return (n, None)
    if s.endswith("-") and parse_float(s[:-1]) is not None:
        return (parse_float(s[:-1]), None)
    if s.startswith("-") and parse_float(s[1:]) is not None:
        return (None, parse_float(s[1:]))

    # a-b / a - b
    parts = [p.strip() for p in s.split("-") if p.strip()]
    if len(parts) >= 2:
        lo = parse_float(parts[0])
        hi = parse_float(parts[1])
        return (lo, hi)

    n = parse_float(s)
    return (n, n)


def score_from_thresholds(value: float, thresholds: list[tuple[Optional[float], Optional[float]]]) -> Optional[int]:
    # Option B: thresholds kolon sırası puan 1..5'i temsil eder.
    for idx, (lo, hi) in enumerate(thresholds, start=1):
        if lo is None and hi is None:
            continue
        if lo is not None and value < lo:
            continue
        if hi is not None and value > hi:
            continue
        return idx
    return None


def infer_direction_from_thresholds(thresholds: list[tuple[Optional[float], Optional[float]]]) -> Optional[str]:
    # Sadece sayısal başladığı yerlerden yön çıkar.
    nums: list[float] = []
    for lo, hi in thresholds:
        n = lo if lo is not None else hi
        if n is not None:
            nums.append(float(n))
    if len(nums) < 2:
        return None
    inc = sum(1 for a, b in zip(nums, nums[1:]) if b > a)
    dec = sum(1 for a, b in zip(nums, nums[1:]) if b < a)
    if inc and not dec:
        return "Increasing"
    if dec and not inc:
        return "Decreasing"
    return None


def normalize_alt_code(v: Any) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip().rstrip(".").upper()


def resolve_alt_strateji(kurum_id: int, code: str) -> Optional[AltStrateji]:
    if not code:
        return None
    return (
        AltStrateji.query.join(AnaStrateji, AltStrateji.ana_strateji_id == AnaStrateji.id)
        .filter(AnaStrateji.kurum_id == kurum_id, AltStrateji.code == code)
        .first()
    )


def ensure_bireysel_pg(user_id: int, surec: Surec, surec_pg: SurecPerformansGostergesi, stats: ImportStats) -> BireyselPerformansGostergesi:
    existing = BireyselPerformansGostergesi.query.filter_by(
        user_id=user_id,
        kaynak="Süreç",
        kaynak_surec_id=surec.id,
        kaynak_surec_pg_id=surec_pg.id,
    ).first()

    if existing:
        changed = False
        if existing.ad != surec_pg.ad:
            existing.ad = surec_pg.ad
            changed = True
        if existing.olcum_birimi != surec_pg.olcum_birimi:
            existing.olcum_birimi = surec_pg.olcum_birimi
            changed = True
        if existing.periyot != surec_pg.periyot:
            existing.periyot = surec_pg.periyot
            changed = True
        if existing.agirlik != (surec_pg.agirlik or 0):
            existing.agirlik = surec_pg.agirlik or 0
            changed = True
        if changed:
            stats.bireysel_pg_updated += 1
        return existing

    new_pg = BireyselPerformansGostergesi(
        user_id=user_id,
        ad=surec_pg.ad,
        aciklama=surec_pg.aciklama,
        kodu=surec_pg.kodu,
        hedef_deger=surec_pg.hedef_deger,
        olcum_birimi=surec_pg.olcum_birimi,
        periyot=surec_pg.periyot,
        agirlik=surec_pg.agirlik or 0,
        kaynak="Süreç",
        kaynak_surec_id=surec.id,
        kaynak_surec_pg_id=surec_pg.id,
    )
    db.session.add(new_pg)
    db.session.flush()
    stats.bireysel_pg_created += 1
    return new_pg


def upsert_pg_veri(
    bireysel_pg_id: int,
    yil: int,
    veri_tarihi: date,
    user_id: int,
    periyot_tipi: str,
    periyot_no: Optional[int],
    hedef: Optional[float],
    fiili: Optional[float],
    stats: ImportStats,
) -> None:
    existing = PerformansGostergeVeri.query.filter_by(
        bireysel_pg_id=bireysel_pg_id,
        yil=yil,
        veri_tarihi=veri_tarihi,
    ).first()

    hedef_s = "" if hedef is None else str(hedef)
    fiili_s = "" if fiili is None else str(fiili)

    if existing:
        changed = False
        if existing.giris_periyot_tipi != periyot_tipi:
            existing.giris_periyot_tipi = periyot_tipi
            changed = True
        if existing.giris_periyot_no != periyot_no:
            existing.giris_periyot_no = periyot_no
            changed = True
        if hedef is not None and existing.hedef_deger != hedef_s:
            existing.hedef_deger = hedef_s
            changed = True
        if fiili is not None and existing.gerceklesen_deger != fiili_s:
            existing.gerceklesen_deger = fiili_s
            changed = True
        if existing.user_id != user_id:
            existing.user_id = user_id
            changed = True
        if changed:
            stats.veri_updated += 1
        return

    new_veri = PerformansGostergeVeri(
        bireysel_pg_id=bireysel_pg_id,
        yil=yil,
        veri_tarihi=veri_tarihi,
        giris_periyot_tipi=periyot_tipi,
        giris_periyot_no=periyot_no,
        hedef_deger=hedef_s if hedef is not None else None,
        gerceklesen_deger=fiili_s if fiili is not None else "0",
        user_id=user_id,
        created_by=user_id,
        updated_by=user_id,
    )
    db.session.add(new_veri)
    stats.veri_created += 1


def iterate_year_sheets(xlsx_path: Path) -> list[str]:
    xl = pd.ExcelFile(xlsx_path)
    years: list[str] = []
    for name in xl.sheet_names:
        if re.fullmatch(r"\d{4}", str(name).strip()):
            years.append(str(name).strip())
    return sorted(years)


def extract_period_values_sr4(row: pd.Series, year: int) -> dict[date, Optional[float]]:
    q = quarter_end_dates(year)
    mapping = {
        q[1]: parse_float(row.get("1.Ç")),
        q[2]: parse_float(row.get("2.Ç")),
        q[3]: parse_float(row.get("3.Ç")),
        q[4]: parse_float(row.get("4.Ç")),
    }
    return {d: v for d, v in mapping.items() if v is not None}


def extract_period_values_sr6(row: pd.Series, year: int) -> dict[date, Optional[float]]:
    per_raw = str(row.get("Ölçüm Per.") or "").strip().lower().replace(" ", "")
    q = quarter_end_dates(year)
    p1 = parse_float(row.get("1.P"))
    p2 = parse_float(row.get("2.P"))
    p3 = parse_float(row.get("3.P"))
    p4 = parse_float(row.get("4.P"))

    # (1) mutabakat: SR6 periyot okuma
    if "6ay" in per_raw:
        out: dict[date, Optional[float]] = {}
        if p1 is not None:
            out[q[2]] = p1  # 30/06
        if p2 is not None:
            out[q[4]] = p2  # 31/12
        return out

    if "1yıl" in per_raw or "1yil" in per_raw or "1yıl" in per_raw or "1yil" in per_raw or "1yıl" in per_raw:
        # 1.P doluysa yıl sonu kabul
        if p1 is not None:
            return {q[4]: p1}
        return {}

    # default: 3 ay
    out = {}
    if p1 is not None:
        out[q[1]] = p1
    if p2 is not None:
        out[q[2]] = p2
    if p3 is not None:
        out[q[3]] = p3
    if p4 is not None:
        out[q[4]] = p4
    return out


def pick_year_end_value(row: pd.Series, year: int, period_values: dict[date, Optional[float]], is_sr6: bool) -> Optional[float]:
    yil_sonu = parse_float(row.get("Yıl Sonu"))
    if yil_sonu is not None:
        return yil_sonu

    if not period_values:
        return None

    # son dolu dönem
    last_date = max(period_values.keys())
    return period_values.get(last_date)


def import_one_file(xlsx_path: Path, process_code: str, kurum_id: int, stats: ImportStats) -> None:
    surec = Surec.query.filter_by(kurum_id=kurum_id, code=process_code, silindi=False).first()
    if not surec:
        raise SystemExit(f"Process not found for kurum_id={kurum_id} code={process_code}")

    leader = None
    if surec.liderler:
        leader = surec.liderler[0]
    elif surec.owners:
        leader = surec.owners[0]

    if not leader:
        stats.warnings += 1
        print(f"[WARN] No leader/owner set for {process_code}. Skipping import for this file.")
        return

    years = iterate_year_sheets(xlsx_path)
    if not years:
        print(f"[WARN] No year sheets found in {xlsx_path.name}")
        return

    max_year = max(int(y) for y in years)

    for sheet in years:
        year = int(sheet)
        df = pd.read_excel(xlsx_path, sheet_name=sheet, header=5)

        # SR6 dosyasında başta boş bir kolon var
        if "Unnamed: 0" in df.columns:
            df = df.drop(columns=["Unnamed: 0"])

        df = df[df.get("Gösterge").notna()].copy()

        thr_cols = get_threshold_cols(df)

        # fiili/hedef ayır
        df["Fiili/ Hedef"] = df["Fiili/ Hedef"].astype(str).str.strip()
        fiili_df = df[df["Fiili/ Hedef"].str.contains("Fiili", case=False, na=False)].copy()
        hedef_df = df[df["Fiili/ Hedef"].str.contains("Hedef", case=False, na=False)].copy()

        # KPI key: (alt strateji code, gösterge adı)
        def build_map(src: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
            m: dict[tuple[str, str], pd.Series] = {}
            for _, r in src.iterrows():
                alt_code = normalize_alt_code(r.get("Alt Strateji"))
                g = str(r.get("Gösterge") or "").strip()
                if not g:
                    continue
                m[(alt_code, g)] = r
            return m

        fiili_map = build_map(fiili_df)
        hedef_map = build_map(hedef_df)

        keys = sorted(set(fiili_map.keys()) | set(hedef_map.keys()))

        for alt_code, gosterge in keys:
            r_f = fiili_map.get((alt_code, gosterge))
            r_h = hedef_map.get((alt_code, gosterge))
            r_any = r_f if r_f is not None else r_h
            if r_any is None:
                continue

            alt = resolve_alt_strateji(kurum_id, alt_code)

            agirlik = safe_int_percent(r_any.get("Göst. Ağırlığı (%)"))
            birim = str(r_any.get("Birim") or "").strip() or None
            per_raw = str(r_any.get("Ölçüm Per.") or "").strip()

            gosterge_turu = str(r_any.get("Göst. Türü") or "").strip() or None
            target_method = str(r_any.get("Hedef Belirl. Yön.") or "").strip() or None
            onceki = parse_float(r_any.get("Önceki Yıl Ort."))

            thresholds_raw = []
            for c in thr_cols:
                v = r_any.get(c)
                if v is None or (isinstance(v, float) and pd.isna(v)):
                    thresholds_raw.append(None)
                else:
                    thresholds_raw.append(str(v).strip())
            thresholds_parsed = [parse_threshold_cell(v) for v in thresholds_raw if v not in (None, "", "-", "—")]

            kpi = SurecPerformansGostergesi.query.filter_by(
                surec_id=surec.id,
                ad=gosterge,
                alt_strateji_id=(alt.id if alt else None),
            ).first()

            kpi_code = build_kpi_code(process_code, alt_code or "NA", gosterge)

            if kpi:
                changed = False
                if kpi.kodu != kpi_code:
                    kpi.kodu = kpi_code
                    changed = True
                if kpi.olcum_birimi != birim:
                    kpi.olcum_birimi = birim
                    changed = True
                if kpi.periyot != per_raw:
                    kpi.periyot = per_raw
                    changed = True
                if (kpi.agirlik or 0) != agirlik:
                    kpi.agirlik = agirlik
                    changed = True
                if kpi.gosterge_turu != gosterge_turu:
                    kpi.gosterge_turu = gosterge_turu
                    changed = True
                if kpi.target_method != target_method:
                    kpi.target_method = target_method
                    changed = True
                if kpi.unit != birim:
                    kpi.unit = birim
                    changed = True
                if onceki is not None and (kpi.onceki_yil_ortalamasi is None or abs(kpi.onceki_yil_ortalamasi - onceki) > 1e-9):
                    kpi.onceki_yil_ortalamasi = onceki
                    changed = True
                if thr_cols and thresholds_raw:
                    new_json = json.dumps(thresholds_raw, ensure_ascii=False)
                    if kpi.basari_puani_araliklari != new_json:
                        kpi.basari_puani_araliklari = new_json
                        changed = True

                dir_inferred = infer_direction_from_thresholds(thresholds_parsed)
                if dir_inferred and kpi.direction != dir_inferred:
                    kpi.direction = dir_inferred
                    changed = True

                if changed:
                    stats.kpi_updated += 1
            else:
                kpi = SurecPerformansGostergesi(
                    surec_id=surec.id,
                    ad=gosterge,
                    kodu=kpi_code,
                    olcum_birimi=birim,
                    periyot=per_raw,
                    agirlik=agirlik,
                    gosterge_turu=gosterge_turu,
                    target_method=target_method,
                    unit=birim,
                    onceki_yil_ortalamasi=onceki,
                    basari_puani_araliklari=json.dumps(thresholds_raw, ensure_ascii=False) if thr_cols else None,
                    alt_strateji_id=(alt.id if alt else None),
                )
                dir_inferred = infer_direction_from_thresholds(thresholds_parsed)
                if dir_inferred:
                    kpi.direction = dir_inferred
                db.session.add(kpi)
                db.session.flush()
                stats.kpi_created += 1

            bireysel_pg = ensure_bireysel_pg(leader.id, surec, kpi, stats)

            is_sr6 = process_code.upper() == "SR6"

            # dönem değerleri
            if is_sr6:
                period_f = extract_period_values_sr6(r_f, year) if r_f is not None else {}
                period_h = extract_period_values_sr6(r_h, year) if r_h is not None else {}
            else:
                period_f = extract_period_values_sr4(r_f, year) if r_f is not None else {}
                period_h = extract_period_values_sr4(r_h, year) if r_h is not None else {}

            # her dönem için upsert (hedef + fiili aynı kayda yazılır)
            all_dates = sorted(set(period_f.keys()) | set(period_h.keys()))
            for d in all_dates:
                fi = period_f.get(d)
                he = period_h.get(d)
                # periyot tipi ve no: tarih üzerinden çeyrek no çıkar
                per_type = "ceyrek"
                qno = 1
                if d.month == 3:
                    qno = 1
                elif d.month == 6:
                    qno = 2
                elif d.month == 9:
                    qno = 3
                else:
                    qno = 4
                upsert_pg_veri(
                    bireysel_pg_id=bireysel_pg.id,
                    yil=year,
                    veri_tarihi=d,
                    user_id=leader.id,
                    periyot_tipi=per_type,
                    periyot_no=qno,
                    hedef=he,
                    fiili=fi,
                    stats=stats,
                )

            # yıl sonu (2.d)
            year_end_date = date(year, 12, 31)
            year_end_f = None
            year_end_h = None
            if r_f is not None:
                year_end_f = pick_year_end_value(r_f, year, period_f, is_sr6=is_sr6)
            if r_h is not None:
                year_end_h = pick_year_end_value(r_h, year, period_h, is_sr6=is_sr6)

            if year_end_f is not None or year_end_h is not None:
                upsert_pg_veri(
                    bireysel_pg_id=bireysel_pg.id,
                    yil=year,
                    veri_tarihi=year_end_date,
                    user_id=leader.id,
                    periyot_tipi="yillik",
                    periyot_no=None,
                    hedef=year_end_h,
                    fiili=year_end_f,
                    stats=stats,
                )

            # (latest year) başarı puanı ve ağırlıklı başarı puanı güncelle
            if year == max_year and year_end_f is not None and thresholds_parsed:
                s = score_from_thresholds(year_end_f, thresholds_parsed)
                if s is not None:
                    kpi.basari_puani = int(s)
                    kpi.agirlikli_basari_puani = float(s) * float((kpi.agirlik or 0) / 100.0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kurum-id", type=int, default=None)
    parser.add_argument("--belge-dir", type=str, default=str(PROJECT_ROOT / "belge"))
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--apply", action="store_true", default=False)
    args = parser.parse_args()

    if args.apply and args.dry_run:
        raise SystemExit("Use either --apply or --dry-run, not both.")
    dry_run = not args.apply

    app = create_app()
    with app.app_context():
        kurum_id = resolve_kmf_kurum_id(args.kurum_id)
        belge_dir = Path(args.belge_dir)

        stats = ImportStats()

        for process_code, fname in SR_FILES.items():
            xlsx_path = belge_dir / fname
            if not xlsx_path.exists():
                stats.warnings += 1
                print(f"[WARN] Missing file: {xlsx_path}")
                continue
            import_one_file(xlsx_path, process_code=process_code, kurum_id=kurum_id, stats=stats)

        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()

        print("\n=== IMPORT STATS ===")
        print(stats)
        print("mode=", "dry-run" if dry_run else "apply")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
