# -*- coding: utf-8 -*-
"""
Score Engine Service
PG verisinden Vizyon puanına hiyerarşik skorlama.
PG -> Süreç -> Alt Strateji -> Ana Strateji -> Vizyon (0-100)

Soft Delete: Sadece is_active=True olan Process, ProcessKpi, SubStrategy, Strategy ve KpiData
kayıtları hesaplamaya dahil edilir.

Cache: Vision score ve ara hesaplamalar cache'lenir.

TEK HESAP MOTORU - GENEL API (Dalga 3, adim 1; ekranlar bu fonksiyonlari cagirir)
Saf fonksiyonlar (DB'siz):
  parse_tr_number(s) -> float|None      serbest metin; TR kural, gecersiz desen -> None
  _parse_float(val) -> float|None       DB'de sakli deger (kanonik 'x.y' dogrudan float)
  normalize_direction(d) -> 'Increasing'|'Decreasing'
  achievement(actual, target, direction) -> float|None   (0-100, tek yon/oran kurali)
  normalize_aggregation_method(m) -> 'AVG'|'SUM'|'LAST'  (AVG/SUM/Son Deger/ortalama/toplam)
  aggregate_actuals(values_newest_first, method) -> float|None
  weighted_average([(skor|None, agirlik|None)]) -> float|None  (normalize eder)
  period_start(year, period_type, period_no, period_month, data_date) -> date|None
  entry_in_scope(entry, as_of) -> bool  (donem basladiysa dahil)
DB'li genel API:
  calculate_kpi_score(kpi_id, plan_year_id, as_of=None) -> float|None
  calculate_kpi_detail(kpi_id, plan_year_id, as_of=None) -> dict
  calculate_process_score(process_id, plan_year_id, as_of=None) -> float|None (None=olculmedi)
  get_pg_scores_from_kpi_data / compute_process_scores_internal / compute_vision_score
"""
import re as _re_mod
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
from app.utils.tr_time import today_tr
import logging

logger = logging.getLogger(__name__)


# Sayı olmayan ama kullanıcının hedef/gerçekleşen alanına yazdığı süsler.
# ÖLÇÜM (B6/B8, 2026-07-21): hedefi dolu 1914 aktif PG'nin 126'sı sayıya
# çevrilemiyordu; 84'ü sırf '%' işareti yüzünden.
_SAYI_SUSLERI = ('%', '₺', 'TL', '$', '€', ' ')

# Geçerli Türkçe binlik gruplama: 1.234 / 1.234.567 / 1.234,5 / -12.345,67
_TR_BINLIK_RE = _re_mod.compile(r'^-?[1-9]\d{0,2}(\.\d{3})+(,\d+)?$')
_TR_ONDALIK_RE = _re_mod.compile(r'^-?\d*,\d+$')
_DUZ_TAMSAYI_RE = _re_mod.compile(r'^-?\d+$')
# DB'de saklanan kanonik biçim (Python str(float)): '98.75', '0.125', '-3.5'
_KANONIK_RE = _re_mod.compile(r'^-?\d+\.\d+$')


def parse_tr_number(s) -> Optional[float]:
    """SERBEST METİN girişi için Türkçe sayı ayrıştırıcı (A-003).

    Kurallar:
      - '%', '₺', 'TL', '$', '€' ve boşluk temizlenir.
      - ',' varsa ondalıktır; '.' o durumda yalnız geçerli binlik gruplamada kabul edilir.
      - ',' yoksa '.' YALNIZ geçerli binlik desende (1.234, 1.234.567) binliktir.
      - Geçersiz desen ('98.75', '1.2.3', '1,234.5', 'abc') -> None: sessizce
        yanlış sayı üretmek yerine REDDEDİLİR; çağıran kullanıcıya hata gösterir.
      - '-', '--', '.', ',' ve boş -> None ("veri yok").
    DB'den okunan kanonik değerler için bunu DEĞİL `_parse_float` kullanın.
    """
    if s is None or isinstance(s, bool):
        return None
    if isinstance(s, (int, float)):
        return float(s)
    t = str(s).strip()
    for sus in _SAYI_SUSLERI:
        t = t.replace(sus, '')
    t = t.strip()
    if not t or t in ('-', '.', ',', '--'):
        return None
    if _TR_BINLIK_RE.match(t):
        return float(t.replace('.', '').replace(',', '.'))
    if _TR_ONDALIK_RE.match(t):
        return float(t.replace(',', '.'))
    if _DUZ_TAMSAYI_RE.match(t):
        return float(t)
    return None


