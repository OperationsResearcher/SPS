# -*- coding: utf-8 -*-
"""Hedef Manipülasyonu Radarı (TASK-262).

SORU: Rakip strateji yazılımları "hedefe ulaştın mı?" diye sorar. Bu servis
farklı bir soru sorar: **"Hedefin kendisi dürüst mü?"**

NEDEN ÖNEMLİ: Bu kategorinin en bilinen eleştirisi "shelf-ware oluyor,
kimse ciddiye almıyor". Mekanizma basit — hedef tutmayınca hedef değişir,
sistem yeşil gösterir, kimse fark etmez. Microsoft bunu kendi ürününde
yaşadı ve yazılı olarak itiraf etti (Viva Goals, 31.12.2025 kapandı:
"overall adoption and usage… hasn't grown"). Bir dashboard "hedefe ulaştın
mı" sorduğu sürece tiyatroya hizmet eder; "hedef dürüst mü" sorusu tiyatroyu
bozar.

VERİ: `kpi_data_audits.old_target/new_target` (TASK-261'de eklendi).
Öncesinde hedef değişikliğinin NE'den NE'ye olduğu kaydedilmiyordu.

⚠️ SINIR — dürüstlük şart:
  - Bu servis NİYET OKUMAZ. "Hedef aşağı çekildi" bir OLGU; sebebi meşru
    olabilir (pazar çöktü, kapsam değişti). Çıktı suçlama değil, SORU üretir.
  - TASK-261 öncesi kayıtlarda hedef izi YOK → radar yalnız o tarihten
    sonraki değişiklikleri görür. Geriye dönük üretilemez.
  - Aralık hedefleri ('90-100') ve '-' sayıya indirgenemez → sapma yüzdesi
    hesaplanamaz; bunlar "yön belirsiz" sayılır, atılmaz.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from extensions import db
from app.models.core import User
from app.models.process import KpiData, KpiDataAudit, Process, ProcessKpi
from app.utils.numeric import safe_float

# Dönem kapanışına bu kadar gün kala yapılan hedef değişikliği "geç" sayılır.
# 7 gün: aylık dönemde son haftaya denk gelir — gerçekleşme büyük ölçüde
# bellidir, yani hedef sonuca göre ayarlanabilir konumdadır.
GEC_DEGISIM_GUN = 7

# Yönü "aşağı" saymak için gereken en küçük sapma (%). Ölçüm gürültüsünü
# (yuvarlama, birim düzeltmesi) manipülasyondan ayırır.
ANLAMLI_SAPMA_YUZDE = 1.0


def _yon(old_t: str | None, new_t: str | None) -> tuple[str, float | None]:
    """Hedef değişiminin yönü ve sapma yüzdesi.

    Returns: ("asagi"/"yukari"/"sabit"/"belirsiz", yuzde|None)
    "belirsiz": aralık hedefi ('90-100'), '-' vb. → sayıya indirgenemez.
    """
    o, n = safe_float(old_t), safe_float(new_t)
    if o is None or n is None:
        return "belirsiz", None
    if o == 0:
        return ("sabit", 0.0) if n == 0 else ("yukari" if n > 0 else "asagi", None)
    yuzde = (n - o) / abs(o) * 100
    if abs(yuzde) < ANLAMLI_SAPMA_YUZDE:
        return "sabit", round(yuzde, 2)
    return ("asagi" if yuzde < 0 else "yukari"), round(yuzde, 2)


def _gun_farki(a, b) -> int | None:
    """b - a, gün. İkisi de doluysa."""
    if not a or not b:
        return None
    a_ = a if isinstance(a, datetime) else datetime.combine(a, datetime.min.time())
    b_ = b if isinstance(b, datetime) else datetime.combine(b, datetime.min.time())
    if a_.tzinfo and not b_.tzinfo:
        b_ = b_.replace(tzinfo=timezone.utc)
    if b_.tzinfo and not a_.tzinfo:
        a_ = a_.replace(tzinfo=timezone.utc)
    return (b_ - a_).days


def hedef_degisimleri(tenant_id: int, gun: int = 365) -> list[dict]:
    """Ham hedef değişiklik kayıtları (tenant kapsamında).

    Her kayıt: hangi KPI, kim, ne zaman, ne'den ne'ye, yön, dönem kapanışına
    kaç gün kala.
    """
    esik = datetime.now(timezone.utc) - timedelta(days=gun)

    satirlar = (
        db.session.query(KpiDataAudit, KpiData, ProcessKpi, Process, User)
        .join(KpiData, KpiDataAudit.kpi_data_id == KpiData.id)
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .outerjoin(User, KpiDataAudit.user_id == User.id)
        .filter(
            Process.tenant_id == tenant_id,
            KpiDataAudit.new_target.isnot(None),   # yalnız hedefi değişenler
            KpiDataAudit.created_at >= esik,
        )
        .order_by(KpiDataAudit.created_at.desc())
        .all()
    )

    sonuc = []
    for audit, veri, kpi, surec, kullanici in satirlar:
        yon, yuzde = _yon(audit.old_target, audit.new_target)
        # Dönem kapanışına kaç gün kala? (data_date = dönem sonu kabulü)
        kala = _gun_farki(audit.created_at, veri.data_date)
        sonuc.append({
            "audit_id": audit.id,
            "kpi_id": kpi.id,
            "kpi_adi": kpi.name,
            "surec_adi": surec.name,
            "yil": veri.year,
            "donem": f"{veri.period_type or ''} {veri.period_no or ''}".strip(),
            "eski_hedef": audit.old_target,
            "yeni_hedef": audit.new_target,
            "yon": yon,
            "sapma_yuzde": yuzde,
            "kim": (f"{kullanici.first_name or ''} {kullanici.last_name or ''}".strip()
                    or (kullanici.email if kullanici else None)) if kullanici else None,
            "ne_zaman": audit.created_at.isoformat() if audit.created_at else None,
            "kapanisa_kala_gun": kala,
            # "Geç" = dönem kapanışına GEC_DEGISIM_GUN'den az kala VE aşağı.
            # Gerçekleşme büyük ölçüde belliyken hedefi düşürmek, hedefi
            # sonuca uydurmak anlamına gelebilir.
            "gec_ve_asagi": bool(
                yon == "asagi" and kala is not None and 0 <= kala <= GEC_DEGISIM_GUN
            ),
        })
    return sonuc


def radar_ozeti(tenant_id: int, gun: int = 365) -> dict:
    """Yönetim için tek ekran özeti.

    Returns:
        {
          "pencere_gun": 365,
          "toplam_degisim": 12,
          "asagi": 8, "yukari": 3, "sabit": 1, "belirsiz": 0,
          "gec_ve_asagi": 4,                 # en kritik sinyal
          "ortalama_asagi_sapma": -18.4,     # % (yalnız aşağı olanlar)
          "cok_revize_edilen": [{kpi_adi, kez, ...}],
          "degisimler": [...],               # ham liste (detay tablosu için)
          "veri_notu": "...",                # sınır uyarısı
        }
    """
    degisimler = hedef_degisimleri(tenant_id, gun)

    sayac = {"asagi": 0, "yukari": 0, "sabit": 0, "belirsiz": 0}
    for d in degisimler:
        sayac[d["yon"]] = sayac.get(d["yon"], 0) + 1

    asagi_sapmalar = [
        d["sapma_yuzde"] for d in degisimler
        if d["yon"] == "asagi" and d["sapma_yuzde"] is not None
    ]
    ort_asagi = round(sum(asagi_sapmalar) / len(asagi_sapmalar), 2) if asagi_sapmalar else None

    # Aynı KPI'ın hedefi kaç kez revize edilmiş? Tekrar, tek seferlik
    # düzeltmeden farklı bir sinyal.
    kez = {}
    for d in degisimler:
        k = kez.setdefault(d["kpi_id"], {"kpi_adi": d["kpi_adi"], "surec_adi": d["surec_adi"],
                                         "kez": 0, "asagi": 0})
        k["kez"] += 1
        if d["yon"] == "asagi":
            k["asagi"] += 1
    cok_revize = sorted(
        [v for v in kez.values() if v["kez"] >= 2],
        key=lambda x: (-x["asagi"], -x["kez"]),
    )[:10]

    return {
        "pencere_gun": gun,
        "toplam_degisim": len(degisimler),
        **sayac,
        "gec_ve_asagi": sum(1 for d in degisimler if d["gec_ve_asagi"]),
        "ortalama_asagi_sapma": ort_asagi,
        "cok_revize_edilen": cok_revize,
        "degisimler": degisimler,
        "veri_notu": (
            "Hedef değişiklik izi 2026-07-15'te (TASK-261) açıldı; öncesindeki "
            "revizyonlar kayıtlı değil. Radar bir OLGU gösterir, niyet okumaz — "
            "hedef düşürmenin meşru sebepleri olabilir."
        ),
    }
