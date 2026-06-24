# -*- coding: utf-8 -*-
"""Otomatik KART keşfi — template'lerdeki data-card-* işaretlerini tarar.

İşaretleme şeması (template):
  Kart konteyneri:
    data-card-code="kurum_ozet_kartlar"        (zorunlu — kart kodu)
    data-card-name="Kurum Özet Kartları"       (opsiyonel — görünen ad)
    data-card-component="surec_performansi_karti" (opsiyonel — bağlı bileşen)
  Veri parçası (kart içinde):
    data-card-key="process_count"              (zorunlu — veri anahtarı)
    data-card-label="Aktif Süreç"              (opsiyonel — etiket)
    data-requires="surec_performansi_karti"    (opsiyonel — gereken bileşen)

Keşif idempotent: var olan kart/veri güncellenir, yeni eklenir. Silinen işaret
→ kart is_active=False (bırakılır, RouteRegistry felsefesi: tekrar tetiklenebilir).

Admin'den tetiklenir (RouteRegistry sync gibi). Saf okuma + DB seed.
"""
from __future__ import annotations

import re
from pathlib import Path

from flask import current_app

from extensions import db
from app.models.saas import SystemCard, CardDataSource, SystemComponent


# data-card-code="..." ve aynı div'in tüm attribute bloğunu yakala
_CARD_RE = re.compile(r'data-card-code\s*=\s*"([^"]+)"')
_ATTR_RE = lambda name: re.compile(name + r'\s*=\s*"([^"]*)"')  # noqa: E731
_KEY_RE = re.compile(r'data-card-key\s*=\s*"([^"]+)"')


def _templates_dir() -> Path:
    # ui/templates/platform
    return Path(current_app.root_path).parent / "ui" / "templates" / "platform"


def _attr(tag_text: str, name: str) -> str | None:
    m = _ATTR_RE(name).search(tag_text)
    return m.group(1) if m else None


def _scan_file(text: str) -> list[dict]:
    """Bir template metninden kartları + veri anahtarlarını çıkar.

    Basit yaklaşım: her data-card-code işaretli açılış tag'ini bul; o tag'ten
    sonraki metinde (bir sonraki data-card-code'a kadar) data-card-key'leri topla.
    """
    cards = []
    # data-card-code'lu açılış tag pozisyonları
    code_positions = [(m.start(), m.group(1)) for m in _CARD_RE.finditer(text)]
    if not code_positions:
        return cards
    bounds = [p[0] for p in code_positions] + [len(text)]
    for i, (pos, code) in enumerate(code_positions):
        # JS/Jinja literal'lerini atla: data-card-code="${code}", "{{ ... }}" gibi
        # dinamik ifadeler gerçek kart kodu değildir (sadece runtime'da değer alır).
        if "${" in code or "{{" in code or "}" in code:
            continue
        segment = text[pos:bounds[i + 1]]
        # kart açılış tag'i: pos'tan ilk '>' kadar
        open_tag = segment[: segment.find(">") + 1] if ">" in segment else segment
        name = _attr(open_tag, "data-card-name") or code
        component = _attr(open_tag, "data-card-component")
        # veri anahtarları: segment içindeki tüm data-card-key blokları
        keys = []
        for km in re.finditer(r'<[^>]*data-card-key\s*=\s*"[^"]+"[^>]*>', segment):
            tag = km.group(0)
            keys.append({
                "data_key": _attr(tag, "data-card-key"),
                "label": _attr(tag, "data-card-label"),
                "required_component_code": _attr(tag, "data-requires"),
            })
        cards.append({"code": code, "name": name,
                      "component": component, "keys": keys})
    return cards


def discover_cards(dry_run: bool = False) -> dict:
    """Tüm platform template'lerini tara, SystemCard + CardDataSource'a yansıt.

    Döner: {"cards": n, "data_sources": n, "files": n, "details": [...]}
    """
    tdir = _templates_dir()
    if not tdir.exists():
        return {"ok": False, "error": f"Template dizini yok: {tdir}"}

    comp_by_code = {c.code: c for c in SystemComponent.query.all()}
    found_cards: dict[str, dict] = {}
    scanned_files = 0

    for path in tdir.rglob("*.html"):
        try:
            txt = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if "data-card-code" not in txt:
            continue
        scanned_files += 1
        for card in _scan_file(txt):
            # aynı kart birden çok dosyada olabilir → keys birleştir
            slot = found_cards.setdefault(card["code"], {
                "name": card["name"], "component": card["component"], "keys": {}})
            for k in card["keys"]:
                if k["data_key"]:
                    slot["keys"][k["data_key"]] = k

    card_n = 0
    ds_n = 0
    details = []
    for code, info in found_cards.items():
        card = SystemCard.query.filter_by(code=code).first()
        comp = comp_by_code.get(info["component"]) if info["component"] else None
        if not card:
            card = SystemCard(code=code, name=info["name"],
                              component_id=comp.id if comp else None,
                              is_active=True)
            if not dry_run:
                db.session.add(card)
                db.session.flush()
            card_n += 1
        else:
            card.name = info["name"]
            card.is_active = True
            if comp:
                card.component_id = comp.id
        # veri kaynakları (idempotent upsert)
        for dk, k in info["keys"].items():
            existing = None
            if card.id:
                existing = CardDataSource.query.filter_by(
                    card_id=card.id, data_key=dk).first()
            if not existing:
                if not dry_run and card.id:
                    db.session.add(CardDataSource(
                        card_id=card.id, data_key=dk,
                        required_component_code=k.get("required_component_code"),
                        label=k.get("label"), is_active=True))
                ds_n += 1
            else:
                existing.required_component_code = k.get("required_component_code")
                existing.label = k.get("label")
                existing.is_active = True
        details.append({"code": code, "keys": list(info["keys"].keys())})

    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()

    return {"ok": True, "files": scanned_files, "cards": card_n,
            "data_sources": ds_n, "details": details}
