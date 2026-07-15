# -*- coding: utf-8 -*-
"""base.html — KURALLAR §3 "inline <script>/<style> yasak" koruması.

2026-07-15: base.html'de 6 inline <script> (271 satır) + 2 inline <style>
(42 satır) + inline style=""/onclick="" attribute'ları vardı. Saf JS/CSS
olanlar harici dosyalara taşındı; Jinja ifadesi İÇEREN script blokları
kaldı (veri enjeksiyonu — data-* refactor'ü ayrı iş).

Bu testler geriye gidişi engeller: yeni inline <style> eklenemez, taşınan
varlıklar sayfadan düşerse fark edilir.
"""
import re

import pytest
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import User, Tenant, Role

BASE_HTML = "ui/templates/platform/base.html"

# Jinja içerdiği için ŞU AN taşınamayan script blokları. Bu sayı ARTMAMALI.
# Azalırsa (data-* refactor'ü yapılırsa) burayı düşür.
IZIN_VERILEN_INLINE_SCRIPT = 5


@pytest.fixture
def oturumlu_client(app):
    """base.html render eden gerçek bir platform sayfası için giriş yapmış kullanıcı."""
    with app.app_context():
        t = Tenant(name="Base T", short_name="baset", is_active=True)
        db.session.add(t)
        db.session.flush()
        r = Role(name="tenant_admin", description="a")
        db.session.add(r)
        db.session.flush()
        u = User(
            email="base@local.test", first_name="B", last_name="T",
            tenant_id=t.id, role_id=r.id,
            password_hash=generate_password_hash("x"), is_active=True,
        )
        db.session.add(u)
        db.session.commit()
        uid = u.id

    c = app.test_client()
    with c.session_transaction() as s:
        s["_user_id"] = str(uid)
        s["_fresh"] = True
    return c


def _base_kaynak() -> str:
    with open(BASE_HTML, encoding="utf-8") as f:
        return f.read()


def _render_edilen_kaynak() -> str:
    """Jinja yorumları ({# … #}) çıkarılmış kaynak.

    Yorum içindeki kod render EDİLMEZ; kural ihlali sayılmaz. Örn. Kule
    yardımcı sistemi ERTELENDİ (E1) ve tüm bloğu yorumda bekliyor.
    """
    return re.sub(r"\{#.*?#\}", "", _base_kaynak(), flags=re.S)


# ─── Kaynak dosya kuralları ──────────────────────────────────────────────────

def test_base_html_inline_style_blogu_icermez():
    """KURALLAR §3: inline <style> yasak — harici CSS dosyasına taşı."""
    bloklar = re.findall(r"<style[^>]*>", _render_edilen_kaynak())
    assert not bloklar, (
        f"base.html'e {len(bloklar)} inline <style> eklenmiş. "
        f"ui/static/platform/css/ altına taşı ve <link> ile bağla."
    )


def test_base_html_onclick_attribute_icermez():
    """Davranış markup'ta olmaz — JS dosyasında addEventListener kullan."""
    bulunan = re.findall(r'\sonclick="', _render_edilen_kaynak())
    assert not bulunan, (
        f"base.html'de {len(bulunan)} onclick=\"\" var. İlgili JS dosyasına "
        f"addEventListener olarak taşı (örn. command_palette.js)."
    )


def test_base_html_inline_script_sayisi_artmamis():
    """Kalan inline script'ler Jinja veri enjeksiyonu içeriyor (i18n sözlüğü,
    url_for, kart sistemi). Sayı artıyorsa yeni ihlal eklenmiş demektir."""
    bloklar = re.findall(r"<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>", _render_edilen_kaynak(), re.S)
    assert len(bloklar) <= IZIN_VERILEN_INLINE_SCRIPT, (
        f"base.html'de {len(bloklar)} inline <script> var, izin verilen "
        f"{IZIN_VERILEN_INLINE_SCRIPT}. Yeni JS'i harici dosyaya yaz."
    )


def test_kalan_inline_scriptler_gercekten_jinja_iceriyor():
    """Kalanlar 'Jinja gerekiyor' diye muaf — biri saf JS'e dönüşmüşse taşınmalı."""
    bloklar = re.findall(r"<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>", _render_edilen_kaynak(), re.S)
    saf_js = [
        b.strip()[:80] for b in bloklar
        if not re.search(r"\{\{.*?\}\}|\{%.*?%\}", b) and b.strip()
    ]
    # FOUC önleyici tema bloğu bilinçli inline (harici dosya geç yüklenir → titreme)
    saf_js = [b for b in saf_js if "kk_theme" not in b and "data-theme" not in b]
    assert not saf_js, (
        f"Bu inline script'ler Jinja içermiyor → harici dosyaya taşınabilir:\n"
        + "\n".join(f"  - {s}" for s in saf_js)
    )


# ─── Render doğrulaması: taşınan varlıklar gerçekten yükleniyor mu ───────────

@pytest.mark.parametrize("varlik", [
    "chart_defaults.js",   # Chart.js global ayarları
    "card_layer.css",      # kart kısa-ID rozeti + (i) modalı
    "topbar_search.css",   # Ctrl+K arama butonu
])
def test_tasinan_varlik_sayfada_yukleniyor(oturumlu_client, varlik):
    """Taşıma sırasında <link>/<script> bağlamayı unutmak = sessiz görsel bozulma."""
    resp = oturumlu_client.get("/desktop-launcher")
    assert resp.status_code == 200
    assert varlik in resp.data.decode("utf-8", errors="ignore"), (
        f"'{varlik}' base.html'den yüklenmiyor — taşındı ama bağlanmamış olabilir."
    )


def test_arama_butonu_render_ediliyor(oturumlu_client):
    """onclick kaldırıldı; buton hâlâ basılmalı (JS ayrıca event bağlar)."""
    resp = oturumlu_client.get("/desktop-launcher")
    html = resp.data.decode("utf-8", errors="ignore")
    assert "topbar-search-btn" in html
    assert "onclick=" not in html, "Render edilen sayfada onclick kalmamalı"
