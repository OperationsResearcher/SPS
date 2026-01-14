# -*- coding: utf-8 -*-
"""Basit kural motoru (tetikleyici/koşul/aksiyon)."""
import json
from typing import Dict, Any, List
from models import RuleDefinition
from extensions import db


def ensure_table():
    try:
        RuleDefinition.__table__.create(db.engine, checkfirst=True)
    except Exception:
        pass


def list_rules(project_id: int | None = None) -> List[Dict[str, Any]]:
    ensure_table()
    q = RuleDefinition.query
    if project_id:
        q = q.filter_by(project_id=project_id)
    rules = []
    for r in q.all():
        rules.append({
            'id': r.id,
            'project_id': r.project_id,
            'name': r.name,
            'trigger': r.trigger,
            'condition': _safe_json(r.condition_json),
            'actions': _safe_json(r.actions_json),
            'is_active': r.is_active,
        })
    return rules


def save_rule(project_id: int | None, name: str, trigger: str, condition: Dict[str, Any], actions: List[Dict[str, Any]], is_active: bool = True) -> int:
    ensure_table()
    rule = RuleDefinition(
        project_id=project_id,
        name=name,
        trigger=trigger,
        condition_json=json.dumps(condition or {}),
        actions_json=json.dumps(actions or []),
        is_active=is_active
    )
    db.session.add(rule)
    db.session.commit()
    return rule.id


def _safe_json(val: str | None):
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return None


def evaluate_rules(trigger: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Dönüş: uygulanması gereken aksiyonlar listesi (dict).
    Şimdilik sadece filtreleme yapar, aksiyonu icra etmez.
    """
    ensure_table()
    results = []
    for r in RuleDefinition.query.filter_by(trigger=trigger, is_active=True).all():
        cond = _safe_json(r.condition_json) or {}
        if _match(cond, context):
            acts = _safe_json(r.actions_json) or []
            results.extend(acts)
    return results


def _match(condition: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    # Basit eşitlik kontrolleri
    for k, v in (condition or {}).items():
        if ctx.get(k) != v:
            return False
    return True