def _parse_float(val) -> Optional[float]:
    """DB'de SAKLI (String kolon) değeri float'a çevirir.

    kpi_data.actual_value/target_value String(100) kolonlardır. Yerel DB ölçümü
    (2026-10-10): '.' içeren 365.922 aktif kayıttan 365.921'i kanonik 'x.y',
    0'ı 3-haneli belirsiz; 1'i '₺100.070.853' (TR binlik). Bu yüzden kanonik
    biçim Türkçe kuralla YORUMLANMAZ ('0.125' -> 0.125, 125 değil); diğer her
    şey `parse_tr_number`dan geçer.
    """
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    t = str(val).strip()
    for sus in _SAYI_SUSLERI:
        t = t.replace(sus, '')
    t = t.strip()
    if _KANONIK_RE.match(t):
        return float(t)
    return parse_tr_number(t)


def normalize_direction(direction) -> str:
    """Yön eş anlamlılarını tek koda indirger: 'Increasing' | 'Decreasing' (A-021)."""
    d = str(direction or '').strip().lower()
    if d in ('decreasing', 'azalan', 'azalis', 'azalış', 'lower_is_better', 'dusuk', 'düşük'):
        return 'Decreasing'
    return 'Increasing'


# Toplulaştırma yöntemi — İKİ DİL BİR ARADA yaşıyor (D1/D2/M2, ölçüm 2026-07-21):
#
#   process_kpis.calculation_method       AVG 2389 · SUM 10           (kod)
#   process_kpis.data_collection_method   Ortalama 1747 · Toplama 493 ·
#                                          Son Değer 124 · AVG 35     (Türkçe + KİRLİ)
#   kpi_year_configs.calculation_method   Ortalama 1050 · AVG 35 ·
#                                          Son Değer 5 · NULL 24      (tek kolonda iki dil)
#
# Eskiden toplulaştırma yalnız ÜÇ Türkçe etikete bakıyordu; `AVG` hiçbir dala
# düşmeyip `else` ile TESADÜFEN doğru sonuç veriyordu. Ama biri `SUM` yazsaydı
# sessizce ortalama alınacaktı — stok/akım karışması demek ("yıllık satış"ı
# ortalamak 12 kat küçültür).
#
# Kolonları tek dile göç ettirmek bir VERİ kararı (kullanıcı onayı ister);
# burada okuma katmanı iki dili de doğru tanıyor. Tanınmayan değer log'a düşer.
_AGGREGATION_ALIASES = {
    'SUM': 'SUM', 'TOPLAMA': 'SUM', 'TOPLAM': 'SUM',
    'LAST': 'LAST', 'SON DEĞER': 'LAST', 'SON DEGER': 'LAST', 'LATEST': 'LAST',
    'AVG': 'AVG', 'ORTALAMA': 'AVG', 'MEAN': 'AVG', 'AVERAGE': 'AVG',
}


def normalize_aggregation_method(raw) -> str:
    """Toplulaştırma yöntemini kanonik koda çevirir: 'AVG' | 'SUM' | 'LAST'.

    Hem Türkçe etiketleri ('Ortalama', 'Toplama', 'Son Değer') hem İngilizce
    kodları ('AVG', 'SUM') tanır. Bilinmeyen değer AVG'ye düşer ve log'a
    yazılır — sessizce yanlış toplulaştırma yapmaktansa iz bırakmak gerekir.
    """
    if raw is None:
        return 'AVG'
    anahtar = str(raw).strip().upper()
    if not anahtar:
        return 'AVG'
    kanonik = _AGGREGATION_ALIASES.get(anahtar)
    if kanonik is None:
        try:
            current_app.logger.warning(
                "[score_engine] bilinmeyen toplulaştırma yöntemi %r — "
                "ortalama (AVG) varsayıldı.", raw,
            )
        except Exception as e:
            logger.error(f"normalize_aggregation_method failed: {e}")
        return 'AVG'
    return kanonik


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


