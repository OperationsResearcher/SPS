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

from flask import current_app
from flask_babel import gettext as _

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

# Boşluk etki seviyeleri — "temel" boşluklar (yapının iskeleti hiç yok) her
# zaman "kısmi" boşlukların (iskelet var, eksik tamamlanıyor) önüne geçer.
_ETKI_TEMEL = "temel"   # hiç strateji/süreç/faaliyet/değerlendirme yok
_ETKI_KISMI = "kismi"   # iskelet var, kısmi eksik
_ETKI_AGIRLIK = {_ETKI_TEMEL: 100, _ETKI_KISMI: 40}


def _oncelik_puani(bosluk: dict) -> float:
    """Ağırlıklı öncelik = etki × aciliyet. Yüksek puan = daha öncelikli.

    etki: temel(100) > kısmi(40) — yapı iskeleti hiç yoksa her şeyin önünde.
    aciliyet: (100 - severity) — düşük skorlu boyut daha acil.
    """
    etki_w = _ETKI_AGIRLIK.get(bosluk.get("etki"), _ETKI_AGIRLIK[_ETKI_KISMI])
    aciliyet = 100 - float(bosluk.get("severity", 100))
    return etki_w + aciliyet  # toplamsal: temel daima kısmının üstünde başlar


def _bosluklari_tespit_et(koe: dict) -> list[dict]:
    """KOE detayından somut yapısal boşlukları çıkar. Her biri severity (0-100,
    düşük skor = yüksek aciliyet) + etki (temel/kısmi) ile döner."""
    b = koe["boyutlar"]
    bosluklar = []

    # Boyut 1 — Kimlik & Strateji
    k = b["kimlik_strateji"]
    if k["kimlik_dolu_alan"] < 5:
        eksik = 5 - k["kimlik_dolu_alan"]
        bosluklar.append({
            "boyut": "kimlik_strateji", "severity": k["kimlik_doluluk_pct"],
            "etki": _ETKI_KISMI,
            "baslik": _("%(n)s kimlik alanı boş") % {"n": eksik},
            "oneri": _("Misyon, Vizyon, Değerler, Etik ve Kalite alanlarından eksik olanları doldur."),
        })
    if k["toplam_strateji"] == 0:
        bosluklar.append({
            "boyut": "kimlik_strateji", "severity": 0,
            "etki": _ETKI_TEMEL,
            "baslik": _("Hiç stratejin yok"),
            "oneri": _("En az birkaç ana strateji tanımla — yapının iskeleti budur."),
        })
    elif k["alt_stratejisi_olan"] < k["toplam_strateji"]:
        yetim = k["toplam_strateji"] - k["alt_stratejisi_olan"]
        bosluklar.append({
            "boyut": "kimlik_strateji", "severity": k["strateji_butunluk_pct"],
            "etki": _ETKI_KISMI,
            "baslik": _("%(n)s strateji alt stratejisiz (yetim)") % {"n": yetim},
            "oneri": _("Her ana stratejiyi alt stratejilerle somutlaştır."),
        })

    # Boyut 2 — Süreç Mimarisi
    s = b["surec_mimarisi"]
    if s["toplam_surec"] == 0:
        bosluklar.append({
            "boyut": "surec_mimarisi", "severity": 0,
            "etki": _ETKI_TEMEL,
            "baslik": _("Hiç sürecin yok"),
            "oneri": _("Süreçleri tanımla ve stratejilerine bağla."),
        })
    else:
        bosta = s["toplam_surec"] - s["stratejiye_bagli"]
        if bosta > 0:
            bosluklar.append({
                "boyut": "surec_mimarisi", "severity": s["bagli_pct"],
                "etki": _ETKI_KISMI,
                "baslik": _("%(n)s süreç stratejiye bağlı değil (boşta)") % {"n": bosta},
                "oneri": _("Boştaki süreçleri hizmet ettikleri stratejilere bağla."),
            })
        olcutsuz = s["toplam_surec"] - s["pg_tanimli"]
        if olcutsuz > 0:
            bosluklar.append({
                "boyut": "surec_mimarisi", "severity": s["pg_pct"],
                "etki": _ETKI_KISMI,
                "baslik": _("%(n)s sürecin ölçütü (PG) tanımsız") % {"n": olcutsuz},
                "oneri": _("Her süreç için neyi ölçeceğini tanımla (PGV girmeden, sadece ölçüt)."),
            })

    # Boyut 3 — Olgunluk
    o = b["olgunluk"]
    if o["degerlendirme_sayisi"] == 0:
        bosluklar.append({
            "boyut": "olgunluk", "severity": 0,
            "etki": _ETKI_TEMEL,
            "baslik": _("Hiç olgunluk değerlendirmesi yapılmamış"),
            "oneri": _("Süreçlerinin olgunluğunu 1-5 arası kendin değerlendir — ilerlemeyi böyle görürsün."),
        })
    elif o["ortalama_seviye"] and o["ortalama_seviye"] < 3:
        bosluklar.append({
            "boyut": "olgunluk", "severity": o["skor"],
            "etki": _ETKI_KISMI,
            "baslik": _("Ortalama olgunluk düşük (%(sev)s/5)") % {"sev": o['ortalama_seviye']},
            "oneri": _("Düşük olgunluktaki süreçler için iyileştirme faaliyetleri planla."),
        })

    # Boyut 4 — İcra Disiplini
    i = b["icra_disiplini"]
    if i["toplam_faaliyet"] == 0:
        bosluklar.append({
            "boyut": "icra_disiplini", "severity": 0,
            "etki": _ETKI_TEMEL,
            "baslik": _("Hiç iyileştirme faaliyetin yok"),
            "oneri": _("Süreçlerini geliştirmek için somut faaliyetler tanımla ve takip et."),
        })
    elif i["skor"] < 50:
        bekleyen = i["toplam_faaliyet"] - i["tamamlanan"]
        bosluklar.append({
            "boyut": "icra_disiplini", "severity": i["skor"],
            "etki": _ETKI_KISMI,
            "baslik": _("%(n)s faaliyet tamamlanmamış (icra %%%(skor)s)") % {"n": bekleyen, "skor": int(i['skor'])},
            "oneri": _("Planladığın iyileştirme faaliyetlerini hayata geçir."),
        })

    # Ağırlıklı öncelik: temel boşluklar (iskelet hiç yok) en üstte, sonra
    # aciliyet (düşük skor). Yüksek öncelik puanı önce.
    bosluklar.sort(key=_oncelik_puani, reverse=True)
    return bosluklar


