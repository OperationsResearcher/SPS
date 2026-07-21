# -*- coding: utf-8 -*-
"""
Score Engine Service
PG verisinden Vizyon puanına hiyerarşik skorlama.
PG -> Süreç -> Alt Strateji -> Ana Strateji -> Vizyon (0-100)

Soft Delete: Sadece is_active=True olan Process, ProcessKpi, SubStrategy, Strategy ve KpiData
kayıtları hesaplamaya dahil edilir.

Cache: Vision score ve ara hesaplamalar cache'lenir.
"""
from datetime import date
from app.services.date_sovereign import resolve_request_year
from typing import Optional, Dict, Any

from flask import current_app
from sqlalchemy import or_, and_
from sqlalchemy.orm import selectinload, joinedload

from app.models import db
from app.models.process import Process, ProcessKpi, KpiData, ProcessSubStrategyLink
from app.models.core import SubStrategy, Strategy
from app.extensions import cache
from app.utils.cache_utils import CACHE_KEYS


# Sayı olmayan ama kullanıcının hedef/gerçekleşen alanına yazdığı süsler.
# ÖLÇÜM (B6/B8, 2026-07-21): hedefi dolu 1914 aktif PG'nin 126'sı sayıya
# çevrilemiyordu; 84'ü sırf '%' işareti yüzünden. Kardeş parse_aralik_degeri
# (karne tarafı) bunları zaten temizliyordu — bu motor temizlemiyordu.
_SAYI_SUSLERI = ('%', '₺', 'TL', '$', '€', ' ')