def aggregate_actuals(values_newest_first, method) -> Optional[float]:
    """Yıl içi ham değerlerden TEK özet değer (Karar 6, Faz 1B).

    values_newest_first: en yeniden en eskiye sıralı sayılar. Yöntem: Toplama/Ortalama/Son Değer
    (Türkçe etiket veya SUM/AVG/LAST). Eskiden motor yalnız en yeni 100 kaydı topluyordu;
    günlük girilen PG'lerde yıl özeti kesiliyordu (HATA-06)."""
    vals = [float(v) for v in (values_newest_first or []) if v is not None]
    if not vals:
        return None
    yontem = normalize_aggregation_method(method)
    if yontem == 'SUM':
        return sum(vals)
    if yontem == 'LAST':
        return vals[0]
    return sum(vals) / len(vals)


def achievement(actual, target, direction='Increasing') -> Optional[float]:
    """TEK başarı oranı kuralı (0-100) — tüm ekranlar bunu kullanır (A-011, A-021).

    Artan : actual/target. Azalan: target/actual.
    Azalan + actual <= 0 -> 100 (Karar 5). Azalan + target 0 -> actual<=0 ? 100 : 0 (Karar 4).
    Artan + target 0 -> None (anlamsız). target < 0 -> None (A-011: oran yön
    bilgisini tersine çevirir; kâr/zarar gibi negatif hedefler uydurma puan
    yerine PUANLANMAZ, çağıran "puanlanamadı" gösterir).
    """
    if target is None or actual is None:
        return None
    try:
        hedef_f = float(target)
        gercek_f = float(actual)
    except (TypeError, ValueError):
        return None
    azalan = normalize_direction(direction) == 'Decreasing'
    if hedef_f < 0:
        return None
    if hedef_f == 0:
        if azalan:
            return 100.0 if gercek_f <= 0 else 0.0
        return None
    if azalan:
        if gercek_f <= 0:
            return 100.0
        ratio = hedef_f / gercek_f
    else:
        ratio = gercek_f / hedef_f
    return round(min(100.0, max(0.0, ratio * 100.0)), 2)


def adverse_deviation_pct(actual, target, direction='Increasing') -> Optional[float]:
    """Hedefe göre OLUMSUZ sapma yüzdesi (>0 = kötü yönde, <=0 = hedefte/iyi yönde).

    Artan : (hedef - gerçek) / hedef. Azalan: (gerçek - hedef) / hedef. Yön `normalize_direction`
    ile çözülür. Hedef <= 0 veya değer eksikse None (negatif/sıfır hedefte oran anlamsız —
    `achievement` ile aynı kural). Sapma/uyarı formülleri bunu kullanır; kendi formülünü yazmaz."""
    if target is None or actual is None:
        return None
    try:
        hedef_f = float(target)
        gercek_f = float(actual)
    except (TypeError, ValueError):
        return None
    if hedef_f <= 0:
        return None
    if normalize_direction(direction) == 'Decreasing':
        return (gercek_f - hedef_f) / hedef_f * 100.0
    return (hedef_f - gercek_f) / hedef_f * 100.0


def compute_pg_score(
    hedef_val: Optional[float],
    gerceklesen_val: Optional[float],
    direction: str = 'Increasing'
) -> Optional[float]:
    """Geriye dönük ad: `achievement` ile aynı (hedef, gerçekleşen sırası)."""
    return achievement(gerceklesen_val, hedef_val, direction)