def _anlati_uret(koe: dict, bosluklar: list[dict]) -> str:
    """KOE skoruna + boşluk sayısına göre tek cümlelik durum anlatısı (heuristik)."""
    skor = koe["koe"]
    n = len(bosluklar)
    if skor >= 75:
        durum = _("Yapın olgun ve büyük ölçüde tam")
    elif skor >= 50:
        durum = _("Yapının temeli kurulmuş, geliştirilecek alanlar var")
    elif skor >= 25:
        durum = _("Yapı kısmen kurulmuş, önemli eksikler var")
    else:
        durum = _("Yapı henüz başlangıç aşamasında")
    if n == 0:
        return _("%(durum)s. Belirgin bir yapısal boşluk görünmüyor.") % {"durum": durum}
    return _("%(durum)s. %(n)s yapısal boşluk tespit edildi; en kritiğinden başla.") % {"durum": durum, "n": n}


def _llm_anlatim(koe: dict, oncelikler: list[dict], heuristik_anlati: str,
                 tenant_id: int) -> dict | None:
    """Opsiyonel LLM zenginleştirme — anlatıyı ve öneri cümlelerini yeniden yazar.

    Boşluk TESPİTİ heuristik kalır (LLM bulguyu değiştiremez); LLM yalnızca
    mevcut bulguların ifadesini doğallaştırır. Gateway provider'sız ya da çıktı
    bozuksa None döner → caller heuristik metinlerde kalır.
    """
    import json as _json
    from app.services.llm_gateway import call_llm

    # LLM'e yalnızca yapısal bulguları ver; uydurmasını engelle.
    payload = {
        "koe_skoru": koe.get("koe"),
        "oncelikler": [
            {"no": i + 1, "boyut": o.get("boyut"), "bulgu": o.get("baslik")}
            for i, o in enumerate(oncelikler)
        ],
    }
    system_prompt = (
        "Sen bir kurumsal yapı danışmanısın. Sana bir kurumun olgunluk endeksi (KOE) "
        "ve TESPİT EDİLMİŞ yapısal boşluklar verilir. Görevin yalnızca bu bulguları "
        "Türkçe, yöneticiye hitap eden, kısa ve somut bir dile çevirmek. "
        "YENİ bulgu UYDURMA, sayı EKLEME, verilenleri değiştirme. "
        "Yanıtı SADECE şu JSON formatında ver: "
        '{\"anlati\": \"tek cümle genel durum\", '
        '\"oneriler\": [\"1. öncelik için tek cümle öneri\", \"2. için\", ...]}. '
        "oneriler dizisi öncelik sırasıyla ve öncelik sayısı kadar olmalı."
    )
    prompt = _json.dumps(payload, ensure_ascii=False)

    res = call_llm(
        tenant_id=tenant_id, endpoint="koe_yapi_danismani",
        prompt=prompt, system_prompt=system_prompt, max_output_tokens=600,
    )
    text = res.get("text")
    if not text:
        return None  # provider yok / kota / hata → heuristik
    try:
        # LLM bazen ```json ... ``` sarar; ilk { ile son } arasını al
        i, j = text.find("{"), text.rfind("}")
        if i < 0 or j <= i:
            return None  # JSON gövdesi yok → heuristik
        data = _json.loads(text[i:j + 1])
        anlati = (data.get("anlati") or "").strip()
        oneriler = data.get("oneriler") or []
        # "Hem anlatı hem öneri LLM" — ikisi de gelmeli, yoksa tümüyle heuristik
        if not anlati or not isinstance(oneriler, list) or not oneriler:
            return None
        return {"anlati": anlati, "oneriler": [str(x).strip() for x in oneriler]}
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"[koe_yapi_danismani] LLM parse hatası: {e}")
        return None


