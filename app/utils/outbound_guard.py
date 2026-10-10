"""Giden isteklerde SSRF koruması (GUV-05/06).

Kullanıcının verdiği URL / host'a sunucudan istek atan her yer bu modülü kullanır.
Kural: hedef adresin TÜM çözümlenmiş IP'leri global olmalı (özel, loopback,
link-local, rezerve, multicast reddedilir) ve yönlendirme (redirect) izlenmez.

Not: doğrulama ile bağlantı arasındaki DNS rebinding penceresi tamamen kapatılmaz
(IP sabitleme sertifika doğrulamasını bozar); yönlendirme kapalı olduğu için
pratik risk düşüktür.
"""
from __future__ import annotations

import ipaddress
import socket
import urllib.parse
from urllib import request as _urlreq

_MSG_BLOCKED = "İç ağ adreslerine istek gönderilemez"


def is_public_host(host: str, port: int | None = None) -> tuple[bool, str]:
    """Host'un çözümlenen tüm adresleri global mi? (ok, hata_mesajı)."""
    host = (host or "").strip().strip("[]")
    if not host:
        return False, "Adres gerekli"
    try:
        infos = socket.getaddrinfo(host, port or 443, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError):
        return False, "Adres çözümlenemedi"
    if not infos:
        return False, "Adres çözümlenemedi"
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global or ip.is_multicast:
            return False, _MSG_BLOCKED
    return True, ""


def validate_outbound_url(url: str) -> tuple[bool, str]:
    """Yalnız https, kullanıcı bilgisiz, global IP'ye çözümlenen URL'leri kabul eder."""
    if not url:
        return False, "webhook_url gerekli"
    try:
        p = urllib.parse.urlparse(url)
        port = p.port
    except ValueError:
        return False, "Geçersiz URL"
    if p.scheme != "https":
        return False, "Yalnızca https URL'ler kabul edilir"
    if p.username or p.password:
        return False, "URL kullanıcı bilgisi içeremez"
    return is_public_host(p.hostname or "", port)


class _NoRedirect(_urlreq.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


_opener = _urlreq.build_opener(_NoRedirect)


def open_no_redirect(req: _urlreq.Request, timeout: float = 5):
    """urllib isteği; 3xx yanıtları izlenmez (HTTPError olarak döner)."""
    return _opener.open(req, timeout=timeout)


SMTP_ALLOWED_PORTS = (25, 465, 587, 2525)


def validate_smtp_target(host: str, port) -> tuple[bool, str]:
    """Kurum SMTP hedefi: izinli port + global IP (GUV-06)."""
    try:
        port_i = int(port)
    except (TypeError, ValueError):
        return False, "Geçersiz port"
    if port_i not in SMTP_ALLOWED_PORTS:
        return False, "SMTP portu 25, 465, 587 veya 2525 olmalıdır"
    return is_public_host(host, port_i)


_METADATA_IPS = {
    ipaddress.ip_address("169.254.169.254"),  # AWS/GCP/Azure/Oracle metadata
    ipaddress.ip_address("fd00:ec2::254"),
}


def validate_llm_base_url(url: str, allow_private: bool = False) -> tuple[bool, str]:
    """Kurumun LLM base_url'ini doğrular (GV-002).

    - Yalnız http/https, kullanıcı bilgisi yok.
    - Link-local / metadata / multicast / unspecified HER ZAMAN reddedilir.
    - Özel ağ ve loopback yalnız ``allow_private`` açıkken (kurum içi kurulum,
      Yerel LLM / Ollama — TASK-265) kabul edilir. Bulutta barındırılan
      ortamlarda kapalıdır; aksi halde sunucunun iç ağına istek atılabilir.
    """
    if not url:
        return True, ""
    try:
        p = urllib.parse.urlparse(url)
        port = p.port
    except ValueError:
        return False, "Geçersiz URL"
    if p.scheme not in ("http", "https"):
        return False, "Yalnızca http/https URL'ler kabul edilir"
    if p.username or p.password:
        return False, "URL kullanıcı bilgisi içeremez"
    host = (p.hostname or "").strip().strip("[]")
    if not host:
        return False, "Adres gerekli"
    try:
        infos = socket.getaddrinfo(host, port or (443 if p.scheme == "https" else 80),
                                   proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError):
        return False, "Adres çözümlenemedi"
    if not infos:
        return False, "Adres çözümlenemedi"
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip in _METADATA_IPS or ip.is_link_local or ip.is_multicast
                or ip.is_unspecified or ip.is_reserved):
            return False, _MSG_BLOCKED
        if not ip.is_global and not allow_private:
            return False, _MSG_BLOCKED
    return True, ""
