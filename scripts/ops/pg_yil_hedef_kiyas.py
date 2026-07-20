# -*- coding: utf-8 -*-
"""
PG yıl bazlı hedef kıyas raporu — SALT OKUNUR.

Bir tenant'ta plan yılı sistemi açıkken, her (PG × plan yılı) hücresi için
hedefin fiilen nereden geldiğini çıkarır:

  CONFIG    → kpi_year_configs.target_value dolu (yıl bazlı hedef gerçekten var)
  SNAPSHOT  → config yok, ama o yıl kpi_data.target_value girilmiş (geçmiş kurtarılabilir)
  FALLBACK  → config de snapshot da yok → ProcessKpi.target_value'ya düşüyor (yılsız)
  YOK       → hiçbir kaynakta hedef yok

CAKISMA satırları ayrıca işaretlenir: snapshot ile temel hedef farklı, yani
temel hedef bir noktada ezilmiş ve geçmiş yılın gerçek hedefi yalnızca
kpi_data içinde kalmış.

Kullanım (Yayın konteyneri içinde):
    python scripts/ops/pg_yil_hedef_kiyas.py --tenant 16
    python scripts/ops/pg_yil_hedef_kiyas.py --tenant 16 --csv /tmp/kmf_kiyas.csv

Hiçbir yazma yapmaz. UPDATE/INSERT/DELETE içermez.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


def _repo_root() -> Path:
    script = Path(__file__).resolve()
    for d in [script.parent, *script.parents]:
        if (d / "run.py").exists():
            return d
    if (Path("/app") / "run.py").exists():
        return Path("/app")
    raise RuntimeError("run.py bulunamadi (repo veya /app bekleniyor).")


ROOT = _repo_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import text  # noqa: E402

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402


def _norm(value) -> str:
    """Hedefi kıyas için normalize eder. Serbest metin ('50-59', '-') korunur."""
    if value is None:
        return ""
    return str(value).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", type=int, required=True, help="Tenant id")
    ap.add_argument("--csv", type=str, default=None, help="CSV çıktı yolu (opsiyonel)")
    args = ap.parse_args()
    tid = args.tenant

    app = create_app()
    with app.app_context():
        tenant = db.session.execute(
            text("SELECT id, name, plan_year_enabled FROM tenants WHERE id = :t"),
            {"t": tid},
        ).mappings().first()
        if not tenant:
            print(f"HATA: tenant {tid} bulunamadi.", file=sys.stderr)
            return 1

        years = db.session.execute(
            text(
                "SELECT id, year, status FROM plan_years "
                "WHERE tenant_id = :t ORDER BY year"
            ),
            {"t": tid},
        ).mappings().all()

        kpis = db.session.execute(
            text(
                "SELECT k.id, k.name AS pg, k.target_value AS temel, k.unit, "
                "       k.period, p.name AS surec "
                "FROM process_kpis k "
                "JOIN processes p ON p.id = k.process_id "
                "WHERE p.tenant_id = :t AND k.is_active "
                "ORDER BY p.name, k.name"
            ),
            {"t": tid},
        ).mappings().all()

        # config: (plan_year_id, kpi_id) -> target_value
        cfg_rows = db.session.execute(
            text(
                "SELECT kyc.plan_year_id, kyc.process_kpi_id, "
                "       kyc.target_value, kyc.is_included "
                "FROM kpi_year_configs kyc "
                "JOIN plan_years py ON py.id = kyc.plan_year_id "
                "WHERE py.tenant_id = :t"
            ),
            {"t": tid},
        ).mappings().all()
        cfg = {(r["plan_year_id"], r["process_kpi_id"]): r for r in cfg_rows}

        # snapshot: (year, kpi_id) -> ilk dolu target_value
        snap_rows = db.session.execute(
            text(
                "SELECT kd.process_kpi_id, kd.year, kd.target_value, "
                "       count(*) AS satir "
                "FROM kpi_data kd "
                "JOIN process_kpis k ON k.id = kd.process_kpi_id "
                "JOIN processes p ON p.id = k.process_id "
                "WHERE p.tenant_id = :t AND kd.target_value IS NOT NULL "
                "  AND kd.target_value <> '' "
                "GROUP BY kd.process_kpi_id, kd.year, kd.target_value"
            ),
            {"t": tid},
        ).mappings().all()
        snap: dict[tuple[int, int], set[str]] = {}
        for r in snap_rows:
            snap.setdefault((r["year"], r["process_kpi_id"]), set()).add(
                _norm(r["target_value"])
            )

        out_rows = []
        durum_sayaci: Counter[str] = Counter()
        cakisma = []

        for k in kpis:
            temel = _norm(k["temel"])
            for y in years:
                key_cfg = (y["id"], k["id"])
                key_snap = (y["year"], k["id"])
                c = cfg.get(key_cfg)
                c_target = _norm(c["target_value"]) if c else ""
                s_targets = snap.get(key_snap, set())
                s_target = sorted(s_targets)[0] if s_targets else ""

                if c_target:
                    durum = "CONFIG"
                    etkin = c_target
                elif s_target:
                    durum = "SNAPSHOT"
                    etkin = s_target
                elif temel:
                    durum = "FALLBACK"
                    etkin = temel
                else:
                    durum = "YOK"
                    etkin = ""

                durum_sayaci[durum] += 1

                # Çakışma: snapshot var ve temel hedeften farklı
                catisma_var = bool(s_target and temel and s_target != temel)
                if catisma_var:
                    cakisma.append(
                        {
                            "yil": y["year"],
                            "kpi_id": k["id"],
                            "pg": k["pg"],
                            "snapshot": s_target,
                            "temel": temel,
                        }
                    )

                out_rows.append(
                    {
                        "tenant_id": tid,
                        "yil": y["year"],
                        "yil_durum": y["status"],
                        "surec": k["surec"],
                        "kpi_id": k["id"],
                        "pg": k["pg"],
                        "durum": durum,
                        "etkin_hedef": etkin,
                        "config_hedef": c_target,
                        "snapshot_hedef": s_target,
                        "temel_hedef": temel,
                        "cakisma": "EVET" if catisma_var else "",
                        "config_var": "EVET" if c else "",
                        "is_included": ""
                        if not c
                        else ("EVET" if c["is_included"] else "HAYIR"),
                        "birim": k["unit"] or "",
                        "periyot": k["period"] or "",
                    }
                )

        # ---- Rapor ----
        print("=" * 72)
        print(f"PG YIL BAZLI HEDEF KIYAS RAPORU  (SALT OKUNUR)")
        print("=" * 72)
        print(f"Kurum          : [{tenant['id']}] {tenant['name']}")
        print(f"plan_year_enabled : {tenant['plan_year_enabled']}")
        print(f"Aktif PG       : {len(kpis)}")
        print(f"Plan yili      : {len(years)}  "
              f"({', '.join(str(y['year']) for y in years)})")
        print(f"Toplam hucre   : {len(out_rows)}  (PG x yil)")
        print()

        print("--- Hedef kaynagi dagilimi ---")
        toplam = max(len(out_rows), 1)
        for durum in ("CONFIG", "SNAPSHOT", "FALLBACK", "YOK"):
            n = durum_sayaci.get(durum, 0)
            print(f"  {durum:<9} {n:>6}  ({100.0 * n / toplam:5.1f}%)")
        print()

        print("--- Yil bazinda config kapsami ---")
        for y in years:
            dolu = sum(
                1
                for k in kpis
                if _norm((cfg.get((y["id"], k["id"])) or {}).get("target_value"))
            )
            print(
                f"  {y['year']} ({y['status']:<7}) : "
                f"{dolu:>4}/{len(kpis)} PG'de yil bazli hedef var"
            )
        print()

        print(f"--- Cakisma (snapshot != temel hedef) : {len(cakisma)} satir ---")
        if cakisma:
            print("  Bu satirlarda gecmis yilin gercek hedefi YALNIZCA kpi_data'da.")
            print("  Temel hedef sonradan ezilmis demektir.")
            for c in cakisma[:25]:
                print(
                    f"  {c['yil']}  PG#{c['kpi_id']:<5} "
                    f"snapshot={c['snapshot']!r:<12} temel={c['temel']!r:<12} "
                    f"{c['pg'][:42]}"
                )
            if len(cakisma) > 25:
                print(f"  ... +{len(cakisma) - 25} satir daha (CSV'ye bakin)")
        else:
            print("  Cakisma yok.")
        print()

        # Hedef format dagilimi — serbest metin riski
        print("--- Temel hedef format dagilimi ---")
        fmt: Counter[str] = Counter()
        for k in kpis:
            t = _norm(k["temel"])
            if not t:
                fmt["bos"] += 1
            elif t in ("-", "—"):
                fmt["tire (-)"] += 1
            elif "-" in t:
                fmt["aralik (50-59)"] += 1
            else:
                try:
                    float(t.replace(",", "."))
                    fmt["sayi"] += 1
                except ValueError:
                    fmt["diger metin"] += 1
        for key, n in fmt.most_common():
            print(f"  {key:<18} {n:>4}")
        print()

        if args.csv:
            csv_path = Path(args.csv)
            with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
                w.writeheader()
                w.writerows(out_rows)
            print(f"CSV yazildi: {csv_path}  ({len(out_rows)} satir)")

        print()
        print("Not: Bu script hicbir yazma yapmaz.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
