"""Hata Kontrolü — Aktif CRUD senaryoları (Faz 3d, "tam aktif").

Her senaryo, headless tarayıcıda tomofiltest admini olarak GERÇEK UI etkileşimi yapar
(buton/modal/form/AJAX) ve adımları doğrular. Senaryolar veri yazar → koşu sonunda
tomofiltest otomatik sıfırlanır (wipe + yeniden klonla).

Senaryo imzası: fn(page, base_url) -> {"name", "passed", "steps":[{"step","ok","detail"}]}
Yeni senaryolar SCENARIOS listesine eklenerek büyür.
"""
from __future__ import annotations

import datetime as _dt
import json
import re as _re
import time


def _csrf(page, base_url):
    """Giriş yapmış sayfadan CSRF token'ı (POST uçları için)."""
    try:
        page.goto(base_url + "/masaustu", wait_until="domcontentloaded", timeout=20000)
    except Exception:
        pass
    try:
        return page.get_attribute('meta[name="csrf-token"]', "content") or ""
    except Exception:
        return ""


def _post_json(page, base_url, path, payload, token):
    """POST'u tarayıcının kendi fetch'iyle yap (session çerezi + CSRF doğal gider)."""
    return page.evaluate(
        """async (a) => {
            const r = await fetch(a.path, {method:'POST', credentials:'same-origin',
              headers:{'Content-Type':'application/json','X-CSRFToken':a.token,'X-Requested-With':'XMLHttpRequest'},
              body: JSON.stringify(a.payload)});
            let b=null; try { b = await r.json(); } catch(e) { b = null; }
            return {status: r.status, ok: r.ok, json: b};
        }""",
        {"path": path, "token": token, "payload": payload},
    )


def _get_json(page, path):
    """GET'i tarayıcının fetch'iyle (session çerezi doğal gider)."""
    return page.evaluate(
        """async (p) => {
            const r = await fetch(p, {credentials:'same-origin', headers:{'X-Requested-With':'XMLHttpRequest'}});
            let b=null; try { b = await r.json(); } catch(e) { b = null; }
            return {status: r.status, ok: r.ok, json: b};
        }""", path)


def _post_form(page, path, formobj, token):
    """Form POST'u tarayıcının fetch'iyle (redirect'i izler, final url döner)."""
    return page.evaluate(
        """async (a) => {
            const fd = new URLSearchParams();
            for (const k in a.form) fd.append(k, a.form[k]);
            fd.append('csrf_token', a.token);
            const r = await fetch(a.path, {method:'POST', credentials:'same-origin',
              headers:{'X-CSRFToken':a.token,'Content-Type':'application/x-www-form-urlencoded'},
              body: fd.toString()});
            return {status: r.status, ok: r.ok, url: r.url};
        }""",
        {"path": path, "form": formobj, "token": token},
    )


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
    """SP: Ana strateji + Alt strateji oluştur (API-seviyesi).

    /sp ana sayfası ağır tenant'ta (vizyon skoru 91k+ satır) çok yavaş render
    olduğu için UI-tıklama güvenilmez; gerçek create uçları çağrılır (tomofiltest'e
    gerçek yazma + validation).
    """
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    token = _csrf(page, base_url)
    try:
        res = _post_json(page, base_url, "/sp/api/strategy/add",
                         {"title": "HK-Strateji-" + suf, "code": "HKS" + suf[-4:]}, token)
        j = res.get("json") or {}
        sid = j.get("id")
        step("Ana strateji oluşturuldu (API)", bool(res.get("ok") and j.get("success") and sid),
             f"id={sid}" if sid else (j.get("message", "") or f"HTTP {res.get('status')}"))
        if not sid:
            return _result("Strateji CRUD", steps)

        res = _post_json(page, base_url, "/sp/api/sub-strategy/add",
                         {"strategy_id": sid, "title": "HK-Alt-" + suf, "code": "HKA" + suf[-4:]}, token)
        j = res.get("json") or {}
        ssid = j.get("id")
        step("Alt strateji oluşturuldu (API)", bool(res.get("ok") and j.get("success") and ssid),
             f"id={ssid}" if ssid else (j.get("message", "") or f"HTTP {res.get('status')}"))
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Strateji CRUD", steps)


