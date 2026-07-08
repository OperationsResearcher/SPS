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

import datetime
import json
import logging
import os
import threading
import time

from app.services.tenant_clone_service import SYNTH_ADMIN_EMAIL, SYNTH_ADMIN_PW

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://127.0.0.1:5001"
_MAX_RUNS = 20   # bellekte tutulacak en son koşu sayısı (sınırsız büyümeyi önler)

# Bellekte koşu durumu (kalıcılık: dosya — _persist_run)
_RUNS: dict[str, dict] = {}
_RUN_SEQ = {"n": 0}
_LOCK = threading.Lock()

# Eşzamanlılık koruması: tarama / senaryo / yenile aynı tomofiltest'i paylaşır.
# Biri çalışırken diğeri tomofiltest'i sıfırlarsa çalışan koşunun oturumu ölür
# (bkz. 244/210 sahte-FAIL kök nedeni). Aynı anda yalnız BİR işlem.
_BUSY = {"label": None}


def busy_label() -> str | None:
    """Çalışan Hata Kontrolü işleminin etiketi (tarama/senaryo/yenile) ya da None."""
    with _LOCK:
        return _BUSY["label"]


def try_acquire(label: str) -> bool:
    """İşlem kilidini al. Başka işlem çalışıyorsa False döner (başlatma)."""
    with _LOCK:
        if _BUSY["label"]:
            return False
        _BUSY["label"] = label
        return True


def release() -> None:
    with _LOCK:
        _BUSY["label"] = None


def _new_run_id() -> str:
    with _LOCK:
        _RUN_SEQ["n"] += 1
        # Bellek sınırı: en eski koşuları at (en son _MAX_RUNS kalsın)
        if len(_RUNS) >= _MAX_RUNS:
            for old in list(_RUNS.keys())[: len(_RUNS) - _MAX_RUNS + 1]:
                _RUNS.pop(old, None)
        return f"run{_RUN_SEQ['n']}"


def get_progress(run_id: str) -> dict | None:
    return _RUNS.get(run_id)


# ─── Kalıcı kayıt (dosya) ────────────────────────────────────────────────────

def _runs_dir(app) -> str:
    d = os.path.join(app.instance_path, "hata_kontrol_runs")
    os.makedirs(d, exist_ok=True)
    return d


def _persist_run(app, run_id: str) -> None:
    """Biten koşuyu JSON dosyasına yazar (yeniden başlatmada kaybolmaz)."""
    try:
        st = _RUNS.get(run_id)
        if not st:
            return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        kind = st.get("kind", "tarama")
        fn = f"{ts}_{kind}_{run_id}.json"
        rec = dict(st)
        rec["saved_at"] = ts
        with open(os.path.join(_runs_dir(app), fn), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False)
        st["saved_file"] = fn
    except Exception as e:
        try:
            app.logger.info(f"[hata_kontrol] kayıt atlandı: {e}")
        except Exception:
            pass


def list_saved_runs(app, limit: int = 30) -> list[dict]:
    """Kaydedilmiş koşuların özet listesi (yeni→eski)."""
    out = []
    try:
        d = _runs_dir(app)
        for fn in sorted(os.listdir(d), reverse=True)[:limit]:
            if not fn.endswith(".json"):
                continue
            try:
                with open(os.path.join(d, fn), encoding="utf-8") as f:
                    r = json.load(f)
                out.append({
                    "file": fn, "kind": r.get("kind", "tarama"),
                    "saved_at": r.get("saved_at"), "status": r.get("status"),
                    "counts": r.get("counts"), "total": r.get("total"),
                    "passed": r.get("passed"), "failed": r.get("failed"),
                })
            except Exception:
                continue
    except Exception as e:
        logger.warning("[hata_kontrol] list_saved_runs suppressed: %s", e)
    return out


