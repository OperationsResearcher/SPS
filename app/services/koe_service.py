"""KOE — Kurumsal Olgunluk Endeksi.

L1 paketinin ölçüm omurgası. PGV (performans verisi girişi) YOKKEN, mevcut
yapısal veriden kurumun olgunluğunu hesaplar. Saf OKUMA — hiçbir şey yazmaz.

4 boyut (eşit ağırlık, her biri 0-100):
  1. Kimlik & Strateji Netliği — kimlik doluluğu + strateji bütünlüğü (sistem-hesaplı)
  2. Süreç Mimarisi — süreç-strateji bağı + PG tanımlılığı (sistem-hesaplı, PGV değil)
  3. Olgunluk — process_maturity öz-değerlendirme ortalaması (hafif öznel)
  4. İcra Disiplini — iyileştirme faaliyeti hayata geçirme oranı (sistem-hesaplı)

KOE = boyutların ağırlıklı ortalaması (şimdilik eşit %25).
"""
from __future__ import annotations

from extensions import db
from app.models.core import Tenant, Strategy, SubStrategy
from app.models.process import Process, ProcessKpi, ProcessSubStrategyLink, ProcessActivity


# Boyut ağırlıkları (toplam 1.0). Başlangıçta eşit; veriyle kalibre edilebilir.
_WEIGHTS = {
    "kimlik_strateji": 0.25,
    "surec_mimarisi": 0.25,
    "olgunluk": 0.25,
    "icra_disiplini": 0.25,
}


def _pct(part: int, whole: int) -> float:
    """part/whole yüzdesi (0-100), whole=0 ise 0."""
    return round(100.0 * part / whole, 1) if whole else 0.0


def _boyut_kimlik_strateji(tenant_id: int) -> dict:
    """Boyut 1 — Kimlik doluluğu + strateji bütünlüğü. Sistem-hesaplı."""
    t = Tenant.query.get(tenant_id)
    # Kimlik alanlarının doluluğu (5 alan)
    kimlik_alanlari = [
        getattr(t, f, None) if t else None
        for f in ("purpose", "vision", "core_values", "code_of_ethics", "quality_policy")
    ]
    dolu = sum(1 for v in kimlik_alanlari if v and str(v).strip())
    kimlik_pct = _pct(dolu, len(kimlik_alanlari))

    # Strateji bütünlüğü: kaç ana stratejinin ≥1 alt stratejisi var (yetim strateji cezası)
    strategies = Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    toplam_strateji = len(strategies)
    if toplam_strateji:
        strateji_ids = [s.id for s in strategies]
        # Alt stratejisi olan ana stratejiler (DISTINCT parent)
        sub_parents = {
            r[0] for r in db.session.query(SubStrategy.strategy_id)
            .filter(SubStrategy.strategy_id.in_(strateji_ids), SubStrategy.is_active.is_(True))
            .distinct().all()
        }
        baglanmis = len(sub_parents)
        strateji_pct = _pct(baglanmis, toplam_strateji)
    else:
        strateji_pct = 0.0
        baglanmis = 0

    skor = round((kimlik_pct + strateji_pct) / 2, 1)
    return {
        "skor": skor,
        "kimlik_doluluk_pct": kimlik_pct,
        "kimlik_dolu_alan": dolu,
        "strateji_butunluk_pct": strateji_pct,
        "toplam_strateji": toplam_strateji,
        "alt_stratejisi_olan": baglanmis,
    }


