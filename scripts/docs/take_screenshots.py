"""Kokpitim sayfalarının otomatik ekran görüntüsü alır.

Kullanım:
    .venv/Scripts/python scripts/docs/take_screenshots.py

Gereksinimler (.venv'de):
    pip install playwright
    playwright install chromium

Ortam:
    Flask localhost:5001'de çalışıyor olmalı
    .env'de TEST_TENANT_EMAIL / TEST_TENANT_PASSWORD ya da varsayılan: admin@tomofil.com / MfG_4660

Çıktı:
    docs/test/screenshots/NN-isim.png
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path


# ─── Yapılandırma ─────────────────────────────────────────────────────────────

BASE_URL = os.environ.get("KOKPITIM_BASE_URL", "http://localhost:5001")
LOGIN_EMAIL = os.environ.get("TEST_TENANT_EMAIL", "admin@tomofil.com")
LOGIN_PASSWORD = os.environ.get("TEST_TENANT_PASSWORD", "MfG_4660")
OUTPUT_DIR = Path(__file__).parent.parent.parent / "docs" / "test" / "screenshots"
VIEWPORT = {"width": 1440, "height": 900}
WAIT_AFTER_LOAD = 1500  # ms — JS render + chart için

PAGES = [
    # (sıra_no, slug, path, açıklama, ek_bekleme_ms)
    (1,  "masaustu",          "/masaustu",                     "Masaüstüm",                  1500),
    (2,  "sp-anasayfa",       "/sp",                           "SP Ana Sayfa",               1500),
    (3,  "plan-yillari",      "/sp/periods",                   "Plan Yılları",               1000),
    (4,  "exec-dashboard",    "/sp/exec-dashboard",            "Exec Dashboard",             2500),
    (5,  "ceyreklik-review",  "/sp/ceyreklik-review",          "Çeyreklik Review",           2500),
    (6,  "initiatives",       "/sp/initiatives",               "Initiative'ler",             1500),
    (7,  "senaryolar",        "/sp/scenarios",                 "Senaryolar",                 1500),
    (8,  "hoshin-xmatrix",    "/sp/xmatrix",                   "Hoshin X-Matrix",            2000),
    (9,  "blue-ocean",        "/sp/blue-ocean",                "Blue Ocean",                 1500),
    (10, "vrio",              "/sp/vrio",                      "VRIO Analizi",               1500),
    (11, "replan-triggers",   "/sp/replan-triggers",           "Replan Trigger'lar",         1500),
    (12, "strateji-haritasi", "/sp/strateji-haritasi",         "Strateji Haritası",          3000),
    (13, "ai-ayarlari",       "/sp/ayarlar/ai",                "AI Ayarları (BYOK)",         1000),
    (14, "llm-usage",         "/sp/llm-usage",                 "LLM Kullanım Paneli",        1500),
    (15, "k-radar",           "/k-radar",                      "K-Radar Hub",                1500),
    (16, "surec-listesi",     "/process",                      "Süreç Listesi",              1500),
    (17, "bireysel-karne",    "/bireysel/karne",               "Bireysel Karne",             1500),
    (18, "projeler",          "/project/list",                 "Projeler",                   1500),
    (19, "kurum",             "/kurum",                        "Kurum Paneli",               1000),
    (20, "bildirim",          "/bildirim",                     "Bildirimler",                1000),
]


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("HATA: playwright kurulu degil. Şu komutları çalıştır:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Çıktı dizini: {OUTPUT_DIR}")
    print(f"Base URL: {BASE_URL}")
    print(f"Login: {LOGIN_EMAIL}")
    print(f"{len(PAGES)} sayfa için ekran görüntüsü alınacak.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=VIEWPORT, locale="tr-TR")
        page = ctx.new_page()

        # ─── Login ──────────────────────────────────────────────────────────
        print("[login] Giriş yapılıyor...")
        try:
            page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded", timeout=20000)
            page.wait_for_selector("input[name='email']", timeout=10000)
        except Exception as e:
            print(f"HATA: Login sayfası açılamadı. Flask çalışıyor mu? ({e})")
            sys.exit(1)

        # Form alanlarını dene (id'leri farklı olabilir)
        try:
            email_selector = "input[name='email'], input[type='email'], #email"
            pwd_selector = "input[name='password'], input[type='password'], #password"
            page.fill(email_selector, LOGIN_EMAIL)
            page.fill(pwd_selector, LOGIN_PASSWORD)
            page.click("button[type='submit'], input[type='submit']")
            page.wait_for_url("**/masaustu**", timeout=10000)
            print("[login] Başarılı.\n")
        except Exception as e:
            print(f"HATA: Login başarısız. Bilgileri kontrol et ({e})")
            print(f"  E-posta: {LOGIN_EMAIL}")
            print(f"  Şifre: {'*' * len(LOGIN_PASSWORD)}")
            browser.close()
            sys.exit(1)

        # ─── Sayfaları gez ──────────────────────────────────────────────────
        success = 0
        skipped = []
        for idx, slug, path, desc, extra_wait in PAGES:
            filename = f"{idx:02d}-{slug}.png"
            outfile = OUTPUT_DIR / filename
            url = f"{BASE_URL}{path}"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(WAIT_AFTER_LOAD + extra_wait)
                # Full-page screenshot
                page.screenshot(path=str(outfile), full_page=True)
                size_kb = outfile.stat().st_size // 1024
                print(f"  [{idx:02d}/{len(PAGES)}] OK {filename} ({size_kb} KB) — {desc}")
                success += 1
            except Exception as e:
                msg = str(e).split("\n")[0][:80]
                print(f"  [{idx:02d}/{len(PAGES)}] SKIP {filename} — {msg}")
                skipped.append((idx, slug, msg))

        browser.close()

    # ─── Özet ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Başarılı: {success}/{len(PAGES)}")
    if skipped:
        print(f"Atlanan: {len(skipped)}")
        for idx, slug, msg in skipped:
            print(f"  - {idx:02d}-{slug}: {msg}")
    print(f"{'='*60}")
    print(f"Görüntüler: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
