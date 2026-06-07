"""Hata Kontrolü — Aktif CRUD senaryoları (Faz 3d, "tam aktif").

Her senaryo, headless tarayıcıda tomofiltest admini olarak GERÇEK UI etkileşimi yapar
(buton/modal/form/AJAX) ve adımları doğrular. Senaryolar veri yazar → koşu sonunda
tomofiltest otomatik sıfırlanır (wipe + yeniden klonla).

Senaryo imzası: fn(page, base_url) -> {"name", "passed", "steps":[{"step","ok","detail"}]}
Yeni senaryolar SCENARIOS listesine eklenerek büyür.
"""
from __future__ import annotations

import time


def _result(name, steps):
    return {"name": name, "passed": all(s["ok"] for s in steps) if steps else False, "steps": steps}


def scenario_blue_ocean(page, base_url):
    """Mavi Okyanus: Tuval oluştur → aç → Faktör ekle (buton+modal+AJAX)."""
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    cname = "HK-Test-" + str(int(time.time()))
    try:
        page.goto(base_url + "/sp/blue-ocean", wait_until="domcontentloaded", timeout=20000)
        try:
            page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
        ok_page = ("/sp/blue-ocean" in page.url) and page.locator("#bo-new").count() > 0
        step("Mavi Okyanus sayfası açıldı", ok_page)
        if not ok_page:
            return _result("Mavi Okyanus CRUD", steps)

        # Yeni Tuval (buton → modal → form → AJAX)
        page.click("#bo-new")
        page.wait_for_timeout(300)
        page.fill("#bo-c-name", cname)
        page.click("#bo-modal-save")
        page.wait_for_timeout(1200)
        created = page.locator("#bo-list", has_text=cname).count() > 0
        step("Tuval oluşturuldu (buton+form+AJAX)", created, cname)
        if not created:
            return _result("Mavi Okyanus CRUD", steps)

        # Tuvali aç (kart tıkla)
        page.click("#bo-list .mc-card:has-text('" + cname + "')")
        page.wait_for_timeout(900)
        opened = page.locator("button:has-text('Faktör Ekle')").count() > 0
        step("Tuval detayı açıldı", opened)

        if opened:
            # Faktör ekle (buton → modal → form → AJAX)
            page.click("button:has-text('Faktör Ekle')")
            page.wait_for_timeout(400)
            page.fill("#bo-f-name", "Fiyat")
            page.fill("#bo-f-self", "7")
            page.click("#bo-f-save")
            page.wait_for_timeout(1200)
            # başarı: faktör modalı kapandı
            factor_ok = not page.locator("#modal-bo-factor").is_visible()
            step("Faktör eklendi (modal+AJAX)", factor_ok, "Fiyat=7")
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Mavi Okyanus CRUD", steps)


def scenario_sp_strateji(page, base_url):
    """SP: Ana strateji oluştur + Alt strateji oluştur (buton+mc-modal+kaydet)."""
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    sname = "HK-Strateji-" + suf
    try:
        page.goto(base_url + "/sp", wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("networkidle", timeout=4000)
        except Exception:
            pass
        has_btn = page.locator("#btn-strategy-add, #btn-strategy-add-empty").count() > 0
        step("SP sayfası açıldı", has_btn)
        if not has_btn:
            return _result("Strateji CRUD", steps)

        # Ana strateji
        page.locator("#btn-strategy-add, #btn-strategy-add-empty").first.click()
        page.wait_for_selector("#sp-modal-add-title", state="visible", timeout=6000)
        page.fill("#sp-modal-add-title", sname)
        page.fill("#sp-modal-add-code", "HKS" + suf[-4:])
        page.click("#mc-modal-form-save")
        page.wait_for_timeout(2600)  # sp.js ~1200ms sonra reload
        created = page.locator("body", has_text=sname).count() > 0
        step("Ana strateji oluşturuldu (buton+form+kaydet)", created, sname)

        # Alt strateji (herhangi bir stratejinin '+' butonu)
        if page.locator(".btn-sub-add").count() > 0:
            ssname = "HK-Alt-" + suf
            page.locator(".btn-sub-add").first.click()
            page.wait_for_selector("#sp-modal-sub-add-title", state="visible", timeout=6000)
            page.fill("#sp-modal-sub-add-title", ssname)
            page.fill("#sp-modal-sub-add-code", "HKA" + suf[-4:])
            page.click("#mc-modal-form-save")
            page.wait_for_timeout(2600)
            sub_ok = page.locator("body", has_text=ssname).count() > 0
            step("Alt strateji oluşturuldu (buton+form+kaydet)", sub_ok, ssname)
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Strateji CRUD", steps)


# Senaryo kütüphanesi — zamanla büyür
SCENARIOS = [
    scenario_blue_ocean,
    scenario_sp_strateji,
]