def load_saved_run(app, fname: str) -> dict | None:
    """Tek bir kaydedilmiş koşunun tam içeriği (dosya adı doğrulanır)."""
    if not fname or "/" in fname or "\\" in fname or not fname.endswith(".json"):
        return None
    path = os.path.join(_runs_dir(app), fname)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _classify(status, js_errors, failed_ajax, html, final_url) -> tuple[str, str]:
    """(durum, sebep) — §7 kuralları. durum: ok | warn | fail | skip."""
    low = (html or "").lower()
    if status == 403:
        return "skip", "403 yetki — kapsam dışı"
    if status == 404:
        return "skip", "404 — devre dışı / kapsam dışı uç (ör. demo)"
    if status == 400:
        return "skip", "400 — parametre/POST isteyen uç (beklenen validation)"
    if status and status >= 500:
        return "fail", f"HTTP {status}"
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


def start_run(app, base_url: str | None = None, limit: int | None = None, visual: bool = False) -> str | None:
    """Arka planda tarama başlatır, run_id döner. Başka işlem çalışıyorsa None."""
    if not try_acquire("tarama"):
        return None
    run_id = _new_run_id()
    try:
        app.logger.info(f"[hata_kontrol] Tarama baslatiliyor (visual={visual}, limit={limit})")
    except Exception:
        pass
    _RUNS[run_id] = {
        "id": run_id, "status": "starting", "visual": visual, "total": 0, "done": 0,
        "current": "", "results": [], "counts": {"ok": 0, "warn": 0, "fail": 0},
        "error": None, "base_url": base_url or DEFAULT_BASE_URL,
        "links": {"harvested": 0, "dead": [], "orphans": []},
    }
    t = threading.Thread(target=_run, args=(app, run_id, base_url or DEFAULT_BASE_URL, limit, visual), daemon=True)
    t.start()
    return run_id


def start_scenarios(app, base_url: str | None = None, visual: bool = False) -> str | None:
    """Arka planda CRUD senaryolarını başlatır, run_id döner. Meşgulse None."""
    if not try_acquire("senaryo"):
        return None
    run_id = _new_run_id()
    try:
        app.logger.info(f"[hata_kontrol] Senaryolar baslatiliyor (visual={visual})")
    except Exception:
        pass
    _RUNS[run_id] = {
        "id": run_id, "kind": "scenario", "status": "starting", "visual": visual,
        "total": 0, "done": 0, "current": "", "scenarios": [],
        "passed": 0, "failed": 0, "reset": False, "error": None,
        "base_url": base_url or DEFAULT_BASE_URL,
    }
    t = threading.Thread(target=_run_scenarios, args=(app, run_id, base_url or DEFAULT_BASE_URL, visual), daemon=True)
    t.start()
    return run_id


def _run_scenarios(app, run_id: str, base_url: str, visual: bool = False) -> None:
    st = _RUNS[run_id]
    try:
        from app.services.hata_kontrol_scenarios import SCENARIOS
        st["total"] = len(SCENARIOS)
        st["status"] = "running"

        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            if visual:
                browser = p.chromium.launch(headless=False, slow_mo=1000)
            else:
                browser = p.chromium.launch(headless=True)
            try:
                video_dir = os.path.join(app.static_folder, "videos", "hata_kontrol")
                os.makedirs(video_dir, exist_ok=True)
                ctx = browser.new_context(
                    ignore_https_errors=True,
                    record_video_dir=video_dir if visual else None,
                    record_video_size={"width": 1280, "height": 720} if visual else None
                )
                page = ctx.new_page()
                if not _login(page, base_url):
                    st["status"] = "error"
                    st["error"] = "Login başarısız (tomofiltest admini)."
                    return
                for fn in SCENARIOS:
                    st["current"] = getattr(fn, "__name__", "senaryo")
                    try:
                        res = fn(page, base_url)
                    except Exception as e:
                        res = {"name": getattr(fn, "__name__", "senaryo"), "passed": False,
                               "steps": [{"step": "İstisna", "ok": False, "detail": str(e)[:120]}]}
                    st["scenarios"].append(res)
                    st["passed" if res.get("passed") else "failed"] += 1
                    st["done"] += 1
                    if visual:
                        time.sleep(2.0)
            finally:
                if visual and 'page' in locals() and page and page.video:
                    try:
                        vpath = page.video.path()
                        st["video_url"] = f"/static/videos/hata_kontrol/{os.path.basename(vpath)}"
                    except Exception:
                        pass
                browser.close()

        # Senaryolar veri yazdı → tomofiltest'i baseline'a döndür (K8)
        st["current"] = "tomofiltest sıfırlanıyor…"
        try:
            with app.app_context():
                from app.services.tenant_clone_service import clone_tomofiltest
                rep = clone_tomofiltest(dry_run=False)
                st["reset"] = bool(rep.get("ok"))
        except Exception as e:
            st["reset"] = False
            try:
                app.logger.error(f"[hata_kontrol_scenarios] reset hatası: {e}")
            except Exception:
                pass

        st["status"] = "done"
        st["current"] = ""
        _persist_run(app, run_id)
    except Exception as e:
        st["status"] = "error"
        st["error"] = str(e)[:300]
        try:
            app.logger.error(f"[hata_kontrol_scenarios] {e}", exc_info=True)
        except Exception:
            pass
        _persist_run(app, run_id)
    finally:
        release()


