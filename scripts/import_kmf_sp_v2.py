# -*- coding: utf-8 -*-
"""Import KMF strategies + processes from belge/SP_V2.xlsx.

What it does (based on agreed rules):
- Target kurum: KMF (default id=2, or resolved by kisa_ad='KMF')
- Processes: upsert from sheet "KMF Süreçler" (main SR* rows only)
  - weight: percent -> 0..1 (e.g. 25 -> 0.25)
  - owners/leaders: derived from "Ana Süreç Sahibi" (grouped per main process)
- Strategies: upsert from sheet "KMF Stratejiler"
  - AnaStrateji: ST1, ST2, ...
  - AltStrateji: ST1.1, ST1.2, ...
  - AltStrateji.aciklama: HEDEF AÇIKLAMASI (+ optional note column)
- Relations:
  - StrategyProcessMatrix: Strong=9, Weak=3 (SR codes parsed from the two columns)
  - Surec.alt_stratejiler M2M also populated for any related SR

Safety:
- Default is dry-run (no DB writes). Use --apply to commit.

Run:
  C:/SPY_Cursor/SP_Code/.venv/Scripts/python.exe scripts/import_kmf_sp_v2.py --dry-run
  C:/SPY_Cursor/SP_Code/.venv/Scripts/python.exe scripts/import_kmf_sp_v2.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from models import AnaStrateji, AltStrateji, Surec, StrategyProcessMatrix, Kurum, User


SR_RE = re.compile(r"SR\d+", re.IGNORECASE)
ST_MAIN_RE = re.compile(r"^ST\d+$", re.IGNORECASE)
ST_SUB_RE = re.compile(r"^ST\d+\.\d+$", re.IGNORECASE)


@dataclass
class ImportStats:
    processes_created: int = 0
    processes_updated: int = 0
    strategies_main_created: int = 0
    strategies_main_updated: int = 0
    strategies_sub_created: int = 0
    strategies_sub_updated: int = 0
    matrix_created: int = 0
    matrix_updated: int = 0
    m2m_links_added: int = 0
    leaders_added: int = 0
    owners_added: int = 0
    warnings: int = 0


def _norm(s: str) -> str:
    s = " ".join(str(s).strip().split())
    s = s.casefold()
    # Normalize Turkish dotless i and remove diacritics for more robust matching
    s = s.replace("ı", "i")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def parse_sr_codes(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    s = str(value)
    return [m.upper() for m in SR_RE.findall(s)]


def resolve_kmf_kurum_id(kurum_id: Optional[int]) -> int:
    if kurum_id is not None:
        return kurum_id
    kmf = Kurum.query.filter(Kurum.kisa_ad.ilike("KMF")).first()
    if not kmf:
        raise SystemExit("KMF kurum not found. Pass --kurum-id explicitly or create kurum with kisa_ad='KMF'.")
    return int(kmf.id)


def find_user_by_fullname(kurum_id: int, fullname: str) -> Optional[User]:
    # Supports "First Last" (single user) and is called per-person.
    parts = [p for p in str(fullname).strip().split() if p]
    if len(parts) < 2:
        return None
    first = _norm(" ".join(parts[:-1]))
    last = _norm(parts[-1])

    # Small user bases: simple scan; avoids DB-specific concat quirks.
    users = User.query.filter_by(kurum_id=kurum_id, silindi=False).all()
    for u in users:
        user_last = _norm(u.last_name or "")
        if user_last != last:
            continue

        user_first = _norm(u.first_name or "")
        # Exact match, or match against tokens to handle titles like "Dr. Ebru"
        if user_first == first:
            return u
        if first in {t for t in user_first.split() if t}:
            return u
    return None


def import_processes(xlsx_path: Path, kurum_id: int, stats: ImportStats) -> dict[str, Surec]:
    df = pd.read_excel(xlsx_path, sheet_name="KMF Süreçler", header=2)

    # Columns we rely on (as observed in the file)
    code_col = "No"
    weight_col = "Ağırlık"
    name_col = "Ana Süreç"
    owner_col = "Ana Süreç Sahibi"

    if code_col not in df.columns or weight_col not in df.columns or name_col not in df.columns:
        raise SystemExit(f"Unexpected 'KMF Süreçler' columns: {list(df.columns)}")

    df[code_col] = df[code_col].astype(str).where(df[code_col].notna(), None)
    df[name_col] = df[name_col].astype(str).where(df[name_col].notna(), None)

    # Identify main process rows where code is SR*
    main_rows = df[df[code_col].notna() & df[code_col].astype(str).str.match(r"^SR\d+$", na=False)]

    processes_by_code: dict[str, Surec] = {}

    # Upsert main processes
    for _, row in main_rows.iterrows():
        code = str(row[code_col]).strip().upper()
        if not code:
            continue
        name = str(row[name_col]).strip() if row[name_col] is not None else code
        weight_raw = row.get(weight_col, None)
        weight = 0.0
        if pd.notna(weight_raw):
            try:
                weight = float(weight_raw) / 100.0
            except Exception:
                weight = 0.0

        existing = Surec.query.filter_by(kurum_id=kurum_id, code=code, silindi=False).first()
        if existing:
            changed = False
            if existing.ad != name:
                existing.ad = name
                changed = True
            if weight is not None and abs((existing.weight or 0.0) - weight) > 1e-9:
                existing.weight = weight
                changed = True
            if changed:
                stats.processes_updated += 1
            processes_by_code[code] = existing
        else:
            p = Surec(kurum_id=kurum_id, code=code, ad=name, weight=weight)
            db.session.add(p)
            db.session.flush()
            processes_by_code[code] = p
            stats.processes_created += 1

    # Owners/leaders: group owner names by main process
    # We need to forward-fill main code over sub-rows, then collect "Ana Süreç Sahibi".
    df_ff = df.copy()
    df_ff[code_col] = df_ff[code_col].where(df_ff[code_col].notna(), None)
    df_ff[code_col] = df_ff[code_col].ffill()

    owners_by_code: dict[str, set[str]] = {}
    if owner_col in df_ff.columns:
        for _, row in df_ff.iterrows():
            code_val = row.get(code_col, None)
            if code_val is None or (isinstance(code_val, float) and pd.isna(code_val)):
                continue
            code = str(code_val).strip().upper()
            if not re.match(r"^SR\d+$", code):
                continue
            owner_cell = row.get(owner_col, None)
            if owner_cell is None or (isinstance(owner_cell, float) and pd.isna(owner_cell)):
                continue
            # Can be comma-separated
            for person in str(owner_cell).split(","):
                person = " ".join(person.strip().split())
                if person:
                    owners_by_code.setdefault(code, set()).add(person)

    for code, people in owners_by_code.items():
        proc = processes_by_code.get(code)
        if not proc:
            continue
        for person in sorted(people):
            user = find_user_by_fullname(kurum_id, person)
            if not user:
                stats.warnings += 1
                print(f"[WARN] User not found for owner/leader '{person}' (process {code}). Skipped.")
                continue

            if user not in proc.liderler:
                proc.liderler.append(user)
                stats.leaders_added += 1
            if user not in proc.owners:
                proc.owners.append(user)
                stats.owners_added += 1

    return processes_by_code


def import_strategies_and_relations(xlsx_path: Path, kurum_id: int, processes_by_code: dict[str, Surec], stats: ImportStats) -> None:
    df = pd.read_excel(xlsx_path, sheet_name="KMF Stratejiler", header=3)

    main_code_col = "No "
    main_text_col = "ANA STRATEJİLER \n(Stratejik Amaçlar)"
    sub_code_col = "No"
    sub_text_col = "ALT STRATEJİLER \n(Stratejik Hedefler)"
    hedef_col = "HEDEF AÇIKLAMASI"
    strong_col = "Güçlü İlişki"
    weak_col = "Zayıf İlişki"
    note_col = "Unnamed: 9"

    for col in [main_code_col, main_text_col, sub_code_col, sub_text_col]:
        if col not in df.columns:
            raise SystemExit(f"Unexpected 'KMF Stratejiler' columns: {list(df.columns)}")

    # Forward-fill main strategy info over sub rows
    df[main_code_col] = df[main_code_col].ffill()
    df[main_text_col] = df[main_text_col].ffill()

    ana_by_code: dict[str, AnaStrateji] = {}

    for _, row in df.iterrows():
        main_code_raw = row.get(main_code_col, None)
        sub_code_raw = row.get(sub_code_col, None)

        main_code = str(main_code_raw).strip().upper() if pd.notna(main_code_raw) else None
        sub_code = str(sub_code_raw).strip().upper() if pd.notna(sub_code_raw) else None

        if not main_code or not ST_MAIN_RE.match(main_code):
            continue

        main_text = row.get(main_text_col, None)
        main_ad = str(main_text).strip() if pd.notna(main_text) else main_code

        ana = ana_by_code.get(main_code)
        if not ana:
            existing = AnaStrateji.query.filter_by(kurum_id=kurum_id, code=main_code).first()
            if existing:
                if existing.ad != main_ad:
                    existing.ad = main_ad
                    stats.strategies_main_updated += 1
                ana = existing
            else:
                ana = AnaStrateji(kurum_id=kurum_id, code=main_code, ad=main_ad)
                db.session.add(ana)
                db.session.flush()
                stats.strategies_main_created += 1
            ana_by_code[main_code] = ana

        if not sub_code or not ST_SUB_RE.match(sub_code):
            continue

        sub_text = row.get(sub_text_col, None)
        sub_ad = str(sub_text).strip() if pd.notna(sub_text) else sub_code

        hedef = row.get(hedef_col, None)
        aciklama_parts: list[str] = []
        if pd.notna(hedef):
            aciklama_parts.append(str(hedef).strip())
        note = row.get(note_col, None)
        if pd.notna(note):
            aciklama_parts.append(str(note).strip())
        aciklama = "\n\n".join([p for p in aciklama_parts if p]) if aciklama_parts else None

        alt = AltStrateji.query.filter_by(ana_strateji_id=ana.id, code=sub_code).first()
        if alt:
            changed = False
            if alt.ad != sub_ad:
                alt.ad = sub_ad
                changed = True
            if (aciklama or None) != (alt.aciklama or None):
                alt.aciklama = aciklama
                changed = True
            if changed:
                stats.strategies_sub_updated += 1
        else:
            alt = AltStrateji(ana_strateji_id=ana.id, code=sub_code, ad=sub_ad, aciklama=aciklama)
            db.session.add(alt)
            db.session.flush()
            stats.strategies_sub_created += 1

        strong = set(parse_sr_codes(row.get(strong_col, None)))
        weak = set(parse_sr_codes(row.get(weak_col, None)))

        # Prefer strong if overlap
        weak -= strong

        def upsert_relation(sr_code: str, score: int) -> None:
            proc = processes_by_code.get(sr_code)
            if not proc:
                # Process sheet might be incomplete; try DB lookup
                proc = Surec.query.filter_by(kurum_id=kurum_id, code=sr_code, silindi=False).first()
                if not proc:
                    stats.warnings += 1
                    print(f"[WARN] Process not found for relation: {sr_code} (sub {sub_code})")
                    return
                processes_by_code[sr_code] = proc

            rel = StrategyProcessMatrix.query.filter_by(sub_strategy_id=alt.id, process_id=proc.id).first()
            if rel:
                if (rel.relationship_score or 0) != score or (rel.relationship_strength or 0) != score:
                    rel.relationship_score = score
                    rel.relationship_strength = score
                    stats.matrix_updated += 1
            else:
                rel = StrategyProcessMatrix(
                    sub_strategy_id=alt.id,
                    process_id=proc.id,
                    relationship_score=score,
                    relationship_strength=score,
                )
                db.session.add(rel)
                stats.matrix_created += 1

            # Also fill M2M
            if alt not in proc.alt_stratejiler:
                proc.alt_stratejiler.append(alt)
                stats.m2m_links_added += 1

        for sr in sorted(strong):
            upsert_relation(sr, 9)
        for sr in sorted(weak):
            upsert_relation(sr, 3)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import KMF strategies/processes from SP_V2.xlsx")
    parser.add_argument(
        "--xlsx",
        default=str(Path(__file__).resolve().parents[1] / "belge" / "SP_V2.xlsx"),
        help="Path to SP_V2.xlsx",
    )
    parser.add_argument("--kurum-id", type=int, default=None, help="Target kurum id (defaults to kisa_ad='KMF')")

    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument("--apply", action="store_true", help="Apply changes (commit)")
    mode.add_argument("--dry-run", action="store_true", help="Dry run (rollback)")

    args = parser.parse_args()

    xlsx_path = Path(args.xlsx)
    if not xlsx_path.exists():
        raise SystemExit(f"Excel not found: {xlsx_path}")

    app = create_app()
    stats = ImportStats()

    with app.app_context():
        kurum_id = resolve_kmf_kurum_id(args.kurum_id)

        try:
            processes_by_code = import_processes(xlsx_path, kurum_id, stats)
            import_strategies_and_relations(xlsx_path, kurum_id, processes_by_code, stats)

            if args.apply and not args.dry_run:
                db.session.commit()
                print("[OK] Import committed.")
            else:
                db.session.rollback()
                print("[OK] Dry-run complete (rolled back). Use --apply to commit.")

        except Exception:
            db.session.rollback()
            raise

    print("\n=== SUMMARY ===")
    print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
