"""Slack webhook entegrasyonu (Sprint 14.2).

Tenant başına Slack webhook URL'si tutar (tenant_email_configs benzeri).
KPI anomali, faaliyet gecikmesi, kritik risk bildirimi için kullanılır.

Konfigürasyon: tenants.notification_settings JSON field içinde:
    {"slack_webhook_url": "https://hooks.slack.com/services/...", "slack_enabled": true}

Bu modül lock-in olmamak için diğer webhook'lara (Discord, Teams) genişletilebilir.
"""
from __future__ import annotations

import json
from typing import Optional
from urllib import request as _urlreq, error as _urlerr

from flask import current_app


def _get_tenant_webhook(tenant_id: int) -> Optional[str]:
    """Tenant'ın Slack webhook URL'sini settings JSON'undan al."""
    from app.models.core import Tenant
    t = Tenant.query.get(tenant_id)
    if not t:
        return None
    # Tenant model'inde notification_settings yok — şimdilik env veya config'den al
    # Production: tenants tablosuna slack_webhook_url kolonu eklenmeli
    return current_app.config.get(f"SLACK_WEBHOOK_TENANT_{tenant_id}")


def send_slack_message(
    text_msg: str,
    tenant_id: Optional[int] = None,
    webhook_url: Optional[str] = None,
    blocks: Optional[list] = None,
    username: str = "Kokpitim",
    icon_emoji: str = ":bar_chart:",
) -> dict:
    """Slack incoming webhook'a mesaj gönder.

    Args:
        text_msg: Düz metin mesaj
        tenant_id: Webhook URL'sini bulmak için tenant id
        webhook_url: Manuel webhook URL (test için)
        blocks: Slack block kit zengin formatlama
        username: Bot adı
        icon_emoji: Bot ikonu

    Returns:
        {"success": bool, "message": str}
    """
    url = webhook_url or (_get_tenant_webhook(tenant_id) if tenant_id else None)
    if not url:
        return {"success": False, "message": "Slack webhook yapılandırılmamış."}

    payload = {
        "text": text_msg,
        "username": username,
        "icon_emoji": icon_emoji,
    }
    if blocks:
        payload["blocks"] = blocks

    try:
        data = json.dumps(payload).encode("utf-8")
        req = _urlreq.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with _urlreq.urlopen(req, timeout=5) as resp:
            ok = resp.status == 200
            return {"success": ok, "message": "Gönderildi" if ok else f"HTTP {resp.status}"}
    except _urlerr.URLError as e:
        try:
            current_app.logger.error(f"[slack] URL hatası: {e}")
        except Exception:
            pass
        return {"success": False, "message": str(e)}
    except Exception as e:
        try:
            current_app.logger.error(f"[slack] {e}")
        except Exception:
            pass
        return {"success": False, "message": str(e)}


def send_teams_message(text_msg: str, webhook_url: str, title: str = "Kokpitim") -> dict:
    """Microsoft Teams incoming webhook'a mesaj gönder (MessageCard formatı).

    Teams webhook URL formatı: https://*.webhook.office.com/...
    """
    if not webhook_url:
        return {"success": False, "message": "Teams webhook URL boş."}

    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "1A4D80",
        "summary": title,
        "title": title,
        "text": text_msg,
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = _urlreq.Request(
            webhook_url, data=data,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with _urlreq.urlopen(req, timeout=5) as resp:
            return {"success": resp.status == 200, "message": f"HTTP {resp.status}"}
    except _urlerr.URLError as e:
        try:
            current_app.logger.error(f"[teams] {e}")
        except Exception:
            pass
        return {"success": False, "message": str(e)}


def send_discord_message(text_msg: str, webhook_url: str, username: str = "Kokpitim") -> dict:
    """Discord incoming webhook'a mesaj gönder."""
    if not webhook_url:
        return {"success": False, "message": "Discord webhook URL boş."}

    payload = {
        "content": text_msg[:2000],  # Discord limit
        "username": username,
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = _urlreq.Request(
            webhook_url, data=data,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with _urlreq.urlopen(req, timeout=5) as resp:
            return {"success": resp.status in (200, 204), "message": f"HTTP {resp.status}"}
    except _urlerr.URLError as e:
        try:
            current_app.logger.error(f"[discord] {e}")
        except Exception:
            pass
        return {"success": False, "message": str(e)}


def dispatch_webhook(provider: str, text_msg: str, webhook_url: str, **kwargs) -> dict:
    """Provider'a göre webhook gönderim — slack/teams/discord seçimi.

    Args:
        provider: "slack" | "teams" | "discord"
    """
    provider = (provider or "").lower()
    if provider == "slack":
        return send_slack_message(text_msg, webhook_url=webhook_url, **kwargs)
    if provider == "teams":
        return send_teams_message(text_msg, webhook_url=webhook_url, **kwargs)
    if provider == "discord":
        return send_discord_message(text_msg, webhook_url=webhook_url, **kwargs)
    return {"success": False, "message": f"Bilinmeyen provider: {provider}"}


def format_anomaly_blocks(anomaly: dict) -> list:
    """KPI anomali sonucunu Slack block kit formatına çevir."""
    severity_emoji = {"high": ":rotating_light:", "medium": ":warning:", "low": ":information_source:"}.get(
        anomaly.get("severity", "low"), ":grey_question:"
    )
    direction = anomaly.get("direction", "—")
    z = anomaly.get("z_score", 0)
    arrow = "↓" if z < 0 else "↑"
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{severity_emoji} *KPI Anomali Tespit Edildi*\n"
                    f"*Süreç:* `{anomaly.get('process_code', '—')}`\n"
                    f"*KPI:* {anomaly.get('kpi_name', '—')} ({anomaly.get('kpi_code', '—')})\n"
                    f"*Son değer:* {anomaly.get('latest_value', '—')} {arrow}\n"
                    f"*Ortalama:* {anomaly.get('mean', '—')} (σ={anomaly.get('std', '—')})\n"
                    f"*Z-Score:* {z}\n"
                    f"*Yön:* {direction}"
                ),
            },
        }
    ]
