"""Marketing (tanıtım sitesi) route'ları."""
from __future__ import annotations

import os
import re
from datetime import datetime

from flask import (
    abort, current_app, jsonify, redirect, render_template,
    request, url_for,
)

from micro.modules.marketing import marketing_bp

# ── Blog yardımcıları ─────────────────────────────────────────────────────────

BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "content", "blog")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """YAML-benzeri frontmatter'ı parse eder."""
    meta: dict = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            body = parts[2].strip()
    return meta, body


def _get_all_posts() -> list[dict]:
    """Tüm blog yazılarını döndürür (tarih sıralı, en yeni önce)."""
    posts = []
    if not os.path.isdir(BLOG_DIR):
        return posts
    for fname in os.listdir(BLOG_DIR):
        if not fname.endswith(".md"):
            continue
        slug = fname[:-3]
        try:
            with open(os.path.join(BLOG_DIR, fname), encoding="utf-8") as f:
                meta, _ = _parse_frontmatter(f.read())
            posts.append({
                "slug":    slug,
                "title":   meta.get("title", slug),
                "date":    meta.get("date", ""),
                "summary": meta.get("summary", ""),
                "author":  meta.get("author", "Kokpitim"),
            })
        except Exception as e:
            current_app.logger.warning(f"[marketing] blog parse hatası {fname}: {e}")
    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts


def _get_post(slug: str) -> tuple[dict, str] | None:
    """Slug'a göre blog yazısını döndürür."""
    path = os.path.join(BLOG_DIR, f"{slug}.md")
    if not os.path.isfile(path):
        return None
    try:
        import markdown as _md
        with open(path, encoding="utf-8") as f:
            meta, body = _parse_frontmatter(f.read())
        html = _md.markdown(body, extensions=["extra", "codehilite", "toc"])
        return meta, html
    except Exception as e:
        current_app.logger.error(f"[marketing] blog render hatası {slug}: {e}")
        return None


# ── Honeypot spam koruması ────────────────────────────────────────────────────

def _is_spam(form_data: dict) -> bool:
    """Honeypot alanı doluysa spam sayar."""
    return bool(form_data.get("website"))  # gizli alan


# ── Ana Sayfa ─────────────────────────────────────────────────────────────────

@marketing_bp.route("/")
@marketing_bp.route("/home")
def index():
    # Demo subdomain — root daima demo'ya yönlenir
    if current_app.config.get("KOKPITIM_DEMO_MODE"):
        from flask import session as _sess
        from flask_login import current_user as _cu
        if _cu.is_authenticated and _sess.get("demo_session_active"):
            return redirect(url_for("app_bp.launcher"))
        return redirect(url_for("app_bp.demo_landing"))
    return render_template(
        "index.html",
        page_title="Kokpitim — Stratejik Yönetim Platformu",
        page_description=(
            "Strateji, süreç, KPI ve bireysel performansı tek platformda yönetin. "
            "Türkiye'nin kurumsal performans yönetim yazılımı."
        ),
    )


# ── Özellikler ────────────────────────────────────────────────────────────────

@marketing_bp.route("/ozellikler")
def ozellikler():
    return render_template(
        "ozellikler/index.html",
        page_title="Özellikler — Kokpitim",
        page_description="Stratejik planlama, süreç yönetimi, performans takibi, proje yönetimi ve analiz merkezi.",
    )


@marketing_bp.route("/ozellikler/stratejik-planlama")
def stratejik_planlama():
    return render_template(
        "ozellikler/stratejik_planlama.html",
        page_title="Stratejik Planlama — Kokpitim",
        page_description="SWOT, TOWS, OKR, BSC ile stratejik planınızı yıl boyunca canlı tutun.",
    )


@marketing_bp.route("/ozellikler/surec-yonetimi")
def surec_yonetimi():
    return render_template(
        "ozellikler/surec_yonetimi.html",
        page_title="Süreç Yönetimi — Kokpitim",
        page_description="Süreç karnesi, KPI bağlantısı ve tam audit log ile süreçlerinizi ölçün.",
    )


@marketing_bp.route("/ozellikler/performans-takibi")
def performans_takibi():
    return render_template(
        "ozellikler/performans_takibi.html",
        page_title="Performans Takibi — Kokpitim",
        page_description="Otomatik başarı puanı, anomali tespiti ve tahminleme ile KPI'larınızı izleyin.",
    )


