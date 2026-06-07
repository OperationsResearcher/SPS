"""Hata Kontrolü — Tarayıcı motoru (Faz 3b, Playwright).

Arka plan thread'inde headless Chromium ile:
  - tomofiltest sentetik admini olarak login
  - keşfedilen her sayfayı aç (taze navigasyon, kuyruk tabanlı)
  - HTTP kodu + JS konsol hatası + başarısız AJAX + sunucu hata izini yakala
  - ✅/⚠️/❌ sınıflandır

GÜVENLİK: yalnız Yerel (çağıran katman kilitler). Tarama hedefi base_url (varsayılan
127.0.0.1:5001). Yazma yok (pasif gözlem); aktif CRUD senaryoları sonraki adım.

Tasarım: docs/HATA-KONTROLU-TASARIM.md (Faz 3, §7 yorumlama kuralları).
"""
from __future__ import annotations

import threading
import time

from app.services.tenant_clone_service import SYNTH_ADMIN_EMAIL

SYNTH_ADMIN_PW = "HataKontrol!123"   # tenant_clone_service ile aynı
DEFAULT_BASE_URL = "http://127.0.0.1:5001"

# Bellekte koşu durumu (kalıcılık Faz 5'te DB tablosuna taşınacak)
_RUNS: dict[str, dict] = {}
_RUN_SEQ = {"n": 0}
_LOCK = threading.Lock()


def _new_run_id() -> str:
    with _LOCK:
        _RUN_SEQ["n"] += 1
        return f"run{_RUN_SEQ['n']}"


def get_progress(run_id: str) -> dict | None:
    return _RUNS.get(run_id)


def _classify(status, js_errors, failed_ajax, html, final_url) -> tuple[str, str]:
    """(durum, sebep) — §7 kuralları. durum: ok | warn | fail | skip."""
    low = (html or "").lower()
    if status == 403:
        return "skip", "403 yetki — kapsam dışı"
    if status and status >= 500:
        return "fail", f"HTTP {status}"
    if status == 404:
        return "fail", "404 bulunamadı"
    if "/login" in (final_url or "") and status in (200, 302, None):
        return "fail", "oturum/erişim (login'e döndü)"
    if "traceback (most recent call last)" in low or "werkzeug.exceptions" in low:
        return "fail", "sunucu hata izi (traceback)"
    if "işlem tamamlanamadı" in low or "işlem tamamlanamad" in low:
        return "warn", "sayfa içi hata mesajı"
    if failed_ajax:
        return "warn", f"başarısız AJAX ({len(failed_ajax)})"
    if js_errors:
        return "warn", f"JS hatası ({len(js_errors)})"
    if status and 200 <= status < 400:
        return "ok", f"HTTP {status}"
    return "warn", f"HTTP {status}"


def start_run(app, base_url: str | None = None, limit: int | None = None) -> str:
    """Arka planda tarama başlatır, run_id döner."""
    run_id = _new_run_id()
    _RUNS[run_id] = {
        "id": run_id, "status": "starting", "total": 0, "done": 0,
        "current": "", "results": [], "counts": {"ok": 0, "warn": 0, "fail": 0},
        "error": None, "base_url": base_url or DEFAULT_BASE_URL,
    }
    t = threading.Thread(target=_run, args=(app, run_id, base_url or DEFAULT_BASE_URL, limit), daemon=True)
    t.start()
    return run_id


def _run(app, run_id: str, base_url: str, limit: int | None) -> None:
    st = _RUNS[run_id]
    try:
        with app.app_context():
            from app.services.hata_kontrol_service import discover_routes
            urls = [u["url"] for u in discover_routes()["urls"]]
        if limit:
            urls = urls[:limit]
        st["total"] = len(urls)
        st["status"] = "running"

        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(ignore_https_errors=True)
            page = ctx.new_page()

            # Sinyal toplayıcılar (her ziyaret öncesi temizlenir)
            sig = {"js": [], "ajax": []}
            page.on("pageerror", lambda e: sig["js"].append(str(e)[:200]))
            page.on("console", lambda m: sig["js"].append(m.text[:200]) if m.type == "error" else None)
            def _on_resp(resp):
                try:
                    rt = resp.request.resource_type
                    if resp.status >= 500 or (resp.status >= 400 and rt in ("xhr", "fetch")):
                        sig["ajax"].append(f"{resp.status} {resp.url[:120]}")
                except Exception:
                    pass
            page.on("response", _on_resp)

            # 1) Login (tomofiltest sentetik admini)
            if not _login(page, base_url):
                st["status"] = "error"
                st["error"] = "Login başarısız (tomofiltest admini). Sunucu çalışıyor mu / tomofiltest kurulu mu?"
                browser.close()
                return

            # 2) Sayfaları gez
            for url in urls:
                sig["js"].clear(); sig["ajax"].clear()
                st["current"] = url
                status = None
                html = ""
                try:
                    resp = page.goto(base_url + url, wait_until="domcontentloaded", timeout=20000)
                    status = resp.status if resp else None
                    try:
                        page.wait_for_load_state("networkidle", timeout=2500)
                    except Exception:
                        pass
                    html = page.content()
                    durum, sebep = _classify(status, sig["js"], sig["ajax"], html, page.url)
                except Exception as e:
                    emsg = str(e).splitlines()[0]
                    if "Download is starting" in emsg or "net::ERR_ABORTED" in emsg:
                        durum, sebep = "skip", "indirme/yönlendirme ucu (atlandı)"
                    else:
                        durum, sebep = "fail", f"yüklenemedi: {emsg[:80]}"
                st["results"].append({
                    "url": url, "status": status, "durum": durum, "sebep": sebep,
                    "js": list(sig["js"])[:3], "ajax": list(sig["ajax"])[:3],
                })
                st["counts"][durum] = st["counts"].get(durum, 0) + 1
                st["done"] += 1

            browser.close()
        st["status"] = "done"
        st["current"] = ""
    except Exception as e:
        st["status"] = "error"
        st["error"] = str(e)[:300]
        try:
            app.logger.error(f"[hata_kontrol_executor] {e}", exc_info=True)
        except Exception:
            pass


def _login(page, base_url: str) -> bool:
    try:
        page.goto(base_url + "/login", wait_until="domcontentloaded", timeout=20000)
        page.fill("input[name='email']", SYNTH_ADMIN_EMAIL)
        page.fill("input[name='password']", SYNTH_ADMIN_PW)
        page.click("button[type='submit'], input[type='submit']")
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(0.4)
        return "/login" not in page.url
    except Exception:
        return False
