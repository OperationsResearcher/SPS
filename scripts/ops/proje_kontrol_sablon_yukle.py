# -*- coding: utf-8 -*-
"""Proje kontrol listesi: Excel'den kurum şablonu yükle + mevcut projelere kopyala.

Varsayılan KONTROL modudur (hiçbir şey yazmaz). Yazmak için --calistir.
KURALLAR-MASTER §8: Test/Demo/Yayın DB'sine yazan işlem yalnızca kullanıcı isteyince çalıştırılır.

Kullanım:
    # Şablonu yükle (KONTROL → önce ne yapacağını gösterir)
    python scripts/ops/proje_kontrol_sablon_yukle.py --tenant-id 1 --yil 2026
    python scripts/ops/proje_kontrol_sablon_yukle.py --tenant-id 1 --yil 2026 --calistir

    # Mevcut (maddesi olmayan) projelere şablonu kopyala
    python scripts/ops/proje_kontrol_sablon_yukle.py --tenant-id 1 --mevcut-projelere
    python scripts/ops/proje_kontrol_sablon_yukle.py --tenant-id 1 --mevcut-projelere --calistir

Şablon yüklemede hedef yılın şablonunda zaten aktif madde varsa durur; üzerine yazmak için --degistir.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tenant-id", type=int, required=True)
    ap.add_argument("--yil", type=int, help="Şablon yılı (şablon yüklemede zorunlu)")
    ap.add_argument("--excel", default=str(ROOT / "docs" / "ProjeKontrol.xlsx"))
    ap.add_argument("--degistir", action="store_true", help="Yılın mevcut şablon maddelerinin yerine yaz")
    ap.add_argument("--mevcut-projelere", action="store_true", help="Maddesi olmayan projelere şablonu kopyala")
    ap.add_argument("--calistir", action="store_true", help="Gerçekten yaz (yoksa KONTROL)")
    args = ap.parse_args()

    from app import create_app
    from extensions import db
    from app.models.core import Tenant
    from app.models.portfolio_project import Project
    from app.models.project_checklist import ProjectChecklistItem
    from app.services import project_checklist_service as svc
    from app.services.checklist_excel import parse_workbook

    app = create_app()
    with app.app_context():
        tenant = db.session.get(Tenant, args.tenant_id)
        if not tenant:
            print(f"HATA: tenant {args.tenant_id} yok")
            return 2
        mode = "ÇALIŞTIR" if args.calistir else "KONTROL (yazmaz)"
        print(f"Kurum: {tenant.name} (id={tenant.id}) · mod: {mode}")

        if args.mevcut_projelere:
            projects = Project.query.filter_by(kurum_id=tenant.id, is_active=True, is_archived=False).all()
            todo, total = [], 0
            for p in projects:
                if ProjectChecklistItem.query.filter_by(project_id=p.id).count():
                    continue
                tpl = svc.get_template(tenant.id, svc.project_year(p))
                n = len(svc.template_active_items(tpl)) if tpl and tpl.is_active else 0
                todo.append((p, n))
                total += n
            for p, n in todo:
                print(f"  proje {p.id} «{p.name}» (yıl {svc.project_year(p)}): {n} madde eklenecek")
            print(f"Toplam {len(todo)} proje, {total} madde.")
            if args.calistir:
                for p, n in todo:
                    if n:
                        svc.copy_template_to_project(p)
                db.session.commit()
                print("YAZILDI.")
            return 0

        if not args.yil:
            print("HATA: şablon yüklemek için --yil verin.")
            return 2
        rows = parse_workbook(Path(args.excel).read_bytes())
        stages = []
        for r in rows:
            if r["stage"] not in stages:
                stages.append(r["stage"])
        print(f"Excel: {len(rows)} madde, {len(stages)} aşama: {', '.join(stages)}")
        print(f"Periyotlu madde: {sum(1 for r in rows if r['period_days'])}")
        tpl = svc.get_template(tenant.id, args.yil, create=args.calistir)
        existing = len(svc.template_active_items(tpl)) if tpl else 0
        if existing and not args.degistir:
            print(f"DUR: {args.yil} şablonunda zaten {existing} madde var. Değiştirmek için --degistir.")
            return 1
        if args.calistir:
            svc.template_import(tpl, rows, replace=True)
            db.session.commit()
            print(f"YAZILDI: {args.yil} şablonu · {len(rows)} madde.")
        else:
            print(f"Yazılacak: {args.yil} şablonu · {len(rows)} madde" + (" (mevcut değiştirilecek)" if existing else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
