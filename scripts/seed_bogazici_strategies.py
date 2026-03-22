# -*- coding: utf-8 -*-
"""
Boğaziçi Üniversitesi — Stratejik Planlama (Ana / Alt Strateji) tohum verisi.

Kullanım (proje kökünden):
  py scripts/seed_bogazici_strategies.py
  py scripts/seed_bogazici_strategies.py --tenant-id 3
  py scripts/seed_bogazici_strategies.py --tenant-name "Boğaziçi Üniversitesi"
  py scripts/seed_bogazici_strategies.py --replace   # mevcut aktif stratejileri pasifleştirip yeniden yazar

  py scripts/seed_bogazici_strategies.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys

# Proje kökü
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app import create_app
from app.models import db
from app.models.core import Strategy, SubStrategy, Tenant

# ── Kaynak: Kurumsal strateji tablosu (SA = ana, H = alt) ────────────────────
BOGAZICI_DATA: list[dict] = [
    {
        "code": "SA1",
        "title": (
            "Evrensel, kapsayıcı, yenilikçi ve sürdürülebilir yaklaşımlar benimseyerek "
            "eğitim ve öğretim deneyimini zenginleştirmek."
        ),
        "description": None,
        "subs": [
            ("H1.1", "İletişimi, iş birliğini, eleştirel düşünmeyi ve yaratıcılığı teşvik eden kapsayıcı eğitim ve öğretim ortamları geliştirmek."),
            ("H1.2", "Geleneksel eğitim yöntemlerinin yanı sıra teknoloji destekli, etkileşimli ve deneyime dayalı eğitim yöntemlerinin kullanımını artırmak."),
            ("H1.3", "Öğrenci ve öğretim elemanı hareketliliğini ve kurumlar arası iş birliğini artırmak."),
            ("H1.4", "Ulusal/uluslararası akredite program sayısını artırmak."),
            ("H1.5", "Eğitim, öğretim, insan kaynağı ve fiziksel/dijital alt yapısını geliştirmek."),
        ],
    },
    {
        "code": "SA2",
        "title": "Öncü araştırma faaliyetleri yürüterek nitelikli bilgi ve yenilikçi teknoloji üretmek.",
        "description": None,
        "subs": [
            ("H2.1", "Ulusal ve uluslararası iş birliği ve proje sayısını artırmak."),
            ("H2.2", "Araştırma ve geliştirmeye yönelik fiziksel altyapıları geliştirmek ve güçlendirmek."),
            ("H2.3", "Boğaziçi üniversitesi adresli nitelikli araştırma, yayın ve bilimsel etkinliklerin sayısını artırmak."),
            ("H2.4", "Araştırma ve geliştirme faaliyetlerini destekleyici insan kaynaklarını artırmak."),
            ("H2.5", "Üniversite-Sanayi iş birliğini artırmak."),
        ],
    },
    {
        "code": "SA3",
        "title": "Girişimcilik ekosistemini güçlendirmek ve sürdürülebilirliğini sağlamak.",
        "description": None,
        "subs": [
            ("H3.1", "Girişimciliğin sürdürülebilirliğini sağlamak."),
            ("H3.2", "Boğaziçi Üniversitesi bünyesinde yeni girişimcilik merkezlerinin ve inkübatörlerin (kuluçka merkezleri) kurulması ve olanların geliştirilmesi."),
            (
                "H3.3",
                "Girişimcilik ile ilgilenen lisans öğrencilerinin temel muhasebe, finans, pazarlama, strateji ve ticaret hukuku derslerini seçmeli ders olarak alabilecekleri bir sertifika programı oluşturmak.",
            ),
        ],
    },
    {
        "code": "SA4",
        "title": "Sürekli iyileştirme ilkesi doğrultusunda kurumsal kapasiteyi güçlendirmek.",
        "description": None,
        "subs": [
            ("H4.1", "Kurum içi ve kurum dışı iletişimi ve iş birliğini geliştirmek."),
            ("H4.2", "Personelin mesleki ve kişisel gelişimini desteklemek."),
            ("H4.3", "Bilgi sistemlerine güçlü bir siber güvenlik stratejisi oluşturmak."),
            ("H4.4", "Kampüs yaşamını desteklemek için fiziksel alt yapıyı artırmak ve geliştirmek."),
            ("H4.5", "İdari süreçlerin dijitalleştirilmesi ve verimliliğin artırılması."),
        ],
    },
    {
        "code": "SA5",
        "title": (
            "Sosyal sorumluluk faaliyetlerini ve iş birliklerini güçlendirerek sürdürülebilir "
            "toplumsal refaha katkıda bulunmak."
        ),
        "description": None,
        "subs": [
            (
                "H5.1",
                "Toplumsal sorunlara yönelik yenilikçi çözümlerin geliştirilmesini teşvik etmek amacıyla öğrenci, akademisyenler ve diğer paydaşlar arasında iş birliği platformlarının oluşturulması.",
            ),
            (
                "H5.2",
                "Toplumsal farkındalığı artırmak için sürdürülebilir kalkınma hedefleri ve çevre koruma gibi konularla ilgili etkinliklerin düzenlenmesi.",
            ),
        ],
    },
]


def _truncate_field(text: str | None, max_len: int = 200) -> tuple[str, str | None]:
    """title alanı 200 karakter; taşanı description'a tam metin olarak yaz."""
    if not text:
        return "", None
    t = text.strip()
    if len(t) <= max_len:
        return t, None
    return t[:max_len].rstrip(), t


