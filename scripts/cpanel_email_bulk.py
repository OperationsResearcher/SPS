"""cPanel UAPI ile Tomofil kullanıcıları için toplu e-posta hesabı oluşturma.

Mevcut: deniz.tunc@tomofil.test  →  Yeni cPanel hesabı: deniz.tunc@kokpitim.com
Şifre: TmF_2626 (sabit, sistemde de aynı)

Kullanım:
    python scripts/cpanel_email_bulk.py --test            # 1 test hesabı dene
    python scripts/cpanel_email_bulk.py                   # dry-run, kim açılacak
    python scripts/cpanel_email_bulk.py --apply           # uygula
    python scripts/cpanel_email_bulk.py --update-db       # cPanel'de açıldıktan SONRA sistem email'lerini @kokpitim.com'a güncelle (opsiyonel)

API: cPanel UAPI Email::add_pop
    POST https://<host>:2083/execute/Email/add_pop
    Auth: Authorization: cpanel <username>:<api_token>
    Form: email=<local>&password=<pw>&quota=<MB>&domain=<domain>
"""
from __future__ import annotations

import os
import sys
import time
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# .env yükle
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

CPANEL_HOST = os.environ["CPANEL_HOST"]
CPANEL_PORT = int(os.environ.get("CPANEL_PORT", "2083"))
CPANEL_USER = os.environ["CPANEL_USER"]
CPANEL_TOKEN = os.environ["CPANEL_TOKEN"]
CPANEL_DOMAIN = os.environ["CPANEL_DOMAIN"]
QUOTA_MB = int(os.environ.get("CPANEL_DEFAULT_QUOTA_MB", "250"))

TOMOFIL_TENANT_ID = 27
NEW_PASSWORD = "TmF_2626"

API_BASE = f"https://{CPANEL_HOST}:{CPANEL_PORT}/execute/Email"
HEADERS = {"Authorization": f"cpanel {CPANEL_USER}:{CPANEL_TOKEN}"}


def cpanel_call(endpoint: str, params: dict, method: str = "POST") -> dict:
    """UAPI çağrısı yap, JSON döndür.

    Not: cPanel 2083 portu yerel self-signed cert kullanır. verify=False bilinçli.
    """
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f"{API_BASE}/{endpoint}"
    if method == "GET":
        r = requests.get(url, headers=HEADERS, params=params, timeout=30, verify=False)
    else:
        r = requests.post(url, headers=HEADERS, data=params, timeout=30, verify=False)
    return r.json()


def cpanel_get(endpoint: str, params: dict) -> dict:
    return cpanel_call(endpoint, params, method="GET")


def list_existing_emails() -> set[str]:
    """Var olan hesapları sor — duplicate engelle."""
    res = cpanel_get("list_pops", {"domain": CPANEL_DOMAIN})
    if not res.get("status"):
        print(f"  ! list_pops hata: {res.get('errors')}")
        return set()
    return {row["email"].lower() for row in res.get("data", []) if "email" in row}


def create_email(local_part: str, password: str, quota_mb: int) -> tuple[bool, str]:
    res = cpanel_call("add_pop", {
        "email": local_part,
        "password": password,
        "quota": quota_mb,
        "domain": CPANEL_DOMAIN,
    })
    if res.get("status") == 1:
        return True, "OK"
    errs = res.get("errors") or [res.get("error", "bilinmeyen hata")]
    return False, " | ".join(str(e) for e in errs)


def local_from_email(email: str) -> str:
    """deniz.tunc@tomofil.test → deniz.tunc"""
    return email.split("@", 1)[0]


