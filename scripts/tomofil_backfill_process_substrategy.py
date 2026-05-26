"""Tomofil — Process ↔ SubStrategy bağlantı backfill.

Tomofil_Strateji_Agaci.md'den her yaprak madde (örn 1.A.1, 2.C.3) için
süreç kodlarını çıkarır ve `ProcessSubStrategyLink` kayıtları üretir.

Kullanım:
    python scripts/tomofil_backfill_process_substrategy.py            # dry-run
    python scripts/tomofil_backfill_process_substrategy.py --apply
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MD_FILE = ROOT / "docs" / "tomofil" / "Tomofil_Strateji_Agaci.md"
TENANT_ID = 27


def parse_leaves(md_text: str):
    """Yaprak maddeleri ayrıştır.

    Yapı:
        ### │   ├── 1.A.1 Başlık
        - **Süreçler:** `A2R` · `C2L`
    """
    lines = md_text.splitlines()
    re_leaf = re.compile(r"^###\s+[│\s]*[├└]──\s+(\d+\.[A-Z]\.\d+)\s+(.+?)\s*$")
    re_surec = re.compile(r"^-\s+\*\*Süreçler:\*\*\s+(.+)$")

    leaves = []
    current = None
    for line in lines:
        m = re_leaf.match(line)
        if m:
            if current:
                leaves.append(current)
            current = {
                "leaf_code": m.group(1),
                "sub_code": ".".join(m.group(1).split(".")[:2]),  # 1.A.1 → 1.A
                "title": m.group(2).strip(),
                "surec_codes": [],
            }
            continue
        if current:
            m = re_surec.match(line)
            if m:
                codes = re.findall(r"`([A-Z0-9]{3,5})`", m.group(1))
                current["surec_codes"] = codes
    if current:
        leaves.append(current)
    return leaves


def main():
    apply_mode = "--apply" in sys.argv

    text = MD_FILE.read_text(encoding="utf-8")
    leaves = parse_leaves(text)
    leaves_with_proc = [l for l in leaves if l["surec_codes"]]
    print(f"Markdown'dan: {len(leaves)} yaprak madde, {len(leaves_with_proc)} tanesi süreç bağı içeriyor")

    from app import create_app
    from app.extensions import db
    from app.models.core import Strategy, SubStrategy
    from app.models.process import Process, ProcessSubStrategyLink
    from app.models.plan_year import PlanYear

    app = create_app()
    with app.app_context():
        py = PlanYear.query.filter_by(tenant_id=TENANT_ID, status="active").first()
        if not py:
            print("! Aktif plan yılı bulunamadı"); return
        print(f"Aktif plan yılı: {py.year} (id={py.id})")

        # SubStrategy kodu → id
        subs = (
            SubStrategy.query
            .join(Strategy, SubStrategy.strategy_id == Strategy.id)
            .filter(Strategy.tenant_id == TENANT_ID, SubStrategy.plan_year_id == py.id)
            .all()
        )
        sub_by_code = {s.code: s.id for s in subs if s.code}
        print(f"SubStrategy ({py.year}): {len(sub_by_code)}")

        # Process kodu → id (aktif plan yılı + plan_year_id NULL legacy dahil)
        from sqlalchemy import or_
        procs = (
            Process.query
            .filter(Process.tenant_id == TENANT_ID, Process.is_active == True)
            .filter(or_(Process.plan_year_id == py.id, Process.plan_year_id.is_(None)))
            .all()
        )
        # Aynı kodda birden çok proc olabilir (plan_year_id'li ve NULL'lı) — plan_year_id'li öncelikli
        proc_by_code = {}
        for p in procs:
            if not p.code:
                continue
            existing = proc_by_code.get(p.code)
            if existing is None or (existing.plan_year_id is None and p.plan_year_id is not None):
                proc_by_code[p.code] = p
        print(f"Process kodları: {len(proc_by_code)} → {sorted(proc_by_code.keys())}")

        # Şu anki bağlantılar (idempotent için)
        existing_links = set()
        for link in (
            ProcessSubStrategyLink.query
            .join(Process, ProcessSubStrategyLink.process_id == Process.id)
            .filter(Process.tenant_id == TENANT_ID)
            .all()
        ):
            existing_links.add((link.process_id, link.sub_strategy_id))
        print(f"Mevcut bağlantı: {len(existing_links)}")

        # Plan: her yaprak için sub_code çöz, surec_codes çöz, link oluştur
        # contribution_pct: bir sürecin bağlı olduğu alt strateji sayısı N → 100/N
        proposed = []  # (process_id, sub_strategy_id, leaf_code, proc_code)
        unmapped_subs = set()
        unmapped_procs = set()
        for leaf in leaves_with_proc:
            sub_id = sub_by_code.get(leaf["sub_code"])
            if not sub_id:
                unmapped_subs.add(leaf["sub_code"])
                continue
            for pc in leaf["surec_codes"]:
                p = proc_by_code.get(pc)
                if not p:
                    unmapped_procs.add(pc)
                    continue
                proposed.append((p.id, sub_id, leaf["leaf_code"], pc))

        # Tekilleştir (aynı process+sub çifti birden çok yaprakta geçebilir)
        unique_pairs = list({(pi, si): (pi, si, lc, pc) for (pi, si, lc, pc) in proposed}.values())

        # Her process için kaç farklı sub_strategy'e bağlı → contrib_pct hesap
        proc_sub_count = defaultdict(int)
        for pi, si, _, _ in unique_pairs:
            proc_sub_count[pi] += 1

        to_create = []
        for pi, si, lc, pc in unique_pairs:
            if (pi, si) in existing_links:
                continue
            n = proc_sub_count[pi]
            pct = round(100.0 / n, 2) if n > 0 else 100.0
            to_create.append((pi, si, lc, pc, pct))

        print(f"\nÖnerilen yeni bağlantı: {len(to_create)}")
        if unmapped_subs:
            print(f"! SubStrategy bulunamadı (kodlar): {sorted(unmapped_subs)}")
        if unmapped_procs:
            print(f"! Süreç bulunamadı (kodlar): {sorted(unmapped_procs)}")

        if not apply_mode:
            print("\n--- Önizleme (ilk 15) ---")
            for pi, si, lc, pc, pct in to_create[:15]:
                p = next(x for x in procs if x.id == pi)
                s = next(x for x in subs if x.id == si)
                print(f"  [{lc}]  {pc} {p.name[:30]:<32} ↔ {s.code} {s.title[:40]}  ({pct}%)")
            print("\n--apply ile uygula")
            return

        # Apply
        added = 0
        for pi, si, _, _, pct in to_create:
            link = ProcessSubStrategyLink(process_id=pi, sub_strategy_id=si, contribution_pct=pct)
            db.session.add(link)
            added += 1
        db.session.commit()
        print(f"\n✓ {added} bağlantı oluşturuldu.")

        # Doğrulama: K-Vektör tekrar hesapla
        print("\nK-Vektör yeniden hesaplanıyor...")
        from app.services.score_engine_service import compute_vision_score
        bundle = compute_vision_score(TENANT_ID, year=py.year, persist_pg_scores=False, plan_year=py)
        print(f"  vision_score (0-100): {bundle.get('vision_score'):.2f}")
        print(f"  vision_score_1000:    {bundle.get('vision_score_1000'):.2f}")
        ss = bundle.get('strategy_scores') or {}
        non_zero = sum(1 for v in ss.values() if v > 0)
        print(f"  Sıfır olmayan strateji skoru: {non_zero}/{len(ss)}")


if __name__ == "__main__":
    main()
