# -*- coding: utf-8 -*-
"""Paket-gating ortak yardımcıları (kart-düzeyi zorlama — 2026-07-08 revizyonu).

Zincir: Tenant.package → SystemModule → module_component_slugs.component_slug.
Kart tarafı: SystemCard.component_id → SystemComponent.code (= component_slug).

Tutarlı desen (component_visible ile aynı):
- Platform Admin → kısıt yok
- Paketsiz tenant / hata → fail-open (kısıt yok)
- Hiçbir modüle atanmamış component → fail-open (sabit alanlar)
"""


def allowed_component_slugs(user):
    """Kullanıcının paketine açık component_slug kümesi.

    None → kısıtlama yok (Admin / paketsiz / anonim / hata: fail-open)."""
    try:
        if not getattr(user, "is_authenticated", False):
            return None
        if user.role and user.role.name == "Admin":
            return None
        pkg = getattr(user.tenant, "package", None) if user.tenant else None
        if pkg is None:
            return None
        slugs = set()
        for mod in pkg.modules:
            for comp in mod.component_slugs:
                slugs.add(comp.component_slug)
        return slugs
    except Exception:
        import logging

        logging.getLogger(__name__).warning("[package-gating] slug resolution failed", exc_info=True)
        return None


def hidden_card_codes(codes, slugs):
    """Verilen kart kodlarından, kullanıcının paketinde OLMAYAN'ları döner.

    slugs None ise hiçbir kart gizlenmez. Kart→component zinciri kurulamayan
    veya component'i hiçbir modüle atanmamış kartlar fail-open (görünür)."""
    if slugs is None or not codes:
        return []
    from app.models.saas import ModuleComponentSlug, SystemCard, SystemComponent

    rows = (
        SystemCard.query.with_entities(SystemCard.code, SystemComponent.code)
        .join(SystemComponent, SystemCard.component_id == SystemComponent.id)
        .filter(SystemCard.code.in_(list(codes)), SystemCard.is_active.is_(True))
        .all()
    )
    comp_codes = {c for _, c in rows if c}
    if not comp_codes:
        return []
    registered = {
        r[0]
        for r in ModuleComponentSlug.query.with_entities(
            ModuleComponentSlug.component_slug
        )
        .filter(ModuleComponentSlug.component_slug.in_(list(comp_codes)))
        .all()
    }
    hidden = []
    for card_code, comp_code in rows:
        if comp_code and comp_code in registered and comp_code not in slugs:
            hidden.append(card_code)
    return hidden