def main():
    args = set(sys.argv[1:])
    test_mode = "--test" in args
    apply_mode = "--apply" in args
    update_db = "--update-db" in args

    print(f"cPanel host : {CPANEL_HOST}:{CPANEL_PORT}")
    print(f"cPanel user : {CPANEL_USER}")
    print(f"Hedef domain: @{CPANEL_DOMAIN}")
    print(f"Kota / hesap: {QUOTA_MB} MB\n")

    from app import create_app
    from app.extensions import db
    from app.models.core import User
    app = create_app()
    with app.app_context():
        users = User.query.filter_by(tenant_id=TOMOFIL_TENANT_ID).all()
        # Admin "Tomofil Yönetici" hariç
        users = [u for u in users if (u.first_name or "").lower() != "tomofil" and u.email]

        # Yeni cPanel email'lerini hesapla
        plans = []
        for u in users:
            local = local_from_email(u.email)
            new_email = f"{local}@{CPANEL_DOMAIN}"
            plans.append((u, local, new_email))

        # Duplicate local part var mı? (tomofil_test'te olmayabilir ama kokpitim.com'da olabilir)
        seen = {}
        for u, local, _ in plans:
            seen.setdefault(local, []).append(u)
        dups = {k: v for k, v in seen.items() if len(v) > 1}
        if dups:
            print("! Yerel kısım çakışması var:")
            for k, vs in dups.items():
                print(f"  {k}@{CPANEL_DOMAIN}: {[u.email for u in vs]}")
            print("  Bu hesaplar için manuel müdahale gerek.")

        # Test modu
        if test_mode:
            test_user, test_local, test_new = plans[0]
            print(f"\n[TEST] {test_user.first_name} {test_user.last_name}")
            print(f"  Açılacak: {test_new}")
            print(f"  Şifre: {NEW_PASSWORD}")
            print("\nDevam? (Evet için 'y' bas)", end=" ", flush=True)
            if input().strip().lower() != "y":
                print("İptal."); return
            ok, msg = create_email(test_local, NEW_PASSWORD, QUOTA_MB)
            print(f"  Sonuç: {'✓' if ok else '✗'} {msg}")
            return

        # cPanel'de mevcut hesapları listele
        print("Mevcut hesaplar sorgulanıyor...")
        existing = list_existing_emails()
        print(f"  Mevcut @{CPANEL_DOMAIN} hesap sayısı: {len(existing)}")

        to_create = []
        skip = []
        for u, local, new_email in plans:
            if new_email.lower() in existing:
                skip.append((u, new_email))
            else:
                to_create.append((u, local, new_email))

        print(f"\nAçılacak  : {len(to_create)}")
        print(f"Atlanacak : {len(skip)} (zaten var)")

        if not apply_mode and not update_db:
            print("\n--- Önizleme (ilk 10) ---")
            for u, local, new_email in to_create[:10]:
                print(f"  {u.first_name} {u.last_name}: {u.email}  →  {new_email}")
            print("\n--apply ile uygula | --update-db ile sistem DB email'lerini de güncelle")
            return

        if apply_mode:
            success = 0
            errors = []
            log_path = ROOT / "data" / "cpanel_email_log.csv"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            # 'a' modu — önceki başarılı kayıtları korur (idempotent restart)
            existed = log_path.exists() and log_path.stat().st_size > 0
            with log_path.open("a", encoding="utf-8") as f:
                if not existed:
                    f.write("user_id,old_email,new_email,status,detail\n")
                for i, (u, local, new_email) in enumerate(to_create, 1):
                    try:
                        ok, msg = create_email(local, NEW_PASSWORD, QUOTA_MB)
                    except Exception as e:
                        ok, msg = False, f"exception: {type(e).__name__}: {e}"
                    f.write(f"{u.id},{u.email},{new_email},{'OK' if ok else 'FAIL'},{msg}\n")
                    f.flush()
                    if ok:
                        success += 1
                    else:
                        errors.append((u, new_email, msg))
                        # Timeout/connection hatası → daha uzun bekle
                        if "timeout" in msg.lower() or "connection" in msg.lower():
                            print(f"  ! {new_email}: {msg[:80]} — 30s bekleniyor")
                            time.sleep(30)
                    if i % 10 == 0:
                        print(f"  ... {i}/{len(to_create)}  (basarili={success})")
                    time.sleep(1.0)  # cPanel rate limit'i kibarca aşma
            print(f"\n✓ {success}/{len(to_create)} hesap oluşturuldu")
            if errors:
                print(f"! {len(errors)} hata:")
                for u, e, m in errors[:5]:
                    print(f"  {e}: {m}")
            print(f"Log: {log_path}")

        if update_db:
            print("\nSistem DB email'lerini @kokpitim.com'a güncelliyorum...")
            updated = 0
            for u, _, new_email in plans:
                if u.email != new_email:
                    u.email = new_email
                    updated += 1
            db.session.commit()
            print(f"✓ {updated} kullanıcının email'i güncellendi.")


if __name__ == "__main__":
    main()
