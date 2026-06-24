"""Kullanım Kılavuzu & Video Oluşturucu — Arka Plan Yürütücüsü.

Bu servis, YeniTomofil kurumu üzerinden sıfırdan otonom ekran görüntüleri ve kısa konu videoları çeker,
ardından kullanım kılavuzu PDF'ini günceller.
"""
from __future__ import annotations

import datetime
import glob
import json
import os
import shutil
import subprocess
import threading
import time
from sqlalchemy import text
from extensions import db
from werkzeug.security import generate_password_hash
from playwright.sync_api import sync_playwright

TEST_TENANT_NAME = "YeniTomofil"
SYNTH_ADMIN_EMAIL = "admin@yenitomofil.local"
SYNTH_ADMIN_PW = "YeniTomofil!123"

# Bölüm 1'de oluşturulacak kullanıcılar (senaryo v2.0). Hepsi SYNTH_ADMIN_PW şifresiyle
# açılır ki Bölüm 2'de bu hesaplarla giriş yapılabilsin.
ROLE_EXEC = "Kurum Üst Yönetimi"   # executive_manager (ua-role label)
ROLE_STD = "Kurum Kullanıcısı"     # standard_user
USERS_EXEC = [
    ("Selin", "Demir", "selin.demir@yenitomofil.local"),
    ("Mert", "Kaya", "mert.kaya@yenitomofil.local"),
]
USERS_STD = [
    ("Ahmet", "Yılmaz", "ahmet.yilmaz@yenitomofil.local"),
    ("Ayşe", "Şahin", "ayse.sahin@yenitomofil.local"),
    ("Burak", "Çelik", "burak.celik@yenitomofil.local"),
    ("Deniz", "Aydın", "deniz.aydin@yenitomofil.local"),
    ("Elif", "Korkmaz", "elif.korkmaz@yenitomofil.local"),
    ("Furkan", "Arslan", "furkan.arslan@yenitomofil.local"),
    ("Gizem", "Yıldız", "gizem.yildiz@yenitomofil.local"),
    ("Hakan", "Doğan", "hakan.dogan@yenitomofil.local"),
    ("İrem", "Koç", "irem.koc@yenitomofil.local"),
    ("Kerem", "Öztürk", "kerem.ozturk@yenitomofil.local"),
]

# Senaryo v3: simdilik yalniz Bolum 1. SP/Surec/Proje/K-Radar kodu korunur ama calismaz.
_INCLUDE_DEFERRED = False