def yapi_danismani(koe: dict, max_oncelik: int = 3, tenant_id: int | None = None,
                   use_llm: bool = False) -> dict:
    """L1 AI Yapı-Danışmanı. KOE detayından boşluk raporu + önceliklendirilmiş
    öneri + anlatı üretir. Boşluk tespiti her zaman heuristik (deterministik).

    use_llm=True ve tenant_id verilirse anlatı + öneri cümleleri LLM ile
    zenginleştirilir; provider yoksa/çıktı bozuksa heuristik metne düşülür.

    Args:
        koe: compute_koe(tenant_id) çıktısı.
        max_oncelik: kaç öncelikli öneri döndürülecek.
        tenant_id: LLM çağrısı için (use_llm=True iken zorunlu).
        use_llm: opsiyonel LLM zenginleştirme.

    Returns:
        {
          "anlati": str,
          "oncelikler": [{boyut, baslik, oneri, severity, etki}, ...],
          "toplam_bosluk": int,
          "kaynak": "heuristik" | "llm",   # anlatının kaynağı
        }
    """
    bosluklar = _bosluklari_tespit_et(koe)
    oncelikler = bosluklar[:max_oncelik]
    anlati = _anlati_uret(koe, bosluklar)
    kaynak = "heuristik"

    if use_llm and tenant_id is not None and oncelikler:
        llm = _llm_anlatim(koe, oncelikler, anlati, tenant_id)
        if llm:
            anlati = llm["anlati"]
            # LLM önerilerini eşle (sayı tutarsa); heuristik öneri yedek
            llm_oneriler = llm["oneriler"]
            for idx, o in enumerate(oncelikler):
                if idx < len(llm_oneriler) and llm_oneriler[idx]:
                    o["oneri"] = llm_oneriler[idx]
            kaynak = "llm"

    return {
        "anlati": anlati,
        "oncelikler": oncelikler,
        "toplam_bosluk": len(bosluklar),
        "kaynak": kaynak,
    }