def find_tenant(name_query: str | None, tenant_id: int | None) -> Tenant | None:
    if tenant_id is not None:
        return Tenant.query.filter_by(id=tenant_id, is_active=True).first()
    q = (name_query or "").strip()
    if q:
        return Tenant.query.filter(Tenant.name.ilike(f"%{q}%")).first()
    return (
        Tenant.query.filter(
            or_(
                Tenant.name.ilike("%boğaziçi%"),
                Tenant.name.ilike("%bogazici%"),
                Tenant.short_name.ilike("%boun%"),
            )
        ).first()
    )


def soft_delete_tenant_strategies(tenant_id: int) -> int:
    strategies = (
        Strategy.query.options(selectinload(Strategy.sub_strategies))
        .filter_by(tenant_id=tenant_id, is_active=True)
        .all()
    )
    n = 0
    for st in strategies:
        st.is_active = False
        n += 1
        for ss in st.sub_strategies:
            if ss.is_active:
                ss.is_active = False
    return n


def seed(tenant: Tenant, replace: bool, dry_run: bool) -> None:
    tid = tenant.id
    print(f"Kurum: id={tid} | {tenant.name!r}")

    existing = Strategy.query.filter_by(tenant_id=tid, is_active=True).count()
    print(f"Mevcut aktif ana strateji sayısı: {existing}")

    if dry_run:
        print("[dry-run] Veri yazılmadı.")
        if existing and not replace:
            print("Not: Aktif strateji var; gerçek çalıştırmada --replace gerekir veya önce manuel silin.")
        for block in BOGAZICI_DATA:
            print(f"  {block['code']}: {block['title'][:60]}...")
            for code, tit in block["subs"]:
                print(f"    {code}: {tit[:50]}...")
        return

    if existing and not replace:
        print("Çıkılıyor: Bu kurumda zaten aktif strateji var. Üzerine yazmak için --replace kullanın.")
        sys.exit(1)

    if replace and existing:
        removed = soft_delete_tenant_strategies(tid)
        db.session.commit()
        print(f"Pasifleştirilen ana strateji kaydı: {removed}")

    for block in BOGAZICI_DATA:
        title, desc_overflow = _truncate_field(block["title"], 200)
        if not title:
            continue
        desc = block.get("description") or desc_overflow

        main = Strategy(
            tenant_id=tid,
            code=block["code"],
            title=title,
            description=desc,
            is_active=True,
        )
        db.session.add(main)
        db.session.flush()

        for sub_code, sub_title_full in block["subs"]:
            stitle, sub_desc_overflow = _truncate_field(sub_title_full, 200)
            sub = SubStrategy(
                strategy_id=main.id,
                code=sub_code,
                title=stitle,
                description=sub_desc_overflow,
                is_active=True,
            )
            db.session.add(sub)

    db.session.commit()
    print("Tamamlandı: 5 ana strateji ve alt stratejiler eklendi.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Boğaziçi Üniversitesi strateji tohumu")
    parser.add_argument("--tenant-id", type=int, default=None)
    parser.add_argument("--tenant-name", type=str, default=None, help="Kurum adında arama (içerir)")
    parser.add_argument("--replace", action="store_true", help="Mevcut aktif stratejileri pasifleştirip ekle")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        tenant = find_tenant(args.tenant_name, args.tenant_id)
        if not tenant:
            print(
                "Hata: Kurum bulunamadı. --tenant-id veya --tenant-name ile deneyin.\n"
                "Örnek: py scripts/seed_bogazici_strategies.py --tenant-name Üniversite"
            )
            sys.exit(2)
        seed(tenant, replace=args.replace, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
