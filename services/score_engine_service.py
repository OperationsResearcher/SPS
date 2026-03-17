# -*- coding: utf-8 -*-
"""
Skor Motoru Servisi
-------------------
PG (Performans Göstergesi) verisinden Vizyon puanına kadar hiyerarşik,
ağırlıklandırılmış skorlama. Tüm hiyerarşi 0-100 arası Vizyon skoru üretir.

- PG skoru: hedef_yonu (Artan/Azalan) ile (Gerçekleşen/Hedef) oranı → 0-100
- Özyinelemeli yukarı taşıma: PG → Süreç → Alt Strateji → Ana Strateji → Vizyon
- Varsayılan ağırlık: Eşit dağılım (100 / kardeş sayısı)
"""
from datetime import date
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload

from extensions import db
from models import (
    AnaStrateji, AltStrateji, Surec, SurecPerformansGostergesi,
    BireyselPerformansGostergesi, PerformansGostergeVeri,
    StrategyProcessMatrix,
)


def _parse_float(val: Any) -> Optional[float]:
    """String veya sayıyı float'a çevirir; geçersizse None."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    try:
        s = str(val).strip().replace(',', '.')
        return float(s) if s else None
    except (ValueError, TypeError):
        return None


def compute_pg_score(
    hedef_val: Optional[float],
    gerceklesen_val: Optional[float],
    direction: str = 'Increasing'
) -> Optional[float]:
    """
    PG başarı puanı (0-100). Hedef yönüne göre oran hesaplanır.
    - Artan (Increasing): oran = gerceklesen / hedef; puan = min(100, oran * 100)
    - Azalan (Decreasing): oran = hedef / gerceklesen; puan = min(100, oran * 100)
    Hedef veya gerçekleşen 0/None ise None döner.
    """
    if hedef_val is None or gerceklesen_val is None:
        return None
    try:
        hedef_f = float(hedef_val)
        gercek_f = float(gerceklesen_val)
    except (TypeError, ValueError):
        return None
    if hedef_f == 0:
        return None
    dir_ = (direction or 'Increasing').strip()
    if dir_.lower() == 'decreasing':
        if gercek_f == 0:
            return None
        ratio = hedef_f / gercek_f
    else:
        ratio = gercek_f / hedef_f
    score = min(100.0, max(0.0, ratio * 100.0))
    return round(score, 2)


def get_pg_representative_data(
    kurum_id: int,
    as_of_date: Optional[date] = None
) -> Dict[int, Tuple[Optional[float], Optional[float], Optional[float]]]:
    """
    Her SurecPerformansGostergesi (PG) için, as_of_date'e kadar son veriyi döndürür.
    Returns: { pg_id: (hedef, gerceklesen, calculated_score) }
    Veri BireyselPerformansGostergesi -> PerformansGostergeVeri üzerinden toplanır.
    """
    as_of = as_of_date or date.today()
    pgs = (
        SurecPerformansGostergesi.query
        .join(Surec)
        .filter(Surec.kurum_id == kurum_id, Surec.silindi == False)
        .options(joinedload(SurecPerformansGostergesi.surec))
        .all()
    )
    out = {}
    for pg in pgs:
        # Bu PG'ye bağlı bireysel PG'lerin verilerinden en son kaydı al (veri_tarihi <= as_of)
        sub = (
            db.session.query(
                PerformansGostergeVeri.hedef_deger,
                PerformansGostergeVeri.gerceklesen_deger
            )
            .join(BireyselPerformansGostergesi)
            .filter(
                BireyselPerformansGostergesi.kaynak_surec_pg_id == pg.id,
                PerformansGostergeVeri.veri_tarihi <= as_of
            )
            .order_by(PerformansGostergeVeri.veri_tarihi.desc())
            .limit(1)
        )
        row = sub.first()
        hedef = _parse_float(row.hedef_deger) if row else _parse_float(pg.hedef_deger)
        gercek = _parse_float(row.gerceklesen_deger) if row else None
        if hedef is None and row:
            hedef = _parse_float(row.hedef_deger)
        direction = (pg.direction or 'Increasing').strip()
        score = compute_pg_score(hedef, gercek, direction) if (hedef is not None and gercek is not None) else None
        out[pg.id] = (hedef, gercek, score)
    return out


def _default_weight(weight: Optional[float], sibling_count: int) -> float:
    """Ağırlık atanmamışsa eşit dağılım: 100 / kardeş sayısı."""
    if sibling_count <= 0:
        return 100.0
    if weight is not None and weight > 0:
        return min(100.0, max(0.0, float(weight)))
    return 100.0 / sibling_count


def compute_vision_score(
    kurum_id: int,
    as_of_date: Optional[date] = None,
    persist_pg_scores: bool = True
) -> Dict[str, Any]:
    """
    Point-in-time Vizyon puanı (0-100).
    as_of_date: O tarihe kadar olan verilerle hesaplar (None = bugün).
    persist_pg_scores: True ise PG calculated_score alanlarını günceller.
    """
    as_of = as_of_date or date.today()
    pg_data = get_pg_representative_data(kurum_id, as_of)

    # PG skorlarını süreç bazında topla; ağırlık varsayılan = 100 / kardeş sayısı
    pg_scores = {}
    for pg_id, (_, _, score) in pg_data.items():
        pg = SurecPerformansGostergesi.query.get(pg_id)
        if not pg or not pg.surec_id:
            continue
        pg_scores[pg_id] = score

    # Süreç puanları (yaprak süreçler: sadece PG'lerden; üst süreçler: alt süreç puanlarından)
    surec_scores = {}
    surecler = Surec.query.filter_by(kurum_id=kurum_id, silindi=False).all()
    # Alt süreçleri bilmek için parent_id -> [child_id]
    children_by_parent = {}
    for s in surecler:
        pid = s.parent_id
        if pid not in children_by_parent:
            children_by_parent[pid] = []
        children_by_parent[pid].append(s.id)

    def process_score(surec_id: int) -> float:
        if surec_id in surec_scores:
            return surec_scores[surec_id]
        surec = next((s for s in surecler if s.id == surec_id), None)
        if not surec:
            return 0.0
        child_ids = children_by_parent.get(surec_id, [])
        if child_ids:
            # Üst süreç: alt süreç puanlarının ağırlıklı ortalaması
            n = len(child_ids)
            w_sum = 0.0
            ws = []
            for cid in child_ids:
                c = next((s for s in surecler if s.id == cid), None)
                w = _default_weight(c.weight if c else None, n)
                ws.append((cid, w))
                w_sum += w
            if w_sum <= 0:
                surec_scores[surec_id] = 0.0
                return 0.0
            total = 0.0
            for cid, w in ws:
                total += process_score(cid) * (w / w_sum)
            surec_scores[surec_id] = round(total, 2)
            return surec_scores[surec_id]
        # Yaprak süreç: PG puanlarının ağırlıklı ortalaması
        pgs = SurecPerformansGostergesi.query.filter_by(surec_id=surec_id).all()
        if not pgs:
            surec_scores[surec_id] = 0.0
            return 0.0
        n = len(pgs)
        w_sum = 0.0
        total = 0.0
        for pg in pgs:
            w = _default_weight(pg.weight, n)
            sc = pg_scores.get(pg.id)
            if sc is None:
                sc = 0.0
            total += sc * w
            w_sum += w
            if persist_pg_scores and hasattr(pg, 'calculated_score'):
                pg.calculated_score = sc
        surec_scores[surec_id] = round(total / w_sum, 2) if w_sum else 0.0
        return surec_scores[surec_id]

    for s in surecler:
        if s.id not in surec_scores:
            process_score(s.id)

    # Alt Strateji puanları: StrategyProcessMatrix ile süreç puanlarının ağırlıklı ortalaması
    alt_strateji_scores = {}
    for alt in AltStrateji.query.join(AnaStrateji).filter(AnaStrateji.kurum_id == kurum_id).all():
        rows = StrategyProcessMatrix.query.filter_by(sub_strategy_id=alt.id).all()
        if not rows:
            alt_strateji_scores[alt.id] = 0.0
            continue
        total = 0.0
        w_sum = 0.0
        for r in rows:
            sc = surec_scores.get(r.process_id, 0.0)
            w = r.relationship_score or 1
            total += sc * w
            w_sum += w
        alt_strateji_scores[alt.id] = round(total / w_sum, 2) if w_sum else 0.0

    # Ana Strateji puanları: alt strateji puanlarının ağırlıklı ortalaması
    ana_list = AnaStrateji.query.filter_by(kurum_id=kurum_id).all()
    ana_scores = {}
    for ana in ana_list:
        alts = [a for a in ana.alt_stratejiler]
        if not alts:
            ana_scores[ana.id] = 0.0
            continue
        n = len(alts)
        total = 0.0
        w_sum = 0.0
        for a in alts:
            w = _default_weight(a.weight, n)
            total += alt_strateji_scores.get(a.id, 0.0) * w
            w_sum += w
        ana_scores[ana.id] = round(total / w_sum, 2) if w_sum else 0.0

    # Vizyon puanı: ana strateji puanlarının ağırlıklı ortalaması (0-100)
    n_ana = len(ana_list)
    if n_ana == 0:
        vision = 0.0
    else:
        total = 0.0
        w_sum = 0.0
        for ana in ana_list:
            w = _default_weight(ana.weight, n_ana)
            total += ana_scores.get(ana.id, 0.0) * w
            w_sum += w
        vision = round(total / w_sum, 2) if w_sum else 0.0

    if persist_pg_scores:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    return {
        'vision_score': min(100.0, max(0.0, vision)),
        'as_of_date': as_of.isoformat(),
        'kurum_id': kurum_id,
        'ana_strateji_scores': ana_scores,
        'alt_strateji_scores': alt_strateji_scores,
        'surec_scores': surec_scores,
        'pg_scores': {k: v for k, v in pg_scores.items() if v is not None},
    }


def recalc_on_pg_data_change(kurum_id: Optional[int], as_of_date: Optional[date] = None) -> Dict[str, Any]:
    """
    PG verisi girildiğinde veya güncellendiğinde çağrılır.
    Vizyon puanını tüm hiyerarşide yeniden hesaplar ve PG calculated_score alanlarını günceller.
    kurum_id None ise boş sonuç döner (hatasız).
    """
    if not kurum_id:
        return {'vision_score': 0.0, 'as_of_date': (as_of_date or date.today()).isoformat(), 'kurum_id': None}
    return compute_vision_score(kurum_id, as_of_date or date.today(), persist_pg_scores=True)


def recalc_on_faaliyet_change(surec_pg_id: Optional[int], kurum_id: int) -> Optional[Dict[str, Any]]:
    """
    Aksiyon (SurecFaaliyet) güncellendiğinde, sadece bağlı PG'nin verisi üzerinden
    ispat ile vizyona etki eder. Bağlı PG varsa skor motorunu tetikler.
    """
    if not surec_pg_id:
        return None
    pg = SurecPerformansGostergesi.query.get(surec_pg_id)
    if not pg or not pg.surec_id:
        return None
    s = Surec.query.get(pg.surec_id)
    if not s or s.kurum_id != kurum_id:
        return None
    return recalc_on_pg_data_change(kurum_id)
