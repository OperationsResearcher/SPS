# -*- coding: utf-8 -*-
"""K-Vektör yapılandırması: ağırlık okuma/yazma ve snapshot (kurum + SP API ortak)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app

from app.models import db
from app.models.core import Strategy, SubStrategy, Tenant
from app.models.k_vektor import (
    KVektorConfigSnapshot,
    KVektorStrategyWeight,
    KVektorSubStrategyWeight,
)


def add_k_vektor_snapshot(
    tenant_id: int,
    user_id: Optional[int],
    snapshot_type: str,
    payload: Dict[str, Any],
) -> None:
    row = KVektorConfigSnapshot(
        tenant_id=tenant_id,
        user_id=user_id,
        snapshot_type=snapshot_type,
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    db.session.add(row)


def k_vektor_weights_get_dict(tenant_id: int) -> Dict[str, Any]:
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {"success": False, "message": "Kurum bulunamadı."}

    tid = tenant_id
    sw_map = {r.strategy_id: r.weight_raw for r in KVektorStrategyWeight.query.filter_by(tenant_id=tid).all()}
    ssw_map = {r.sub_strategy_id: r.weight_raw for r in KVektorSubStrategyWeight.query.filter_by(tenant_id=tid).all()}
    strategies = (
        Strategy.query.filter_by(tenant_id=tid, is_active=True)
        .order_by(Strategy.code)
        .all()
    )
    out: List[Dict[str, Any]] = []
    for st in strategies:
        subs = []
        for ss in st.sub_strategies or []:
            if not getattr(ss, "is_active", True):
                continue
            subs.append(
                {
                    "id": ss.id,
                    "code": ss.code,
                    "title": ss.title,
                    "weight_raw": ssw_map.get(ss.id),
                }
            )
        out.append(
            {
                "id": st.id,
                "code": st.code,
                "title": st.title,
                "weight_raw": sw_map.get(st.id),
                "sub_strategies": subs,
            }
        )
    return {"success": True, "k_vektor_enabled": tenant.k_vektor_enabled, "strategies": out}


def _parse_weight_raw(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, str) and not v.strip():
        return None
    return float(v)


def apply_single_strategy_k_vektor_weight(
    tenant_id: int,
    user_id: Optional[int],
    strategy_id: int,
    raw_in: Any,
) -> Optional[str]:
    """
    Tek ana strateji ham ağırlığı (session’da upsert; commit yok).
    Dönüş: hata metni veya None.
    """
    tenant = Tenant.query.get(tenant_id)
    if not tenant or not tenant.k_vektor_enabled:
        return None
    st = Strategy.query.filter_by(id=strategy_id, tenant_id=tenant_id, is_active=True).first()
    if not st:
        return "Strateji bulunamadı."
    raw = _parse_weight_raw(raw_in)
    row = KVektorStrategyWeight.query.filter_by(tenant_id=tenant_id, strategy_id=strategy_id).first()
    if raw is None:
        if row:
            db.session.delete(row)
    else:
        if not row:
            db.session.add(
                KVektorStrategyWeight(tenant_id=tenant_id, strategy_id=strategy_id, weight_raw=raw)
            )
        else:
            row.weight_raw = raw
    add_k_vektor_snapshot(
        tenant_id,
        user_id,
        "k_vektor_weight_strategy",
        {"strategy_id": strategy_id, "weight_raw": raw},
    )
    return None


def apply_single_sub_strategy_k_vektor_weight(
    tenant_id: int,
    user_id: Optional[int],
    sub_strategy_id: int,
    raw_in: Any,
) -> Optional[str]:
    """Tek alt strateji ham ağırlığı (session’da upsert; commit yok)."""
    tenant = Tenant.query.get(tenant_id)
    if not tenant or not tenant.k_vektor_enabled:
        return None
    sub = (
        SubStrategy.query.join(Strategy)
        .filter(
            SubStrategy.id == sub_strategy_id,
            Strategy.tenant_id == tenant_id,
            SubStrategy.is_active == True,  # noqa: E712
        )
        .first()
    )
    if not sub:
        return "Alt strateji bulunamadı."
    raw = _parse_weight_raw(raw_in)
    row = KVektorSubStrategyWeight.query.filter_by(
        tenant_id=tenant_id, sub_strategy_id=sub_strategy_id
    ).first()
    if raw is None:
        if row:
            db.session.delete(row)
    else:
        if not row:
            db.session.add(
                KVektorSubStrategyWeight(
                    tenant_id=tenant_id, sub_strategy_id=sub_strategy_id, weight_raw=raw
                )
            )
        else:
            row.weight_raw = raw
    add_k_vektor_snapshot(
        tenant_id,
        user_id,
        "k_vektor_weight_sub_strategy",
        {"sub_strategy_id": sub_strategy_id, "weight_raw": raw},
    )
    return None


def save_k_vektor_weights(
    tenant_id: int,
    user_id: Optional[int],
    data: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Ana/alt ham ağırlıkları kaydeder. K-Vektör kapalıysa reddeder.
    Dönüş: (True, "") veya (False, hata_metni).
    """
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return False, "Kurum bulunamadı."
    if not tenant.k_vektor_enabled:
        return False, "Önce K-Vektörü kurum ayarlarından açın."

    allowed_strat = {s.id for s in Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).all()}
    allowed_sub: set[int] = set()
    for st in Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).all():
        for ss in st.sub_strategies or []:
            if getattr(ss, "is_active", True):
                allowed_sub.add(ss.id)

    for it in data.get("strategy_weights") or []:
        sid_raw = it.get("strategy_id")
        if sid_raw is None:
            continue
        sid = int(sid_raw)
        if sid not in allowed_strat:
            continue
        raw = _parse_weight_raw(it.get("weight_raw"))
        row = KVektorStrategyWeight.query.filter_by(tenant_id=tenant_id, strategy_id=sid).first()
        if raw is None:
            if row:
                db.session.delete(row)
        else:
            if not row:
                row = KVektorStrategyWeight(tenant_id=tenant_id, strategy_id=sid, weight_raw=raw)
                db.session.add(row)
            else:
                row.weight_raw = raw

    for it in data.get("sub_strategy_weights") or []:
        ssid_raw = it.get("sub_strategy_id")
        if ssid_raw is None:
            continue
        ssid = int(ssid_raw)
        if ssid not in allowed_sub:
            continue
        raw = _parse_weight_raw(it.get("weight_raw"))
        row = KVektorSubStrategyWeight.query.filter_by(tenant_id=tenant_id, sub_strategy_id=ssid).first()
        if raw is None:
            if row:
                db.session.delete(row)
        else:
            if not row:
                row = KVektorSubStrategyWeight(tenant_id=tenant_id, sub_strategy_id=ssid, weight_raw=raw)
                db.session.add(row)
            else:
                row.weight_raw = raw

    add_k_vektor_snapshot(
        tenant_id,
        user_id,
        "k_vektor_weights",
        {
            "strategy_weights": data.get("strategy_weights") or [],
            "sub_strategy_weights": data.get("sub_strategy_weights") or [],
        },
    )

    try:
        db.session.commit()
        return True, ""
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[save_k_vektor_weights] {e}", exc_info=True)
        return False, "Kayıt sırasında hata oluştu."