def _boyut_surec_mimarisi(tenant_id: int) -> dict:
    """Boyut 2 — Süreç-strateji bağı + PG tanımlılığı (PGV değil). Sistem-hesaplı."""
    processes = Process.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    toplam_surec = len(processes)
    if not toplam_surec:
        return {"skor": 0.0, "toplam_surec": 0, "stratejiye_bagli": 0,
                "bagli_pct": 0.0, "pg_tanimli": 0, "pg_pct": 0.0}

    proc_ids = [p.id for p in processes]
    # Stratejiye bağlı süreçler (boşta süreç cezası)
    bagli_ids = {
        r[0] for r in db.session.query(ProcessSubStrategyLink.process_id)
        .filter(ProcessSubStrategyLink.process_id.in_(proc_ids)).distinct().all()
    }
    bagli_pct = _pct(len(bagli_ids), toplam_surec)

    # PG tanımlı süreçler (sadece tanım — PGV değil)
    pg_ids = {
        r[0] for r in db.session.query(ProcessKpi.process_id)
        .filter(ProcessKpi.process_id.in_(proc_ids), ProcessKpi.is_active.is_(True))
        .distinct().all()
    }
    pg_pct = _pct(len(pg_ids), toplam_surec)

    skor = round((bagli_pct + pg_pct) / 2, 1)
    return {
        "skor": skor,
        "toplam_surec": toplam_surec,
        "stratejiye_bagli": len(bagli_ids),
        "bagli_pct": bagli_pct,
        "pg_tanimli": len(pg_ids),
        "pg_pct": pg_pct,
    }


def _boyut_olgunluk(tenant_id: int) -> dict:
    """Boyut 3 — process_maturity öz-değerlendirme ortalaması (1-5 → 0-100).

    process_maturity tablosu raw sorgulanır (modern model yok; kolonlar:
    tenant_id, maturity_level, dimension, is_active).
    """
    from sqlalchemy import text
    row = db.session.execute(
        text(
            "SELECT AVG(maturity_level), COUNT(*) FROM process_maturity "
            "WHERE tenant_id = :tid AND COALESCE(is_active, true) = true"
        ),
        {"tid": tenant_id},
    ).first()
    ort = float(row[0]) if row and row[0] is not None else 0.0
    adet = int(row[1]) if row and row[1] is not None else 0
    # 1-5 ölçeği → 0-100
    skor = round(_pct(ort, 5.0), 1) if ort else 0.0
    return {"skor": skor, "ortalama_seviye": round(ort, 2), "degerlendirme_sayisi": adet}


def _boyut_icra_disiplini(tenant_id: int) -> dict:
    """Boyut 4 — İyileştirme faaliyeti hayata geçirme oranı. Sistem-hesaplı."""
    # Tenant'ın süreçlerine bağlı faaliyetler
    proc_ids = [
        r[0] for r in db.session.query(Process.id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True)).all()
    ]
    if not proc_ids:
        return {"skor": 0.0, "toplam_faaliyet": 0, "tamamlanan": 0}

    faaliyetler = ProcessActivity.query.filter(
        ProcessActivity.process_id.in_(proc_ids), ProcessActivity.is_active.is_(True)
    ).all()
    toplam = len(faaliyetler)
    if not toplam:
        return {"skor": 0.0, "toplam_faaliyet": 0, "tamamlanan": 0}

    tamamlanan = sum(1 for f in faaliyetler if _is_tamamlandi(f))
    skor = _pct(tamamlanan, toplam)
    return {"skor": skor, "toplam_faaliyet": toplam, "tamamlanan": tamamlanan}


def compute_koe(tenant_id: int) -> dict:
    """Bir tenant için KOE'yi hesapla. Saf okuma — hiçbir şey yazmaz.

    Returns:
        {
          "tenant_id": int,
          "koe": float,                 # 0-100 ağırlıklı toplam
          "boyutlar": {
            "kimlik_strateji": {...}, "surec_mimarisi": {...},
            "olgunluk": {...}, "icra_disiplini": {...}
          },
          "agirliklar": {...}
        }
    """
    boyutlar = {
        "kimlik_strateji": _boyut_kimlik_strateji(tenant_id),
        "surec_mimarisi": _boyut_surec_mimarisi(tenant_id),
        "olgunluk": _boyut_olgunluk(tenant_id),
        "icra_disiplini": _boyut_icra_disiplini(tenant_id),
    }
    koe = round(sum(boyutlar[k]["skor"] * w for k, w in _WEIGHTS.items()), 1)
    return {
        "tenant_id": tenant_id,
        "koe": koe,
        "boyutlar": boyutlar,
        "agirliklar": dict(_WEIGHTS),
    }


def _is_tamamlandi(activity) -> bool:
    """Faaliyet 'tamamlandı' mı? status alanına bakar (esnek)."""
    st = (getattr(activity, "status", "") or "").strip().lower()
    return st in ("tamamlandı", "tamamlandi", "completed", "done", "yapıldı", "yapildi")
