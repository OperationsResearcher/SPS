"""Hata Kontrolü — Aktif CRUD senaryoları (Faz 3d, "tam aktif").

Her senaryo, headless tarayıcıda tomofiltest admini olarak GERÇEK UI etkileşimi yapar
(buton/modal/form/AJAX) ve adımları doğrular. Senaryolar veri yazar → koşu sonunda
tomofiltest otomatik sıfırlanır (wipe + yeniden klonla).

Senaryo imzası: fn(page, base_url) -> {"name", "passed", "steps":[{"step","ok","detail"}]}
Yeni senaryolar SCENARIOS listesine eklenerek büyür.
"""
from __future__ import annotations

import re as _re
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
    """SP: Ana strateji + Alt strateji oluştur — GERÇEK UI tıklama (buton+mc-modal+kaydet).

    Not: /sp ağır tenant'ta yavaş render olabilir; cömert timeout kullanılır.
    """
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    sname = "HK-Strateji-" + suf
    try:
        page.goto(base_url + "/sp", wait_until="domcontentloaded", timeout=120000)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        page.wait_for_selector("#btn-strategy-add, #btn-strategy-add-empty", state="visible", timeout=20000)
        step("SP sayfası açıldı", True)

        # Ana strateji (gerçek tıklama)
        page.locator("#btn-strategy-add, #btn-strategy-add-empty").first.click()
        page.wait_for_selector("#sp-modal-add-title", state="visible", timeout=20000)
        page.fill("#sp-modal-add-title", sname)
        page.fill("#sp-modal-add-code", "HKS" + suf[-4:])
        page.click("#mc-modal-form-save")
        page.wait_for_timeout(3000)  # sp.js ~1200ms sonra location.reload()
        created = page.locator("body", has_text=sname).count() > 0
        step("Ana strateji oluşturuldu (UI tıklama)", created, sname)

        # Alt strateji (gerçek tıklama)
        page.wait_for_selector(".btn-sub-add", state="visible", timeout=20000)
        ssname = "HK-Alt-" + suf
        page.locator(".btn-sub-add").first.click()
        page.wait_for_selector("#sp-modal-sub-add-title", state="visible", timeout=20000)
        page.fill("#sp-modal-sub-add-title", ssname)
        page.fill("#sp-modal-sub-add-code", "HKA" + suf[-4:])
        page.click("#mc-modal-form-save")
        page.wait_for_timeout(3000)
        sub_ok = page.locator("body", has_text=ssname).count() > 0
        step("Alt strateji oluşturuldu (UI tıklama)", sub_ok, ssname)
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Strateji CRUD", steps)


def scenario_sp_kimlik(page, base_url):
    """SP: Misyon ve Vizyon güncelle — GERÇEK UI tıklama (kart-düzenle + mc-modal + kaydet)."""
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    try:
        for kind, modal_id, label in [
            ("misyon", "#sp-modal-mission", "Misyon"),
            ("vizyon", "#sp-modal-vision", "Vizyon"),
        ]:
            trig = '.btn-sp-card-edit[data-sp-edit="%s"]' % kind
            page.goto(base_url + "/sp", wait_until="domcontentloaded", timeout=120000)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            try:
                page.wait_for_selector(trig, state="visible", timeout=20000)
            except Exception:
                step(f"{label} düzenle butonu görünmedi", False)
                continue
            page.wait_for_timeout(500)
            marker = f"HK-{label}-{suf}"
            page.locator(trig).first.click()
            try:
                page.wait_for_selector(modal_id, state="visible", timeout=12000)
            except Exception:
                page.locator(trig).first.click()
                page.wait_for_selector(modal_id, state="visible", timeout=12000)
            page.fill(modal_id, marker)
            page.click("#mc-modal-form-save")
            page.wait_for_timeout(2500)
            ok = page.locator("body", has_text=marker).count() > 0
            step(f"{label} güncellendi (UI tıklama)", ok, marker)
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Vizyon/Misyon", steps)


