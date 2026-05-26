"""Tomofil strateji ağacını markdown ile reconcile (hard delete + rebuild).

Kanonik kaynak: docs/tomofil/Tomofil_Strateji_Agaci.md
Hedef: tenant_id=27, plan_year 2026

Fazlar:
  1. Snapshot (before)
  2. Markdown parse
  3. Hard delete: mevcut Strategy + SubStrategy (Tomofil 2026)
                  + KVektorWeight kayıtları + ProcessSubStrategyLink + Initiative
  4. Markdown'dan kanonik yapıyı kur (6 Strategy / 18 SubStrategy / 55 Initiative)
  5. 4 eksik Process ekle (F2D, O2C, S2E, W2R)
  6. Process↔SubStrategy bağlarını markdown'a göre kur
  7. ProcessKpi.sub_strategy_id'leri uygun yere taşı (mevcut bağ ad eşleşmesiyle)
  8. K-Vektör recalc + doğrulama
  9. Snapshot (after)
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
LOG_DIR = ROOT / "data" / "tomofil_reconcile"


# ─── Markdown parse ─────────────────────────────────────────────────────────
def parse_markdown():
    text = MD_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()
    re_main = re.compile(r"^# H(\d)\s+[—–-]\s+(.+?)\s*$")
    re_sub = re.compile(r"^##\s+[├└]──\s+(\d+\.[A-Z])\s+(.+?)\s*$")
    re_leaf = re.compile(r"^###\s+[│\s]*[├└]──\s+(\d+\.[A-Z]\.\d+)\s+(.+?)\s*$")
    re_aciklama = re.compile(r"^-\s+\*\*Açıklama:\*\*\s+(.+)$")
    re_surec = re.compile(r"^-\s+\*\*Süreçler:\*\*\s+(.+)$")
    re_kpi = re.compile(r"^-\s+\*\*KPI'lar:\*\*\s+(.+)$")

    strategies = []   # [(code, title)]
    subs = []         # [(parent_code, code, title)]
    leaves = []       # [{code, sub_code, title, aciklama, surec_codes, kpi_text}]
    cur_main = None
    cur_sub = None
    cur_leaf = None

    for line in lines:
        if (m := re_main.match(line)):
            if cur_leaf:
                leaves.append(cur_leaf); cur_leaf = None
            cur_main = f"H{m.group(1)}"
            strategies.append((cur_main, m.group(2).strip()))
        elif (m := re_sub.match(line)):
            if cur_leaf:
                leaves.append(cur_leaf); cur_leaf = None
            cur_sub = m.group(1)
            subs.append((cur_main, cur_sub, m.group(2).strip()))
        elif (m := re_leaf.match(line)):
            if cur_leaf:
                leaves.append(cur_leaf)
            cur_leaf = {
                "code": m.group(1),
                "sub_code": cur_sub,
                "title": m.group(2).strip(),
                "aciklama": "",
                "surec_codes": [],
                "kpi_text": "",
            }
        elif cur_leaf:
            if (m := re_aciklama.match(line)):
                cur_leaf["aciklama"] = m.group(1).strip()
            elif (m := re_surec.match(line)):
                cur_leaf["surec_codes"] = re.findall(r"`([A-Z0-9]{3,5})`", m.group(1))
            elif (m := re_kpi.match(line)):
                cur_leaf["kpi_text"] = m.group(1).strip()
    if cur_leaf:
        leaves.append(cur_leaf)
    return strategies, subs, leaves


# ─── Eksik süreçler ─────────────────────────────────────────────────────────
MISSING_PROCESSES = [
    ("F2D", "Forecast-to-Deliver", "Tahmin-den Teslime",
     "Talep tahmini, üretim planı ve müşteri teslim koordinasyonu."),
    ("O2C", "Order-to-Cash", "Sipariş-ten Tahsilata",
     "Sipariş alımı, sevkiyat, faturalama ve tahsilat süreci."),
    ("S2E", "Strategy-to-Execution", "Strateji-den Uygulamaya",
     "Stratejik kararların operasyonel projelere dökülmesi."),
    ("W2R", "Warehouse-to-Receipt", "Depo-dan Sevke",
     "Mamul depolama, sevkiyat hazırlığı ve teslim onayı."),
]


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    from app import create_app
    from app.extensions import db
    from app.models.core import Strategy, SubStrategy
    from app.models.process import Process, ProcessKpi, ProcessSubStrategyLink
    from app.models.plan_year import PlanYear
    from app.models.k_vektor import KVektorStrategyWeight, KVektorSubStrategyWeight
    from app.models.initiative import Initiative
    from app.models.okr import OkrObjective
    from sqlalchemy import or_

    app = create_app()
    with app.app_context():
        py = PlanYear.query.filter_by(tenant_id=TENANT_ID, status="active").first()
        if not py:
            raise SystemExit("! Tomofil 2026 plan yılı yok")
        print(f"PlanYear: {py.year} (id={py.id})")

        # ── FAZ 1 — SNAPSHOT BEFORE ───────────────────────────────────────
        before_strats = Strategy.query.filter_by(tenant_id=TENANT_ID, plan_year_id=py.id).all()
        before_subs = (SubStrategy.query.join(Strategy)
                       .filter(Strategy.tenant_id == TENANT_ID, SubStrategy.plan_year_id == py.id).all())
        with (LOG_DIR / "snapshot_before.csv").open("w", encoding="utf-8") as f:
            f.write("type,id,code,title,parent_id\n")
            for s in before_strats:
                f.write(f"strategy,{s.id},{s.code},{s.title!r},\n")
            for ss in before_subs:
                f.write(f"substrategy,{ss.id},{ss.code},{ss.title!r},{ss.strategy_id}\n")
        print(f"[1] Snapshot before: {len(before_strats)} strategy / {len(before_subs)} sub")

        # ── FAZ 2 — MARKDOWN PARSE ────────────────────────────────────────
        md_strats, md_subs, md_leaves = parse_markdown()
        print(f"[2] Markdown: {len(md_strats)} ana / {len(md_subs)} alt / {len(md_leaves)} yaprak")

        # ── FAZ 3 — HARD DELETE ───────────────────────────────────────────
        # 3a — Initiative (zaten yok ama olabilir)
        init_del = Initiative.query.filter_by(tenant_id=TENANT_ID).delete(synchronize_session=False)
        # 3b — ProcessSubStrategyLink (cascade ile zaten gidecek ama açık silelim)
        tomofil_proc_ids = [p.id for p in Process.query.filter_by(tenant_id=TENANT_ID).all()]
        psl_del = ProcessSubStrategyLink.query.filter(
            ProcessSubStrategyLink.process_id.in_(tomofil_proc_ids)
        ).delete(synchronize_session=False)
        # 3c — KVektorWeight kayıtları
        kvs_del = KVektorStrategyWeight.query.filter_by(tenant_id=TENANT_ID).delete(synchronize_session=False)
        kvss_del = KVektorSubStrategyWeight.query.filter_by(tenant_id=TENANT_ID).delete(synchronize_session=False)
        # 3d — OkrObjective bağ alanlarını NULL'la (cascade SET NULL zaten var ama emin olalım)
        objs = OkrObjective.query.filter_by(tenant_id=TENANT_ID, plan_year_id=py.id).all()
        for o in objs:
            o.linked_strategy_id = None
            o.linked_sub_strategy_id = None
        # 3e — ProcessKpi.sub_strategy_id NULL'la (FK SET NULL var ama önce manuel temizle)
        pkis = (ProcessKpi.query.join(Process)
                .filter(Process.tenant_id == TENANT_ID).all())
        for pki in pkis:
            pki.sub_strategy_id = None
        db.session.flush()
        # 3f — Strategy + SubStrategy hard delete (cascade SubStrategy'leri de siler)
        tomofil_strat_ids = [s.id for s in Strategy.query.filter_by(tenant_id=TENANT_ID, plan_year_id=py.id).all()]
        sub_del = SubStrategy.query.filter(
            SubStrategy.strategy_id.in_(tomofil_strat_ids),
            SubStrategy.plan_year_id == py.id,
        ).delete(synchronize_session=False)
        strat_del = Strategy.query.filter_by(tenant_id=TENANT_ID, plan_year_id=py.id).delete(synchronize_session=False)
        db.session.commit()
        print(f"[3] Hard delete: {strat_del} strategy + {sub_del} sub + {init_del} init "
              f"+ {psl_del} link + {kvs_del+kvss_del} kv-weight")

        # ── FAZ 4 — REBUILD STRATEGY HİYERARŞİSİ ─────────────────────────
        strat_id_by_code = {}
        for code, title in md_strats:
            s = Strategy(tenant_id=TENANT_ID, code=code, title=title,
                         plan_year_id=py.id, is_active=True)
            db.session.add(s); db.session.flush()
            strat_id_by_code[code] = s.id

        sub_id_by_code = {}
        for parent_code, sub_code, title in md_subs:
            ps_id = strat_id_by_code.get(parent_code)
            if not ps_id:
                continue
            ss = SubStrategy(strategy_id=ps_id, code=sub_code, title=title,
                             plan_year_id=py.id, is_active=True)
            db.session.add(ss); db.session.flush()
            sub_id_by_code[sub_code] = ss.id

        # Initiative
        init_count = 0
        for leaf in md_leaves:
            ps_code = f"H{leaf['code'].split('.')[0]}"
            sub_id = sub_id_by_code.get(leaf["sub_code"])
            i = Initiative(
                tenant_id=TENANT_ID,
                code=leaf["code"],
                name=leaf["title"],
                description=leaf["aciklama"] or None,
                strategy_id=strat_id_by_code.get(ps_code),
                sub_strategy_id=sub_id,
                start_year=2026, end_year=2030,
                status="planned", priority="high",
                is_active=True,
            )
            db.session.add(i); init_count += 1
        db.session.commit()
        print(f"[4] Rebuild: {len(strat_id_by_code)} strategy / {len(sub_id_by_code)} sub / {init_count} init")

        # ── FAZ 5 — EKSİK 4 SÜREÇ ─────────────────────────────────────────
        proc_added = 0
        existing_codes = {p.code for p in Process.query.filter(
            Process.tenant_id == TENANT_ID, Process.is_active == True,
            or_(Process.plan_year_id == py.id, Process.plan_year_id.is_(None))
        ).all() if p.code}
        for code, eng, tr, desc in MISSING_PROCESSES:
            if code in existing_codes:
                continue
            p = Process(tenant_id=TENANT_ID, code=code, name=tr, english_name=eng,
                        description=desc, plan_year_id=py.id, status="Aktif", is_active=True)
            db.session.add(p); proc_added += 1
        db.session.commit()
        print(f"[5] Eksik süreç eklendi: {proc_added}")

        # ── FAZ 6 — PROCESS↔SUBSTRATEGY BAĞLARI ──────────────────────────
        # Proc by code
        procs = Process.query.filter(
            Process.tenant_id == TENANT_ID, Process.is_active == True,
            or_(Process.plan_year_id == py.id, Process.plan_year_id.is_(None))
        ).all()
        proc_by_code = {}
        for p in procs:
            if not p.code:
                continue
            ex = proc_by_code.get(p.code)
            if ex is None or (ex.plan_year_id is None and p.plan_year_id is not None):
                proc_by_code[p.code] = p

        # Her yaprak için sub_code çöz, surec_codes çöz, link önerisi üret
        pairs = set()  # (proc_id, sub_id)
        for leaf in md_leaves:
            sub_id = sub_id_by_code.get(leaf["sub_code"])
            if not sub_id:
                continue
            for pc in leaf["surec_codes"]:
                p = proc_by_code.get(pc)
                if not p:
                    continue
                pairs.add((p.id, sub_id))

        # contribution_pct: her süreç için bağlı sub sayısına göre
        proc_sub_count = defaultdict(int)
        for pi, si in pairs:
            proc_sub_count[pi] += 1
        for pi, si in pairs:
            n = proc_sub_count[pi]
            pct = round(100.0 / n, 2) if n > 0 else 100.0
            db.session.add(ProcessSubStrategyLink(
                process_id=pi, sub_strategy_id=si, contribution_pct=pct
            ))
        db.session.commit()
        print(f"[6] Process↔SubStrategy bağı: {len(pairs)}")

        # ── FAZ 7 — DOĞRULAMA ────────────────────────────────────────────
        after_strats = Strategy.query.filter_by(tenant_id=TENANT_ID, plan_year_id=py.id).all()
        after_subs = (SubStrategy.query.join(Strategy)
                      .filter(Strategy.tenant_id == TENANT_ID, SubStrategy.plan_year_id == py.id).all())
        after_inits = Initiative.query.filter_by(tenant_id=TENANT_ID).all()

        # Yetim kontrol
        sub_ids_set = {s.id for s in after_subs}
        orphan_subs = [s for s in after_subs if s.strategy_id not in {x.id for x in after_strats}]
        psl_count = (db.session.query(ProcessSubStrategyLink)
                     .join(Process, ProcessSubStrategyLink.process_id == Process.id)
                     .filter(Process.tenant_id == TENANT_ID).count())
        linked_proc_ids = {pi for pi, _ in pairs}
        orphan_procs = [p for p in proc_by_code.values() if p.id not in linked_proc_ids]

        # K-Vektör
        from app.services.score_engine_service import compute_vision_score
        bundle = compute_vision_score(TENANT_ID, year=py.year, persist_pg_scores=False, plan_year=py)
        v100 = bundle.get("vision_score") or 0.0
        v1000 = bundle.get("vision_score_1000") or 0.0
        ss = bundle.get("strategy_scores") or {}
        non_zero = sum(1 for v in ss.values() if v > 0)

        print("\n" + "─" * 60)
        print(f"DOĞRULAMA")
        print("─" * 60)
        print(f"  Strategy   : {len(after_strats)}  (markdown: {len(md_strats)})")
        print(f"  SubStrategy: {len(after_subs)}  (markdown: {len(md_subs)})")
        print(f"  Initiative : {len(after_inits)}  (markdown: {len(md_leaves)})")
        print(f"  Process(uniq code): {len(proc_by_code)}")
        print(f"  Process↔Sub bağı  : {psl_count}")
        print(f"  Yetim alt strateji: {len(orphan_subs)}")
        print(f"  Yetim süreç       : {len(orphan_procs)}")
        print(f"  K-Vektör vision   : {v100:.2f} / 100  (= {v1000:.1f} / 1000)")
        print(f"  Strateji skoru non-zero: {non_zero}/{len(ss)}")
        print("─" * 60)

        # Snapshot after
        with (LOG_DIR / "snapshot_after.csv").open("w", encoding="utf-8") as f:
            f.write("type,id,code,title,parent_id\n")
            for s in after_strats:
                f.write(f"strategy,{s.id},{s.code},{s.title!r},\n")
            for ss_ in after_subs:
                f.write(f"substrategy,{ss_.id},{ss_.code},{ss_.title!r},{ss_.strategy_id}\n")
            for i in after_inits:
                f.write(f"initiative,{i.id},{i.code},{i.name!r},{i.sub_strategy_id}\n")
        print(f"\nSnapshot: {LOG_DIR}/snapshot_before.csv + snapshot_after.csv")


if __name__ == "__main__":
    main()