def weighted_average(pairs) -> Optional[float]:
    """[(skor|None, ağırlık|None)] -> normalize ağırlıklı ortalama (A-005).

    Skoru None olan ölçülmemiştir, paydan düşer. Ağırlıklar `_distribute_weights`
    ile (boş kalan pay eşit bölünür) toplu dağıtılır ve toplam üzerinden
    normalize edilir. Hiçbiri ölçülmemişse None.
    """
    pairs = list(pairs or [])
    if not pairs:
        return None
    ws = _distribute_weights([w for _, w in pairs])
    total = w_sum = 0.0
    for (sc, _), w in zip(pairs, ws):
        if sc is None or not w or w <= 0:
            continue
        total += sc * w
        w_sum += w
    if w_sum <= 0:
        return None
    return round(total / w_sum, 2)


def period_start(year, period_type, period_no=None, period_month=None, data_date=None) -> Optional[date]:
    """Girişin ait olduğu dönemin İLK günü (A-007). Türetilemezse None."""
    if not year or not period_type:
        return None
    pt = str(period_type).lower().strip()
    try:
        pn = int(period_no) if period_no is not None else 1
        pm = int(period_month) if period_month is not None else None
        if pt == 'yillik':
            return date(year, 1, 1)
        if pt == 'halfyear':
            return date(year, 1 if pn <= 1 else 7, 1)
        if pt == 'ceyrek':
            return date(year, (max(1, min(4, pn)) - 1) * 3 + 1, 1)
        if pt == 'aylik':
            return date(year, max(1, min(12, pn)), 1)
        if pt in ('haftalik', 'gunluk') and pm is not None:
            return date(year, max(1, min(12, pm)), 1)
    except (ValueError, TypeError):
        return None
    return None


def entry_in_scope(entry, as_of: date) -> bool:
    """TEK tarih kesimi kuralı (A-007): dönem BAŞLAMIŞSA dahil.

    Sihirbaz data_date'i dönem SONU yapar (Eylül verisi 30 Eylül). 10 Eylül'de
    girilen cari dönem verisi `data_date <= as_of` ile dışlanıyordu. Artık
    dönemin ilk günü (veya data_date, hangisi daha erkense) as_of'u geçmediyse
    kayıt dahildir. Dönem alanı yoksa data_date <= as_of.
    """
    dd = getattr(entry, 'data_date', None)
    ps = period_start(
        getattr(entry, 'year', None), getattr(entry, 'period_type', None),
        getattr(entry, 'period_no', None), getattr(entry, 'period_month', None), dd,
    )
    cand = [d for d in (ps, dd) if d is not None]
    if not cand:
        return True
    return min(cand) <= as_of


def _default_weight(weight: Optional[float], sibling_count: int) -> float:
    """TEK bir kardeşin ağırlığı — kardeşlerin toplu durumunu BİLMEZ.

    ⚠ Karışık durumda (bazı kardeşlerde ağırlık dolu, bazılarında boş) toplam
    100 etmez. Böyle bir grubu hesaplarken `_distribute_weights` kullanın.
    Bu fonksiyon geriye dönük uyum için duruyor.
    """
    if sibling_count <= 0:
        return 100.0
    if weight is not None and weight > 0:
        return min(100.0, max(0.0, float(weight)))
    return 100.0 / sibling_count


def _distribute_weights(weights: list) -> list:
    """Kardeş grubunun ağırlıklarını tutarlı biçimde dağıtır (toplam 100).

    B5 (2026-07-21): `_default_weight` her kardeşi BAĞIMSIZ değerlendiriyordu:
    ağırlık doluysa o değer, boşsa `100/n`. Aynı süreçte ikisi karışıksa
    payda 100 etmiyordu.

        3 KPI, skorlar [100, 0, 0], ağırlıklar [60, 0, 0]
        _default_weight → [60.0, 33.33, 33.33]   toplam 126.67
        sonuç           : 47.37
        beklenen (60/20/20)                     : 60.00   → 12.6 puan sapma

    Ölçüm: 2327 aktif KPI'nın 469'unun ağırlığı 0; **64 süreçte** hem dolu
    hem boş ağırlık bir arada.

    Kural: tanımlı ağırlıklar aynen korunur; KALAN pay (100 − tanımlı toplam)
    ağırlıksız kardeşlere eşit bölünür. Tanımlılar zaten 100'ü aşıyorsa
    ağırlıksızlara pay kalmaz (0) — kullanıcının açık tercihi ezilmez.
    """
    n = len(weights)
    if n == 0:
        return []

    tanimli = [
        (float(w) if (w is not None and float(w) > 0) else None) for w in weights
    ]
    tanimli_toplam = sum(w for w in tanimli if w is not None)
    bossayi = sum(1 for w in tanimli if w is None)

    if bossayi == 0:
        return [w for w in tanimli]          # hepsi tanımlı → dokunma
    if tanimli_toplam <= 0:
        return [100.0 / n] * n               # hiçbiri tanımlı değil → eşit

    kalan = max(0.0, 100.0 - tanimli_toplam)
    pay = kalan / bossayi
    return [(pay if w is None else w) for w in tanimli]