@marketing_bp.route("/ozellikler/proje-yonetimi")
def proje_yonetimi():
    return render_template(
        "ozellikler/proje_yonetimi.html",
        page_title="Proje Yönetimi — Kokpitim",
        page_description="Gantt, RAID, EVM ve strateji bağlantısı ile projelerinizi yönetin.",
    )


@marketing_bp.route("/ozellikler/analiz-merkezi")
def analiz_merkezi():
    return render_template(
        "ozellikler/analiz_merkezi.html",
        page_title="K-Radar & K-Rapor — Kokpitim",
        page_description="Kurumsal analitik merkez ve tek tıkla raporlama.",
    )


# ── Nasıl Çalışır? ────────────────────────────────────────────────────────────

@marketing_bp.route("/nasil-calisir")
def nasil_calisir():
    return render_template(
        "nasil_calisir.html",
        page_title="Nasıl Çalışır? — Kokpitim",
        page_description="İlk haftadan itibaren çalışan kurumsal yönetim platformu.",
    )


# ── Demo Talep ────────────────────────────────────────────────────────────────

@marketing_bp.route("/demo-talep", methods=["GET", "POST"])
def demo_talep():
    if request.method == "POST":
        try:
            if _is_spam(request.form):
                return redirect(url_for("marketing_bp.index"))

            ad_soyad   = request.form.get("ad_soyad", "").strip()
            kurum      = request.form.get("kurum", "").strip()
            gorev      = request.form.get("gorev", "").strip()
            sektor     = request.form.get("sektor", "").strip()
            calisan    = request.form.get("calisan", "").strip()
            email      = request.form.get("email", "").strip()
            telefon    = request.form.get("telefon", "").strip()
            moduller   = request.form.getlist("moduller")
            mesaj      = request.form.get("mesaj", "").strip()

            if not all([ad_soyad, kurum, email]):
                return render_template(
                    "demo_talep.html",
                    page_title="Demo Talep — Kokpitim",
                    page_description="30 dakikalık ücretsiz demo için formu doldurun.",
                    error="Ad Soyad, Kurum Adı ve E-posta alanları zorunludur.",
                    form_data=request.form,
                )

            # E-posta gönder
            email_gonderildi = False
            try:
                from micro.services.email_service import send_notification_email
                text_body = f"""Yeni Demo Talebi

Ad Soyad:    {ad_soyad}
Kurum:       {kurum}
Görev:       {gorev}
Sektör:      {sektor}
Çalışan:     {calisan}
E-posta:     {email}
Telefon:     {telefon}
Modüller:    {', '.join(moduller) if moduller else '—'}
Mesaj:       {mesaj or '—'}
Tarih:       {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
                html_body = "<pre>" + text_body + "</pre>"
                email_gonderildi, mail_err = send_notification_email(
                    to_email="info@kokpitim.com",
                    subject=f"Demo Talebi — {kurum} / {ad_soyad}",
                    html_body=html_body,
                    text_body=text_body,
                )
                if not email_gonderildi:
                    current_app.logger.warning(f"[marketing] demo e-posta gönderilemedi: {mail_err}")
            except Exception as mail_err:
                current_app.logger.warning(f"[marketing] demo e-posta gönderilemedi: {mail_err}")

            # DB'ye kaydet (e-posta gönderimi başarısız olsa bile talep kaybolmasın)
            try:
                from extensions import db
                from app.models.marketing import DemoRequest
                db.session.add(DemoRequest(
                    ad_soyad=ad_soyad,
                    kurum=kurum,
                    gorev=gorev,
                    sektor=sektor,
                    calisan=calisan,
                    email=email,
                    telefon=telefon,
                    moduller=", ".join(moduller) if moduller else None,
                    mesaj=mesaj,
                    email_gonderildi=email_gonderildi,
                ))
                db.session.commit()
            except Exception as db_err:
                db.session.rollback()
                current_app.logger.error(f"[marketing] demo talebi DB kaydı başarısız: {db_err}", exc_info=True)

            return render_template(
                "demo_talep.html",
                page_title="Demo Talep — Kokpitim",
                page_description="30 dakikalık ücretsiz demo için formu doldurun.",
                success=True,
            )

        except Exception as e:
            current_app.logger.error(f"[marketing] demo_talep POST hatası: {e}", exc_info=True)
            return render_template(
                "demo_talep.html",
                page_title="Demo Talep — Kokpitim",
                page_description="30 dakikalık ücretsiz demo için formu doldurun.",
                error="Bir hata oluştu. Lütfen tekrar deneyin.",
                form_data=request.form,
            )

    return render_template(
        "demo_talep.html",
        page_title="Demo Talep — Kokpitim",
        page_description="30 dakikalık ücretsiz demo için formu doldurun.",
    )


# ── Blog ──────────────────────────────────────────────────────────────────────

@marketing_bp.route("/blog")
def blog_index():
    posts = _get_all_posts()
    return render_template(
        "blog/index.html",
        page_title="Blog — Kokpitim",
        page_description="Stratejik planlama ve kurumsal performans yönetimi üzerine içerikler.",
        posts=posts,
    )


@marketing_bp.route("/blog/<slug>")
def blog_post(slug: str):
    result = _get_post(slug)
    if result is None:
        abort(404)
    meta, html_content = result
    return render_template(
        "blog/post.html",
        page_title=f"{meta.get('title', slug)} — Kokpitim",
        page_description=meta.get("summary", ""),
        meta=meta,
        html_content=html_content,
    )


# ── İletişim ──────────────────────────────────────────────────────────────────

@marketing_bp.route("/iletisim", methods=["GET", "POST"])
def iletisim():
    if request.method == "POST":
        try:
            if _is_spam(request.form):
                return redirect(url_for("marketing_bp.index"))

            ad_soyad = request.form.get("ad_soyad", "").strip()
            email    = request.form.get("email", "").strip()
            konu     = request.form.get("konu", "").strip()
            mesaj    = request.form.get("mesaj", "").strip()

            if not all([ad_soyad, email, mesaj]):
                return render_template(
                    "iletisim.html",
                    page_title="İletişim — Kokpitim",
                    page_description="Kokpitim ile iletişime geçin.",
                    error="Tüm zorunlu alanları doldurun.",
                    form_data=request.form,
                )

            try:
                from micro.services.email_service import send_email
                send_email(
                    to="info@kokpitim.com",
                    subject=f"İletişim Formu — {konu} / {ad_soyad}",
                    body=f"Ad Soyad: {ad_soyad}\nE-posta: {email}\nKonu: {konu}\n\n{mesaj}",
                )
            except Exception as mail_err:
                current_app.logger.warning(f"[marketing] iletisim e-posta gönderilemedi: {mail_err}")

            return render_template(
                "iletisim.html",
                page_title="İletişim — Kokpitim",
                page_description="Kokpitim ile iletişime geçin.",
                success=True,
            )

        except Exception as e:
            current_app.logger.error(f"[marketing] iletisim POST hatası: {e}", exc_info=True)
            return render_template(
                "iletisim.html",
                page_title="İletişim — Kokpitim",
                page_description="Kokpitim ile iletişime geçin.",
                error="Bir hata oluştu. Lütfen tekrar deneyin.",
                form_data=request.form,
            )

    return render_template(
        "iletisim.html",
        page_title="İletişim — Kokpitim",
        page_description="Kokpitim ile iletişime geçin.",
    )


# ── SEO ───────────────────────────────────────────────────────────────────────

@marketing_bp.route("/sitemap.xml")
def sitemap():
    base = "https://kokpitim.com"
    static_urls = [
        "/", "/ozellikler", "/ozellikler/stratejik-planlama",
        "/ozellikler/surec-yonetimi", "/ozellikler/performans-takibi",
        "/ozellikler/proje-yonetimi", "/ozellikler/analiz-merkezi",
        "/nasil-calisir", "/demo-talep", "/blog", "/iletisim",
    ]
    blog_urls = [f"/blog/{p['slug']}" for p in _get_all_posts()]
    all_urls = static_urls + blog_urls
    today = datetime.now().strftime("%Y-%m-%d")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in all_urls:
        xml += f"  <url><loc>{base}{u}</loc><lastmod>{today}</lastmod></url>\n"
    xml += "</urlset>"
    from flask import Response
    return Response(xml, mimetype="application/xml")


@marketing_bp.route("/robots.txt")
def robots():
    from flask import Response
    txt = "User-agent: *\nAllow: /\nSitemap: https://kokpitim.com/sitemap.xml\n"
    return Response(txt, mimetype="text/plain")
