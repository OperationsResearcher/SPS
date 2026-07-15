# -*- coding: utf-8 -*-
"""Yerel LLM (veri ikametgâhı) yolu — TASK-265.

BULGU: Bu özellik ZATEN ÇALIŞIYOR ama belgesizdi. `provider=openai` +
`base_url=<kendi sunucu>` verildiğinde çağrı OpenAI'a değil o adrese gider;
Ollama/vLLM OpenAI-uyumlu API sunduğu için kurumun kendi modeli kullanılır.

NEDEN ÖNEMLİ: KVKK hiçbir ülkeye yeterlilik kararı vermemiş → her yurt dışı
LLM çağrısı "uygun güvence + 5 iş günü bildirim" yüküne giriyor. Yerel LLM'de
veri kurumun ağından hiç çıkmaz.

Bu testler yolun sessizce bozulmasını engeller — `base_url` zincirin
herhangi bir halkasında düşerse veri yurt dışına gider ve KİMSE FARK ETMEZ.
"""
import pytest

from app.models import db
from app.models.core import Tenant
from app.models.tenant_llm_config import TenantLLMConfig


@pytest.fixture
def yerel_llm_tenant(app):
    """Kendi sunucusundaki Ollama'yı kullanan kurum."""
    with app.app_context():
        t = Tenant(name="KVKK T", short_name="kvkkt", is_active=True)
        db.session.add(t)
        db.session.commit()

        cfg = TenantLLMConfig(
            tenant_id=t.id,
            provider="openai",                     # OpenAI-uyumlu API
            model="llama3.1:70b",
            base_url="http://10.0.0.5:11434/v1",   # kurumun kendi sunucusu
            is_active=True,
        )
        cfg.set_api_key("ollama")
        db.session.add(cfg)
        db.session.commit()
        yield t.id


def test_base_url_cozumlemede_korunuyor(app, yerel_llm_tenant):
    """ASIL KORUMA: base_url zincirde düşerse veri OpenAI'a (yurt dışına)
    gider ve kimse fark etmez."""
    from app.services.llm_gateway import _resolve_provider

    with app.app_context():
        r = _resolve_provider(yerel_llm_tenant)

        assert r["provider"] == "openai"
        assert r["base_url"] == "http://10.0.0.5:11434/v1", (
            "base_url kayboldu — cagri kurumun sunucusuna DEGIL OpenAI'a gider"
        )
        assert r["model"] == "llama3.1:70b"


def test_yerel_llm_sistem_kotasina_yazilmaz(app, yerel_llm_tenant):
    """BYOK = tenant kendi faturasını yönetir; sistem kotası harcanmamalı."""
    from app.services.llm_gateway import _resolve_provider

    with app.app_context():
        r = _resolve_provider(yerel_llm_tenant)
        assert r.get("count_against_system_quota") is False


def test_api_key_sifreli_saklaniyor(app, yerel_llm_tenant):
    """Yerel LLM'de bile key şifreli — savunma derinliği."""
    with app.app_context():
        cfg = TenantLLMConfig.query.filter_by(tenant_id=yerel_llm_tenant).first()
        assert cfg.api_key_encrypted
        assert "ollama" not in cfg.api_key_encrypted, "Key duz metin saklanmis!"
        assert cfg.api_key_plain == "ollama", "Sifre cozulemedi"


def test_pii_maskeleme_varsayilan_acik(app, yerel_llm_tenant):
    """Yerel LLM veri ikametgâhını çözer ama PII maskeleme yine de açık
    olmalı (savunma derinliği — model log tutabilir)."""
    with app.app_context():
        cfg = TenantLLMConfig.query.filter_by(tenant_id=yerel_llm_tenant).first()
        assert cfg.pii_mask_enabled is True


def test_base_url_yoksa_resmi_apiye_gider(app):
    """base_url verilmemişse davranış değişmemeli (geriye dönük uyum)."""
    from app.services.llm_gateway import _resolve_provider

    with app.app_context():
        t = Tenant(name="Bulut T", short_name="bulutt", is_active=True)
        db.session.add(t)
        db.session.commit()

        cfg = TenantLLMConfig(
            tenant_id=t.id, provider="openai", model="gpt-4o-mini",
            base_url=None, is_active=True,
        )
        cfg.set_api_key("sk-test")
        db.session.add(cfg)
        db.session.commit()

        r = _resolve_provider(t.id)
        assert r["base_url"] is None, "base_url yokken None kalmali"


def test_pasif_config_kullanilmaz(app, yerel_llm_tenant):
    """is_active=False → tenant BYOK devre dışı, sistem default'a düşer."""
    from app.services.llm_gateway import _resolve_provider

    with app.app_context():
        cfg = TenantLLMConfig.query.filter_by(tenant_id=yerel_llm_tenant).first()
        cfg.is_active = False
        db.session.commit()

        r = _resolve_provider(yerel_llm_tenant)
        assert r["base_url"] != "http://10.0.0.5:11434/v1", (
            "Pasif config hala kullaniliyor"
        )