def _load_entries(pg_ids, year, as_of) -> Dict[int, list]:
    """PG başına yıl içi aktif KpiData (en yeni önce), tarih kesimi `entry_in_scope`."""
    out: Dict[int, list] = {}
    if not pg_ids:
        return out
    for d in (
        KpiData.query.filter(
            KpiData.process_kpi_id.in_(list(pg_ids)),
            KpiData.year == year,
            KpiData.is_active.is_(True),
        ).order_by(KpiData.process_kpi_id, KpiData.data_date.desc()).all()
    ):
        if entry_in_scope(d, as_of):
            out.setdefault(d.process_kpi_id, []).append(d)  # sınır YOK (Karar 6)
    return out


def _resolve_ancestor_entries(pending_pgs, year, as_of, max_steps: int = 8) -> Dict[int, list]:
    """Verisi olmayan klon PG'ler için `source_kpi_id` zincirinde ilk verili atanın kayıtları.

    Her seviye için en fazla 2 toplu sorgu (O(derinlik)); en fazla 8 ata, döngü korumalı.
    """
    result: Dict[int, list] = {}
    cur = {pg.id: getattr(pg, 'source_kpi_id', None) for pg in pending_pgs}
    visited = {pg.id: {pg.id} for pg in pending_pgs}
    for _ in range(max_steps):
        cur = {k: a for k, a in cur.items() if a and a not in visited[k]}
        if not cur:
            break
        ancestors = set(cur.values())
        ent_by = _load_entries(ancestors, year, as_of)
        src = dict(
            db.session.query(ProcessKpi.id, ProcessKpi.source_kpi_id)
            .filter(ProcessKpi.id.in_(ancestors)).all()
        )
        nxt = {}
        for k, a in cur.items():
            visited[k].add(a)
            if ent_by.get(a):
                result[k] = ent_by[a]
            else:
                nxt[k] = src.get(a)
        cur = nxt
    return result


def _kpi_effective_cfg(pg, cfg_map: Dict[int, Dict]) -> Dict[str, Any]:
    """PG için etkin yapılandırma: yıllık config varsa o, yoksa ProcessKpi."""
    cfg = cfg_map.get(pg.id)
    if cfg:
        return {
            'target_raw': cfg["target_value"],
            'direction': cfg["direction"] or "Increasing",
            'method': cfg["data_collection_method"] or "Ortalama",
            'weight': cfg.get("weight"),
            'is_included': cfg.get("is_included", True) is not False,
        }
    return {
        'target_raw': pg.target_value,
        'direction': pg.direction or "Increasing",
        'method': pg.data_collection_method or "Ortalama",
        'weight': pg.weight,
        'is_included': True,
    }