def scenario_surec_zinciri(page, base_url):
    """Süreç → PG → PGV — GERÇEK UI tıklama.

    Süreç: /process'te 'Yeni Süreç' modalı (ad+kod+alt-strateji checkbox+kaydet).
    PG: bir sürecin Karnesinde '+PG' modalı. PGV: karne veri girişi (en iyi çaba).
    """
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    sname = "HK-Surec-" + suf
    try:
        # ── Süreç (Yeni Süreç modalı) ──
        page.goto(base_url + "/process", wait_until="domcontentloaded", timeout=120000)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        page.wait_for_selector("#btn-surec-add", state="visible", timeout=20000)
        page.click("#btn-surec-add")
        page.wait_for_selector("#surec-name", state="visible", timeout=15000)
        page.fill("#surec-name", sname)
        page.fill("#surec-code", "HKP" + suf[-4:])
        # Süreç en az bir alt stratejiye bağlanmalı → ilk checkbox'ı işaretle
        try:
            page.wait_for_selector("input[id^='ss-']", timeout=8000)
            page.locator("input[id^='ss-']").first.check()
        except Exception:
            pass
        page.click("#btn-surec-save")
        page.wait_for_timeout(3000)
        created = page.locator("body", has_text=sname).count() > 0
        step("Süreç oluşturuldu (UI tıklama)", created, sname)

        # ── PG (bir sürecin Karnesinde) ──
        page.goto(base_url + "/process", wait_until="domcontentloaded", timeout=120000)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        karne = page.locator("a:has-text('Süreç Karnesi')")
        if karne.count() == 0:
            step("Karne linki bulunamadı", False)
            return _result("Süreç/PG/PGV", steps)
        karne.first.click()
        page.wait_for_load_state("domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        pgname = "HK-PG-" + suf
        page.wait_for_selector("#btn-kpi-add", state="visible", timeout=20000)
        page.click("#btn-kpi-add")
        page.wait_for_selector("#kpi-add-name", state="visible", timeout=15000)
        page.fill("#kpi-add-name", pgname)
        page.fill("#kpi-add-code", "HKK" + suf[-4:])
        try:
            page.fill("#kpi-add-target", "100")
            page.fill("#kpi-add-unit", "%")
        except Exception:
            pass
        page.click("#btn-kpi-add-modal-save")
        page.wait_for_timeout(2500)
        pg_ok = page.locator("body", has_text=pgname).count() > 0
        step("PG oluşturuldu (UI tıklama)", pg_ok, pgname)

        # ── PGV (GERÇEK UI: .btn-kpi-vgs → #modal-kpi-data-entry → değer → #btn-vgs-confirm) ──
        if page.locator(".btn-kpi-vgs").count() == 0:
            step("PGV: veri-giriş butonu (.btn-kpi-vgs) bulunamadı", False)
        else:
            page.locator(".btn-kpi-vgs").first.click()
            page.wait_for_selector("#kpi-data-entry-value", state="visible", timeout=12000)
            page.fill("#kpi-data-entry-value", "80")
            page.click("#btn-vgs-confirm")
            page.wait_for_timeout(2500)
            pgv_ok = not page.locator("#modal-kpi-data-entry").is_visible()
            step("PGV girildi (UI tıklama)", pgv_ok, "değer=80")
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Süreç/PG/PGV", steps)


def scenario_proje_task(page, base_url):
    """Proje (/project/new formu) → Task (/project/<id>/task/new formu) — GERÇEK UI tıklama."""
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    pname = "HK-Proje-" + suf
    try:
        # ── Proje (form sayfası) ──
        page.goto(base_url + "/project/new", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("input[name='name']", state="visible", timeout=20000)
        page.fill("input[name='name']", pname)
        # form submit (görünür Kaydet butonu)
        submit = page.locator("form button[type='submit'], form input[type='submit']").first
        submit.click()
        page.wait_for_load_state("domcontentloaded", timeout=60000)
        m = _re.search(r"/project/(\d+)", page.url or "")
        pid = int(m.group(1)) if m else None
        step("Proje oluşturuldu (form+kaydet)", bool(pid), f"id={pid}" if pid else f"url={page.url}")
        if not pid:
            return _result("Proje/Task", steps)

        # ── Task (form sayfası) ──
        tname = "HK-Task-" + suf
        page.goto(base_url + f"/project/{pid}/task/new", wait_until="domcontentloaded", timeout=60000)
        # başlık alanı (title veya name)
        title_sel = None
        for sel in ["input[name='title']", "input[name='name']", "#task-title", "#title"]:
            if page.locator(sel).count() > 0:
                title_sel = sel
                break
        if not title_sel:
            step("Task başlık alanı bulunamadı", False)
            return _result("Proje/Task", steps)
        page.fill(title_sel, tname)
        page.locator("form button[type='submit'], form input[type='submit']").first.click()
        page.wait_for_load_state("domcontentloaded", timeout=60000)
        ok = (tname in page.content()) or ("/project/" in (page.url or "") and "task/new" not in (page.url or ""))
        step("Task oluşturuldu (form+kaydet)", ok, tname)
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Proje/Task", steps)


# Senaryo kütüphanesi — zamanla büyür
SCENARIOS = [
    scenario_blue_ocean,
    scenario_sp_strateji,
    scenario_sp_kimlik,
    scenario_surec_zinciri,
    scenario_proje_task,
]
