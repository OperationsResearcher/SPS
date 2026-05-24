#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docs/test/kokpitimtanitim.md'yi screenshot'ları gömerek PDF'e dönüştürür.

Kullanım:
    .venv/Scripts/python scripts/docs/build_tanitim_pdf.py

Gereksinimler:
    pip install weasyprint markdown pygments
    (WeasyPrint Windows için ek lib gerektirebilir — yoksa reportlab fallback HTML üretir)

Çıktı:
    docs/test/kokpitimtanitim.pdf  (veya .html fallback)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Windows cp1254 encoding sorunu için stdout'u UTF-8'e zorla
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).parent.parent.parent
SCREENSHOTS_DIR = ROOT / "docs" / "test" / "screenshots"

# Hangi md'yi PDF'e çevireceğimiz — komut satırı argümanı (varsayılan tanıtım)
if len(sys.argv) > 1:
    MD_FILE = Path(sys.argv[1]).resolve()
else:
    MD_FILE = ROOT / "docs" / "test" / "kokpitimtanitim.md"

OUT_PDF = MD_FILE.with_suffix(".pdf")
OUT_HTML = MD_FILE.with_suffix(".html")

# Belge başlığı + kapak alt yazısı (md'nin ilk H1'inden çıkar)
DOC_TITLE = MD_FILE.stem.replace("_", " ").title()


# ─── Screenshot enjekte edilecek bölümler ────────────────────────────────────
# Markdown'daki H2/H3 başlıklarına göre eşleme — her başlık altına ekran görüntüsü ekler

# Tanıtım belgesi için screenshot eşlemeleri
INJECT_TANITIM = {
    "## 1. Kokpitim Nedir":                          "01-masaustu",
    "### 5.1 Stratejik Planlama":                    "02-sp-anasayfa",
    "### 5.2 Süreç Yönetimi":                        "16-surec-listesi",
    "### 5.3 K-Radar":                               "15-k-radar",
    "### 5.5 Proje Yönetimi":                        "18-projeler",
    "### 5.6 Bireysel Performans":                   "17-bireysel-karne",
    "### 5.7 Kurum":                                 "20-bildirim",
    "## 9. AI/LLM Sistemi":                          "13-ai-ayarlari",
}

# Kurulum rehberi için screenshot eşlemeleri
INJECT_REHBER = {
    "## ADIM 2 — Kurum Profili":                     "01-masaustu",
    "## ADIM 3 — Kurumsal Kimlik":                   "02-sp-anasayfa",
    "## ADIM 4 — İlk Plan Yılı":                     "03-plan-yillari",
    "## ADIM 5 — Ana ve Alt Stratejiler":            "02-sp-anasayfa",
    "## ADIM 6 — Süreçler":                          "16-surec-listesi",
    "## ADIM 10 — Bireysel PG":                      "17-bireysel-karne",
    "## ADIM 12 — Initiative":                       "06-initiatives",
    "## ADIM 14 — Hoshin / Blue Ocean / VRIO":       "08-hoshin-xmatrix",
    "## ADIM 15 — Replan Trigger":                   "11-replan-triggers",
    "## ADIM 16 — AI Yapılandırması":                "13-ai-ayarlari",
    "## ADIM 17 — Bildirim ve E-posta":              "20-bildirim",
    "## İlk Exec Dashboard Görüntüleme":             "04-exec-dashboard",
    "## İlk Çeyreklik Review":                       "05-ceyreklik-review",
}

# Hangi haritayı kullan? Dosya adına göre
SCREENSHOT_INJECT = INJECT_REHBER if "rehber" in MD_FILE.stem.lower() or "kurulum" in MD_FILE.stem.lower() else INJECT_TANITIM

# Galeri varsayılan: tanıtımda var, rehberde yok (rehber zaten lineer)
INCLUDE_GALLERY = "rehber" not in MD_FILE.stem.lower() and "kurulum" not in MD_FILE.stem.lower()


