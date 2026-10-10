"""Karne hesap yollarını yan yana koyan SALT-OKUNUR kıyas aracı (Faz 1A).

Aynı PG/yıl için sistemdeki hesap yollarının ne ürettiğini karşılaştırır ve tutarsızlık
SINIFLARINI sayar. Hiçbir şey yazmaz (persist yok, commit yok).

    python scripts/ops/karne_kiyas.py                 # KMF (16) + Tomofil (27)
    python scripts/ops/karne_kiyas.py --tenant 27
    python scripts/ops/karne_kiyas.py --cikti docs/ekim2026/kiyas

Karşılaştırılan yollar:
  karne   : micro/modules/surec/routes_karne.py — yıl özeti (PG'nin kendi yöntemi) + ESKİ 1-5 parser
  bant    : hesapla_basari_puani_ham — bant (0-100) VE eski format birlikte (doğru fonksiyon)
  motor   : score_engine_service.get_pg_scores_from_kpi_data — yıllık config, en yeni 100 kayıt
  k_rapor : k_rapor/routes.py kritik-PG yüzdesi — yalnız SON veri noktası
  js      : ui/static/platform/js/surec.js formatKanbanBasariPuaniLikeTable yedek hesabı
            (backend puanı boşsa; entries tüm periyot anahtarlarını içerir) — YAKLAŞIK
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

os.environ.setdefault("SCHEDULER_ENABLED", "false")  # açılışta zamanlayıcı başlatma
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

DEFAULT_TENANTS = (16, 27)  # KMF, Tomofil (2026-09-30 kararı)

SINIFLAR = {
    "BANT_BOS": "HATA-02: bant formatlı kayıt, karne/eski parser puan üretemiyor (bant doğru fonksiyonla puan veriyor)",
    "ESKI_PUAN_YOK": "Aralık tanımlı ama hiçbir yol puan üretemiyor (aralık boşluğu / parse)",
    "YONTEM_FARK": "HATA-05: PG'nin kendi yöntemi ≠ yıllık config yöntemi → karne ve motor farklı özet çıkarır",
    "MOTOR_KESIK": "HATA-06: yıl içinde 100'den fazla kayıt var, motor yalnız en yeni 100'ünü kullanıyor (SUM/AVG kesilir)",
    "JS_SISME": "HATA-03: sunucu puanı boş → JS yedek hesabı devrede; 'Toplama'da tüm periyot anahtarlarını toplayıp değeri şişirir",
    "ACIK_ALT_SINIR": "BİLGİ (Faz 1B'de düzeltildi): tek sınırlı bant ('-4', '79-') kullanan PG — eski ham parser yanlış okurdu",
    "ARTI_FORMAT": "BİLGİ (Faz 1B'de düzeltildi): 'N+' biçimi kullanan PG — eskiden parse edilemiyordu",
    "PUAN_DEGISIR": "ÇAPRAZ KONTROL: araçtaki bağımsız parser ile üretimdeki parser ayrışıyor (0 olmalı)",
    "KRAPOR_FARK": "HATA-14: k_rapor son veri noktası ile motor özeti ≥10 puan ayrışıyor",
    "YON_SIFIR": "HATA-04: 'azalması iyi' + gerçekleşen 0 → k_rapor %0, motor 100",
    "HEDEF_SIFIR": "HATA-13: hedef 0 → motor ve k_rapor puanlamıyor",
    "ARALIK_NOKTA": "HATA-07: eski formatta ondalık nokta içeren aralık (parse_aralik_degeri noktayı siler)",
    "AGIRLIK_1": "HATA-09: ağırlık tam 1 → %1 mi %100 mü belirsiz",
    "PUAN_FARK": "karne(1-5) ile motor(0-100) sıralaması çelişiyor (karne ≥4 ama motor <50 ya da tersi)",
}

_NOKTALI = re.compile(r"\d\.\d")


def _f(v):
    try:
        return float(str(v).replace(",", ".")) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _bpa_format(raw) -> str:
    from app.utils.karne_hesaplamalar import parse_bant_listesi, parse_basari_puani_araliklari
    if raw is None or not str(raw).strip():
        return "yok"
    if parse_bant_listesi(raw):
        return "bant"
    return "eski" if parse_basari_puani_araliklari(raw) else "bozuk"


_RE_TEK_NEGATIF = re.compile(r"^\s*-\s*\d+([.,]\d+)?\s*$")
_RE_ARTI = re.compile(r"^\s*\d+([.,]\d+)?\s*\+\s*$")
_RE_SONDA_TIRE = re.compile(r"^\s*\d+([.,]\d+)?\s*-\s*$")


def _sayi(x: str) -> float:
    """Binlik/ondalık ayrımı: '.' + tam 3 hane = binlik ('400.000'); diğerleri ondalık."""
    x = x.strip().replace("%", "").replace("TL", "").strip()
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", x):
        x = x.replace(".", "")
    return float(x.replace(",", "."))


def _parse_duz(txt):
    """ÖNERİLEN parser. Dönüş: ('kapali', lo, hi) | ('acik', N) | None.

    'acik' = tek sınırlı bant ('-4', '79-', '20+'): yönü BANDIN KONUMU belirler
    (en kötü bant → 'N ve altı', en iyi bant → 'N ve üstü'); bkz. puan_duzeltilmis."""
    t = (str(txt) if txt is not None else "").replace("%", "").replace("TL", "").strip()
    if not t or t == "-":
        return None
    try:
        if _RE_TEK_NEGATIF.match(t):
            return ("acik", _sayi(t.lstrip(" -")))
        if _RE_ARTI.match(t):
            return ("acik", _sayi(t.rstrip(" +")))
        if _RE_SONDA_TIRE.match(t):
            return ("acik", _sayi(t.rstrip(" -")))
        m = re.match(r"^\s*(-?\d[\d.,%TL ]*?)\s*-\s*(-?\d[\d.,%TL ]*)$", t)
        if m:
            return ("kapali", _sayi(m.group(1)), _sayi(m.group(2)))
        v = _sayi(t)
        return ("kapali", v, v)
    except ValueError:
        return None


def _bantlar_duz(bpa_dict, direction):
    """{puan: (lo, hi)} — açık uçlu bantlar konuma göre çözülür."""
    from app.utils.karne_hesaplamalar import _coerce_aralik_str_for_hesap
    ham = {}
    for puan, raw in (bpa_dict or {}).items():
        r = _parse_duz(_coerce_aralik_str_for_hesap(raw))
        if r is not None:
            ham[int(puan)] = r
    if not ham:
        return {}
    en_kotu, en_iyi = min(ham), max(ham)
    artan = (direction or "").lower() != "decreasing"
    out = {}
    for puan, r in ham.items():
        if r[0] == "kapali":
            out[puan] = (r[1], r[2])
            continue
        n = r[1]
        alta_dogru = (puan == en_kotu) if artan else (puan == en_iyi)
        out[puan] = (None, n) if alta_dogru else (n, None)
    return out


def puan_duzeltilmis(deger, bpa_dict, direction):
    """Eski format (1-5) için öneri hesap: bağlama duyarlı açık uçlu bantlar."""
    if deger is None or not bpa_dict:
        return None
    bantlar = _bantlar_duz(bpa_dict, direction)
    if not bantlar:
        return None
    azalan = (direction or "").lower() == "decreasing"
    sirali = sorted(bantlar.items(), reverse=azalan)
    for puan, (lo, hi) in sirali:
        if (lo is None or deger >= lo) and (hi is None or deger <= hi):
            return puan
    # Hiçbir banda düşmedi: bugünkü yedek kural (karne_hesaplamalar.hesapla_basari_puani) korunur.
    _, (son_lo, son_hi) = sirali[-1]
    _, (ilk_lo, ilk_hi) = sirali[0]
    if azalan:
        if son_hi is not None and deger > son_hi:
            return 1
        if son_lo is not None and deger < son_lo:
            return 5
    else:
        if son_hi is not None and deger > son_hi:
            return 5
        if ilk_lo is not None and deger < ilk_lo:
            return 1
    return 3


def _eski_sorunlar(bpa_dict, direction):
    """(yorum_farki, arti_format): bugünkü parser ile önerilen bant sınırları ayrışıyor mu?"""
    from app.utils.karne_hesaplamalar import _coerce_aralik_str_for_hesap, parse_aralik_degeri
    yeni = _bantlar_duz(bpa_dict, direction)
    fark = arti = False
    for puan, raw in (bpa_dict or {}).items():
        t = _coerce_aralik_str_for_hesap(raw) or ""
        arti = arti or bool(_RE_ARTI.match(t))
        eski = parse_aralik_degeri(t) if t else None
        if eski is not None and int(puan) in yeni and tuple(eski) != tuple(yeni[int(puan)]):
            fark = True
    return fark, arti


def _karne_rollup(method, rows):
    """routes_karne._rollup_year_actual birebir (PG'nin KENDİ yöntemi)."""
    m = (method or "").lower()
    nums = [x for x in (_f(r.actual_value) for r in rows) if x is not None]
    if m in ("toplama", "toplam"):
        return float(sum(nums)) if nums else None
    if m == "ortalama":
        return round(sum(nums) / len(nums), 6) if nums else None
    if rows:
        last = max(rows, key=lambda e: e.data_date or date(1900, 1, 1))
        return _f(last.actual_value)
    return None


def _js_value(method, rows, year):
    """surec.js yedek hesabındaki 'compareVal' (yaklaşık): entries'in tüm periyot anahtarları."""
    from app.utils.process_utils import data_date_to_period_keys
    by_key = defaultdict(list)
    for r in sorted(rows, key=lambda e: (e.data_date or date(1900, 1, 1), e.id)):
        for key in data_date_to_period_keys(r.data_date, year):
            by_key[key].append((r, _f(r.actual_value)))
    m = (method or "").lower()
    agg = {}
    for key, items in by_key.items():
        nums = [v for _, v in items if v is not None]
        if m in ("toplama", "toplam") and nums:
            agg[key] = sum(nums)
        elif m == "ortalama" and nums:
            agg[key] = round(sum(nums) / len(nums), 2)
        else:
            agg[key] = _f(max(items, key=lambda x: x[0].data_date or date(1900, 1, 1))[0].actual_value)
    vals = [v for v in agg.values() if v is not None]
    if not vals:
        return None
    return sum(vals) if m in ("toplama", "toplam") else vals[-1]


def _krapor_pct(kpi, last_row):
    """k_rapor kritik-PG yüzdesi: SON veri noktası, ortak kural (Faz 1B sonrası compute_pg_score)."""
    from app.services.score_engine_service import compute_pg_score
    if not kpi.target_value or not last_row or not last_row.actual_value:
        return None
    t, a = _f(kpi.target_value), _f(last_row.actual_value)
    if t is None or a is None:
        return None
    azalan = getattr(kpi, "direction", None) in ("Decreasing", "decreasing", "lower_is_better")
    pct = compute_pg_score(t, a, "Decreasing" if azalan else "Increasing")
    return None if pct is None else round(pct, 1)


def kiyasla(tenant_id: int, yillar=None):
    from app.models.process import KpiData, Process, ProcessKpi
    from app.services.plan_year_service import get_kpi_configs_bulk, get_plan_year
    from app.services.score_engine_service import (
        _resolve_target_for_calculation, aggregate_actuals, compute_pg_score, normalize_aggregation_method,
    )
    from app.utils.karne_hesaplamalar import (
        hesapla_basari_puani_ham, parse_basari_puani_araliklari,
    )

    procs = {p.id: p for p in Process.query.filter_by(tenant_id=tenant_id, is_active=True).all()}
    kpis = ProcessKpi.query.filter(
        ProcessKpi.process_id.in_(list(procs)), ProcessKpi.is_active.is_(True)
    ).all() if procs else []
    kpi_ids = [k.id for k in kpis]
    rows_all = KpiData.query.filter(
        KpiData.process_kpi_id.in_(kpi_ids), KpiData.is_active.is_(True)
    ).all() if kpi_ids else []
    by = defaultdict(list)
    for r in rows_all:
        by[(r.process_kpi_id, r.year)].append(r)
    years = sorted({y for (_, y) in by}) if yillar is None else list(yillar)

    out = []
    for year in years:
        py = get_plan_year(tenant_id, year)
        cfg_map = get_kpi_configs_bulk(kpis, py)
        as_of = min(date.today(), date(year, 12, 31))
        for k in kpis:
            rows = [r for r in by.get((k.id, year), []) if r.data_date and r.data_date <= as_of]
            if not rows:
                continue
            cfg = cfg_map.get(k.id) or {}
            if cfg.get("is_included") is False:
                continue
            direction = cfg.get("direction") or k.direction or "Increasing"
            method_cfg = cfg.get("data_collection_method") or k.data_collection_method or "Ortalama"
            bpa = cfg.get("basari_puani_araliklari", k.basari_puani_araliklari)
            target_raw = cfg.get("target_value", k.target_value)
            target = _resolve_target_for_calculation(target_raw, direction)
            weight = cfg.get("weight", k.weight)

            # karne (sunucu) — Faz 1B sonrası route ile birebir: yıllık config yöntemi + ham fonksiyon
            r_karne = _karne_rollup(method_cfg, rows)
            r_cfg = r_karne
            karne_puan, karne_olcek = None, None
            if r_karne is not None and bpa:
                try:
                    karne_puan, karne_olcek = hesapla_basari_puani_ham(
                        r_karne, bpa if isinstance(bpa, str) else json.dumps(bpa), direction or "Increasing")
                except Exception:  # noqa: BLE001 — araç, kaydı atla
                    karne_puan, karne_olcek = None, None
            bant_puan, bant_olcek = (karne_puan, karne_olcek) if karne_olcek == "0-100" else (None, None)
            # motor: Faz 1B sonrası — tüm kayıtlar, ortak özet + ortak puan fonksiyonu
            newest = sorted(rows, key=lambda e: e.data_date, reverse=True)
            vals = [v for v in (_f(e.actual_value) for e in newest) if v is not None]
            engine_actual = aggregate_actuals(vals, method_cfg)
            engine_pct = compute_pg_score(target, engine_actual, direction)
            tam_pct = engine_pct
            last_row = max(rows, key=lambda e: e.data_date)
            krapor = _krapor_pct(k, last_row)
            js_val = _js_value(k.data_collection_method or "Ortalama", rows, year)

            fmt = _bpa_format(bpa)
            try:
                bpa_d = parse_basari_puani_araliklari(bpa) if isinstance(bpa, str) and fmt == "eski" else None
            except Exception:  # noqa: BLE001
                bpa_d = None
            acik, arti = _eski_sorunlar(bpa_d, direction)
            duz = puan_duzeltilmis(r_karne, bpa_d, direction) if bpa_d else None
            n_engine = normalize_aggregation_method(method_cfg)
            n_pg = normalize_aggregation_method(k.data_collection_method or "Ortalama")
            sinif = []
            if fmt == "bant" and karne_puan is None:
                sinif.append("BANT_BOS")
            if fmt in ("eski", "bant") and bpa and karne_puan is None:
                sinif.append("ESKI_PUAN_YOK")
            if n_pg != n_engine:
                sinif.append("YONTEM_FARK")
            if acik:
                sinif.append("ACIK_ALT_SINIR")
            if arti:
                sinif.append("ARTI_FORMAT")
            if fmt == "eski" and duz != karne_puan:
                sinif.append("PUAN_DEGISIR")
            if krapor is not None and engine_pct is not None and abs(krapor - engine_pct) >= 10:
                sinif.append("KRAPOR_FARK")
            if (direction or "").lower() == "decreasing" and _f(last_row.actual_value) == 0 \
                    and krapor == 0.0 and engine_pct == 100.0:
                sinif.append("YON_SIFIR")
            if _f(target_raw) == 0 and engine_pct is None:
                sinif.append("HEDEF_SIFIR")
            if fmt == "eski" and _NOKTALI.search(str(bpa)):
                sinif.append("ARALIK_NOKTA")
            if _f(weight) == 1.0:
                sinif.append("AGIRLIK_1")
            if karne_puan is not None and engine_pct is not None and fmt == "eski" \
                    and ((karne_puan >= 4 and engine_pct < 50) or (karne_puan <= 2 and engine_pct >= 90)):
                sinif.append("PUAN_FARK")

            out.append({
                "tenant": tenant_id, "yil": year, "pg_id": k.id, "kod": k.code or "",
                "ad": (k.name or "")[:60], "surec": (procs[k.process_id].name or "")[:40],
                "yon": direction, "yontem_pg": k.data_collection_method, "yontem_cfg": method_cfg,
                "hedef": target_raw, "aralik_format": fmt, "n_veri": len(rows),
                "ozet_karne": r_karne, "ozet_motor": engine_actual, "son_deger": last_row.actual_value,
                "js_deger": js_val, "puan_karne_1_5": karne_puan, "puan_duzeltilmis": duz,
                "puan_bant": bant_puan, "puan_bant_olcek": bant_olcek,
                "motor_pct": engine_pct, "motor_pct_tam": tam_pct, "krapor_pct": krapor, "agirlik": weight,
                "siniflar": "|".join(sinif),
            })
    return out


def ozet_yaz(rows, yol: Path, tenantlar):
    lines = ["# Karne kıyas özeti (Faz 1A)", "",
             f"Tarih: {date.today().isoformat()} · Kurumlar: {', '.join(map(str, tenantlar))} · "
             "Salt-okunur; hiçbir kayıt değiştirilmedi.", ""]
    for t in tenantlar:
        tr = [r for r in rows if r["tenant"] == t]
        lines += [f"## Kurum {t} — {len(tr)} PG×yıl kaydı", "",
                  "| Sınıf | Kayıt | Açıklama |", "|---|--:|---|"]
        c = Counter(s for r in tr for s in r["siniflar"].split("|") if s)
        for s, n in c.most_common():
            lines.append(f"| `{s}` | {n} | {SINIFLAR[s]} |")
        gecis = Counter((r["puan_karne_1_5"], r["puan_duzeltilmis"]) for r in tr
                        if "PUAN_DEGISIR" in r["siniflar"].split("|"))
        if gecis:
            lines += ["**Düzeltilmiş parser ile karne puanı değişimi (bugünkü → önerilen):**", "",
                      "| bugünkü | önerilen | PG×yıl |", "|--:|--:|--:|"]
            for (a, b), n in sorted(gecis.items(), key=lambda x: (-x[1], str(x[0]))):
                lines.append(f"| {a if a is not None else '—'} | {b if b is not None else '—'} | {n} |")
            lines.append("")
        kesik = [r for r in tr if "MOTOR_KESIK" in r["siniflar"].split("|")
                 and r["motor_pct"] is not None and r["motor_pct_tam"] is not None]
        if kesik:
            farklar = sorted(abs(r["motor_pct"] - r["motor_pct_tam"]) for r in kesik)
            lines += [f"**Motor 100-kayıt sınırı etkisi ({len(kesik)} PG×yıl):** puan farkı "
                      f"ortalama {sum(farklar)/len(farklar):.2f}, medyan {farklar[len(farklar)//2]:.2f}, "
                      f"en büyük {farklar[-1]:.2f}; ≥5 puan fark: {sum(1 for f in farklar if f >= 5)} kayıt.", ""]
        bant = [r for r in tr if r["siniflar"] and "BANT_BOS" in r["siniflar"].split("|")]
        if bant:
            lines += [f"**Bant formatı:** {len(bant)} PG×yıl kaydında karne sayfası puan üretemiyor; "
                      f"bant fonksiyonu 0-100 ölçeğinde puan üretiyor "
                      f"(dağılım: {dict(Counter(r['puan_bant'] for r in bant))}). "
                      "Ekranda 1-5 ölçeğiyle nasıl gösterileceği karar gerektirir.", ""]
        temiz = sum(1 for r in tr if not r["siniflar"])
        lines += ["", f"Sınıfsız (yollar tutarlı): **{temiz}** / {len(tr)}", ""]
        for s in [s for s, _ in c.most_common()]:
            ornek = [r for r in tr if s in r["siniflar"].split("|")][:4]
            lines += [f"### {s} — örnekler", "",
                      "| yıl | PG | ad | yön | yöntem(pg/cfg) | hedef | karne özet | motor özet | js | karne(1-5) | önerilen(1-5) | bant | motor % | k_rapor % |",
                      "|--:|--:|---|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|"]
            for r in ornek:
                def g(x):
                    return "" if x is None else (f"{x:.4g}" if isinstance(x, float) else str(x))
                lines.append("| " + " | ".join([
                    str(r["yil"]), str(r["pg_id"]), r["ad"].replace("|", "/"), r["yon"],
                    f'{r["yontem_pg"]}/{r["yontem_cfg"]}', g(r["hedef"]), g(r["ozet_karne"]),
                    g(r["ozet_motor"]), g(r["js_deger"]), g(r["puan_karne_1_5"]), g(r["puan_duzeltilmis"]),
                    g(r["puan_bant"]), g(r["motor_pct"]), g(r["krapor_pct"])]) + " |")
            lines.append("")
    yol.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tenant", type=int, action="append", help="kurum id (tekrarlanabilir)")
    ap.add_argument("--cikti", default="docs/ekim2026/kiyas")
    args = ap.parse_args()
    tenantlar = tuple(args.tenant) if args.tenant else DEFAULT_TENANTS

    from app import create_app
    from config import DevelopmentConfig
    app = create_app(DevelopmentConfig)
    with app.app_context():
        from app.models import db
        rows = []
        for t in tenantlar:
            rows += kiyasla(t)
        db.session.rollback()  # salt-okunur güvencesi

    cikti = Path(args.cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    if rows:
        with open(cikti / "karne_farklari.csv", "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    ozet_yaz(rows, cikti / "karne_kiyas_ozet.md", tenantlar)
    print(f"{len(rows)} kayit -> {cikti}")


if __name__ == "__main__":
    main()