def _run(app, run_id: str, base_url: str, limit: int | None, visual: bool = False) -> None:
    st = _RUNS[run_id]
    try:
        with app.app_context():
            from app.services.hata_kontrol_service import discover_routes
            disc_items = discover_routes()["urls"]
        urls = [u["url"] for u in disc_items]
        if limit:
            urls = urls[:limit]
        harvested: dict[str, str] = {}   # path -> kaynak sayfa (BFS link toplama)
        st["total"] = len(urls)
        st["status"] = "running"

        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            if visual:
                browser = p.chromium.launch(headless=False, slow_mo=1000)
            else:
                browser = p.chromium.launch(headless=True)
            try:
                video_dir = os.path.join(app.static_folder, "videos", "hata_kontrol")
                os.makedirs(video_dir, exist_ok=True)
                ctx = browser.new_context(
                    ignore_https_errors=True,
                    record_video_dir=video_dir if visual else None,
                    record_video_size={"width": 1280, "height": 720} if visual else None
                )
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
                    return

                # 2) Sayfaları gez
                for url in urls:
                    sig["js"].clear(); sig["ajax"].clear()
                    st["current"] = url
                    status = None
                    html = ""
                    try:
                        resp = page.goto(base_url + url, wait_until="domcontentloaded", timeout=30000)
                        status = resp.status if resp else None
                        try:
                            page.wait_for_load_state("networkidle", timeout=2500)
                        except Exception:
                            pass
                        if visual:
                            time.sleep(2.0)
                        html = page.content()
                        durum, sebep = _classify(status, sig["js"], sig["ajax"], html, page.url)
                        # BFS — sayfadaki iç bağlantıları topla
                        try:
                            hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
                            for h in hrefs or []:
                                pth = _norm_href(h, base_url)
                                if pth and pth not in harvested:
                                    harvested[pth] = url
                        except Exception:
                            pass
                    except Exception as e:
                        emsg = str(e).splitlines()[0]
                        if "Download is starting" in emsg or "net::ERR_ABORTED" in emsg:
                            durum, sebep = "skip", "indirme/yönlendirme ucu (atlandı)"
                        elif "Timeout" in emsg or "timeout" in emsg:
                            durum, sebep = "warn", "zaman aşımı (yavaş yüklenme, >30s)"
                        else:
                            durum, sebep = "fail", f"yüklenemedi: {emsg[:80]}"
                    st["results"].append({
                        "url": url, "status": status, "durum": durum, "sebep": sebep,
                        "js": list(sig["js"])[:3], "ajax": list(sig["ajax"])[:3],
                    })
                    st["counts"][durum] = st["counts"].get(durum, 0) + 1
                    st["done"] += 1
            finally:
                if visual and 'page' in locals() and page and page.video:
                    try:
                        vpath = page.video.path()
                        st["video_url"] = f"/static/videos/hata_kontrol/{os.path.basename(vpath)}"
                    except Exception:
                        pass
                browser.close()

        # BFS sonrası: ölü linkler + yetim sayfalar
        try:
            st["links"] = _compute_links(app, harvested, disc_items, full=(not limit))
        except Exception as e:
            app.logger.info(f"[hata_kontrol_executor] link analizi atlandı: {e}")
        st["status"] = "done"
        st["current"] = ""
        _persist_run(app, run_id)
    except Exception as e:
        st["status"] = "error"
        st["error"] = str(e)[:300]
        try:
            app.logger.error(f"[hata_kontrol_executor] {e}", exc_info=True)
        except Exception:
            pass
        _persist_run(app, run_id)
    finally:
        release()


