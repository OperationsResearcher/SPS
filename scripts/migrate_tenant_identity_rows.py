# -*- coding: utf-8 -*-
"""
L1 Dal 3b — Kurumsal kimlik veri taşıma (tek-TEXT → çok-satırlı).

tenants.core_values / code_of_ethics / quality_policy tek-TEXT alanlarını
yeni çok-satırlı tablolara (tenant_values / tenant_ethics_codes /
tenant_quality_policies) madde madde aktarır.

Bölme heuristiği (alanına göre):
  - core_values        → virgülle böl (kısa başlık listesi). aciklama = NULL.
  - code_of_ethics     → cümle bazında böl (nokta). baslik = kırpılmış özet,
  - quality_policy       aciklama = cümlenin tamamı. Böylece tam metin korunur.

İDEMPOTENT: Bir tenant'ın bir alanı için o tabloda ZATEN aktif satır varsa
o alan atlanır. Tekrar çalıştırmak satırları çoğaltmaz.

Karar (2026-06): "temiz kesim" — yeni tablolar canonical; eski TEXT kolonları
DB'de KALIR (okunmaz/yazılmaz). Bu script TEXT'i SİLMEZ.

Kullanım:
    python scripts/migrate_tenant_identity_rows.py            # tüm tenant'lar, uygula
    python scripts/migrate_tenant_identity_rows.py --dry-run  # sadece rapor, yazma
    python scripts/migrate_tenant_identity_rows.py --tenant 27
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from app.models.core import Tenant
from app.models.tenant_identity import (
    TenantValue, TenantEthicsCode, TenantQualityPolicy,
)

BASLIK_MAX = 60  # cümle başlığı kırpma sınırı (kelime sınırında)


def _split_csv(text):
    """Virgülle ayrılmış başlık listesi → [(baslik, None), ...]."""
    parts = [p.strip() for p in (text or "").split(",")]
    return [(p, None) for p in parts if p]


def _split_sentences(text):
    """Paragraf → cümle bazında [(baslik, aciklama_tam), ...].

    Nokta sonrası böler; her cümle bir madde. baslik = kelime sınırında
    kırpılmış özet (uzunsa '…'), aciklama = cümlenin tamamı.
    """
    if not text:
        return []
    # Satır sonlarını boşluğa indir, fazla boşlukları sadeleştir.
    flat = " ".join(text.split())
    sentences = [s.strip() for s in flat.split(".")]
    out = []
    for s in sentences:
        if not s:
            continue
        cumle = s if s.endswith(".") else s + "."
        if len(cumle) <= BASLIK_MAX:
            baslik = cumle.rstrip(".")
        else:
            kirp = cumle[:BASLIK_MAX].rsplit(" ", 1)[0].rstrip(".,;")
            baslik = kirp + " …"
        out.append((baslik, cumle))
    return out


# (alan_adı, Model, böl_fonksiyonu, etiket)
PLAN = [
    ("core_values", TenantValue, _split_csv, "Değer"),
    ("code_of_ethics", TenantEthicsCode, _split_sentences, "Etik"),
    ("quality_policy", TenantQualityPolicy, _split_sentences, "Kalite"),
]


def migrate(tenant_id=None, dry_run=False):
    app = create_app()
    with app.app_context():
        q = Tenant.query
        if tenant_id is not None:
            q = q.filter(Tenant.id == tenant_id)
        tenants = q.all()

        toplam_yazilan = 0
        for t in tenants:
            for field, Model, splitter, etiket in PLAN:
                ham = getattr(t, field, None)
                maddeler = splitter(ham)
                if not maddeler:
                    continue

                mevcut = (
                    Model.query
                    .filter(Model.tenant_id == t.id, Model.is_active.is_(True))
                    .count()
                )
                if mevcut > 0:
                    print(f"  [atla] tenant={t.id} {etiket}: zaten {mevcut} aktif satır")
                    continue

                print(f"  [yaz ] tenant={t.id} {etiket}: {len(maddeler)} madde"
                      + (" (DRY-RUN)" if dry_run else ""))
                if dry_run:
                    for i, (b, a) in enumerate(maddeler):
                        print(f"          {i}. {b!r}" + (f"  / {a!r}" if a else ""))
                    continue

                for i, (baslik, aciklama) in enumerate(maddeler):
                    db.session.add(Model(
                        tenant_id=t.id, baslik=baslik,
                        aciklama=aciklama, sira=i, is_active=True,
                    ))
                    toplam_yazilan += 1

        if dry_run:
            print("\nDRY-RUN: hiçbir şey yazılmadı.")
            db.session.rollback()
        else:
            db.session.commit()
            print(f"\nTamamlandı. Toplam {toplam_yazilan} madde yazıldı.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", type=int, default=None, help="Sadece bu tenant_id")
    ap.add_argument("--dry-run", action="store_true", help="Yazmadan rapor ver")
    args = ap.parse_args()
    sys.exit(migrate(tenant_id=args.tenant, dry_run=args.dry_run))