CSS = """
@page {
    size: A4;
    margin: 18mm 16mm;
    @bottom-right {
        content: "Sayfa " counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #94a3b8;
        font-family: 'Segoe UI', sans-serif;
    }
    @bottom-left {
        content: "Kokpitim Tanıtım Belgesi — v1.0 — 2026-05-24";
        font-size: 9pt;
        color: #94a3b8;
        font-family: 'Segoe UI', sans-serif;
    }
}
@page :first {
    @bottom-left { content: ""; }
    @bottom-right { content: ""; }
}

body {
    font-family: 'Segoe UI', 'Inter', sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10.5pt;
}

h1 {
    color: #0f172a;
    font-size: 24pt;
    border-bottom: 3px solid #4f46e5;
    padding-bottom: 8px;
    page-break-after: avoid;
    margin-top: 28pt;
}
h1:first-of-type {
    margin-top: 0;
    page-break-before: avoid;
}
h2 {
    color: #1e293b;
    font-size: 16pt;
    margin-top: 18pt;
    page-break-after: avoid;
    border-left: 4px solid #4f46e5;
    padding-left: 10px;
}
h3 {
    color: #334155;
    font-size: 13pt;
    margin-top: 14pt;
    page-break-after: avoid;
}
h4 {
    color: #475569;
    font-size: 11pt;
    margin-top: 10pt;
    page-break-after: avoid;
}

p { margin: 6pt 0; }
ul, ol { margin: 6pt 0; padding-left: 22pt; }
li { margin: 3pt 0; }

code {
    background: #f1f5f9;
    padding: 1pt 5pt;
    border-radius: 3pt;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9.5pt;
    color: #4f46e5;
}
pre {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #4f46e5;
    padding: 10pt;
    border-radius: 4pt;
    font-family: 'Consolas', monospace;
    font-size: 9pt;
    overflow-x: auto;
    line-height: 1.4;
    page-break-inside: avoid;
}
pre code { background: transparent; color: #1e293b; padding: 0; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}
th {
    background: #4f46e5;
    color: #ffffff;
    padding: 6pt 8pt;
    text-align: left;
    font-weight: 600;
}
td {
    padding: 5pt 8pt;
    border-bottom: 1px solid #e2e8f0;
}
tr:nth-child(even) td { background: #f8fafc; }

blockquote {
    border-left: 4px solid #f59e0b;
    background: #fffbeb;
    padding: 8pt 12pt;
    margin: 8pt 0;
    color: #78350f;
    font-style: italic;
    page-break-inside: avoid;
}

a { color: #4f46e5; text-decoration: none; }

img.screenshot {
    max-width: 100%;
    border: 1px solid #cbd5e1;
    border-radius: 4pt;
    box-shadow: 0 2pt 4pt rgba(0,0,0,0.06);
    margin: 10pt 0;
    page-break-inside: avoid;
}
.screenshot-caption {
    text-align: center;
    color: #64748b;
    font-size: 9pt;
    font-style: italic;
    margin-top: -4pt;
    margin-bottom: 12pt;
}

.cover {
    text-align: center;
    padding-top: 60mm;
    page-break-after: always;
}
.cover h1 {
    border: none;
    font-size: 40pt;
    color: #4f46e5;
    margin-bottom: 12pt;
}
.cover .subtitle {
    font-size: 16pt;
    color: #64748b;
    margin-bottom: 60pt;
}
.cover .meta {
    color: #94a3b8;
    font-size: 11pt;
    line-height: 1.8;
}

.toc-note {
    background: #eef2ff;
    border-left: 4px solid #4f46e5;
    padding: 10pt 14pt;
    margin: 12pt 0;
    border-radius: 3pt;
    font-size: 10pt;
    color: #312e81;
    page-break-inside: avoid;
}

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 14pt 0;
}

.gallery {
    page-break-before: always;
}
.gallery h2 { margin-top: 0; }
.gallery-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10pt;
}
"""


def inject_screenshots(md_text: str) -> str:
    """Belirtilen başlıkların altına screenshot img tag ekler."""
    lines = md_text.split("\n")
    out = []
    for line in lines:
        out.append(line)
        line_stripped = line.strip()
        for heading, shot_prefix in SCREENSHOT_INJECT.items():
            if line_stripped.startswith(heading):
                # Screenshot dosyası var mı?
                matches = list(SCREENSHOTS_DIR.glob(f"{shot_prefix}*.png"))
                if matches:
                    rel = matches[0].relative_to(ROOT / "docs" / "test").as_posix()
                    out.append("")
                    out.append(f'<img src="{rel}" class="screenshot" alt="{shot_prefix}">')
                    out.append(f'<div class="screenshot-caption">{matches[0].name}</div>')
                    out.append("")
                break
    return "\n".join(out)