def scenario_sp_kimlik(page, base_url):
    """SP: Misyon ve Vizyon güncelle (API-seviyesi — /sp ağır render'ına bağımlı değil)."""
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    token = _csrf(page, base_url)
    try:
        for field, label in [("purpose", "Misyon"), ("vision", "Vizyon")]:
            marker = f"HK-{label}-{suf}"
            res = _post_json(page, base_url, "/sp/api/tenant-identity", {field: marker}, token)
            j = res.get("json") or {}
            ok = bool(res.get("ok") and j.get("success"))
            step(f"{label} güncellendi (API)", ok, marker if ok else (j.get("message", "") or f"HTTP {res.get('status')}"))
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Vizyon/Misyon", steps)


def scenario_surec_zinciri(page, base_url):
    """Süreç → PG → PGV zinciri (API-seviyesi, giriş yapmış oturumla gerçek uçlar).

    Süreç sayfası dinamik/bağlam-ağır olduğu için UI-tıklama yerine gerçek create
    uçları çağrılır (tomofiltest'e gerçek yazma + validation). Her create bir
    sonrakine id verir.
    """
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    token = _csrf(page, base_url)
    try:
        # Süreç en az bir alt stratejiye bağlanmalı → geçerli bir alt-strateji id'si al
        gs = _get_json(page, "/sp/api/strategies")
        sub_ids = []
        for s in ((gs.get("json") or {}).get("data") or []):
            for ss in (s.get("sub_strategies") or []):
                if ss.get("id"):
                    sub_ids.append(ss["id"])
        sub_id = sub_ids[0] if sub_ids else None

        # Süreç
        payload = {"name": "HK-Surec-" + suf, "code": "HKP" + suf[-4:]}
        if sub_id:
            payload["sub_strategy_ids"] = [sub_id]
        res = _post_json(page, base_url, "/process/api/add", payload, token)
        j = res.get("json") or {}
        pid = j.get("id")
        step("Süreç oluşturuldu (API)", bool(res.get("ok") and j.get("success") and pid),
             f"id={pid}" if pid else (j.get("message", "") or f"HTTP {res.get('status')}"))
        if not pid:
            return _result("Süreç/PG/PGV", steps)

        # PG (process_kpi)
        res = _post_json(page, base_url, "/process/api/kpi/add",
                         {"process_id": pid, "name": "HK-PG-" + suf, "code": "HKK" + suf[-4:],
                          "target_value": "100", "unit": "%"}, token)
        j = res.get("json") or {}
        kid = j.get("id")
        step("PG oluşturuldu (API)", bool(res.get("ok") and j.get("success") and kid),
             f"id={kid}" if kid else (j.get("message", "") or f"HTTP {res.get('status')}"))
        if not kid:
            return _result("Süreç/PG/PGV", steps)

        # PGV (kpi_data)
        today = _dt.date.today().isoformat()
        res = _post_json(page, base_url, "/process/api/kpi-data/add",
                         {"kpi_id": kid, "data_date": today, "actual_value": "80"}, token)
        j = res.get("json") or {}
        ok = bool(res.get("ok") and j.get("success"))
        step("PGV (veri) girildi (API)", ok, today if ok else (j.get("message", "") or f"HTTP {res.get('status')}"))
    except Exception as e:
        step("İstisna", False, str(e).splitlines()[0][:120])
    return _result("Süreç/PG/PGV", steps)


def scenario_proje_task(page, base_url):
    """Proje (form+kaydet) → Task (API quick-add). Portföy projesi (plan yılı gerekmez)."""
    steps = []
    def step(n, ok, d=""):
        steps.append({"step": n, "ok": bool(ok), "detail": d})

    suf = str(int(time.time()))
    token = _csrf(page, base_url)
    try:
        pname = "HK-Proje-" + suf
        res = _post_form(page, "/project/new", {"name": pname, "priority": "Orta"}, token)
        m = _re.search(r"/project/(\d+)", res.get("url") or "")
        pid = int(m.group(1)) if m else None
        step("Proje oluşturuldu (form+kaydet)", bool(res.get("ok") and pid),
             f"id={pid}" if pid else f"HTTP {res.get('status')} url={res.get('url')}")
        if not pid:
            return _result("Proje/Task", steps)

        # Task (quick-add JSON)
        res2 = _post_json(page, base_url, "/project/api/task/quick-add",
                          {"project_id": pid, "title": "HK-Task-" + suf}, token)
        j = res2.get("json") or {}
        ok = bool(res2.get("ok") and j.get("success"))
        step("Task oluşturuldu (API)", ok, ("HK-Task-" + suf) if ok else (j.get("message", "") or f"HTTP {res2.get('status')}"))
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