def _score_pgs(pgs, year, as_of, plan_year, cfg_map) -> Dict[int, Dict[str, Any]]:
    """ÇEKİRDEK: PG listesi için {pg_id: {score, actual, target, direction, method,
    weight, is_included, entry_count}}. Tek hesap yolu; tüm genel API bunu kullanır."""
    ids = [pg.id for pg in pgs]
    entries_by_pg = _load_entries(ids, year, as_of)
    chain: Dict[int, list] = {}
    if plan_year is not None:
        pending = [pg for pg in pgs if not entries_by_pg.get(pg.id)]
        if pending:
            chain = _resolve_ancestor_entries(pending, year, as_of)

    out: Dict[int, Dict[str, Any]] = {}
    for pg in pgs:
        c = _kpi_effective_cfg(pg, cfg_map)
        row = {
            'score': None, 'actual': None, 'target': None,
            'direction': normalize_direction(c['direction']),
            'method': normalize_aggregation_method(c['method']),
            'weight': c['weight'], 'is_included': c['is_included'], 'entry_count': 0,
        }
        out[pg.id] = row
        if not c['is_included']:
            continue  # A-002: bu yıl dahil değil
        entries = entries_by_pg.get(pg.id) or chain.get(pg.id) or []
        row['entry_count'] = len(entries)
        if not entries:
            continue
        target = _resolve_target_for_calculation(c['target_raw'], c['direction'])
        row['target'] = target
        vals = [v for v in (_parse_float(e.actual_value) for e in entries) if v is not None]
        if not vals:
            continue
        actual = aggregate_actuals(vals, c['method'])
        row['actual'] = actual
        row['score'] = achievement(actual, target, c['direction'])
    return out


def _load_cfg_map(pgs, plan_year) -> Dict[int, Dict]:
    if plan_year is None or not pgs:
        return {}
    try:
        from app.services.plan_year_service import get_kpi_configs_bulk
        return get_kpi_configs_bulk(pgs, plan_year)
    except Exception as e:
        current_app.logger.warning(f"[score_engine] plan_year config çekilemedi: {e}")
        return {}


def get_pg_scores_from_kpi_data(
    tenant_id: int,
    year: Optional[int] = None,
    as_of_date: Optional[date] = None,
    plan_year=None,  # PlanYear instance; None → ProcessKpi fallback
    cfg_map: Optional[Dict[int, Dict]] = None,
) -> Dict[int, Optional[float]]:
    """Her aktif ProcessKpi için skor ({pg_id: skor|None}). Yıllık config uygulanır;
    `is_included=False` PG'ler None döner."""
    if year is None:
        year = resolve_request_year()
    as_of = as_of_date or today_tr()

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
    if cfg_map is None:
        cfg_map = _load_cfg_map(pgs, plan_year)
    res = _score_pgs(pgs, year, as_of, plan_year, cfg_map)
    return {k: v['score'] for k, v in res.items()}


def compute_process_scores_internal(
    tenant_id: int,
    year: int,
    as_of: date,
    persist_pg_scores: bool,
    plan_year=None,  # PlanYear instance; None → ProcessKpi fallback
) -> tuple[Dict[int, float], Dict[int, Optional[float]]]:
    """PG → süreç skorları (0–100). K-Vektör ve klasik vizyon motoru ortak kullanır.

    Kurallar: ölçülmemiş (None) paydan düşer, tüm alt/PG ölçülmediyse süreç None
    (A-001); çocuklu sürecin kendi PG'leri de hesaba girer (çocuk bloğu ile kendi
    PG bloğu eşit ağırlık); yıllık config `is_included`/`weight` uygulanır (A-002)."""
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
    children_by_parent: Dict[Any, list] = {}
    for p in processes:
        children_by_parent.setdefault(p.parent_id, []).append(p.id)
    proc_by_id = {p.id: p for p in processes}

    # P1 (N+1 önlemi): tüm süreçlerin aktif KPI'ları TEK sorguda
    _kpis_by_proc: Dict[int, list] = {}
    if processes:
        for _k in ProcessKpi.query.filter(
            ProcessKpi.process_id.in_(list(proc_by_id)),
            ProcessKpi.is_active.is_(True),
        ).all():
            _kpis_by_proc.setdefault(_k.process_id, []).append(_k)

    all_kpis = [k for ks in _kpis_by_proc.values() for k in ks]
    cfg_map = _load_cfg_map(all_kpis, plan_year)
    pg_scores = get_pg_scores_from_kpi_data(
        tenant_id, year, as_of, plan_year=plan_year, cfg_map=cfg_map)
    # Süreç KPI'ları pg_scores sorgusunun kapsamı dışında kalmış olabilir → tamamla.
    eksik = [k for k in all_kpis if k.id not in pg_scores]
    if eksik:
        ek = _score_pgs(eksik, year, as_of, plan_year, cfg_map)
        for kid, r in ek.items():
            pg_scores[kid] = r['score']

    process_scores: Dict[int, Optional[float]] = {}
    in_progress: set = set()

    def calc_process_score(process_id: int) -> Optional[float]:
        if process_id in process_scores:
            return process_scores[process_id]
        if process_id not in proc_by_id or process_id in in_progress:
            return None
        in_progress.add(process_id)

        # Kendi PG'leri (yıllık config: is_included/weight)
        own_pairs = []
        for kpi in _kpis_by_proc.get(process_id, []):
            c = _kpi_effective_cfg(kpi, cfg_map)
            if not c['is_included']:
                continue
            own_pairs.append((pg_scores.get(kpi.id), c['weight']))
        own_score = weighted_average(own_pairs)
        if own_score is not None and persist_pg_scores:
            for kpi in _kpis_by_proc.get(process_id, []):
                if pg_scores.get(kpi.id) is not None:
                    kpi.calculated_score = pg_scores[kpi.id]

        child_ids = children_by_parent.get(process_id, [])
        child_score = None
        if child_ids:
            child_score = weighted_average(
                [(calc_process_score(cid), proc_by_id[cid].weight) for cid in child_ids]
            )
        parcalar = [x for x in (own_score, child_score) if x is not None]
        sonuc = round(sum(parcalar) / len(parcalar), 2) if parcalar else None
        in_progress.discard(process_id)
        process_scores[process_id] = sonuc
        return sonuc

    for p in processes:
        calc_process_score(p.id)

    # None İÇERİDE korunur ("ölçülmedi" ≠ 0); compute_vision_score dışarıya süzer.
    return process_scores, pg_scores