def build_gallery_html() -> str:
    """Tüm screenshot'ları sıralı gösteren galeri bölümü."""
    if not INCLUDE_GALLERY:
        return ""
    shots = sorted(SCREENSHOTS_DIR.glob("*.png"))
    if not shots:
        return ""
    html = ['<div class="gallery">',
            "<h2>📸 Ekran Görüntüleri Galerisi</h2>",
            '<p style="color:#64748b;">Aşağıda Kokpitim platformunun ana ekranlarının tam görüntüleri yer almaktadır.</p>',
            '<div class="gallery-grid">']
    for shot in shots:
        rel = shot.relative_to(ROOT / "docs" / "test").as_posix()
        nice_name = shot.stem.split("-", 1)[-1].replace("-", " ").title()
        html.append(f'<div>')
        html.append(f'  <h3>{nice_name}</h3>')
        html.append(f'  <img src="{rel}" class="screenshot" alt="{shot.stem}">')
        html.append(f'</div>')
    html.append("</div></div>")
    return "\n".join(html)


def build_cover_html() -> str:
    is_rehber = "rehber" in MD_FILE.stem.lower() or "kurulum" in MD_FILE.stem.lower()
    if is_rehber:
        subtitle1 = "Tenant Admin için"
        subtitle2 = "Sıfırdan Sona Kurulum Rehberi"
        meta = (
            "Versiyon 1.0<br>25 Mayıs 2026<br><br>"
            "17 Adım · Tahmini 4-6 Saat<br>"
            "Profil → Kurumsal Kimlik → Strateji → Süreç → KPI → Kullanıcılar"
        )
    else:
        subtitle1 = "Kurumsal Performans İşletim Sistemi"
        subtitle2 = "Kapsamlı Tanıtım Belgesi"
        meta = (
            "Versiyon 1.0<br>24 Mayıs 2026<br><br>"
            "Stratejik Planlama · KPI Yönetimi · OKR · BSC · Hoshin Kanri<br>"
            "Multi-tenant SaaS · KVKK Uyumlu · Türkçe-first"
        )
    return f"""
<div class="cover">
  <h1>KOKPİTİM</h1>
  <div class="subtitle">{subtitle1}</div>
  <div class="subtitle">{subtitle2}</div>
  <div class="meta">{meta}</div>
</div>
"""


def main():
    if not MD_FILE.exists():
        print(f"HATA: {MD_FILE} bulunamadı")
        sys.exit(1)

    # 1. Markdown → HTML
    try:
        import markdown
    except ImportError:
        print("HATA: 'markdown' paketi yok. Yükle:")
        print("  pip install markdown pygments")
        sys.exit(1)

    md_text = MD_FILE.read_text(encoding="utf-8")
    md_text = inject_screenshots(md_text)

    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "nl2br"])
    body_html = md.convert(md_text)
    gallery = build_gallery_html()
    cover = build_cover_html()

    html = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>Kokpitim Tanıtım</title>
<style>{CSS}</style>
</head>
<body>
{cover}
{body_html}
{gallery}
</body>
</html>"""

    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"HTML üretildi: {OUT_HTML} ({len(html)//1024} KB)")

    # 2. HTML → PDF — Önce Playwright (Windows uyumlu), sonra WeasyPrint fallback
    try:
        from playwright.sync_api import sync_playwright
        print("PDF üretimi: Playwright/Chromium kullanılıyor...")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context()
            page = ctx.new_page()
            page.goto(OUT_HTML.as_uri(), wait_until="domcontentloaded")
            page.wait_for_timeout(1500)  # CSS/img yüklensin
            page.pdf(
                path=str(OUT_PDF),
                format="A4",
                margin={"top": "18mm", "bottom": "18mm", "left": "16mm", "right": "16mm"},
                print_background=True,
                display_header_footer=True,
                header_template="<div></div>",
                footer_template='<div style="font-size:8pt;color:#94a3b8;width:100%;text-align:center;padding:0 16mm;font-family:sans-serif;">'
                                'Kokpitim Tanıtım Belgesi · v1.0 · '
                                '<span class="pageNumber"></span> / <span class="totalPages"></span></div>',
            )
            browser.close()
        size = OUT_PDF.stat().st_size // 1024
        print(f"✓ PDF üretildi: {OUT_PDF} ({size} KB)")
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"Playwright PDF hatası: {e}")

    # Fallback: WeasyPrint
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html, base_url=str(ROOT / "docs" / "test")).write_pdf()
        OUT_PDF.write_bytes(pdf_bytes)
        print(f"PDF üretildi (WeasyPrint): {OUT_PDF} ({len(pdf_bytes)//1024} KB)")
        return True
    except Exception as e:
        print(f"UYARI: PDF üretilemedi: {e}")
        print(f"HTML mevcut: {OUT_HTML}")
        return False


if __name__ == "__main__":
    main()