def _find_ffmpeg() -> str | None:
    """H.264 (mp4) destekli gerçek bir ffmpeg bulur.

    Playwright'in paket içi ffmpeg'i yalnız libvpx (webm) içerir; mp4 üretemez.
    Bu yüzden sistemde kurulu / yerel kopyalanmış tam ffmpeg aranır.
    """
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "ffmpeg.exe"),
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    # Gyan essentials zip kök klasörü değişken adlı: ffmpeg-*/bin/ffmpeg.exe
    candidates += glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "ffmpeg-*", "bin", "ffmpeg.exe"))
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def _to_mp4(webm_path: str, run_id: str | None = None) -> str | None:
    """webm videoyu yanında .mp4 (H.264 + faststart) olarak üretir; yolu döndürür.

    ffmpeg yoksa veya dönüşüm başarısızsa None döner (webm korunur, akış bozulmaz).
    """
    if not webm_path or not os.path.exists(webm_path):
        return None
    ff = _find_ffmpeg()
    if not ff:
        if run_id:
            _add_log(run_id, "⚠ ffmpeg bulunamadı — mp4 dönüşümü atlandı (webm korundu).")
        return None
    mp4_path = os.path.splitext(webm_path)[0] + ".mp4"
    try:
        subprocess.run(
            [ff, "-y", "-i", webm_path, "-c:v", "libx264", "-preset", "fast",
             "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4_path],
            check=True, capture_output=True, timeout=600,
        )
        if os.path.exists(mp4_path) and os.path.getsize(mp4_path) > 0:
            return mp4_path
    except Exception as e:
        if run_id:
            _add_log(run_id, f"⚠ mp4 dönüşümü başarısız: {str(e).splitlines()[0][:120]}")
    return None


# ──────────────────────────────────────────────────────────────────────────────
# SESLİ ANLATI (edge-tts) — Bölüm 1
# Kaynak metin: docs/kılavuz/yenitomofil_anlati_metni.md (v1.0)
# Her beat bir çekim adımına bağlıdır; ses süresi o adımın ekran süresini sürer.
# ──────────────────────────────────────────────────────────────────────────────
NARRATION_VOICE = "tr-TR-AhmetNeural"
BEATS: dict[str, str] = {
    "B00": "Merhaba, Kokpitim'e hoş geldiniz. Veriye dayalı kararlar, geleceği şekillendiren stratejiler. Kurumsal performansınızı en üst seviyeye taşıyın.",
    "B01": "Kokpitim'e giriş yaparak başlıyoruz. YeniTomofil kurumunun yöneticisi olarak e-posta ve şifremizi giriyor, Giriş Yap butonuna tıklıyoruz.",
    "B02": "Karşımıza Masaüstü geliyor. Buradan kurumun tüm modüllerine; stratejik planlama, süreçler, projeler, K Raporlar ve K Analitik modüllerine tek noktadan erişiyoruz.",
    "B03": "İlk işimiz kurumun kimliğini tanımlamak. Kurum Ayarları sayfasından kurum adını, sektörünü, vergi numarasını ve iletişim bilgilerini giriyoruz.",
    "B04": "K-Vektör modülünü etkinleştiriyor, kurum bilgilerini kaydediyor ve logomuzu yüklüyoruz.",
    "B05": "Sırada ekibi tanımlamak var. Yönetim menüsünden Kullanıcılar sayfasını açıyoruz. Burada kullanıcıları tek tek ekleyebilir, ya da Toplu İçe Aktar ile Excel'den onlarca kullanıcıyı bir anda oluşturabiliriz.",
    "B06": "Kullanıcı ekleme formu sade: Ad, Soyad, zorunlu olan ve giriş kimliği işlevi gören E-posta, isteğe bağlı Şifre ve Rol. Şifreyi boş bırakırsak sistem güvenli bir geçici şifre üretir.",
    "B07": "Rol alanında iki seçenek var: stratejik kararlara ve yönetime katılan Kurum Üst Yönetimi, ve standart çalışan rolündeki Kurum Kullanıcısı.",
    "B08": "İki üst yöneticiyi, Selin Demir ve Mert Kaya'yı; ardından ilk iki kurum kullanıcısını form üzerinden ekliyoruz.",
    "B09": "Kalan sekiz kullanıcıyı ise Toplu İçe Aktarma ile ekliyoruz. Örnek Excel şablonunu doldurup yüklüyoruz; sistem her satırı otomatik olarak Kurum Kullanıcısı rolüyle oluşturuyor.",
    "B10": "Sonuçta bir Kurum Yöneticisi, iki Üst Yönetim ve on Kurum Kullanıcısı; toplam on üç kişilik ekibimiz hazır. Kısaca yetkiler şöyle: Yönetici ve Üst Yönetim strateji, süreç, proje ve kurum ayarlarını yönetir; Kurum Kullanıcısı ise yalnızca kendine atanan işleri görür ve kişisel ayarlarını değiştirir.",
    "B11": "Şimdi bu hesaplarla giriş yapıp farkları görelim. Önce Üst Yönetim, Selin Demir ile giriyoruz. Menüde Stratejik Planlama, Kurum Paneli ve Kullanıcılar görünüyor; ancak platforma özel Admin Araçları gizli.",
    "B12": "Üst Yönetim, kurum ayarları kapsamında e-posta sunucusu, yani SMTP yapılandırmasına erişebilir. Sunucu, port, kullanıcı ve gönderici bilgileri buradan girilir.",
    "B13": "Şimdi standart bir Kurum Kullanıcısı, Ahmet Yılmaz ile giriyoruz. Menünün belirgin biçimde kısaldığını görüyoruz; stratejik planlama ve kullanıcı yönetimi artık gizli.",
    "B14": "Kurum Kullanıcısı yalnızca kişisel ayarlarına erişir: bildirim tercihleri, dil, saat dilimi, tarih formatı ve açık-koyu tema.",
    "B15": "Profil sayfasından ad-soyad, telefon, ünvan, profil fotoğrafı, şifre değişikliği ve iki adımlı doğrulama yönetilir. Özetle: Üst Yönetim kurumu yönetirken, Kurum Kullanıcısı kendi profilini ve tercihlerini düzenler.",
}


def _find_ffprobe() -> str | None:
    ff = _find_ffmpeg()
    if ff:
        for name in ("ffprobe.exe", "ffprobe"):
            cand = os.path.join(os.path.dirname(ff), name)
            if os.path.exists(cand):
                return cand
    return shutil.which("ffprobe")


def _audio_duration(path: str) -> float:
    """Ses dosyasının saniye cinsinden süresi (ffprobe). Bulunamazsa 0.0."""
    fp = _find_ffprobe()
    if not fp or not path or not os.path.exists(path):
        return 0.0
    try:
        out = subprocess.run(
            [fp, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=30,
        )
        return float(out.stdout.strip())
    except Exception:
        return 0.0


def _generate_beats(out_dir: str, run_id: str | None = None):
    """Tüm beat metinlerini edge-tts ile mp3'e çevirir. (dosyalar, süreler) döner.

    edge-tts yoksa / internet yoksa boş döner → akış sessiz videoyla devam eder.
    """
    files: dict[str, str] = {}
    durs: dict[str, float] = {}
    try:
        import asyncio
        # Kurumsal SSL kesme/proxy ortamlarında Python certifi MITM kök sertifikasını
        # tanımaz; truststore ile Windows sertifika mağazasını kullandırıyoruz.
        try:
            import truststore
            truststore.inject_into_ssl()
        except Exception:
            pass
        import edge_tts  # noqa: F401
    except Exception:
        if run_id:
            _add_log(run_id, "⚠ edge-tts bulunamadı — anlatı sesi atlanacak (sessiz video).")
        return files, durs
    if run_id:
        _add_log(run_id, f"Anlatı sesi üretiliyor ({NARRATION_VOICE}, {len(BEATS)} beat)...")
    def _edge_save(text_in: str, path_in: str):
        # ÖNEMLİ: _generate_beats, Playwright'in sync_playwright() event loop'u aktifken
        # çağrılıyor. asyncio.run çalışan bir loop içinde patlar. Bu yüzden TTS'i DAİMA
        # taze bir thread'de çalıştırıyoruz — o thread'de çalışan bir loop yoktur.
        box: dict = {}

        def _worker():
            try:
                asyncio.run(edge_tts.Communicate(text_in, NARRATION_VOICE).save(path_in))
                box["ok"] = True
            except Exception as ex:
                box["err"] = ex

        th = threading.Thread(target=_worker, daemon=True)
        th.start()
        th.join()
        if not box.get("ok"):
            raise box.get("err", RuntimeError("edge-tts başarısız"))

    for bid, beat_text in BEATS.items():
        path = os.path.join(out_dir, f"{bid}.mp3")
        try:
            _edge_save(beat_text, path)
            d = _audio_duration(path)
            if d > 0 and os.path.exists(path):
                files[bid] = path
                durs[bid] = d
        except Exception as e:
            if run_id:
                _add_log(run_id, f"[uyari] Anlatı {bid} üretilemedi: {str(e).splitlines()[0][:100]}")
    if run_id and files:
        _add_log(run_id, f"Anlatı sesi hazır: {len(files)}/{len(BEATS)} beat.")
    return files, durs


def _render_video_with_narration(webm_path: str, timeline: list, out_mp4: str,
                                 run_id: str | None = None) -> str | None:
    """webm + zaman çizgili beat seslerini tek mp4'te birleştirir (her ses kendi offset'inde).

    Ses yoksa/başarısızsa sessiz mp4'e düşer (akış bozulmaz).
    timeline: [(audio_path, offset_seconds), ...]
    """
    ff = _find_ffmpeg()
    if not ff or not os.path.exists(webm_path):
        return _to_mp4(webm_path, run_id)
    tl = [(p, off) for (p, off) in timeline if p and os.path.exists(p)]
    if not tl:
        return _to_mp4(webm_path, run_id)
    cmd = [ff, "-y", "-i", webm_path]
    for (p, _off) in tl:
        cmd += ["-i", p]
    parts, labels = [], []
    for idx, (_p, off) in enumerate(tl, start=1):
        ms = int(max(off, 0.0) * 1000)
        parts.append(f"[{idx}]adelay={ms}|{ms}[a{idx}]")
        labels.append(f"[a{idx}]")
    filt = ";".join(parts) + ";" + "".join(labels) + \
        f"amix=inputs={len(tl)}:normalize=0:dropout_transition=0[aout]"
    # -shortest YOK: video sesten uzunsa kırpılmasın (ses biter, sonrası sessiz).
    cmd += ["-filter_complex", filt, "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-c:a", "aac", "-b:a", "160k", out_mp4]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=900)
        if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 0:
            return out_mp4
    except Exception as e:
        if run_id:
            _add_log(run_id, f"⚠ Sesli render başarısız, sessize düşülüyor: {str(e).splitlines()[0][:120]}")
        return _to_mp4(webm_path, run_id)
    return None


_RUNS: dict[str, dict] = {}
_RUN_SEQ = {"n": 0}
_LOCK = threading.Lock()
_BUSY = {"label": None}


def busy_label() -> str | None:
    with _LOCK:
        return _BUSY["label"]


def try_acquire(label: str) -> bool:
    with _LOCK:
        if _BUSY["label"]:
            return False
        _BUSY["label"] = label
        return True


def release() -> None:
    with _LOCK:
        _BUSY["label"] = None


class _Cancelled(Exception):
    """Çekim kullanıcı tarafından durduruldu."""


def request_stop(run_id: str | None = None) -> bool:
    """Çalışan çekimi durdurma isteği koyar. run_id yoksa çalışan koşuyu hedefler."""
    with _LOCK:
        if not run_id:
            # çalışan (done/error/cancelled olmayan) ilk koşuyu bul
            for rid, st in _RUNS.items():
                if st.get("status") in ("starting", "running"):
                    run_id = rid
                    break
        st = _RUNS.get(run_id) if run_id else None
        if not st:
            return False
        st["cancel"] = True
        return True


def _check_cancel(run_id: str) -> None:
    """Güvenli noktalarda çağrılır; durdurma istendiyse _Cancelled fırlatır."""
    with _LOCK:
        if _RUNS.get(run_id, {}).get("cancel"):
            raise _Cancelled()


def get_progress(run_id: str) -> dict | None:
    with _LOCK:
        return _RUNS.get(run_id)


def kilavuz_status() -> dict:
    """YeniTomofil kurumunun mevcut durumu (UI durum kartı için). App context gerekir."""
    tid = db.session.execute(
        text("SELECT id FROM tenants WHERE lower(name)=:n OR lower(coalesce(short_name,''))=:n LIMIT 1"),
        {"n": TEST_TENANT_NAME.lower()},
    ).scalar()
    if not tid:
        return {"exists": False}

    def c(sql: str) -> int:
        try:
            return int(db.session.execute(text(sql), {"t": tid}).scalar() or 0)
        except Exception:
            return 0

    return {
        "exists": True,
        "tid": tid,
        "admin_email": SYNTH_ADMIN_EMAIL,
        "strategies": c("SELECT count(*) FROM strategies WHERE tenant_id=:t"),
        "processes": c("SELECT count(*) FROM processes WHERE tenant_id=:t"),
        "process_kpis": c("SELECT count(*) FROM process_kpis pk JOIN processes p ON pk.process_id=p.id WHERE p.tenant_id=:t"),
        "kpi_data": c("SELECT count(*) FROM kpi_data kd JOIN process_kpis pk ON kd.process_kpi_id=pk.id JOIN processes p ON pk.process_id=p.id WHERE p.tenant_id=:t"),
    }


def start_kilavuz_run(app) -> str | None:
    if not try_acquire("kilavuz"):
        return None
    with _LOCK:
        _RUN_SEQ["n"] += 1
        run_id = f"kilavuz_run{_RUN_SEQ['n']}"
    
    _RUNS[run_id] = {
        "id": run_id,
        "status": "starting",
        "total": 2,  # 1 bölüm videosu + 1 PDF derleme (Senaryo v3 — Bölüm 1 odaklı)
        "done": 0,
        "current": "YeniTomofil temizleniyor...",
        "error": None,
        "cancel": False,
        "logs": [],
    }
    
    t = threading.Thread(target=_run_kilavuz_process, args=(app, run_id), daemon=True)
    t.start()
    return run_id


def _add_log(run_id: str, message: str) -> None:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    log_line = f"[{ts}] {message}"
    # Windows konsolu cp1252 ise ⚠ gibi karakterler print'i çökertebilir;
    # bir log satırı çekimi ASLA düşürmemeli. Panel logu (st["logs"]) tam Unicode kalır.
    try:
        print(f"[kilavuz_olusturucu] {log_line}")
    except Exception:
        try:
            print(("[kilavuz_olusturucu] " + log_line).encode("ascii", "replace").decode("ascii"))
        except Exception:
            pass
    with _LOCK:
        st = _RUNS.get(run_id)
        if st:
            st["logs"].append(log_line)
            st["current"] = message


def _highlight_and_screenshot(page, selector: str, filepath: str) -> None:
    """Belirtilen CSS seçicisinin etrafına kırmızı çerçeve ekler, resim alır, çerçeveyi kaldırır."""
    try:
        page.evaluate(f"""
            const el = document.querySelector("{selector}");
            if (el) {{
                el.style.outline = "4px solid #dc2626";
                el.style.outlineOffset = "3px";
                el.style.boxShadow = "0 0 15px rgba(220, 38, 38, 0.6)";
            }}
        """)
        time.sleep(0.5)
        page.screenshot(path=filepath)
        page.evaluate(f"""
            const el = document.querySelector("{selector}");
            if (el) {{
                el.style.outline = "";
                el.style.outlineOffset = "";
                el.style.boxShadow = "";
            }}
        """)
    except Exception:
        try:
            page.screenshot(path=filepath)
        except Exception:
            pass


def _login(page, base_url: str, email: str = SYNTH_ADMIN_EMAIL, pw: str = SYNTH_ADMIN_PW) -> None:
    """Verilen hesapla giriş yapar."""
    page.goto(base_url + "/login")
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", pw)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    time.sleep(1.0)


def _create_user(page, fname: str, lname: str, email: str, role_label: str, screenshot: str | None = None) -> None:
    """Kullanıcı Ekle modalı ile gerçek form üzerinden bir kullanıcı oluşturur."""
    page.click("#btn-user-add")
    page.wait_for_selector("#ua-fname", state="visible", timeout=12000)
    page.fill("#ua-fname", fname)
    page.fill("#ua-lname", lname)
    page.fill("#ua-email", email)
    page.fill("#ua-pass", SYNTH_ADMIN_PW)  # bilinen şifre (Bölüm 2'de giriş için)
    page.select_option("#ua-role", label=role_label)
    if screenshot:
        _highlight_and_screenshot(page, "#btn-add-modal-save", screenshot)
    page.click("#btn-add-modal-save")
    page.wait_for_timeout(1800)  # AJAX kayıt + tablo yenilenmesi


def _make_bulk_xlsx(path: str, users: list) -> None:
    """users: [(fname, lname, email), ...] → Ad/Soyad/E-posta/Şifre başlıklı .xlsx."""
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(["Ad", "Soyad", "E-posta", "Şifre"])
    for fn, ln, em in users:
        ws.append([fn, ln, em, SYNTH_ADMIN_PW])
    wb.save(path)


def _bulk_import(page, xlsx_path: str, screenshot: str | None = None) -> None:
    """Toplu İçe Aktar akışı: buton → Swal modal → dosya seç → İçe Aktar.

    JS, fetch ile FormData(file) + X-CSRFToken gönderir (gerçek sayfa bağlamı → CSRF hazır).
    """
    page.click("#btn-bulk-import")
    page.wait_for_selector("#bulk-file", state="visible", timeout=10000)
    page.set_input_files("#bulk-file", xlsx_path)
    if screenshot:
        try:
            page.screenshot(path=screenshot)  # Swal modalı görünürken
        except Exception:
            pass
    page.click(".swal2-confirm")
    page.wait_for_timeout(3500)  # upload + toast + tablo reload


def _run_kilavuz_process(app, run_id: str) -> None:
    st = _RUNS[run_id]
    st["status"] = "running"
    
    video_dir = os.path.join(app.static_folder, "videos", "kullanim_kilavuzu")
    img_dir = os.path.join(app.static_folder, "img", "kullanim_kilavuzu")
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    
    base_url = "http://127.0.0.1:5001"
    
    try:
        # ──────────────────────────────────────────────────────────────────────
        # ADIM 1: Veritabanı Sıfırlama ve Boş YeniTomofil Yaratma
        # ──────────────────────────────────────────────────────────────────────
        _add_log(run_id, "YeniTomofil kurumu temizleniyor ve boş olarak kuruluyor...")
        with app.app_context():
            import app.services.tenant_clone_service as cloner
            existing_tables = cloner._existing_tables()
            # Case-safe tenant ID lookup
            old_test = db.session.execute(
                text("SELECT id FROM tenants WHERE lower(name) = :n OR lower(coalesce(short_name,'')) = :n LIMIT 1"),
                {"n": TEST_TENANT_NAME.lower()}
            ).scalar()
            
            if old_test:
                cloner._wipe_test_tenant(old_test, existing_tables)
                db.session.commit()
                
            new_tid = db.session.execute(text(
                "INSERT INTO tenants (name, short_name, tenant_type, is_active) "
                "VALUES (:n, :n, 'normal', true) RETURNING id"
            ), {"n": TEST_TENANT_NAME}).scalar()

            role_id = db.session.execute(text(
                "SELECT id FROM roles WHERE name = 'tenant_admin' LIMIT 1"
            )).scalar()
            db.session.execute(text(
                "INSERT INTO users (email, password_hash, first_name, last_name, tenant_id, role_id, is_active) "
                "VALUES (:e, :p, 'Test', 'Admin', :tid, :rid, true)"
            ), {"e": SYNTH_ADMIN_EMAIL, "p": generate_password_hash(SYNTH_ADMIN_PW),
                "tid": new_tid, "rid": role_id})
                
            cloner._resync_sequences(["tenants", "users"], existing_tables)
            db.session.commit()
        
        _add_log(run_id, "YeniTomofil kurumu başarıyla kuruldu. Playwright başlatılıyor...")
        
        with sync_playwright() as p:
            # 1920x1080 Headed modda çalıştır (kullanıcı görsün ve videolar kaliteli çıksın)
            browser = p.chromium.launch(headless=False, slow_mo=1000)
            
            # ──────────────────────────────────────────────────────────────────────
            # BÖLÜM 1: Giriş ve Temel Kurum ve Kullanıcı Yapılandırmaları (1.1–1.4, tek video)
            # ──────────────────────────────────────────────────────────────────────
            _add_log(run_id, "Bölüm 1 başlatılıyor: Giriş + Kurum Yönetimi + Kullanıcılar + Roller/Ayarlar...")
            _check_cancel(run_id)
            # Sesli anlatı: çekim ÖNCESİ tüm beat seslerini üret (kayıt başlamadan).
            import tempfile as _tf
            narr_dir = _tf.mkdtemp(prefix="kk_narr_")
            beat_files, beat_durs = _generate_beats(narr_dir, run_id)
            _check_cancel(run_id)

            ctx1 = browser.new_context(
                ignore_https_errors=True,
                viewport={"width": 1920, "height": 1080},
                record_video_dir=video_dir,
                record_video_size={"width": 1920, "height": 1080}
            )
            page1 = ctx1.new_page()
            t0 = time.monotonic()
            _timeline = []

            def _beat(bid):
                dur = beat_durs.get(bid, 0.0)
                if bid in beat_files and dur > 0:
                    _timeline.append((beat_files[bid], time.monotonic() - t0))
                    page1.wait_for_timeout(int((dur + 0.4) * 1000))
                else:
                    page1.wait_for_timeout(1200)

            # ── 1.1 Sistem Girişi ve Masaüstü (Launcher) ──
            page1.goto(base_url + "/login")
            page1.wait_for_load_state("networkidle")
            # Açılış tanıtımı: video açılır açılmaz login ekranında karşılama + slogan
            # (ilk ses için bekleme olmasın).
            _beat("B00")
            page1.fill("input[name='email']", SYNTH_ADMIN_EMAIL)
            page1.fill("input[name='password']", SYNTH_ADMIN_PW)
            _highlight_and_screenshot(page1, "button[type='submit']", os.path.join(img_dir, "01_login.png"))
            _beat("B01")
            page1.click("button[type='submit']")
            page1.wait_for_load_state("networkidle")
            time.sleep(1.5)
            page1.screenshot(path=os.path.join(img_dir, "02_launcher.png"))
            _beat("B02")

            # ── 1.2 Kurum Yönetimi (Kurum bilgileri + logo + K-Vektör) ──
            _check_cancel(run_id)
            _add_log(run_id, "1.2 Kurum Yönetimi: kurum bilgileri, logo ve K-Vektör...")
            try:
                page1.goto(base_url + "/kurum/settings")
                page1.wait_for_load_state("networkidle")
                page1.wait_for_selector("#kurum_adi", state="visible", timeout=15000)
                page1.fill("#kurum_adi", "YeniTomofil Otomotiv Sanayi ve Ticaret A.Ş.")
                page1.fill("#sektor", "Otomotiv — Elektrikli Araç Üretimi")
                page1.fill("#vergi_no", "1234567890")
                page1.fill("#adres", "Organize Sanayi Bölgesi 5. Cadde No:12, Bursa")
                page1.fill("#telefon", "0224 555 12 34")
                page1.fill("#email", "info@yenitomofil.com")
                page1.fill("#website", "www.yenitomofil.com")
                # Alanları doldururken sayfa aşağı kaydı; başa dön ki kare formun üstünü
                # göstersin ve anlatı boyunca görüntü kararlı kalsın (aşağı-yukarı gezinme olmasın).
                page1.evaluate("window.scrollTo(0, 0)")
                page1.wait_for_timeout(400)
                _highlight_and_screenshot(page1, "#kurum_adi", os.path.join(img_dir, "03_kurum_form.png"))
                _beat("B03")
                # K-Vektör aç — input gizli/şekillendirilmiş toggle (CSS ile gizli); Playwright
                # check() actionability'yi sağlayamayıp ~30 sn retry eder (üst↔toggle zıplaması).
                # Bu yüzden GÖRÜNÜR label'a tıklıyoruz (toggle'ı görsel olarak çevirir).
                try:
                    if not page1.is_checked("#k_vektor_enabled"):
                        page1.click("label.kv-enable-toggle[for='k_vektor_enabled']")
                        page1.wait_for_timeout(400)
                except Exception as ke:
                    _add_log(run_id, f"[uyari] 1.2 K-Vektör toggle atlandı: {str(ke).splitlines()[0][:100]}")
                # Kaydet (AJAX, sayfa yenilenmez) — metin alanları + K-Vektör DB'ye yazılır.
                page1.click("#btn-save")
                page1.wait_for_timeout(2500)
                # Logo yükle — başarıda JS window.location.href ile /kurum/ayarlar'a döner (reload).
                # Metinleri ÖNCE kaydettiğimiz için reload sonrası kayıtlı bilgiler + logo + K-Vektör görünür.
                try:
                    logo = os.path.abspath("docs/kokpitim-logo.png")
                    if os.path.exists(logo):
                        page1.set_input_files("#kurum_logo", logo)
                        page1.click("#btn-logo-upload")
                        page1.wait_for_load_state("networkidle")
                        page1.wait_for_selector("#kurum_adi", state="visible", timeout=15000)
                        page1.wait_for_timeout(800)
                except Exception as le:
                    _add_log(run_id, f"[uyari] 1.2 Logo yükleme atlandı: {str(le).splitlines()[0][:100]}")
                page1.evaluate("window.scrollTo(0, 0)")
                page1.wait_for_timeout(300)
                page1.screenshot(path=os.path.join(img_dir, "04_kurum_kaydedildi.png"))
                _beat("B04")
                _add_log(run_id, "1.2 Kurum bilgileri kaydedildi")
            except Exception as e:
                _add_log(run_id, f"⚠ 1.2 Kurum Yönetimi atlandı: {str(e).splitlines()[0][:120]}")

            # ── 1.3 Kullanıcı Yönetimi ve Yetkilendirme ──
            _check_cancel(run_id)
            _add_log(run_id, "1.3 Kullanıcı Yönetimi: 2 Üst Yönetim + 10 Kullanıcı...")
            page1.goto(base_url + "/admin/users")
            page1.wait_for_load_state("networkidle")
            time.sleep(1.0)
            _highlight_and_screenshot(page1, "#btn-user-add", os.path.join(img_dir, "05_users_page.png"))
            _beat("B05")

            # İlk Üst Yönetim (Selin Demir) — form alanları + rol dropdown tanıtımı
            try:
                page1.click("#btn-user-add")
                page1.wait_for_selector("#ua-fname", state="visible", timeout=12000)
                fn, ln, em = USERS_EXEC[0]
                page1.fill("#ua-fname", fn)
                page1.fill("#ua-lname", ln)
                page1.fill("#ua-email", em)
                page1.fill("#ua-pass", SYNTH_ADMIN_PW)
                _highlight_and_screenshot(page1, "#ua-email", os.path.join(img_dir, "06_user_form_fields.png"))
                _beat("B06")
                page1.select_option("#ua-role", label=ROLE_EXEC)
                _highlight_and_screenshot(page1, "#ua-role", os.path.join(img_dir, "07_user_form_role.png"))
                _beat("B07")
                page1.click("#btn-add-modal-save")
                page1.wait_for_timeout(1800)
                _add_log(run_id, f"Kurum Üst Yönetimi eklendi: {fn} {ln}")
            except Exception as e:
                _add_log(run_id, f"⚠ {USERS_EXEC[0][0]} eklenemedi: {str(e).splitlines()[0][:120]}")

            # İkinci Üst Yönetim (Mert Kaya)
            try:
                fn, ln, em = USERS_EXEC[1]
                _create_user(page1, fn, ln, em, ROLE_EXEC)
                _add_log(run_id, f"Kurum Üst Yönetimi eklendi: {fn} {ln}")
            except Exception as e:
                _add_log(run_id, f"⚠ {USERS_EXEC[1][0]} eklenemedi: {str(e).splitlines()[0][:120]}")

            # İlk 2 Kurum Kullanıcısı — FORM ile
            for i, (fn, ln, em) in enumerate(USERS_STD[:2]):
                _check_cancel(run_id)
                try:
                    shot = os.path.join(img_dir, "08_std_user_form.png") if i == 0 else None
                    _create_user(page1, fn, ln, em, ROLE_STD, screenshot=shot)
                    _add_log(run_id, f"Kurum Kullanıcısı (form) eklendi: {fn} {ln}")
                except Exception as e:
                    _add_log(run_id, f"⚠ {fn} {ln} (form) eklenemedi: {str(e).splitlines()[0][:120]}")

            _beat("B08")

            # Kalan 8 Kurum Kullanıcısı — TOPLU İÇE AKTARMA (Excel)
            try:
                import tempfile
                fd, xlsx_path = tempfile.mkstemp(suffix=".xlsx")
                os.close(fd)
                _make_bulk_xlsx(xlsx_path, USERS_STD[2:])
                _bulk_import(page1, xlsx_path, screenshot=os.path.join(img_dir, "09_bulk_import.png"))
                _beat("B09")
                try:
                    os.remove(xlsx_path)
                except OSError:
                    pass
                _add_log(run_id, f"Toplu içe aktarma ile {len(USERS_STD[2:])} Kurum Kullanıcısı eklendi")
            except Exception as e:
                _add_log(run_id, f"⚠ Toplu içe aktarma atlandı: {str(e).splitlines()[0][:120]}")

            # Tüm tablo (13 kayıt)
            page1.goto(base_url + "/admin/users")
            page1.wait_for_load_state("networkidle")
            time.sleep(1.5)
            page1.screenshot(path=os.path.join(img_dir, "10_users_table_full.png"))
            _beat("B10")

            # ── 1.4 Farklı Rollerle Giriş ve Kullanıcı Ayarları ──
            _check_cancel(run_id)
            _add_log(run_id, "1.4 Rollerle giriş ve ayarlar (Üst Yönetim + Kullanıcı)...")
            # A) Kurum Üst Yönetimi (Selin Demir)
            try:
                page1.goto(base_url + "/logout"); page1.wait_for_load_state("networkidle"); time.sleep(0.6)
                _login(page1, base_url, USERS_EXEC[0][2], SYNTH_ADMIN_PW)
                time.sleep(1.0)
                page1.screenshot(path=os.path.join(img_dir, "11_exec_menu.png"))
                _beat("B11")
                page1.goto(base_url + "/settings/email")
                page1.wait_for_load_state("networkidle")
                time.sleep(1.2)
                _highlight_and_screenshot(page1, "#smtp_host", os.path.join(img_dir, "12_exec_eposta_ayarlari.png"))
                _beat("B12")
            except Exception as e:
                _add_log(run_id, f"⚠ 1.4 Üst Yönetim adımı: {str(e).splitlines()[0][:120]}")
            # B) Kurum Kullanıcısı (Ahmet Yılmaz)
            try:
                page1.goto(base_url + "/logout"); page1.wait_for_load_state("networkidle"); time.sleep(0.6)
                _login(page1, base_url, USERS_STD[0][2], SYNTH_ADMIN_PW)
                time.sleep(1.0)
                page1.screenshot(path=os.path.join(img_dir, "13_user_menu.png"))
                _beat("B13")
                page1.goto(base_url + "/settings/account")
                page1.wait_for_load_state("networkidle")
                time.sleep(1.2)
                page1.screenshot(path=os.path.join(img_dir, "14_user_hesap_ayarlari.png"))
                _beat("B14")
                page1.goto(base_url + "/profile")
                page1.wait_for_load_state("networkidle")
                time.sleep(1.2)
                _highlight_and_screenshot(page1, "form", os.path.join(img_dir, "15_profil.png"))
                _beat("B15")
            except Exception as e:
                _add_log(run_id, f"⚠ 1.4 Kullanıcı adımı: {str(e).splitlines()[0][:120]}")

            vpath1 = page1.video.path() if page1.video else None
            ctx1.close()
            if vpath1 and os.path.exists(vpath1):
                webm_final = os.path.join(video_dir, "1_giris_kurum_kullanici.webm")
                shutil.move(vpath1, webm_final)
                mp4_final = os.path.splitext(webm_final)[0] + ".mp4"
                _add_log(run_id, "Bölüm 1 videosu sesli anlatıyla mp4'e dönüştürülüyor...")
                if _render_video_with_narration(webm_final, _timeline, mp4_final, run_id):
                    _add_log(run_id, "Bölüm 1 videosu (sesli) mp4 olarak hazır.")
                try:
                    shutil.rmtree(narr_dir, ignore_errors=True)
                except Exception:
                    pass
            st["done"] += 1
            
            if _INCLUDE_DEFERRED:
                # ──────────────────────────────────────────────────────────────────────
                # ADIM 3: Stratejik Planlama Videosu
                # ──────────────────────────────────────────────────────────────────────
                _add_log(run_id, "3. Bölüm Videosu: Stratejik Planlama başlatılıyor...")
                _check_cancel(run_id)
                ctx2 = browser.new_context(
                    ignore_https_errors=True,
                    viewport={"width": 1920, "height": 1080},
                    record_video_dir=video_dir,
                    record_video_size={"width": 1920, "height": 1080}
                )
                page2 = ctx2.new_page()
                page2.goto(base_url + "/login")
                page2.fill("input[name='email']", SYNTH_ADMIN_EMAIL)
                page2.fill("input[name='password']", SYNTH_ADMIN_PW)
                page2.click("button[type='submit']")
                page2.wait_for_load_state("networkidle")
            
                # SP sayfasına git
                page2.goto(base_url + "/sp")
                page2.wait_for_load_state("networkidle")
                time.sleep(1.5)
            
                # Vizyon kartını güncelle (kart-düzenle → mc-modal → kaydet) — doğrulanmış seçiciler
                try:
                    page2.locator('.btn-sp-card-edit[data-sp-edit="vizyon"]').first.click()
                    page2.wait_for_selector("#sp-modal-vision", state="visible", timeout=12000)
                    page2.fill("#sp-modal-vision", "Sürdürülebilir mobilite çözümlerinde lider, en yüksek müşteri memnuniyetine sahip teknolojik otomotiv markası olmak.")
                    page2.click("#mc-modal-form-save")
                    time.sleep(2.5)  # sp.js ~1200ms sonra location.reload()
                except Exception as e:
                    _add_log(run_id, f"⚠ 2. Bölüm — Vizyon güncelleme atlandı: {str(e).splitlines()[0][:120]}")

                # Ana strateji ekle (boş kurumda #btn-strategy-add-empty) — doğrulanmış seçiciler
                try:
                    page2.locator("#btn-strategy-add, #btn-strategy-add-empty").first.click()
                    page2.wait_for_selector("#sp-modal-add-title", state="visible", timeout=15000)
                    page2.fill("#sp-modal-add-title", "Teknoloji ve Ürün Geliştirme")
                    page2.fill("#sp-modal-add-code", "STR-TECH")
                    _highlight_and_screenshot(page2, "#mc-modal-form-save", os.path.join(img_dir, "14_sp_dashboard.png"))
                    page2.click("#mc-modal-form-save")
                    time.sleep(3.0)
                except Exception as e:
                    _add_log(run_id, f"⚠ 2. Bölüm — Strateji ekleme atlandı: {str(e).splitlines()[0][:120]}")
                
                vpath2 = page2.video.path() if page2.video else None
                ctx2.close()
            
                if vpath2 and os.path.exists(vpath2):
                    shutil.move(vpath2, os.path.join(video_dir, "3_stratejik_planlama.webm"))
                st["done"] += 1
            
                # ──────────────────────────────────────────────────────────────────────
                # ADIM 4: Süreç ve Performans Göstergesi Videosu
                # ──────────────────────────────────────────────────────────────────────
                _add_log(run_id, "4. Bölüm Videosu: Süreç ve Performans Göstergeleri başlatılıyor...")
                _check_cancel(run_id)
                ctx3 = browser.new_context(
                    ignore_https_errors=True,
                    viewport={"width": 1920, "height": 1080},
                    record_video_dir=video_dir,
                    record_video_size={"width": 1920, "height": 1080}
                )
                page3 = ctx3.new_page()
                page3.goto(base_url + "/login")
                page3.fill("input[name='email']", SYNTH_ADMIN_EMAIL)
                page3.fill("input[name='password']", SYNTH_ADMIN_PW)
                page3.click("button[type='submit']")
                page3.wait_for_load_state("networkidle")
            
                # Süreç sayfasına git
                page3.goto(base_url + "/process")
                page3.wait_for_load_state("networkidle")
                time.sleep(1.5)
            
                # Yeni Süreç ekle (Yeni Süreç modalı) — doğrulanmış seçiciler
                try:
                    page3.wait_for_selector("#btn-surec-add", state="visible", timeout=15000)
                    page3.click("#btn-surec-add")
                    page3.wait_for_selector("#surec-name", state="visible", timeout=12000)
                    page3.fill("#surec-name", "Elektrikli Motor Montaj Süreci")
                    page3.fill("#surec-code", "PRC-MON")
                    # opsiyonel: bir alt-strateji ile ilişkilendir (varsa)
                    try:
                        page3.wait_for_selector("input[id^='ss-']", timeout=4000)
                        page3.locator("input[id^='ss-']").first.check()
                    except Exception:
                        pass
                    _highlight_and_screenshot(page3, "#btn-surec-save", os.path.join(img_dir, "15_process_list.png"))
                    page3.click("#btn-surec-save")
                    time.sleep(3.0)
                except Exception as e:
                    _add_log(run_id, f"⚠ 3. Bölüm — Süreç ekleme atlandı: {str(e).splitlines()[0][:120]}")
                
                vpath3 = page3.video.path() if page3.video else None
                ctx3.close()
            
                if vpath3 and os.path.exists(vpath3):
                    shutil.move(vpath3, os.path.join(video_dir, "4_surec_ve_pg.webm"))
                st["done"] += 1
            
                # ──────────────────────────────────────────────────────────────────────
                # ADIM 5: Proje ve Görev Yönetimi Videosu
                # ──────────────────────────────────────────────────────────────────────
                _add_log(run_id, "5. Bölüm Videosu: Proje ve Görev Yönetimi başlatılıyor...")
                _check_cancel(run_id)
                ctx4 = browser.new_context(
                    ignore_https_errors=True,
                    viewport={"width": 1920, "height": 1080},
                    record_video_dir=video_dir,
                    record_video_size={"width": 1920, "height": 1080}
                )
                page4 = ctx4.new_page()
                page4.goto(base_url + "/login")
                page4.fill("input[name='email']", SYNTH_ADMIN_EMAIL)
                page4.fill("input[name='password']", SYNTH_ADMIN_PW)
                page4.click("button[type='submit']")
                page4.wait_for_load_state("networkidle")
            
                # Proje sayfasına git
                page4.goto(base_url + "/project/new")
                page4.wait_for_load_state("networkidle")
                time.sleep(1.5)
            
                # Proje formu doldur
                page4.fill("input[name='name']", "Montaj Hattı Kalibrasyon Projesi")
                page4.fill("textarea[name='description']", "Hatalı montaj oranlarını %0.5 altına çekmek için kalibrasyon çalışması.")
                _highlight_and_screenshot(page4, "button[type='submit']", os.path.join(img_dir, "16_project_form.png"))
                page4.click("button[type='submit']")
                page4.wait_for_load_state("networkidle")
                time.sleep(1.5)
            
                vpath4 = page4.video.path() if page4.video else None
                ctx4.close()
            
                if vpath4 and os.path.exists(vpath4):
                    shutil.move(vpath4, os.path.join(video_dir, "5_proje_ve_gorev.webm"))
                st["done"] += 1
            
                # ──────────────────────────────────────────────────────────────────────
                # ADIM 6: K-Radar ve İleri Analiz Videosu
                # ──────────────────────────────────────────────────────────────────────
                _add_log(run_id, "6. Bölüm Videosu: K-Radar ve İleri Düzey Analitik başlatılıyor...")
                _check_cancel(run_id)
                ctx5 = browser.new_context(
                    ignore_https_errors=True,
                    viewport={"width": 1920, "height": 1080},
                    record_video_dir=video_dir,
                    record_video_size={"width": 1920, "height": 1080}
                )
                page5 = ctx5.new_page()
                page5.goto(base_url + "/login")
                page5.fill("input[name='email']", SYNTH_ADMIN_EMAIL)
                page5.fill("input[name='password']", SYNTH_ADMIN_PW)
                page5.click("button[type='submit']")
                page5.wait_for_load_state("networkidle")
            
                # K-Radar hub sayfasına git (doğru route: /k-radar — flag gerekmez)
                page5.goto(base_url + "/k-radar")
                page5.wait_for_load_state("networkidle")
                time.sleep(1.5)

                _highlight_and_screenshot(page5, "#kr-hub-root", os.path.join(img_dir, "17_kradar_main.png"))
                time.sleep(1.0)
            
                vpath5 = page5.video.path() if page5.video else None
                ctx5.close()
            
                if vpath5 and os.path.exists(vpath5):
                    shutil.move(vpath5, os.path.join(video_dir, "6_k_radar_analizleri.webm"))
                st["done"] += 1
            
            browser.close()
            
        # ──────────────────────────────────────────────────────────────────────
        # ADIM 7: PDF Kullanım Kılavuzunu Yeni Resimlerle Derleme
        # ──────────────────────────────────────────────────────────────────────
        _check_cancel(run_id)
        _add_log(run_id, "Güncel ekran görüntüleriyle Kullanım Kılavuzu PDF'i derleniyor...")
        
        # docs/compile_guide.py dosyasını çalıştır
        from docs.compile_guide import compile_pdf
        compile_pdf()
        # Ek güvence: PDF gerçekten oluştu mu? (yoksa "done" demeyiz)
        pdf_path = os.path.abspath("docs/kokpitim_master_kullanim_kilavuzu.pdf")
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise RuntimeError("PDF derleme tamamlandı ama dosya oluşmadı/boş.")

        _add_log(run_id, "Kılavuz PDF başarıyla derlendi!")
        st["done"] += 1
        st["status"] = "done"

    except _Cancelled:
        st["status"] = "cancelled"
        _add_log(run_id, "⏹ Çekim durduruldu. O ana kadarki görsellerle TASLAK kılavuz PDF'i derleniyor...")
        try:
            from docs.compile_guide import compile_pdf
            compile_pdf()  # tam kılavuz HTML → PDF (eksik görseller boş görünür)
            _add_log(run_id, "Taslak kılavuz PDF hazır — 'Kılavuz PDF'ini İndir' ile inceleyebilirsiniz.")
        except Exception as e:
            _add_log(run_id, f"⚠ Taslak PDF derlenemedi: {str(e).splitlines()[0][:120]}")
    except Exception as e:
        st["status"] = "error"
        st["error"] = str(e)
        _add_log(run_id, f"FAILURE: Hata oluştu: {e}")
    finally:
        release()
