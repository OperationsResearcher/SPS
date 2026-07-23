---
name: project_teknik_borc_haritasi
description: "Teknik borç gerçeği (DB-doğrulanmış): çift-model korkulandan hafif, veri zaten modern tek-kaynakta"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

**2026-06-16 sistematik tarama + DB doğrulaması.** Tam envanter: `docs/paketler/TEKNIK-BORC-ENVANTERI.md`.

**🔑 Ana bulgu:** Korkulan "çift-model borcu" (legacy `models/` vs modern `app/models/`) **gerçekte hafifti.**
Asıl tehlike (iki canlı tabloya çatallı yazma) **neredeyse hiç yok.** DB tablo+satır kanıtı:
- Kimlik (Vizyon/Değer/Etik): legacy `kurum`/`deger`/`etik_kural`/`kalite_politikasi` = **0 satır**. Modern `tenants` dolu.
- Strateji: legacy `ana_strateji`/`alt_strateji`/`strategy_process_matrix` = **0/0/0**. Modern `strategies`/`sub_strategies`/`process_sub_strategy_links` = **90/229/250** (canlı).
- Süreç/PG: legacy `surec`/`surec_performans_gostergesi` **tabloları YOK**. Sadece modern `processes`(167)/`process_kpis`(731). `legacy_bridge` = saf alias (Türkçe isim → modern tablo).
- Tenant izolasyonu: **sağlam** (`_tenant_guard`, `accessible_processes_filter` tutarlı; sistemik sızıntı yok).

**Sonuç:** Kalan legacy borç = ölü kod + isim/import temizliği (veri taşıması/migration DEĞİL). Riski düşük.

**DİKKAT — ajan raporları bu konuda birkaç kez YANILDI** (ör. "strategies tablosu hiç yok" → aslında 90 satır dolu).
**Her iddia DB'de / runtime'da teyit edildi.** Gelecekte legacy/borç işinde: ajan çıktısına güvenme, DB sorgusu +
"geçici taşı/test/geri getir" + test_client ile kanıtla.

**Bugün strangler ile silinen (hepsi merge+push):** HGS tümü; Dalga 1 (16 ölü kurum kimlik/strateji yazma route);
1.5 (5 ölü backup template); 1.6 (4 ölü admin upload route); Dalga 4 (`models/process.py` dead). Dalga 3:
`strategy_detail_service` **bug fix** (legacy boş tablo okuyordu → modern `ProcessSubStrategyLink`; skorlar hep 0'dı).

**Bilinçli bırakılanlar:** `kurum_panel.py` `admin_panel()` (url_for bağımlılığı → activity_stream.html); `portfolio_service`
ölü fallback (davranış doğru); BSC `perspective` (canlı mı belirsiz); Türkçe→İng alias çevirisi (kozmetik).
**Dalga 2** (Değerler çok-satırlı) = borç değil **L1 inşası** (DB şema değişimi); L1 inşa aşamasına ertelendi.
[[project_strangler_karari]] [[project_paketleme_segmentasyon]]
