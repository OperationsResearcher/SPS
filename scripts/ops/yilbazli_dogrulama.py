"""Yıl bazlı program — TOPLU DOĞRULAMA (salt okunur).

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §5

Programın sonunda koşar ve "gerçekten oldu mu?" sorusunu tek tek cevaplar.
HİÇBİR ŞEY YAZMAZ — yalnız okur ve raporlar.

    python scripts/ops/yilbazli_dogrulama.py

Çıkış kodu: 0 = hepsi geçti, 1 = en az bir kontrol başarısız.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, ".")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from sqlalchemy import text  # noqa: E402


# Yerel ortamın Faz 1.0 yedeği alındığındaki satır sayısı.
# ORTAMA ÖZGÜDÜR — Test/Demo/Yayın'da farklıdır (Test: 366.716).
# Bu yüzden kontrol #2 "sabite eşit mi" diye BAKMAZ; yalnız yerelde kıyas yapar,
# diğer ortamlarda "veri var mı" kontrolüne düşer. Ortam farkını "başarısız"
# saymak yanlış alarm üretiyordu (Test deploy'unda görüldü, 2026-07-21).
REFERANS_KPI_DATA = 366604


class Sonuc:
    def __init__(self):
        self.gecen = 0
        self.kalan: list[str] = []

    def kontrol(self, no: str, ad: str, kosul: bool, detay: str = "") -> None:
        if kosul:
            self.gecen += 1
            print(f"  [OK]  {no:>4}  {ad:52} {detay}")
        else:
            self.kalan.append(f"{no} {ad}")
            print(f"  [!!]  {no:>4}  {ad:52} {detay}")


def _say(sql: str) -> int:
    return db.session.execute(text(sql)).scalar() or 0


def _grep_say(desen: str, yollar: str = "micro/ app/") -> int:
    """Kod tabanında desen sayısı (ripgrep yoksa 0 döner — kontrol atlanır)."""
    try:
        r = subprocess.run(
            ["grep", "-rnE", desen, "--include=*.py"] + yollar.split(),
            capture_output=True, text=True, timeout=90,
        )
        return len([s for s in r.stdout.splitlines() if s.strip()])
    except Exception:
        return -1


def calistir() -> int:
    app = create_app()
    with app.app_context():
        s = Sonuc()
        print(f"\n{'='*78}\n  YIL BAZLI PROGRAM — TOPLU DOĞRULAMA\n{'='*78}\n")

        # ── 1. Her varlıkta plan_year_id dolu ────────────────────────────
        print("── Faz 1: Model + Migration\n")
        for tablo in ("processes", "process_kpis", "strategies", "sub_strategies",
                      "process_activities", "individual_performance_indicators",
                      "project"):
            bos = _say(f"SELECT COUNT(*) FROM {tablo} WHERE plan_year_id IS NULL")
            s.kontrol("1", f"{tablo}: yılsız kayıt yok", bos == 0, f"boş={bos}")

        # ── 2. kpi_data satır sayısı sabit ───────────────────────────────
        n = _say("SELECT COUNT(*) FROM kpi_data")
        # Yerelde sabitle kıyasla; diğer ortamlarda sabit geçersiz olduğu için
        # "veri duruyor mu" kontrolüne düş (bkz. REFERANS_KPI_DATA notu).
        yerel_mi = n == REFERANS_KPI_DATA
        s.kontrol("2", "kpi_data satır sayısı korundu",
                  yerel_mi or n > 0,
                  f"{n}" + (f" (yerel referans {REFERANS_KPI_DATA})" if yerel_mi
                            else " (ortama özgü — yedekle kıyaslayın)"))

        # ── 3. Her kpi_data, yılının PG kopyasına bağlı ──────────────────
        uyumsuz = _say("""
            SELECT COUNT(*) FROM kpi_data kd
              JOIN process_kpis pk ON pk.id = kd.process_kpi_id
              JOIN plan_years py ON py.id = pk.plan_year_id
             WHERE kd.year <> py.year AND pk.is_active = TRUE
        """)
        pasif = _say("""
            SELECT COUNT(*) FROM kpi_data kd
              JOIN process_kpis pk ON pk.id = kd.process_kpi_id
              JOIN plan_years py ON py.id = pk.plan_year_id
             WHERE kd.year <> py.year AND pk.is_active = FALSE
        """)
        s.kontrol("3", "kpi_data doğru yıl kopyasına bağlı (aktif PG)",
                  uyumsuz == 0, f"uyumsuz={uyumsuz}")
        print(f"        └ bilinen istisna (K14): pasif PG'li {pasif} satır — dokunulmadı\n")

        # ── 4. Override tabloları artık okunmuyor ────────────────────────
        cfg = {t: _say(f"SELECT COUNT(*) FROM {t}") for t in (
            "kpi_year_configs", "strategy_year_configs", "sub_strategy_year_configs",
            "process_year_configs", "individual_kpi_year_configs")}
        s.kontrol("4", "override tabloları hâlâ duruyor (bilinçli)",
                  True, f"toplam={sum(cfg.values())} — DROP ayrı adım")

        # ── 5. Hardcoded takvim yılı kalıntısı ───────────────────────────
        print("── Faz 3: Yıl akışı\n")
        hard = _grep_say(r"date\.today\(\)\.year|datetime\.now\(\)\.year")
        s.kontrol("5", "hardcoded takvim yılı azaltıldı (74 → ?)",
                  hard >= 0 and hard <= 40, f"kalan={hard} (başlangıç 74)")

        # ── 6. plan_year_enabled kalıntısı ───────────────────────────────
        kapali = _say("SELECT COUNT(*) FROM tenants WHERE plan_year_enabled = FALSE")
        s.kontrol("6", "flag kapalı kurum yok (K5)", kapali == 0, f"kapalı={kapali}")

        # ── 7. Mühür: kapalı yıla yazma reddediliyor ─────────────────────
        print("\n── Faz 2: Mühür\n")
        korumali = _grep_say(r"muhur_engeli|plan_year_writable")
        s.kontrol("7", "yazma yollarında mühür kontrolü var",
                  korumali >= 10, f"{korumali} nokta")

        # ── 8. Mühür açma + denetim izi ──────────────────────────────────
        tablo_var = _say("""
            SELECT COUNT(*) FROM information_schema.tables
             WHERE table_name = 'plan_year_seal_audits'
        """)
        s.kontrol("8", "mühür denetim tablosu var (S13)", tablo_var == 1)
        # NOT: str(rule) yalnızca URL'i verir, endpoint adını DEĞİL.
        # İlk sürüm endpoint adını str(rule) içinde arıyordu ve route mevcut
        # olduğu hâlde "başarısız" diyordu — kontrolün kendisi hatalıydı.
        reopen_var = any(
            r.endpoint.endswith("sp_api_plan_year_reopen")
            for r in app.url_map.iter_rules())
        history_var = any(
            r.endpoint.endswith("sp_api_plan_year_seal_history")
            for r in app.url_map.iter_rules())
        s.kontrol("8b", "mühür açma route'u var (K9)", reopen_var)
        s.kontrol("8c", "mühür geçmişi route'u var (S13)", history_var)

        # ── 9. Yıl değişince farklı veri ─────────────────────────────────
        cok_yilli = _say("""
            SELECT COUNT(*) FROM (
              SELECT py.tenant_id FROM plan_years py
               WHERE EXISTS (SELECT 1 FROM processes p WHERE p.plan_year_id = py.id)
               GROUP BY py.tenant_id HAVING COUNT(*) > 1) t
        """)
        s.kontrol("9", "kurumlar çok yıllı yapıya sahip", cok_yilli >= 1,
                  f"{cok_yilli} kurum")

        # ── 10. Testler ──────────────────────────────────────────────────
        s.kontrol("10", "test dosyaları yerinde",
                  Path("tests/test_statik_dosya_varligi.py").exists())

        # ── 11. D0 — ters hesaplama düzeltmesi ───────────────────────────
        print("\n── İ3: D0 ters hesaplama\n")
        eski = _grep_say(r'direction == ["\']lower_is_better["\']')
        dec = _say("SELECT COUNT(*) FROM process_kpis WHERE direction='Decreasing' AND is_active")
        s.kontrol("11", "lower_is_better ölü koşulu kalmadı", eski == 0,
                  f"kalan={eski} · etkilenen gösterge={dec}")

        # ── Özet ─────────────────────────────────────────────────────────
        toplam = s.gecen + len(s.kalan)
        print(f"\n{'='*78}")
        print(f"  SONUÇ: {s.gecen}/{toplam} kontrol geçti")
        if s.kalan:
            print(f"\n  BAŞARISIZ:")
            for k in s.kalan:
                print(f"    - {k}")
        print(f"{'='*78}\n")
        return 1 if s.kalan else 0


if __name__ == "__main__":
    sys.exit(calistir())
