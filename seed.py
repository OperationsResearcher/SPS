"""Database seeding script - reads from docs/Modülleşme_V2.xlsx only. No dummy data."""

import os
import re
import sys

import pandas as pd
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.core import Role, Tenant, User
from app.models.saas import (
    ModuleComponentSlug,
    SystemComponent,
    SystemModule,
    SubscriptionPackage,
)

# Excel'den gelen bu bileşenler artık kullanılmıyor (SWOT özelliği kaldırıldı).
SKIP_COMPONENT_SLUGS = frozenset({"swot_analizi", "swot_analysis"})

# Turkish to English mapping for common terms
TURKISH_TO_ENGLISH = {
    "analizi": "analysis",
    "analiz": "analysis",
    "kartı": "card",
    "kart": "card",
    "vizyon": "vision",
    "misyon": "mission",
    "güç": "force",
    "guc": "force",
    "stratejik": "strategic",
    "kurumsal": "corporate",
    "kimlik": "identity",
    "süreç": "process",
    "surec": "process",
}


def turkish_to_slug(name: str) -> str:
    """Türkçe bileşen/modül adını URL kodu (slug) formatına çevirir."""
    if not name or not isinstance(name, str):
        return ""
    tr_map = {
        "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i",
        "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
    }
    s = str(name).strip()
    for tr, en in tr_map.items():
        s = s.replace(tr, en)
    s = s.lower()
    s = re.sub(r"[^\w]+", "_", s)
    s = s.strip("_")
    for tr_word, en_word in TURKISH_TO_ENGLISH.items():
        s = re.sub(rf"\b{re.escape(tr_word)}\b", en_word, s)
    return s