def _parse_float(val) -> Optional[float]:
    """Kullanıcı girdisini float'a çevirir. Türkçe sayı biçimini tanır.

    '%90'      → 90.0
    '1.234,5'  → 1234.5   ('.' binlik, ',' ondalık)
    '₺100.070' → 100070.0
    '-'        → None     (kullanıcının "veri yok" yazma biçimi)
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip()
    if not s:
        return None

    for sus in _SAYI_SUSLERI:
        s = s.replace(sus, '')
    s = s.strip()

    # Yalnız tire/nokta gibi "boş" işaretler: kullanıcı veri yok demek istiyor.
    if not s or s in ('-', '.', ',', '--'):
        return None

    # Türkçe biçim: '.' binlik ayraç, ',' ondalık ayraç.
    # Sadece '.' varsa binlik mi ondalık mı belirsiz → son grup 3 haneliyse
    # binlik kabul et ('1.234' → 1234), değilse ondalık ('3.99' → 3.99).
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif s.count('.') > 1:
        s = s.replace('.', '')
    elif '.' in s:
        tam, _, kesir = s.rpartition('.')
        if len(kesir) == 3 and tam.lstrip('-').isdigit():
            s = tam + kesir

    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _resolve_target_for_calculation(raw_target, direction: str = "Increasing") -> Optional[float]:
    """
    Hedef değer aralık olarak girildiyse (örn: "20-24"), hesaplama için
    yön bazlı tek değere indirger:
      - Increasing  -> min
      - Decreasing  -> max
    Tek değer girildiyse mevcut davranış korunur.
    """
    if raw_target is None:
        return None
    if isinstance(raw_target, (int, float)):
        return float(raw_target)

    import re as _re
    text = str(raw_target).strip()
    if not text:
        return None

    # B6: '%90-100' gibi süslü aralıklar aşağıdaki regex'e uymuyordu → None
    # dönüp PG sıfır sayılıyordu. Süsleri aralık ayrıştırmasından ÖNCE at.
    # (Tek değerli girdide _parse_float zaten temizliyor.)
    for _sus in _SAYI_SUSLERI:
        text = text.replace(_sus, '')
    text = text.strip()
    if not text:
        return None

    # Negatif aralıkları doğru parse et: "-5-3", "-10--2", "1-10"
    m = _re.match(r'^(-?[\d.,]+)\s*-\s*(-?[\d.,]+)$', text)
    if m:
        left = _parse_float(m.group(1))
        right = _parse_float(m.group(2))
        if left is not None and right is not None:
            lo = min(left, right)
            hi = max(left, right)
            return hi if (direction or "Increasing").strip().lower() == "decreasing" else lo

    return _parse_float(text)


def compute_pg_score(
    hedef_val: Optional[float],
    gerceklesen_val: Optional[float],
    direction: str = 'Increasing'
) -> Optional[float]:
    """PG başarı puanı (0-100). Hedef yönüne göre oran hesaplanır."""
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
            return 100.0  # Hedef sıfır olmayan değer, gerçekleşen sıfır → tam başarı
        ratio = hedef_f / gercek_f
    else:
        ratio = gercek_f / hedef_f
    return round(min(100.0, max(0.0, ratio * 100.0)), 2)


def _default_weight(weight: Optional[float], sibling_count: int) -> float:
    if sibling_count <= 0:
        return 100.0
    if weight is not None and weight > 0:
        return min(100.0, max(0.0, float(weight)))
    return 100.0 / sibling_count


def get_pg_scores_from_kpi_data(
    tenant_id: int,
    year: Optional[int] = None,
    as_of_date: Optional[date] = None,
    plan_year=None,  # PlanYear instance; None → ProcessKpi fallback
) -> Dict[int, Optional[float]]:
    """
    Her ProcessKpi için KpiData'dan hesaplanan skoru döner.
    plan_year verilirse yıllık hedef/yöntem/metod konfigürasyonu kullanılır;
    yoksa ProcessKpi'ın orijinal değerlerine fallback yapılır.
    """
    if year is None:
        # S8: çağıran yıl vermediyse kullanıcının seçtiği yıl (request
        # yoksa takvim yılı). Eskiden session'ı hiç bilmiyordu.
        year = resolve_request_year()
    as_of = as_of_date or date.today()

    if plan_year is not None:
        pgs = (
            ProcessKpi.query
            .join(Process)
            .filter(
                ProcessKpi.is_active.is_(True),
                Process.is_active.is_(True),
                or_(
                    ProcessKpi.plan_year_id == plan_year.id,
                    and_(ProcessKpi.plan_year_id.is_(None), Process.tenant_id == tenant_id),
                ),
            )
            .all()
        )
    else:
        pgs = (
            ProcessKpi.query
            .join(Process)
            .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True))
            .filter(ProcessKpi.is_active.is_(True))
            .all()
        )

    # Yıllık config bulk çek (N+1 önlemi)
    kpi_cfg_map: Dict[int, Dict] = {}
    if plan_year is not None:
        try:
            from app.services.plan_year_service import get_kpi_configs_bulk
            kpi_cfg_map = get_kpi_configs_bulk(pgs, plan_year)
        except Exception as e:
            current_app.logger.warning(f"[score_engine] plan_year config çekilemedi: {e}")

    # Tüm PG'lerin KpiData'sını batch'le çek (N+1 önlemi: 221 PG → 1 sorgu)
    _pg_ids = [pg.id for pg in pgs]
    _entries_by_pg: Dict[int, list] = {}
    if _pg_ids:
        from collections import defaultdict as _dd
        _entries_by_pg = _dd(list)
        for d in (
            KpiData.query.filter(
                KpiData.process_kpi_id.in_(_pg_ids),
                KpiData.year == year,
                KpiData.is_active.is_(True),
                KpiData.data_date <= as_of,
            ).order_by(KpiData.process_kpi_id, KpiData.data_date.desc()).all()
        ):
            if len(_entries_by_pg[d.process_kpi_id]) < 100:
                _entries_by_pg[d.process_kpi_id].append(d)

    out = {}
    for pg in pgs:
        entries = _entries_by_pg.get(pg.id, [])
        if not entries and plan_year is not None:
            # Clone KPI'da veri yoksa source_kpi_id zincirini tara (max 8 adım)
            ancestor_id = getattr(pg, 'source_kpi_id', None)
            visited = {pg.id}
            while ancestor_id and ancestor_id not in visited and len(visited) < 9:
                visited.add(ancestor_id)
                entries = (
                    KpiData.query.filter_by(process_kpi_id=ancestor_id, year=year, is_active=True)
                    .filter(KpiData.data_date <= as_of)
                    .order_by(KpiData.data_date.desc())
                    .limit(100)
                ).all()
                if entries:
                    break
                ancestor = ProcessKpi.query.get(ancestor_id)
                ancestor_id = getattr(ancestor, 'source_kpi_id', None) if ancestor else None
        if not entries:
            out[pg.id] = None
            continue

        # Yıllık config varsa kullan, yoksa ProcessKpi değerleri
        cfg = kpi_cfg_map.get(pg.id)
        if cfg:
            target_raw = cfg["target_value"]
            direction = cfg["direction"] or "Increasing"
            method = cfg["data_collection_method"] or "Ortalama"
        else:
            target_raw = pg.target_value
            direction = pg.direction or "Increasing"
            method = pg.data_collection_method or "Ortalama"

        target = _resolve_target_for_calculation(target_raw, direction)
        actual_values = [_parse_float(e.actual_value) for e in entries]
        actual_values = [v for v in actual_values if v is not None]
        if not actual_values:
            out[pg.id] = None
            continue
        if method in ('Toplama', 'Toplam'):
            actual = sum(actual_values)
        elif method == 'Son Değer':
            actual = actual_values[0]
        else:
            actual = sum(actual_values) / len(actual_values)
        score = compute_pg_score(target, actual, direction)
        out[pg.id] = score
    return out


def compute_process_scores_internal(
    tenant_id: int,
    year: int,
    as_of: date,
    persist_pg_scores: bool,
    plan_year=None,  # PlanYear instance; None → ProcessKpi fallback
) -> tuple[Dict[int, float], Dict[int, Optional[float]]]:
    """PG → süreç skorları (0–100). K-Vektör ve klasik vizyon motoru ortak kullanır."""
    pg_scores = get_pg_scores_from_kpi_data(tenant_id, year, as_of, plan_year=plan_year)

    if plan_year is not None:
        processes = Process.query.filter(
            Process.is_active.is_(True),
            or_(
                Process.plan_year_id == plan_year.id,
                and_(Process.plan_year_id.is_(None), Process.tenant_id == tenant_id),
            ),
        ).all()
    else:
        processes = Process.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    children_by_parent = {}
    for p in processes:
        pid = p.parent_id
        if pid not in children_by_parent:
            children_by_parent[pid] = []
        children_by_parent[pid].append(p.id)

    process_scores: Dict[int, float] = {}

    # P1 (N+1 önlemi): tüm süreçlerin aktif KPI'larını süreç-başına sorgu yerine TEK sorguda yükle.
    _kpis_by_proc: Dict[int, list] = {}
    if processes:
        for _k in ProcessKpi.query.filter(
            ProcessKpi.process_id.in_([p.id for p in processes]),
            ProcessKpi.is_active.is_(True),
        ).all():
            _kpis_by_proc.setdefault(_k.process_id, []).append(_k)

    def calc_process_score(process_id: int) -> float:
        if process_id in process_scores:
            return process_scores[process_id]
        proc = next((p for p in processes if p.id == process_id), None)
        if not proc:
            return 0.0
        child_ids = children_by_parent.get(process_id, [])
        if child_ids:
            n = len(child_ids)
            total = 0.0
            w_sum = 0.0
            for cid in child_ids:
                c = next((p for p in processes if p.id == cid), None)
                child_score = calc_process_score(cid)
                if child_score is None:
                    continue  # KPI'sız alt süreç ağırlıklı ortalamaya dahil edilmez
                w = _default_weight(c.weight if c else None, n)
                total += child_score * w
                w_sum += w
            process_scores[process_id] = round(total / w_sum, 2) if (w_sum and w_sum > 0) else 0.0
            return process_scores[process_id]
        kpis = _kpis_by_proc.get(process_id, [])
        if not kpis:
            # KPI'sız süreç ağırlıklı ortalamayı bozmaması için None döndürür
            process_scores[process_id] = None
            return None
        n = len(kpis)
        total = 0.0
        w_sum = 0.0
        # B1/M4 (2026-07-21): PG skoru None ise (o dönemde veri girilmemiş ya
        # da hedef sayıya çevrilemiyor) eskiden 0.0 sayılıyordu — yani "veri
        # yok" ile "tamamen başarısız" aynı muamele görüyordu.
        #
        # Ölçüm: KMF'nin 11 aktif sürecinin yalnız 2'sinde 2026 verisi var;
        # kalan 9'u veri olmadığı hâlde 0.0 alıp süreç/alt strateji/vizyon
        # ortalamasını dibe çekiyordu (vizyon 6.48 görünüyor).
        #
        # Ölçülemeyen PG artık hem paydan hem paydadan düşer. Hiçbiri
        # ölçülemiyorsa süreç None döner — KPI'sız süreçle aynı muamele
        # (satır 327-330'daki mevcut desen).
        for kpi in kpis:
            sc = pg_scores.get(kpi.id)
            if sc is None:
                continue  # ölçülmedi → ağırlıklı ortalamaya girmez
            w = _default_weight(kpi.weight, n)
            total += sc * w
            w_sum += w
            if persist_pg_scores:
                kpi.calculated_score = sc
        if not w_sum or w_sum <= 0:
            process_scores[process_id] = None
            return None
        process_scores[process_id] = round(total / w_sum, 2)
        return process_scores[process_id]

    for p in processes:
        if p.id not in process_scores:
            calc_process_score(p.id)

    # C2 + B1/M4: Ölçülemeyen süreç None taşır (hiyerarşik ağırlıklı
    # ortalamadan dışlanmak için — bkz. `if child_score is None`).
    #
    # ESKİDEN burada None → 0.0 normalizasyonu vardı: ~10 tüketici
    # (faz0-5, surec, k-vektör, k_rapor) sayısal değer bekliyordu ve
    # None sum()/sorted()'ta TypeError → 500 veriyordu.
    #
    # Ama bu normalizasyon B1'in kök nedeniydi: "ölçülmedi" tam da bu
    # satırda "sıfır başarı"ya dönüşüyor ve üst katmanlardaki hiçbir
    # düzeltme etkili olamıyordu.
    #
    # ÇÖZÜM: None İÇERİDE korunur (üst katmanlar artık doğru işliyor),
    # dışarıya SÜZÜLEREK verilir — compute_vision_score / k_vektor_engine
    # dönüş sözlüklerinde `if v is not None` filtresi var. Tüketici None
    # görmez; ölçülmemiş süreç anahtarı hiç bulunmaz (0.0 görmekten iyidir,
    # çünkü "0 puan aldı" ile "ölçülmedi" ayırt edilebilir).
    return process_scores, pg_scores


def compute_vision_score(
    tenant_id: int,
    year: Optional[int] = None,
    as_of_date: Optional[date] = None,
    persist_pg_scores: bool = True,
    plan_year=None,  # PlanYear instance; None → otomatik çözümlenir
) -> Dict[str, Any]:
    """
    Hiyerarşik vizyon puanı hesaplar.
    PG -> Süreç -> Alt Strateji -> Ana Strateji -> Vizyon (0-100)
    K-Vektör açıksa: app.services.k_vektor_engine.compute_k_vektor_bundle
    plan_year: PlanYear instance; verilmezse tenant+year için otomatik çözümlenir.
    """
    if year is None:
        year = plan_year.year if plan_year is not None else resolve_request_year()
    as_of = as_of_date or date.today()

    # plan_year otomatik çözümle
    if plan_year is None:
        try:
            from app.services.plan_year_service import get_plan_year as _get_py
            plan_year = _get_py(tenant_id, year)
        except Exception:
            plan_year = None

    try:
        from app.models.core import Tenant

        tenant = Tenant.query.get(tenant_id)
        if tenant and getattr(tenant, "k_vektor_enabled", False):
            from app.services.k_vektor_engine import compute_k_vektor_bundle

            return compute_k_vektor_bundle(
                tenant_id, year, as_of,
                persist_pg_scores=persist_pg_scores,
                plan_year=plan_year,
            )

        process_scores, pg_scores = compute_process_scores_internal(
            tenant_id, year, as_of, persist_pg_scores, plan_year=plan_year
        )

        if plan_year is not None:
            sub_strategies = (
                SubStrategy.query.join(Strategy)
                .options(selectinload(SubStrategy.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.process))
                .filter(
                    Strategy.is_active.is_(True),
                    SubStrategy.is_active.is_(True),
                    or_(
                        Strategy.plan_year_id == plan_year.id,
                        and_(Strategy.plan_year_id.is_(None), Strategy.tenant_id == tenant_id),
                    ),
                )
                .all()
            )
        else:
            sub_strategies = (
                SubStrategy.query.join(Strategy)
                .options(selectinload(SubStrategy.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.process))
                .filter(Strategy.tenant_id == tenant_id, Strategy.is_active.is_(True))
                .filter(SubStrategy.is_active.is_(True))
                .all()
            )
        # B1/M4 (2026-07-21): "ölçülmedi" ile "başarısız" ayrımı.
        #
        # Eskiden bağlantısız alt strateji 0.0 alıp ortalamaya giriyordu.
        # Ölçüm: 754 aktif alt stratejinin 230'u hiç aktif sürece bağlı değil.
        #   Tomofil 2026 : vizyon 55.78 görünüyordu, sıfırlar dışlanınca 80.02
        #                  (16 alt stratejinin 6'sı 0.0; sıfır olmayanların
        #                   ortalaması 93.75) → 24.24 puan sapma
        #   KMF          : 21 alt stratejinin 18'i 0.0 → vizyon 6.48 görünüyor,
        #                  ölçülenlerin gerçek ortalaması 27.73
        #
        # Süreç katmanında bu ZATEN doğru yapılmıştı (satır 327-330: KPI'sız
        # süreç None döner, ağırlıklı ortalamaya girmez) — mantık üst
        # katmanlara taşınmamıştı. Şimdi taşındı.
        #
        # Eksik veriyi sıfır saymak kurumu YAPILANDIRMA EKSİKLİĞİ için
        # cezalandırır ve skoru yorumlanamaz kılar.
        sub_strategy_scores = {}
        for ss in sub_strategies:
            linked_processes = list(ss.processes) if hasattr(ss, 'processes') else []
            linked_processes = [p for p in linked_processes if p.is_active]
            if not linked_processes:
                sub_strategy_scores[ss.id] = None  # ölçülmedi ≠ 0
                continue
            # Süreç skoru None olanlar (KPI'sız süreçler) da dışlanır.
            olculen = [
                process_scores.get(p.id) for p in linked_processes
                if process_scores.get(p.id) is not None
            ]
            if not olculen:
                sub_strategy_scores[ss.id] = None
                continue
            sub_strategy_scores[ss.id] = round(sum(olculen) / len(olculen), 2)

        # N+1 önlemi: st.sub_strategies aşağıda iterate edildiği için selectinload
        if plan_year is not None:
            strategies = Strategy.query.options(selectinload(Strategy.sub_strategies)).filter(
                Strategy.is_active.is_(True),
                or_(
                    Strategy.plan_year_id == plan_year.id,
                    and_(Strategy.plan_year_id.is_(None), Strategy.tenant_id == tenant_id),
                ),
            ).all()
        else:
            strategies = Strategy.query.options(selectinload(Strategy.sub_strategies)).filter_by(
                tenant_id=tenant_id, is_active=True
            ).all()
        # B1/M4: aynı None semantiği ana strateji katmanında.
        strategy_scores = {}
        for st in strategies:
            alts = [a for a in st.sub_strategies if a.is_active]
            olculen = [
                sub_strategy_scores.get(a.id) for a in alts
                if sub_strategy_scores.get(a.id) is not None
            ]
            if not olculen:
                strategy_scores[st.id] = None
                continue
            strategy_scores[st.id] = round(sum(olculen) / len(olculen), 2)

        # B1/M4: vizyon katmanı. Hiçbir strateji ölçülemiyorsa vizyon 0 değil
        # None'dır — ama dışarıya 0.0 döneriz (API sözleşmesi float bekliyor),
        # kapsam bilgisi `kapsam` alanında ayrıca taşınır.
        _olculen_strat = [
            strategy_scores.get(s.id) for s in strategies
            if strategy_scores.get(s.id) is not None
        ]
        vision = (
            round(sum(_olculen_strat) / len(_olculen_strat), 2)
            if _olculen_strat else 0.0
        )

        vision = min(100.0, max(0.0, vision))

        # M4/B1 — KAPSAM: skorun ne kadarlık bir tabana dayandığı.
        # Bu olmadan "vizyon 80.02" ile "vizyon 80.02 ama stratejilerin
        # %70'i ölçülmemiş" ayırt edilemez. Sessiz hatanın panzehiri.
        _kapsam_alt_toplam = len(sub_strategies)
        _kapsam_alt_olculen = len(
            [v for v in sub_strategy_scores.values() if v is not None]
        )
        _kapsam_strat_toplam = len(strategies)
        _kapsam_strat_olculen = len(_olculen_strat)
        kapsam = {
            "alt_strateji_toplam": _kapsam_alt_toplam,
            "alt_strateji_olculen": _kapsam_alt_olculen,
            "ana_strateji_toplam": _kapsam_strat_toplam,
            "ana_strateji_olculen": _kapsam_strat_olculen,
            "yuzde": (
                round(_kapsam_alt_olculen / _kapsam_alt_toplam * 100, 1)
                if _kapsam_alt_toplam else 0.0
            ),
        }

        if persist_pg_scores:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"[score_engine_service] Veritabanı commit hatası: {e}", exc_info=True)

        return {
            'vision_score': vision,
            'as_of_date': as_of.isoformat(),
            'tenant_id': tenant_id,
            'year': year,
            # B1/M4: ölçülmemiş (None) girdiler dışarıya sızdırılmaz —
            # `pg_scores` zaten bu deseni kullanıyordu, üst katmanlar da
            # aynı sözleşmeye uyuyor. Tüketiciler float bekliyor; None
            # göndermek onların tarafında sessizce 0'a dönerdi ki bu tam
            # olarak kaçındığımız hata.
            'strategy_scores': {k: v for k, v in strategy_scores.items() if v is not None},
            'sub_strategy_scores': {k: v for k, v in sub_strategy_scores.items() if v is not None},
            'process_scores': {k: v for k, v in process_scores.items() if v is not None},
            'pg_scores': {k: v for k, v in pg_scores.items() if v is not None},
            # Skorun ne kadarlık tabana dayandığı (M4 önerisi).
            'kapsam': kapsam,
        }
    except Exception as e:
        current_app.logger.error(
            f"[score_engine_service] Vizyon skoru hesaplanırken hata oluştu (tenant_id={tenant_id}, year={year}): {e}",
            exc_info=True
        )
        raise


def recalc_on_pg_data_change(
    tenant_id: Optional[int],
    year: Optional[int] = None,
    as_of_date: Optional[date] = None
) -> Dict[str, Any]:
    """PG verisi değiştiğinde skor motorunu tetikler."""
    if not tenant_id:
        return {
            'vision_score': 0.0,
            'as_of_date': (as_of_date or date.today()).isoformat(),
            'tenant_id': None
        }
    return compute_vision_score(
        tenant_id,
        year or resolve_request_year(),
        as_of_date or date.today(),
        persist_pg_scores=True
    )
