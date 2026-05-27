# -*- coding: utf-8 -*-
"""Tarih egemen plan year doktrini — ortak yardımcılar.

Üç ayrı kavramı netleştirir:
  1. VIEW context     → `get_view_year(user)` — UI filtresi, varsayılan: bugünün yılı
  2. RECORD routing   → `resolve_plan_year_for_date(tenant_id, data_date)` — tarihten yıl
  3. EXISTENCE check  → `entity_exists_in_year(entity, plan_year_id)` — clone var mı

Karar (Faz 0): "Bu varlık o yılda var mı?" sorusunun tek doğru kaynağı
**clone yaklaşımıdır** — `entity.plan_year_id == plan_year.id`. Overlay
(`process_year_configs.is_included`) sadece metadata override için kullanılır,
varlık kontrolünde söz sahibi değildir.

Hata mesajları: kullanıcıya soyut "yıl uyumsuz" yerine süreç/PG bağlamlı
mesaj döner — `build_existence_error()` yardımcısı.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, Any, Dict

from flask import session

from app.models.plan_year import PlanYear


# ── 1. VIEW CONTEXT ───────────────────────────────────────────────────────────

def get_view_year(user) -> int:
    """Kullanıcının UI'da görmek istediği yıl.

    Öncelik:
      1. session["sp_active_year"] (kullanıcı plan year bar'dan seçti)
      2. bugünün takvim yılı

    Not: Bu UI bağlamıdır, kayıt routing'inde KULLANILMAZ.
    """
    sel = session.get("sp_active_year")
    if sel:
        try:
            return int(sel)
        except (TypeError, ValueError):
            pass
    return date.today().year


def get_view_plan_year(tenant_id: int, user) -> Optional[PlanYear]:
    """Görüntü bağlamına karşılık gelen PlanYear — yoksa None."""
    y = get_view_year(user)
    return PlanYear.query.filter_by(tenant_id=tenant_id, year=y).first()


# ── 2. RECORD ROUTING ─────────────────────────────────────────────────────────

def resolve_plan_year_for_date(tenant_id: int, when: Any) -> Optional[PlanYear]:
    """Verilen tarihin ait olduğu PlanYear'ı döner.

    `when` str ('YYYY-MM-DD' veya 'YYYY-MM-DDTHH:MM:SS'), date veya datetime olabilir.
    O yıl için PlanYear yoksa None döner — çağıran açık hata vermeli.
    """
    year = _year_of(when)
    if year is None:
        return None
    return PlanYear.query.filter_by(tenant_id=tenant_id, year=year).first()


def _year_of(when: Any) -> Optional[int]:
    if when is None:
        return None
    if isinstance(when, (date, datetime)):
        return when.year
    if isinstance(when, int):
        # Yıl olarak verildi
        return when if 1900 < when < 3000 else None
    s = str(when).strip()
    if not s:
        return None
    # 'YYYY' ile başlamalı
    try:
        return int(s[:4])
    except ValueError:
        return None


# ── 3. EXISTENCE CHECK (clone birincil) ──────────────────────────────────────

def entity_exists_in_year(entity: Any, plan_year: PlanYear) -> bool:
    """Varlığın belirtilen plan yılında **fiziksel olarak** var olup olmadığı.

    Doktrin (Faz 0): clone birincil. Varlığın `plan_year_id`'si yoksa
    (yıllı sisteme dahil değil, global varlık) → True döner — yıl-agnostik kabul.

    plan_year_id varsa → o yıla eşit olmalı.
    """
    if entity is None or plan_year is None:
        return False
    pyid = getattr(entity, "plan_year_id", None)
    if pyid is None:
        return True   # global varlık, her yıl geçerli
    return int(pyid) == int(plan_year.id)


def entity_year_label(entity: Any) -> Optional[int]:
    """Varlığın ait olduğu yılın etiketi (varsa)."""
    pyid = getattr(entity, "plan_year_id", None)
    if pyid is None:
        return None
    py = PlanYear.query.get(pyid)
    return py.year if py else None


# ── 4. ORTAK HATA / DURUM MESAJI ─────────────────────────────────────────────

def build_existence_error(
    entity: Any,
    entity_label: str,
    data_date: Any,
    target_plan_year: Optional[PlanYear],
    entity_kind: str = "süreç",
) -> Dict[str, Any]:
    """Süreç/PG vb. hedef yılda yokken döndürülecek standart hata dict'i.

    Çağıran route bunu `jsonify(...)`, status=409 ile döner.

    Args:
        entity: Kontrol edilen varlık (Process/ProcessKpi/...).
        entity_label: Kullanıcıya gösterilecek ad (örn. 'SR1A - Ürün Ar-Ge').
        data_date: Kullanıcının seçtiği tarih.
        target_plan_year: Tarihten resolve edilen PlanYear (None olabilir).
        entity_kind: 'süreç', 'PG', 'proje' gibi tip etiketi.
    """
    target_year = target_plan_year.year if target_plan_year else _year_of(data_date)
    entity_year = entity_year_label(entity)

    if target_plan_year is None and target_year is not None:
        msg = (
            f"{target_year} yılı için plan dönemi tanımlı değil. "
            f"Bu tarihe veri girmek için önce o yılın planını oluşturun."
        )
        return {
            "success": False,
            "message": msg,
            "plan_year_missing": True,
            "data_date_year": target_year,
        }

    if entity_year and target_year:
        msg = (
            f"\"{entity_label}\" {entity_kind}i {target_year} planında bulunmuyor. "
            f"Bu {entity_kind} {entity_year} dönemine ait — "
            f"yalnızca {entity_year} tarihli veri girilebilir."
        )
    else:
        msg = (
            f"\"{entity_label}\" {entity_kind}i, seçilen tarihin ait olduğu "
            f"plan döneminde mevcut değil."
        )

    return {
        "success": False,
        "message": msg,
        "entity_year_mismatch": True,
        "entity_year": entity_year,
        "target_year": target_year,
    }


def build_cross_year_notice(
    view_year: int,
    target_year: int,
) -> Optional[Dict[str, Any]]:
    """Görüntü yılı ≠ kayıt yılı durumunda kullanıcıya gösterilecek pasif rozet.

    Engel değildir; kayıt başarıyla yapılır. UI bunu yumuşak bilgi olarak gösterir
    (örn. response.notice alanı).
    """
    if view_year == target_year:
        return None
    arrow = "↩️" if target_year < view_year else "↪️"
    return {
        "kind": "cross_year_write",
        "view_year": view_year,
        "target_year": target_year,
        "label": f"{arrow} {target_year} dönemine yazıldı",
    }