# ── GENEL API (ekranlar bunu çağırır) ──────────────────────────────────────

def _load_plan_year(plan_year_id):
    from app.models.plan_year import PlanYear
    py = db.session.get(PlanYear, plan_year_id) if plan_year_id else None
    return py


def calculate_kpi_detail(kpi_id: int, plan_year_id: int, as_of: Optional[date] = None) -> Dict[str, Any]:
    """Tek PG için ayrıntı: {score, actual, target, direction, method, weight,
    is_included, entry_count}. Soft-delete edilmiş PG için score None."""
    py = _load_plan_year(plan_year_id)
    boş = {'score': None, 'actual': None, 'target': None, 'direction': 'Increasing',
           'method': 'AVG', 'weight': None, 'is_included': False, 'entry_count': 0}
    pg = db.session.get(ProcessKpi, kpi_id)
    if pg is None or not pg.is_active or py is None:
        return boş
    cfg_map = _load_cfg_map([pg], py)
    return _score_pgs([pg], py.year, as_of or today_tr(), py, cfg_map)[pg.id]


def calculate_kpi_score(kpi_id: int, plan_year_id: int, as_of: Optional[date] = None) -> Optional[float]:
    """Tek PG skoru (0-100) veya None (ölçülmedi / dahil değil / puanlanamadı)."""
    return calculate_kpi_detail(kpi_id, plan_year_id, as_of)['score']


def calculate_process_score(process_id: int, plan_year_id: int, as_of: Optional[date] = None) -> Optional[float]:
    """Süreç skoru (0-100) veya None (hiçbir PG/alt süreç ölçülmedi — 0 DEĞİL)."""
    py = _load_plan_year(plan_year_id)
    proc = db.session.get(Process, process_id)
    if py is None or proc is None or not proc.is_active:
        return None
    scores, _ = compute_process_scores_internal(
        proc.tenant_id, py.year, as_of or today_tr(), False, plan_year=py)
    return scores.get(process_id)


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
    as_of = as_of_date or today_tr()

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
            'as_of_date': (as_of_date or today_tr()).isoformat(),
            'tenant_id': None
        }
    return compute_vision_score(
        tenant_id,
        year or resolve_request_year(),
        as_of_date or today_tr(),
        persist_pg_scores=True
    )
