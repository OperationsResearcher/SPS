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
from app.models.core import Tenant, Strategy, SubStrategy, User
from app.models.process import (
    Process, ProcessKpi, ProcessSubStrategyLink, ProcessActivity,
    IndividualPerformanceIndicator,
)
from app.models.tenant_identity import (
    TenantValue, TenantEthicsCode, TenantQualityPolicy,
)


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
    # Kimlik doluluğu (5 boyut). purpose/vision hâlâ tek-TEXT; Değer/Etik/Kalite
    # ise çok-satırlı tablolardan (L1 Dal 3 "temiz kesim" — eski TEXT okunmaz):
    # ilgili tabloda ≥1 aktif madde varsa o boyut "dolu" sayılır.
    def _madde_var(Model) -> bool:
        return db.session.query(
            Model.query
            .filter(Model.tenant_id == tenant_id, Model.is_active.is_(True))
            .exists()
        ).scalar()

    kimlik_durumu = [
        bool(t and t.purpose and str(t.purpose).strip()),
        bool(t and t.vision and str(t.vision).strip()),
        _madde_var(TenantValue),
        _madde_var(TenantEthicsCode),
        _madde_var(TenantQualityPolicy),
    ]
    dolu = sum(1 for v in kimlik_durumu if v)
    kimlik_pct = _pct(dolu, len(kimlik_durumu))

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

    # L1 Dal 4: stratejinin bireye inmesi — kaç aktif kullanıcının ≥1 aktif
    # 'Stratejik' bireysel hedefi var (stratejik hizalama sinyali).
    toplam_kullanici = User.query.filter_by(
        tenant_id=tenant_id, is_active=True
    ).count()
    if toplam_kullanici:
        stratejik_sahip = (
            db.session.query(IndividualPerformanceIndicator.user_id)
            .join(User, User.id == IndividualPerformanceIndicator.user_id)
            .filter(
                User.tenant_id == tenant_id,
                IndividualPerformanceIndicator.is_active.is_(True),
                IndividualPerformanceIndicator.katman == "Stratejik",
            )
            .distinct()
            .count()
        )
        stratejik_hedef_pct = _pct(stratejik_sahip, toplam_kullanici)
    else:
        stratejik_hedef_pct = 0.0
        stratejik_sahip = 0

    skor = round((kimlik_pct + strateji_pct + stratejik_hedef_pct) / 3, 1)
    return {
        "skor": skor,
        "kimlik_doluluk_pct": kimlik_pct,
        "kimlik_dolu_alan": dolu,
        "strateji_butunluk_pct": strateji_pct,
        "toplam_strateji": toplam_strateji,
        "alt_stratejisi_olan": baglanmis,
        "stratejik_hedef_pct": stratejik_hedef_pct,
        "stratejik_hedef_sahip_kullanici": stratejik_sahip,
        "toplam_kullanici": toplam_kullanici,
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


# --- AI Yapı-Danışmanı (heuristik) -------------------------------------------
# L1: yapıyı yorumlar, performansı DEĞİL (PGV yok). KOE detayından somut
# boşlukları tespit eder, önceliklendirir, "bu dönem şuna odaklan" der.
# Saf fonksiyon — DB'siz, deterministik. Opsiyonel LLM anlatı sonra eklenebilir.

def _bosluklari_tespit_et(koe: dict) -> list[dict]:
    """KOE detayından somut yapısal boşlukları çıkar. Her biri severity (0-100,
    düşük skor = yüksek aciliyet) ile döner."""
    b = koe["boyutlar"]
    bosluklar = []

    # Boyut 1 — Kimlik & Strateji
    k = b["kimlik_strateji"]
    if k["kimlik_dolu_alan"] < 5:
        eksik = 5 - k["kimlik_dolu_alan"]
        bosluklar.append({
            "boyut": "kimlik_strateji", "severity": k["kimlik_doluluk_pct"],
            "baslik": f"{eksik} kimlik alanı boş",
            "oneri": "Misyon, Vizyon, Değerler, Etik ve Kalite alanlarından eksik olanları doldur.",
        })
    if k["toplam_strateji"] == 0:
        bosluklar.append({
            "boyut": "kimlik_strateji", "severity": 0,
            "baslik": "Hiç stratejin yok",
            "oneri": "En az birkaç ana strateji tanımla — yapının iskeleti budur.",
        })
    elif k["alt_stratejisi_olan"] < k["toplam_strateji"]:
        yetim = k["toplam_strateji"] - k["alt_stratejisi_olan"]
        bosluklar.append({
            "boyut": "kimlik_strateji", "severity": k["strateji_butunluk_pct"],
            "baslik": f"{yetim} strateji alt stratejisiz (yetim)",
            "oneri": "Her ana stratejiyi alt stratejilerle somutlaştır.",
        })

    # Boyut 2 — Süreç Mimarisi
    s = b["surec_mimarisi"]
    if s["toplam_surec"] == 0:
        bosluklar.append({
            "boyut": "surec_mimarisi", "severity": 0,
            "baslik": "Hiç sürecin yok",
            "oneri": "Süreçleri tanımla ve stratejilerine bağla.",
        })
    else:
        bosta = s["toplam_surec"] - s["stratejiye_bagli"]
        if bosta > 0:
            bosluklar.append({
                "boyut": "surec_mimarisi", "severity": s["bagli_pct"],
                "baslik": f"{bosta} süreç stratejiye bağlı değil (boşta)",
                "oneri": "Boştaki süreçleri hizmet ettikleri stratejilere bağla.",
            })
        olcutsuz = s["toplam_surec"] - s["pg_tanimli"]
        if olcutsuz > 0:
            bosluklar.append({
                "boyut": "surec_mimarisi", "severity": s["pg_pct"],
                "baslik": f"{olcutsuz} sürecin ölçütü (PG) tanımsız",
                "oneri": "Her süreç için neyi ölçeceğini tanımla (PGV girmeden, sadece ölçüt).",
            })

    # Boyut 3 — Olgunluk
    o = b["olgunluk"]
    if o["degerlendirme_sayisi"] == 0:
        bosluklar.append({
            "boyut": "olgunluk", "severity": 0,
            "baslik": "Hiç olgunluk değerlendirmesi yapılmamış",
            "oneri": "Süreçlerinin olgunluğunu 1-5 arası kendin değerlendir — ilerlemeyi böyle görürsün.",
        })
    elif o["ortalama_seviye"] and o["ortalama_seviye"] < 3:
        bosluklar.append({
            "boyut": "olgunluk", "severity": o["skor"],
            "baslik": f"Ortalama olgunluk düşük ({o['ortalama_seviye']}/5)",
            "oneri": "Düşük olgunluktaki süreçler için iyileştirme faaliyetleri planla.",
        })

    # Boyut 4 — İcra Disiplini
    i = b["icra_disiplini"]
    if i["toplam_faaliyet"] == 0:
        bosluklar.append({
            "boyut": "icra_disiplini", "severity": 0,
            "baslik": "Hiç iyileştirme faaliyetin yok",
            "oneri": "Süreçlerini geliştirmek için somut faaliyetler tanımla ve takip et.",
        })
    elif i["skor"] < 50:
        bekleyen = i["toplam_faaliyet"] - i["tamamlanan"]
        bosluklar.append({
            "boyut": "icra_disiplini", "severity": i["skor"],
            "baslik": f"{bekleyen} faaliyet tamamlanmamış (icra %{int(i['skor'])})",
            "oneri": "Planladığın iyileştirme faaliyetlerini hayata geçir.",
        })

    # En acil önce (düşük severity = yüksek aciliyet)
    bosluklar.sort(key=lambda x: x["severity"])
    return bosluklar


def _anlati_uret(koe: dict, bosluklar: list[dict]) -> str:
    """KOE skoruna + boşluk sayısına göre tek cümlelik durum anlatısı (heuristik)."""
    skor = koe["koe"]
    n = len(bosluklar)
    if skor >= 75:
        durum = "Yapın olgun ve büyük ölçüde tam"
    elif skor >= 50:
        durum = "Yapının temeli kurulmuş, geliştirilecek alanlar var"
    elif skor >= 25:
        durum = "Yapı kısmen kurulmuş, önemli eksikler var"
    else:
        durum = "Yapı henüz başlangıç aşamasında"
    if n == 0:
        return f"{durum}. Belirgin bir yapısal boşluk görünmüyor."
    return f"{durum}. {n} yapısal boşluk tespit edildi; en kritiğinden başla."


def yapi_danismani(koe: dict, max_oncelik: int = 3) -> dict:
    """L1 AI Yapı-Danışmanı (heuristik). KOE detayından boşluk raporu +
    önceliklendirilmiş öneri + anlatı üretir. Saf fonksiyon, DB'siz.

    Args:
        koe: compute_koe(tenant_id) çıktısı.
        max_oncelik: kaç öncelikli öneri döndürülecek.

    Returns:
        {
          "anlati": str,                 # tek cümle durum
          "oncelikler": [{boyut, baslik, oneri, severity}, ...],  # en kritik N
          "toplam_bosluk": int,
        }
    """
    bosluklar = _bosluklari_tespit_et(koe)
    return {
        "anlati": _anlati_uret(koe, bosluklar),
        "oncelikler": bosluklar[:max_oncelik],
        "toplam_bosluk": len(bosluklar),
    }