def _norm_href(href: str, base_url: str) -> str | None:
    """Bir <a href>'i iç yola normalize eder (aynı origin, sorgu/fragment atılır)."""
    if not href:
        return None
    href = href.strip()
    if href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    if href.startswith("http"):
        if not href.startswith(base_url):
            return None  # dış bağlantı
        path = href[len(base_url):]
    elif href.startswith("/"):
        path = href
    else:
        return None  # göreli/anchor — atla
    path = path.split("#")[0].split("?")[0]
    return path or "/"


def _compute_links(app, harvested: dict[str, str], disc_items: list[dict], full: bool = True) -> dict:
    """Toplanan bağlantılardan ölü linkleri ve (tam taramada) yetim sayfaları çıkarır."""
    from werkzeug.exceptions import NotFound, MethodNotAllowed
    from app.services.hata_kontrol_service import _BLACKLIST

    adapter = app.url_map.bind("localhost")
    reached_eps = set()
    dead = []
    for path, src in harvested.items():
        if _BLACKLIST.search(path) or path.startswith("/static"):
            continue
        try:
            ep, _ = adapter.match(path, method="GET")
            reached_eps.add(ep)
        except MethodNotAllowed:
            try:
                ep, _ = adapter.match(path)
                reached_eps.add(ep)
            except Exception as e:
                logger.warning("[hata_kontrol] url match suppressed for %s: %s", path, e)
        except NotFound:
            dead.append({"path": path, "source": src})
        except Exception as e:
            logger.warning("[hata_kontrol] url match suppressed for %s: %s", path, e)

    # Yetim: keşfedilen (taranabilir) sayfa, hiçbir sayfadan link almıyor
    # (yalnız TAM taramada anlamlı — limitli koşuda baskılanır)
    orphans = []
    if full:
        orphans = [
            {"url": it["url"], "module": it["module"]}
            for it in disc_items
            if it["endpoint"] not in reached_eps
        ]
    return {
        "harvested": len(harvested),
        "dead": dead[:100],
        "orphans": orphans[:150],
        "dead_count": len(dead),
        "orphan_count": len(orphans),
    }


def _login(page, base_url: str) -> bool:
    try:
        page.goto(base_url + "/login", wait_until="domcontentloaded", timeout=20000)
        page.fill("input[name='email']", SYNTH_ADMIN_EMAIL)
        page.fill("input[name='password']", SYNTH_ADMIN_PW)
        page.click("button[type='submit'], input[type='submit']")
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(0.4)
        if "/login" in page.url:
            return False
        # Doğrulama: korumalı bir sayfa gerçekten açılıyor mu? URL'nin /login
        # olmaması yeterli değil — oturum kurulmadan da başka yere savrulabilir.
        # Açılmazsa (login'e döner) tüm taramanın sahte-FAIL olmasını önler.
        page.goto(base_url + "/desktop", wait_until="domcontentloaded", timeout=15000)
        time.sleep(0.3)
        return "/login" not in page.url
    except Exception:
        return False