def main():
    excel_path = os.path.join(os.path.dirname(__file__), "docs", "Modülleşme_V2.xlsx")
    if not os.path.exists(excel_path):
        print(f"ERROR: Excel file not found: {excel_path}")
        sys.exit(1)

    app = create_app()
    with app.app_context():
        df_all = pd.read_excel(excel_path, sheet_name=None)

        # Step 1: Bileşenler
        print("Seeding components...")
        df_comp = df_all.get("Bileşenler")
        if df_comp is None:
            print("ERROR: Sheet 'Bileşenler' not found in Excel.")
            sys.exit(1)
        name_col = "Bileşen" if "Bileşen" in df_comp.columns else df_comp.columns[0]
        for _, row in df_comp.iterrows():
            name = row.get(name_col)
            if pd.isna(name) or not str(name).strip():
                continue
            name = str(name).strip()
            code = turkish_to_slug(name)
            if not code or code in SKIP_COMPONENT_SLUGS:
                continue
            if SystemComponent.query.filter_by(code=code).first():
                continue
            comp = SystemComponent(name=name, code=code, is_active=True)
            db.session.add(comp)
        db.session.commit()
        count_comp = SystemComponent.query.count()
        print(f"Components seeded: {count_comp}")

        # Step 2: Modüller + module_component_slugs (bileşen = Bileşen İsmi / component_slug)
        print("Seeding modules...")
        df_mod = df_all.get("Modüller")
        if df_mod is None:
            print("ERROR: Sheet 'Modüller' not found in Excel.")
            sys.exit(1)
        component_name_to_slug = {c.name: c.code for c in SystemComponent.query.all()}
        mod_name_col = "Modül" if "Modül" in df_mod.columns else df_mod.columns[0]

        for _, row in df_mod.iterrows():
            mod_name = row.get(mod_name_col)
            if pd.isna(mod_name) or not str(mod_name).strip():
                continue
            mod_name = str(mod_name).strip()
            mod_code = turkish_to_slug(mod_name)
            if not mod_code:
                continue
            module = SystemModule.query.filter_by(code=mod_code).first()
            if not module:
                module = SystemModule(name=mod_name, code=mod_code, is_active=True)
                db.session.add(module)
                db.session.flush()

            for col in df_mod.columns:
                if col == mod_name_col:
                    continue
                val = row.get(col)
                if pd.isna(val):
                    continue
                if str(val).strip().lower() == "evet":
                    slug = component_name_to_slug.get(col) or turkish_to_slug(col)
                    if slug in SKIP_COMPONENT_SLUGS:
                        continue
                    if slug and not ModuleComponentSlug.query.filter_by(module_id=module.id, component_slug=slug).first():
                        db.session.add(ModuleComponentSlug(module_id=module.id, component_slug=slug))

        db.session.commit()
        count_mod = SystemModule.query.count()
        print(f"Modules seeded: {count_mod}")

        # Step 3: Paketler + package_modules
        print("Seeding packages...")
        df_pkg = df_all.get("Paketler")
        if df_pkg is None:
            print("ERROR: Sheet 'Paketler' not found in Excel.")
            sys.exit(1)
        module_map = {m.name: m for m in SystemModule.query.all()}
        pkg_name_col = "Paket" if "Paket" in df_pkg.columns else df_pkg.columns[0]

        for _, row in df_pkg.iterrows():
            pkg_name = row.get(pkg_name_col)
            if pd.isna(pkg_name) or not str(pkg_name).strip():
                continue
            pkg_name = str(pkg_name).strip()
            pkg_code = turkish_to_slug(pkg_name)
            if not pkg_code:
                continue
            pkg = SubscriptionPackage.query.filter_by(code=pkg_code).first()
            if not pkg:
                pkg = SubscriptionPackage(name=pkg_name, code=pkg_code, is_active=True)
                db.session.add(pkg)
                db.session.flush()

            for col in df_pkg.columns:
                if col == pkg_name_col:
                    continue
                val = row.get(col)
                if pd.isna(val):
                    continue
                if str(val).strip().lower() == "evet":
                    mod = module_map.get(col)
                    if mod and mod not in pkg.modules:
                        pkg.modules.append(mod)

        db.session.commit()
        count_pkg = SubscriptionPackage.query.count()
        print(f"Packages seeded: {count_pkg}")

        # Step 3b: Ensure dinamik_stratejik_planlama component slug exists
        slug_name = "dinamik_stratejik_planlama"
        target_mod = None
        for m in SystemModule.query.all():
            slugs = [mcs.component_slug for mcs in m.component_slugs]
            if slug_name in slugs:
                target_mod = m
                break
        if not target_mod:
            for code in ("stratejik_planlama", "stratejik_yonetim", "strategic_planning"):
                target_mod = SystemModule.query.filter_by(code=code).first()
                if target_mod:
                    break
        if not target_mod:
            target_mod = SystemModule.query.order_by(SystemModule.id).first()
        if target_mod and not ModuleComponentSlug.query.filter_by(module_id=target_mod.id, component_slug=slug_name).first():
            db.session.add(ModuleComponentSlug(module_id=target_mod.id, component_slug=slug_name))
            db.session.commit()
            print(f"Added component_slug '{slug_name}' to module {target_mod.name}")
        master_pre = SubscriptionPackage.query.filter_by(code="master_package").first()
        if master_pre and target_mod and not any(m.id == target_mod.id for m in master_pre.modules):
            master_pre.modules.append(target_mod)
            db.session.commit()
            print(f"Added module {target_mod.name} to Master Package")

        # Step 4: Roles, master package, tenant and admin user
        print("Seeding roles, master package, tenant and admin user...")
        for role_name in ("Admin", "User", "tenant_admin", "executive_manager", "standard_user"):
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name, description=f"{role_name} role"))
        db.session.commit()

        master = SubscriptionPackage.query.filter_by(code="master_package").first()
        if not master:
            master = SubscriptionPackage(
                name="Master Package",
                code="master_package",
                description="Contains all modules",
                is_active=True,
            )
            db.session.add(master)
            db.session.flush()
            for mod in SystemModule.query.all():
                master.modules.append(mod)
            db.session.commit()

        default_tenant = Tenant.query.filter_by(short_name="default_corp").first()
        if not default_tenant:
            default_tenant = Tenant(
                name="Default Corp",
                short_name="default_corp",
                is_active=True,
                package_id=master.id,
            )
            db.session.add(default_tenant)
            db.session.commit()

        admin_role = Role.query.filter_by(name="Admin").first()
        tenant_admin_role = Role.query.filter_by(name="tenant_admin").first()
        exec_role = Role.query.filter_by(name="executive_manager").first()
        if not User.query.filter_by(email="admin@kokpitim.com").first():
            admin_user = User(
                email="admin@kokpitim.com",
                password_hash=generate_password_hash("123456"),
                first_name="Admin",
                last_name="User",
                is_active=True,
                tenant_id=default_tenant.id,
                role_id=admin_role.id if admin_role else None,
            )
            db.session.add(admin_user)
        if not User.query.filter_by(email="yonetici@kokpitim.com").first():
            tenant_admin_user = User(
                email="yonetici@kokpitim.com",
                password_hash=generate_password_hash("123456"),
                first_name="Kurum",
                last_name="Yöneticisi",
                is_active=True,
                tenant_id=default_tenant.id,
                role_id=tenant_admin_role.id if tenant_admin_role else None,
            )
            db.session.add(tenant_admin_user)
        if not User.query.filter_by(email="ustyonetim@kokpitim.com").first():
            exec_user = User(
                email="ustyonetim@kokpitim.com",
                password_hash=generate_password_hash("123456"),
                first_name="Üst",
                last_name="Yönetim",
                is_active=True,
                tenant_id=default_tenant.id,
                role_id=exec_role.id if exec_role else None,
            )
            db.session.add(exec_user)

        db.session.commit()
        print("Super admin setup complete.")

    print("Seeding finished successfully.")


if __name__ == "__main__":
    main()
