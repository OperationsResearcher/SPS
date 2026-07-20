# Kokpitim Projesi - Detaylı Sistem Tanıtım ve Hiyerarşi Kılavuzu

Bu doküman, Kokpitim SaaS platformunun mimari katmanlarını, paketlerini, modüllerini, bileşenlerini (components) ve en alt seviyedeki işlevsel kartlarını (cards) detaylı bir şekilde tanıtır.

## MİMARİ YAPI (SaaS Hiyerarşisi)
Platform, esnek ve modüler bir SaaS mimarisine dayanmaktadır. Hiyerarşik yapı şu şekildedir:
```
Abonelik Paketi (Subscription Package)
  └── Sistem Modülü (System Module)
        └── Sistem Bileşeni (System Component / Component Slug)
              └── Sistem Kartı (System Card)
                    └── Veri Kaynağı (Card Data Source)
```

### Hiyerarşi Katmanlarının Tanımları:
1. **Abonelik Paketi (Subscription Package):** Kurumların (Tenant) satın alabileceği lisans seviyeleridir (Örn: Standart, Profesyonel, Enterprise, Master). Bir paket birden fazla modül barındırır.
2. **Sistem Modülü (System Module):** Mantıksal ve fonksiyonel olarak gruplanmış ana uygulama alanlarıdır (Örn: Stratejik Planlama Modülü, Süreç Yönetimi Modülü, K-Radar Modülü).
3. **Sistem Bileşeni (System Component):** Modüllerin altındaki bağımsız işlevler veya alt modüllerdir. Yetkilendirme ve lisanslama kontrolleri bileşen seviyesindeki benzersiz anahtarlar (slug / code) üzerinden yapılır (Örn: `k_radar_ks_bsc`, `k_radar_ks_okr`).
4. **Sistem Kartı (System Card):** Kullanıcı ekranlarındaki her bir görsel bileşen, grafik, tablo veya bilgi kartıdır. Bir bileşene bağlıdır ve modüler ekran yönetimini sağlar.
5. **Veri Kaynağı (Card Data Source):** Kartların içindeki her bir veri alanıdır. Çapraz-paket kısıtlamaları için veri bazında yetkilendirme sağlar. Kurumun paketinde ilgili veri kaynağının bileşeni yoksa o veri alanı karttan otomatik olarak gizlenir.

---

## 1. ABONELİK PAKETLERİ (SUBSCRIPTION PACKAGES)
Sistemde tanımlı abonelik paketleri ve içerdikleri modüller aşağıda listelenmiştir:

### 📦 Master Package (`master_package`)
**Açıklama:** Contains all modules  
**Durum:** Aktif  
**İçerdiği Modüller:**
- **Stratejik Planlama Modulü** (`stratejik_planlama_modulu`)
- **İleri Stratejik Planlama Modulü** (`ileri_stratejik_planlama_modulu`)
- **Süreç Yönetimi Modülü** (`surec_yonetimi_modulu`)
- **İleri Süreç Yönetimi Modülü** (`ileri_surec_yonetimi_modulu`)
- **Proje Yönetimi Modülü** (`proje_yonetimi_modulu`)
- **İleri Proje Yönetimi Modülü** (`ileri_proje_yonetimi_modulu`)
- **Kurum Paneli Modülü** (`kurum_paneli_modulu`)
- **Bireysel Performans Modülü** (`bireysel_performans_modulu`)
- **Performans Analitiği Modülü** (`performans_analitigi_modulu`)
- **K-Radar Modülü** (`k_radar_modulu`)
- **K-Rapor Modülü** (`k_rapor_modulu`)
- **Raporlar Modülü** (`raporlar_modulu`)

### 📦 Başlangıç (`baslangic`)
**Açıklama:** L1 — Başlat ve gör: kurum kimliği + stratejik planlama.  
**Durum:** Aktif  
**İçerdiği Modüller:**
- **Stratejik Planlama Modulü** (`stratejik_planlama_modulu`)
- **Kurum Paneli Modülü** (`kurum_paneli_modulu`)

### 📦 Yönetim (`yonetim`)
**Açıklama:** L2 — Yönet ve ölç: süreç/PG/PGV, bireysel, proje, analiz, rapor.  
**Durum:** Aktif  
**İçerdiği Modüller:**
- **Stratejik Planlama Modulü** (`stratejik_planlama_modulu`)
- **Süreç Yönetimi Modülü** (`surec_yonetimi_modulu`)
- **Proje Yönetimi Modülü** (`proje_yonetimi_modulu`)
- **Kurum Paneli Modülü** (`kurum_paneli_modulu`)
- **Bireysel Performans Modülü** (`bireysel_performans_modulu`)
- **Performans Analitiği Modülü** (`performans_analitigi_modulu`)
- **K-Rapor Modülü** (`k_rapor_modulu`)

### 📦 Strateji (`strateji`)
**Açıklama:** L3 — Optimize et: tüm Yönetim + K-Radar (ileri analiz/AI).  
**Durum:** Aktif  
**İçerdiği Modüller:**
- **Stratejik Planlama Modulü** (`stratejik_planlama_modulu`)
- **İleri Stratejik Planlama Modulü** (`ileri_stratejik_planlama_modulu`)
- **Süreç Yönetimi Modülü** (`surec_yonetimi_modulu`)
- **İleri Süreç Yönetimi Modülü** (`ileri_surec_yonetimi_modulu`)
- **Proje Yönetimi Modülü** (`proje_yonetimi_modulu`)
- **İleri Proje Yönetimi Modülü** (`ileri_proje_yonetimi_modulu`)
- **Kurum Paneli Modülü** (`kurum_paneli_modulu`)
- **Bireysel Performans Modülü** (`bireysel_performans_modulu`)
- **Performans Analitiği Modülü** (`performans_analitigi_modulu`)
- **K-Radar Modülü** (`k_radar_modulu`)
- **K-Rapor Modülü** (`k_rapor_modulu`)
- **Raporlar Modülü** (`raporlar_modulu`)


---

## 2. SİSTEM MODÜLLERİ VE BİLEŞENLERİ (MODULES & COMPONENTS)
Kokpitim sisteminde yer alan aktif modüller ve bu modüllere atanmış alt bileşenlerin detayları:

### 🧩 Stratejik Planlama Modulü (`stratejik_planlama_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 33  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **Yapay Zeka Ayarları** | `ai_ayarlari` | - | Aktif |
| **Mavi Okyanus Analizi** | `mavi_okyanus_analizi` | - | Aktif |
| **Dengeli Karne (BSC)** | `dengeli_karne_bsc` | - | Aktif |
| **Çeyreklik Değerlendirme** | `ceyreklik_degerlendirme` | - | Aktif |
| **Stratejik Plan Dönemleri** | `sp_plan_donemleri` | - | Aktif |
| **SP Yönetici Paneli** | `sp_yonetici_paneli` | - | Aktif |
| **Stratejik Girişimler** | `stratejik_girisimler` | - | Aktif |
| **Dinamik Stratejik Planlama** | `dinamik_stratejik_planlama` | - | Aktif |
| **Dönem Mühürleme** | `donem_muhurleme` | - | Aktif |
| **Revizyon başlatma** | `revizyon_baslatma` | - | Aktif |
| **Stratejik Asistan Kartı** | `stratejik_asistan_karti` | - | Aktif |
| **Stratejik İlerleme kartı** | `stratejik_ilerleme_karti` | - | Aktif |
| **Karar Destek Özeti kartı** | `karar_destek_ozeti_karti` | - | Aktif |
| **Öncelik Analizi kartı** | `oncelik_analizi_karti` | - | Aktif |
| **Kaynak Dağılımı kartı** | `kaynak_dagilimi_karti` | - | Aktif |
| **İnteraktif Rehber Sistemi** | `interaktif_rehber_sistemi` | - | Aktif |
| **Hızlı Erişim Menüsü Kartı** | `hizli_erisim_menusu_karti` | - | Aktif |
| **Hızlı İstatistikler Kartı** | `hizli_istatistikler_karti` | - | Aktif |
| **Son Aktiviteler Kartı** | `son_aktiviteler_karti` | - | Aktif |
| **Kıyaslama** | `kiyaslama` | - | Aktif |
| **Yapay Zeka Kullanım Raporu** | `ai_kullanim_raporu` | - | Aktif |
| **OKR Yönetimi** | `okr_yonetimi` | - | Aktif |
| **Yeniden Planlama Tetikleyicileri** | `yeniden_planlama_tetikleyicileri` | - | Aktif |
| **Senaryo Planlama** | `senaryo_planlama` | - | Aktif |
| **Yeni Plan Yılı Sihirbazı** | `yeni_plan_yili_sihirbazi` | - | Aktif |
| **Strateji-Proje Hizalama Matrisi** | `strateji_proje_hizalama_matrisi` | - | Aktif |
| **Strateji Haritası** | `strateji_haritasi` | - | Aktif |
| **Plan Şablonları** | `plan_sablonlari` | - | Aktif |
| **Savaş Odası TV Panosu** | `savas_odasi_tv_panosu` | - | Aktif |
| **Hoshin X-Matrix** | `hoshin_x_matrix` | - | Aktif |
| **K-Vektör Vizyon Skoru** | `k_vektor_vizyon_skoru` | - | Aktif |
| **Bireysel Hedef Hizalama** | `bireysel_hedef_hizalama` | - | Aktif |
| **Vizyon Kartı** | `vizyon_karti` | - | Aktif |


### 🧩 İleri Stratejik Planlama Modulü (`ileri_stratejik_planlama_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 8  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **SWOT Analizi** | `swot_analizi` | - | Aktif |
| **TOWS Analizi** | `tows_analizi` | - | Aktif |
| **PESTEL Analizi** | `pestel_analizi` | - | Aktif |
| **Porter 5 Kuvvet Analizi** | `porter_5_kuvvet_analizi` | - | Aktif |
| **Ansoff Analizi** | `ansoff_analizi` | - | Aktif |
| **BCG Matrisi Analizi** | `bcg_matrisi_analizi` | - | Aktif |
| **VRIO Analizi** | `vrio_analizi` | - | Aktif |
| **Değer Zinciri Analizi** | `deger_zinciri_analizi` | - | Aktif |


### 🧩 Süreç Yönetimi Modülü (`surec_yonetimi_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 9  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **Süreç Özet İstatistikleri** | `surec_ozet_istatistikleri` | - | Aktif |
| **Süreç Karnesi Genel Bilgiler** | `surec_karnesi_genel_bilgiler` | - | Aktif |
| **Performans Göstergesi** | `performans_gostergesi` | - | Aktif |
| **Performans Göstergesi Verisi** | `performans_gostergesi_verisi` | - | Aktif |
| **Süreç Performansı kartı** | `surec_performansi_karti` | - | Aktif |
| **Süreç Faaliyetleri** | `surec_faaliyetleri` | - | Aktif |
| **SÜREÇ FAALİYETLERİM kartı** | `surec_faaliyetlerim_karti` | - | Aktif |
| **Son Faaliyetler Kartı** | `son_faaliyetler_karti` | - | Aktif |
| **Başarı Puanı Yapılandırması** | `basari_puani_yapilandirmasi` | - | Aktif |


### 🧩 İleri Süreç Yönetimi Modülü (`ileri_surec_yonetimi_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 2  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **Süreç Verimlilik Analizi Kartı** | `surec_verimlilik_analizi_karti` | - | Aktif |
| **Performans Trend Analizi  Kartı** | `performans_trend_analizi_karti` | - | Aktif |


### 🧩 Proje Yönetimi Modülü (`proje_yonetimi_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 13  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **Proje Özet İstatistikleri** | `proje_ozet_istatistikleri` | - | Aktif |
| **Proje Operasyon Özeti** | `proje_operasyon_ozeti` | - | Aktif |
| **Proje Listesi Yönetimi** | `proje_listesi_yonetimi` | - | Aktif |
| **Proje Takvim Görünümü** | `proje_takvim_gorunumu` | - | Aktif |
| **Proje Detay Özeti** | `proje_detay_ozeti` | - | Aktif |
| **Proje Formu** | `proje_formu` | - | Aktif |
| **Proje Gantt Şeması** | `proje_gantt_semasi` | - | Aktif |
| **Proje Kanban Panosu** | `proje_kanban_panosu` | - | Aktif |
| **Proje Kapasite Yönetimi** | `proje_kapasite_yonetimi` | - | Aktif |
| **Proje Portföy Yönetimi** | `proje_portfoy_yonetimi` | - | Aktif |
| **Proje RAID Yönetimi** | `proje_raid_yonetimi` | - | Aktif |
| **Proje Stratejik İlişki** | `proje_stratejik_iliski` | - | Aktif |
| **Proje Görev Yönetimi** | `proje_gorev_yonetimi` | - | Aktif |


### 🧩 İleri Proje Yönetimi Modülü (`ileri_proje_yonetimi_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 0  

*Bu modüle bağlı bileşen bulunmamaktadır.*


### 🧩 Kurum Paneli Modülü (`kurum_paneli_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 5  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **Misyon Kartı** | `misyon_karti` | - | Aktif |
| **Amaç Kartı** | `amac_karti` | - | Aktif |
| **Değerler Kartı** | `degerler_karti` | - | Aktif |
| **Etik Kurallar Kartı** | `etik_kurallar_karti` | - | Aktif |
| **Kalite Politikaları Kartı** | `kalite_politikalari_karti` | - | Aktif |


### 🧩 Bireysel Performans Modülü (`bireysel_performans_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 5  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **Bireysel Karne AI Özeti** | `bireysel_karne_ai_ozet` | - | Aktif |
| **Bireysel Karne Özet Görselleri** | `bireysel_karne_ozet_gorseller` | - | Aktif |
| **Bireysel Karne İstatistikleri** | `bireysel_karne_istatistikleri` | - | Aktif |
| **Bireysel Karne Zaman Çizelgesi** | `bireysel_karne_zaman_cizelgesi` | - | Aktif |
| **Bireysel Karne Detay Tabloları** | `bireysel_karne_detay_tablolari` | - | Aktif |


### 🧩 Performans Analitiği Modülü (`performans_analitigi_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 44  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **AI Koç Raporu** | `rapor_ai_coach_grubu` | - | Aktif |
| **AI Danışman Raporu** | `rapor_ai_danisman_grubu` | - | Aktif |
| **AI Sunum Oluşturucu** | `rapor_ai_sunum_grubu` | - | Aktif |
| **Denetim Paketi Raporu** | `rapor_audit_paketi_grubu` | - | Aktif |
| **BI Bağlayıcı** | `rapor_bi_connector_grubu` | - | Aktif |
| **Bireysel Hizalama Raporu** | `rapor_bireysel_hizalama_grubu` | - | Aktif |
| **Toplu Bireysel Karne Üretimi** | `rapor_bireysel_karne_batch_grubu` | - | Aktif |
| **Karbon Trend Raporu** | `rapor_carbon_trend_grubu` | - | Aktif |
| **CFO Panosu** | `rapor_cfo_dashboard_grubu` | - | Aktif |
| **CHRO Panosu** | `rapor_chro_dashboard_grubu` | - | Aktif |
| **CMMI Isı Haritası** | `rapor_cmmi_heatmap_grubu` | - | Aktif |
| **COO Panosu** | `rapor_coo_dashboard_grubu` | - | Aktif |
| **Departman Performans Raporu** | `rapor_departman_performans_grubu` | - | Aktif |
| **Erken Uyarı Raporu** | `rapor_early_warning_grubu` | - | Aktif |
| **ESG Raporu** | `rapor_esg_rapor_grubu` | - | Aktif |
| **ESG Yönetim Sayfası** | `rapor_esg_yonetim_grubu` | - | Aktif |
| **Yıllar Arası Evrim Filmi** | `rapor_evrim_filmi_grubu` | - | Aktif |
| **Hedef Revizyon Raporu** | `rapor_hedef_revizyon_grubu` | - | Aktif |
| **Hizalama Sankey Diyagramı** | `rapor_hizalama_sankey_grubu` | - | Aktif |
| **2FA Güvenlik Raporu** | `rapor_iki_fa_grubu` | - | Aktif |
| **Girişim Balon Grafiği** | `rapor_initiative_bubble_grubu` | - | Aktif |
| **Girişim Yol Haritası** | `rapor_initiative_roadmap_grubu` | - | Aktif |
| **KV Çarpıklık Raporu** | `rapor_kv_carpiklik_grubu` | - | Aktif |
| **ML Anomali Tespiti** | `rapor_ml_anomaly_grubu` | - | Aktif |
| **Mobile Hub Raporu** | `rapor_mobile_grubu` | - | Aktif |
| **Muda (İsraf) Analizi** | `rapor_muda_analizi_grubu` | - | Aktif |
| **Doğal Dil Sorgulama** | `rapor_nlp_query_grubu` | - | Aktif |
| **OKR Kademelendirme Raporu** | `rapor_okr_cascade_grubu` | - | Aktif |
| **Onay Zinciri Raporu** | `rapor_onay_zinciri_grubu` | - | Aktif |
| **PG-Proje Etki Raporu** | `rapor_pg_proje_etki_grubu` | - | Aktif |
| **Çeyreklik Review Raporu** | `rapor_quarterly_review_grubu` | - | Aktif |
| **Risk Isı Haritası** | `rapor_risk_heatmap_grubu` | - | Aktif |
| **Sabah Özeti Raporu** | `rapor_sabah_ozeti_grubu` | - | Aktif |
| **Sektör Kıyaslama Raporu** | `rapor_sektor_benchmark_grubu` | - | Aktif |
| **Sektörel Plan Paketleri** | `rapor_sektorel_grubu` | - | Aktif |
| **Strateji Hikayesi Raporu** | `rapor_strateji_hikayesi_grubu` | - | Aktif |
| **Stratejik Yıllık Rapor** | `rapor_stratejik_yillik_grubu` | - | Aktif |
| **Stratejik Hiyerarşi Sunburst** | `rapor_sunburst_grubu` | - | Aktif |
| **Veri Kalitesi Raporu** | `rapor_veri_kalitesi_grubu` | - | Aktif |
| **VRIO Portföy Raporu** | `rapor_vrio_portfoy_grubu` | - | Aktif |
| **Yatırımcı Sunumu** | `rapor_yatirimci_sunum_grubu` | - | Aktif |
| **Yönetici Liderlik Raporu** | `rapor_yonetici_liderlik_grubu` | - | Aktif |
| **Operasyon İstatistikleri** | `rapor_operasyon_istatistik_grubu` | - | Aktif |
| **Sektörel Paket Detayı** | `rapor_sektorel_detay_grubu` | - | Aktif |


### 🧩 K-Radar Modülü (`k_radar_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 27  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **K-Radar Çapraz Risk Analizi** | `k_radar_cross_risk_analizi` | - | Aktif |
| **K-Radar A3 Raporları** | `k_radar_cross_a3` | - | Aktif |
| **K-Radar Çapraz Anket** | `k_radar_cross_anket` | - | Aktif |
| **K-Radar Paydaş Yönetimi** | `k_radar_cross_paydas` | - | Aktif |
| **K-Radar Rekabet Analizi** | `k_radar_cross_rekabet` | - | Aktif |
| **KP-Radar Skoru** | `k_radar_kp_skoru` | - | Aktif |
| **KP-Radar Kıyaslama** | `k_radar_kp_benchmark` | - | Aktif |
| **KP-Radar Darboğaz Analizi** | `k_radar_kp_darbogaz` | - | Aktif |
| **KP-Radar Kapasite Analizi** | `k_radar_kp_kapasite` | - | Aktif |
| **KP-Radar OEE Analizi** | `k_radar_kp_oee` | - | Aktif |
| **KP-Radar Süreç Olgunluğu** | `k_radar_kp_olgunluk` | - | Aktif |
| **KP-Radar Pareto Analizi** | `k_radar_kp_pareto` | - | Aktif |
| **KP-Radar SLA Analizi** | `k_radar_kp_sla` | - | Aktif |
| **KP-Radar Değer Akışı (VSM)** | `k_radar_kp_vsm` | - | Aktif |
| **KPR Proje Radarı** | `k_radar_kpr_proje_radari` | - | Aktif |
| **KPR Kritik Yol Analizi** | `k_radar_kpr_cpm` | - | Aktif |
| **KPR Kazanılmış Değer Analizi** | `k_radar_kpr_evm` | - | Aktif |
| **KPR Gantt Takibi** | `k_radar_kpr_gantt` | - | Aktif |
| **KPR Kaynak Kapasitesi** | `k_radar_kpr_kaynak_kapasite` | - | Aktif |
| **KPR Risk Yönetimi** | `k_radar_kpr_risk` | - | Aktif |
| **K-Radar Balanced Scorecard** | `k_radar_ks_bsc` | - | Aktif |
| **K-Radar EFQM Olgunluk Modeli** | `k_radar_ks_efqm` | - | Aktif |
| **K-Radar Hedef Gap Analizi** | `k_radar_ks_gap_analizi` | - | Aktif |
| **K-Radar Kurumsal Strateji Skoru** | `k_radar_ks_skoru` | - | Aktif |
| **K-Radar OKR Takibi** | `k_radar_ks_okr` | - | Aktif |
| **K-Radar Strateji-Süreç Kapsama** | `k_radar_ks_strateji_surec_kapsama` | - | Aktif |
| **K-Radar Risk Yönetimi** | `k_radar_risk_yonetimi` | - | Aktif |


### 🧩 K-Rapor Modülü (`k_rapor_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 21  

| Bileşen Adı | Benzersiz Kod (Slug) | Açıklama | Durum |
| :--- | :--- | :--- | :--- |
| **K-Rapor Aktivite Takvimi** | `k_rapor_aktivite_takvim` | - | Aktif |
| **K-Rapor Anomali Tespiti** | `k_rapor_anomali_tespiti` | - | Aktif |
| **K-Rapor Bildirim Analizi** | `k_rapor_bildirim_analiz` | - | Aktif |
| **K-Rapor Bireysel PG Analizi** | `k_rapor_bireysel_pg` | - | Aktif |
| **K-Rapor Denetim Analizi** | `k_rapor_denetim` | - | Aktif |
| **K-Rapor Kazanılmış Değer Analizi** | `k_rapor_evm` | - | Aktif |
| **K-Rapor Faaliyet Analizi** | `k_rapor_faaliyet` | - | Aktif |
| **K-Rapor K-Vektör Ağırlıkları** | `k_rapor_k_vektor` | - | Aktif |
| **K-Rapor Kurum Karşılaştırma** | `k_rapor_kurum_karsilastirma` | - | Aktif |
| **K-Rapor Kurumsal Özet** | `k_rapor_kurumsal_ozet` | - | Aktif |
| **K-Rapor Paydaş Analizi** | `k_rapor_paydas` | - | Aktif |
| **K-Rapor PG Dağılım Analizi** | `k_rapor_pg_dagilim` | - | Aktif |
| **K-Rapor Rekabet ve A3 Analizi** | `k_rapor_rekabet` | - | Aktif |
| **K-Rapor Risk ve Süreç Analizi** | `k_rapor_risk` | - | Aktif |
| **K-Rapor Sorumlu Analizi** | `k_rapor_sorumlu_analiz` | - | Aktif |
| **K-Rapor Strateji Kapsama Analizi** | `k_rapor_strateji_kapsama` | - | Aktif |
| **K-Rapor Süreç-PG Analizi** | `k_rapor_surec_pg` | - | Aktif |
| **K-Rapor SWOT/TOWS Trend Analizi** | `k_rapor_swot_trend` | - | Aktif |
| **K-Rapor Uyarı Paneli** | `k_rapor_uyari` | - | Aktif |
| **K-Rapor Strateji-Süreç Uyum Ağacı** | `k_rapor_uyum` | - | Aktif |
| **K-Rapor Veri Durumu** | `k_rapor_veri_durumu` | - | Aktif |


### 🧩 Raporlar Modülü (`raporlar_modulu`)
**Durum:** Aktif  
**Bileşen Sayısı:** 0  

*Bu modüle bağlı bileşen bulunmamaktadır.*



---

## 3. SİSTEM KARTLARI VE VERİ KAYNAKLARI (SYSTEM CARDS & DATA SOURCES)
Bileşenlerin altında çalışan ve UI ekranlarını oluşturan kartlar ile bu kartların beslendiği veri kaynakları:

### 🎴 Revizyon başlatma Bileşeni Kartları (`revizyon_baslatma`)
**Bileşen:** Revizyon başlatma | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_hata_kontrolu.izole_test_kurumu** | `admin_hata_kontrolu.izole_test_kurumu` | `ADH01` | *Veri kaynağı yok* | Aktif |
| **admin_hata_kontrolu.kesif_taranacak_sayfalar** | `admin_hata_kontrolu.kesif_taranacak_sayfalar` | `ADH02` | *Veri kaynağı yok* | Aktif |
| **admin_hata_kontrolu.otomatik_tarayici_testi** | `admin_hata_kontrolu.otomatik_tarayici_testi` | `ADH03` | *Veri kaynağı yok* | Aktif |
| **admin_hata_kontrolu.tarama_gecmisi** | `admin_hata_kontrolu.tarama_gecmisi` | `ADH04` | *Veri kaynağı yok* | Aktif |
| **admin_hata_kontrolu.senaryo_gecmisi** | `admin_hata_kontrolu.senaryo_gecmisi` | `ADH06` | *Veri kaynağı yok* | Aktif |


### 🎴 Performans Göstergesi Verisi Bileşeni Kartları (`performans_gostergesi_verisi`)
**Bileşen:** Performans Göstergesi Verisi | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **process_karne.hedefte** | `process_karne.hedefte` | `PK05` | *Veri kaynağı yok* | Aktif |
| **process_karne.risk_altinda** | `process_karne.risk_altinda` | `PK06` | *Veri kaynağı yok* | Aktif |
| **process_karne.hedef_disi** | `process_karne.hedef_disi` | `PK07` | *Veri kaynağı yok* | Aktif |


### 🎴 Performans Göstergesi Bileşeni Kartları (`performans_gostergesi`)
**Bileşen:** Performans Göstergesi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **process_karne.surec_karnesi** | `process_karne.surec_karnesi` | `PK04` | *Veri kaynağı yok* | Aktif |


### 🎴 Performans Trend Analizi  Kartı Bileşeni Kartları (`performans_trend_analizi_karti`)
**Bileşen:** Performans Trend Analizi  Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **process_karne.kpi_performans_trend_analizi** | `process_karne.kpi_performans_trend_analizi` | `PK03` | *Veri kaynağı yok* | Aktif |


### 🎴 Süreç Faaliyetleri Bileşeni Kartları (`surec_faaliyetleri`)
**Bileşen:** Süreç Faaliyetleri | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp.surec_iyilestirme_faaliyetleri** | `sp.surec_iyilestirme_faaliyetleri` | `SP12` | *Veri kaynağı yok* | Aktif |
| **process_karne.faaliyet_toplam** | `process_karne.faaliyet_toplam` | `PK08` | *Veri kaynağı yok* | Aktif |
| **process_karne.faaliyet_tamamlanan** | `process_karne.faaliyet_tamamlanan` | `PK09` | *Veri kaynağı yok* | Aktif |
| **process_karne.surec_faaliyetleri** | `process_karne.surec_faaliyetleri` | `PK10` | *Veri kaynağı yok* | Aktif |
| **process_karne.faaliyet_planlananlar** | `process_karne.faaliyet_planlananlar` | `PK11` | *Veri kaynağı yok* | Aktif |
| **process_karne.faaliyet_devam_edenler** | `process_karne.faaliyet_devam_edenler` | `PK12` | *Veri kaynağı yok* | Aktif |
| **process_karne.faaliyet_tamamlanan_iptal** | `process_karne.faaliyet_tamamlanan_iptal` | `PK13` | *Veri kaynağı yok* | Aktif |


### 🎴 Misyon Kartı Bileşeni Kartları (`misyon_karti`)
**Bileşen:** Misyon Kartı | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp.kimlik** | `sp.kimlik` | `SP06` | *Veri kaynağı yok* | Aktif |
| **sp.misyon** | `sp.misyon` | `SP07` | *Veri kaynağı yok* | Aktif |
| **sp_misyon.misyon** | `sp_misyon.misyon` | `SPMS01` | *Veri kaynağı yok* | Aktif |


### 🎴 Değerler Kartı Bileşeni Kartları (`degerler_karti`)
**Bileşen:** Değerler Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp.degerler_ve_etik_kurallar** | `sp.degerler_ve_etik_kurallar` | `SP09` | *Veri kaynağı yok* | Aktif |


### 🎴 Süreç Performansı kartı Bileşeni Kartları (`surec_performansi_karti`)
**Bileşen:** Süreç Performansı kartı | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **Kurum Özet Kartları** | `kurum_ozet_kartlar` | `-` | `user_count` (Aktif Kullanıcı), `strategy_count` (Ana Strateji), `process_count` (Aktif Süreç) | Aktif |
| **process.ortalama_skor** | `process.ortalama_skor` | `PR03` | *Veri kaynağı yok* | Aktif |
| **process.surecler** | `process.surecler` | `PR07` | *Veri kaynağı yok* | Aktif |


### 🎴 Stratejik İlerleme kartı Bileşeni Kartları (`stratejik_ilerleme_karti`)
**Bileşen:** Stratejik İlerleme kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.stratejik_hedefler** | `masaustu.stratejik_hedefler` | `MA13` | *Veri kaynağı yok* | Aktif |


### 🎴 SWOT Analizi Bileşeni Kartları (`swot_analizi`)
**Bileşen:** SWOT Analizi | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.swot_analizi** | `k_radar_ks.swot_analizi` | `KD05` | *Veri kaynağı yok* | Aktif |
| **k_rapor_stratejik_analiz.swot_analizi** | `k_rapor_stratejik_analiz.swot_analizi` | `KR46` | *Veri kaynağı yok* | Aktif |
| **sp_swot.sayfa** | `sp_swot.sayfa` | `SPSW01` | *Veri kaynağı yok* | Aktif |


### 🎴 PESTEL Analizi Bileşeni Kartları (`pestel_analizi`)
**Bileşen:** PESTEL Analizi | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.pestle_analizi** | `k_radar_ks.pestle_analizi` | `KD07` | *Veri kaynağı yok* | Aktif |
| **k_rapor_stratejik_analiz.pestel_analizi** | `k_rapor_stratejik_analiz.pestel_analizi` | `KR44` | *Veri kaynağı yok* | Aktif |
| **sp_pestel.sayfa** | `sp_pestel.sayfa` | `SPPE01` | *Veri kaynağı yok* | Aktif |


### 🎴 TOWS Analizi Bileşeni Kartları (`tows_analizi`)
**Bileşen:** TOWS Analizi | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.tows_matrisi** | `k_radar_ks.tows_matrisi` | `KD06` | *Veri kaynağı yok* | Aktif |
| **k_rapor_stratejik_analiz.tows_matrisi** | `k_rapor_stratejik_analiz.tows_matrisi` | `KR47` | *Veri kaynağı yok* | Aktif |
| **sp_tows.so** | `sp_tows.so` | `SPTW01` | *Veri kaynağı yok* | Aktif |
| **sp_tows.st** | `sp_tows.st` | `SPTW02` | *Veri kaynağı yok* | Aktif |
| **sp_tows.wo** | `sp_tows.wo` | `SPTW03` | *Veri kaynağı yok* | Aktif |
| **sp_tows.wt** | `sp_tows.wt` | `SPTW04` | *Veri kaynağı yok* | Aktif |


### 🎴 Porter 5 Kuvvet Analizi Bileşeni Kartları (`porter_5_kuvvet_analizi`)
**Bileşen:** Porter 5 Kuvvet Analizi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_stratejik_analiz.porter_5_kuvvet** | `k_rapor_stratejik_analiz.porter_5_kuvvet` | `KR45` | *Veri kaynağı yok* | Aktif |
| **sp_porter.sayfa** | `sp_porter.sayfa` | `SPPO01` | *Veri kaynağı yok* | Aktif |


### 🎴 VRIO Analizi Bileşeni Kartları (`vrio_analizi`)
**Bileşen:** VRIO Analizi | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_vrio.aciklama_degerli** | `sp_vrio.aciklama_degerli` | `SPVR01` | *Veri kaynağı yok* | Aktif |
| **sp_vrio.aciklama_nadir** | `sp_vrio.aciklama_nadir` | `SPVR02` | *Veri kaynağı yok* | Aktif |
| **sp_vrio.aciklama_taklit_edilemez** | `sp_vrio.aciklama_taklit_edilemez` | `SPVR03` | *Veri kaynağı yok* | Aktif |
| **sp_vrio.aciklama_organize** | `sp_vrio.aciklama_organize` | `SPVR04` | *Veri kaynağı yok* | Aktif |
| **sp_vrio.kaynak_tablosu** | `sp_vrio.kaynak_tablosu` | `SPVR05` | *Veri kaynağı yok* | Aktif |
| **sp_vrio.sonuc_siniflandirmasi** | `sp_vrio.sonuc_siniflandirmasi` | `SPVR06` | *Veri kaynağı yok* | Aktif |


### 🎴 Değer Zinciri Analizi Bileşeni Kartları (`deger_zinciri_analizi`)
**Bileşen:** Değer Zinciri Analizi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_deger_zinciri.ozet** | `k_radar_kp_deger_zinciri.ozet` | `KDV01` | *Veri kaynağı yok* | Aktif |
| **k_radar_kp_deger_zinciri.faaliyetler** | `k_radar_kp_deger_zinciri.faaliyetler` | `KDV02` | *Veri kaynağı yok* | Aktif |


### 🎴 Hızlı Erişim Menüsü Kartı Bileşeni Kartları (`hizli_erisim_menusu_karti`)
**Bileşen:** Hızlı Erişim Menüsü Kartı | **Kart Sayısı:** 18

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.hizli_islemler** | `masaustu.hizli_islemler` | `MA06` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp** | `sp_menu.sp` | `SPMN01` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-exec-dashboard** | `sp_menu.sp-exec-dashboard` | `SPMN02` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-ceyreklik-review** | `sp_menu.sp-ceyreklik-review` | `SPMN03` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-initiatives** | `sp_menu.sp-initiatives` | `SPMN04` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-scenarios** | `sp_menu.sp-scenarios` | `SPMN05` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-replan-triggers** | `sp_menu.sp-replan-triggers` | `SPMN06` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-xmatrix** | `sp_menu.sp-xmatrix` | `SPMN07` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-blue-ocean** | `sp_menu.sp-blue-ocean` | `SPMN08` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-vrio** | `sp_menu.sp-vrio` | `SPMN09` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-swot** | `sp_menu.sp-swot` | `SPMN10` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-tows** | `sp_menu.sp-tows` | `SPMN11` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-pestel** | `sp_menu.sp-pestel` | `SPMN12` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-porter** | `sp_menu.sp-porter` | `SPMN13` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-bsc** | `sp_menu.sp-bsc` | `SPMN14` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-digest-weekly.pdf** | `sp_menu.sp-digest-weekly.pdf` | `SPMN15` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-settings-ai** | `sp_menu.sp-settings-ai` | `SPMN16` | *Veri kaynağı yok* | Aktif |
| **sp_menu.sp-templates** | `sp_menu.sp-templates` | `SPMN17` | *Veri kaynağı yok* | Aktif |


### 🎴 Stratejik Asistan Kartı Bileşeni Kartları (`stratejik_asistan_karti`)
**Bileşen:** Stratejik Asistan Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **process_karne.ai_yonetici_ozeti** | `process_karne.ai_yonetici_ozeti` | `PK01` | *Veri kaynağı yok* | Aktif |


### 🎴 Dinamik Stratejik Planlama Bileşeni Kartları (`dinamik_stratejik_planlama`)
**Bileşen:** Dinamik Stratejik Planlama | **Kart Sayısı:** 13

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp.ana_strateji** | `sp.ana_strateji` | `SP01` | *Veri kaynağı yok* | Aktif |
| **sp.akis_olgunlugu** | `sp.akis_olgunlugu` | `SP02` | *Veri kaynağı yok* | Aktif |
| **sp.plan_donemi** | `sp.plan_donemi` | `SP04` | *Veri kaynağı yok* | Aktif |
| **sp.etiketsiz_strateji** | `sp.etiketsiz_strateji` | `SP05` | *Veri kaynağı yok* | Aktif |
| **sp.strateji_listesi_ana_stratejiler_alt_stratejiler** | `sp.strateji_listesi_ana_stratejiler_alt_stratejiler` | `SP11` | *Veri kaynağı yok* | Aktif |
| **kurum_ayarlar.yillik_plan_donemleri** | `kurum_ayarlar.yillik_plan_donemleri` | `KUA04` | *Veri kaynağı yok* | Aktif |
| **sp_dynamic_flow.renk_lejandi** | `sp_dynamic_flow.renk_lejandi` | `SPDF01` | *Veri kaynağı yok* | Aktif |
| **sp_dynamic_flow.strateji_grafigi** | `sp_dynamic_flow.strateji_grafigi` | `SPDF02` | *Veri kaynağı yok* | Aktif |
| **sp_flow.ana_strateji_sayisi** | `sp_flow.ana_strateji_sayisi` | `SPFL01` | *Veri kaynağı yok* | Aktif |
| **sp_flow.alt_strateji_sayisi** | `sp_flow.alt_strateji_sayisi` | `SPFL02` | *Veri kaynağı yok* | Aktif |
| **sp_flow.surec_sayisi** | `sp_flow.surec_sayisi` | `SPFL03` | *Veri kaynağı yok* | Aktif |
| **sp_flow.vizyon** | `sp_flow.vizyon` | `SPFL04` | *Veri kaynağı yok* | Aktif |
| **sp_flow.interaktif_grafik** | `sp_flow.interaktif_grafik` | `SPFL05` | *Veri kaynağı yok* | Aktif |


### 🎴 Admin Hata Kontrolü Aracı Bileşeni Kartları (`admin_arac_hata_kontrolu`)
**Bileşen:** Admin Hata Kontrolü Aracı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_araclar.hata_kontrolu** | `admin_araclar.hata_kontrolu` | `ADA01` | *Veri kaynağı yok* | Aktif |


### 🎴 Admin İstatistikler Aracı Bileşeni Kartları (`admin_arac_istatistikler`)
**Bileşen:** Admin İstatistikler Aracı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_araclar.istatistikler** | `admin_araclar.istatistikler` | `ADA02` | *Veri kaynağı yok* | Aktif |


### 🎴 Admin Loglar Aracı Bileşeni Kartları (`admin_arac_loglar`)
**Bileşen:** Admin Loglar Aracı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_araclar.loglar** | `admin_araclar.loglar` | `ADA03` | *Veri kaynağı yok* | Aktif |


### 🎴 Admin Yedekleme Aracı Bileşeni Kartları (`admin_arac_yedekleme`)
**Bileşen:** Admin Yedekleme Aracı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_araclar.yedekleme** | `admin_araclar.yedekleme` | `ADA04` | *Veri kaynağı yok* | Aktif |


### 🎴 Admin Hata Kontrolü Paneli Bileşeni Kartları (`admin_hata_kontrolu_paneli`)
**Bileşen:** Admin Hata Kontrolü Paneli | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_hata_kontrolu.aktif_crud_senaryolari** | `admin_hata_kontrolu.aktif_crud_senaryolari` | `ADH05` | *Veri kaynağı yok* | Aktif |


### 🎴 Kart Hiyerarşisi Görünümü Bileşeni Kartları (`admin_kart_hiyerarsisi`)
**Bileşen:** Kart Hiyerarşisi Görünümü | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_hierarchy.sayfa** | `admin_hierarchy.sayfa` | `ADY01` | *Veri kaynağı yok* | Aktif |


### 🎴 Holding Dashboard Bileşeni Kartları (`holding_dashboard`)
**Bileşen:** Holding Dashboard | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_holding_dashboard.ozet_skor** | `admin_holding_dashboard.ozet_skor` | `HLD01` | *Veri kaynağı yok* | Aktif |
| **admin_holding_dashboard.kritik_risk** | `admin_holding_dashboard.kritik_risk` | `HLD02` | *Veri kaynağı yok* | Aktif |
| **admin_holding_dashboard.yuksek_anomali** | `admin_holding_dashboard.yuksek_anomali` | `HLD03` | *Veri kaynağı yok* | Aktif |
| **admin_holding_dashboard.gecikmis_faaliyet** | `admin_holding_dashboard.gecikmis_faaliyet` | `HLD04` | *Veri kaynağı yok* | Aktif |
| **admin_holding_dashboard.karsilastirma_grafik** | `admin_holding_dashboard.karsilastirma_grafik` | `HLD05` | *Veri kaynağı yok* | Aktif |


### 🎴 Holding Alt Kurum Detayı Bileşeni Kartları (`holding_drilldown`)
**Bileşen:** Holding Alt Kurum Detayı | **Kart Sayısı:** 9

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_holding_drilldown.saglik_skoru** | `admin_holding_drilldown.saglik_skoru` | `HLT01` | *Veri kaynağı yok* | Aktif |
| **admin_holding_drilldown.kpi_hedef_ustu** | `admin_holding_drilldown.kpi_hedef_ustu` | `HLT02` | *Veri kaynağı yok* | Aktif |
| **admin_holding_drilldown.girisim_ortalamasi** | `admin_holding_drilldown.girisim_ortalamasi` | `HLT03` | *Veri kaynağı yok* | Aktif |
| **admin_holding_drilldown.gecikmis_faaliyet** | `admin_holding_drilldown.gecikmis_faaliyet` | `HLT04` | *Veri kaynağı yok* | Aktif |
| **admin_holding_drilldown.kritik_risk** | `admin_holding_drilldown.kritik_risk` | `HLT05` | *Veri kaynağı yok* | Aktif |
| **admin_holding_drilldown.yuksek_anomali** | `admin_holding_drilldown.yuksek_anomali` | `HLT06` | *Veri kaynağı yok* | Aktif |
| **admin_holding_drilldown.kullanici_senaryo** | `admin_holding_drilldown.kullanici_senaryo` | `HLT07` | *Veri kaynağı yok* | Aktif |
| **admin_holding_drilldown.girisimler** | `admin_holding_drilldown.girisimler` | `HLT08` | *Veri kaynağı yok* | Aktif |
| **admin_holding_drilldown.risk_listesi** | `admin_holding_drilldown.risk_listesi` | `HLT09` | *Veri kaynağı yok* | Aktif |


### 🎴 Sistem İstatistikleri Bileşeni Kartları (`admin_sistem_istatistikleri`)
**Bileşen:** Sistem İstatistikleri | **Kart Sayısı:** 10

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_istatistikler.kurum_dagilim_tablosu** | `admin_istatistikler.kurum_dagilim_tablosu` | `ADI01` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_kurum** | `admin_istatistikler.ozet_kurum` | `ADI01X2` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_kullanici** | `admin_istatistikler.ozet_kullanici` | `ADI02` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_ana_strateji** | `admin_istatistikler.ozet_ana_strateji` | `ADI03` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_alt_strateji** | `admin_istatistikler.ozet_alt_strateji` | `ADI04` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_surec** | `admin_istatistikler.ozet_surec` | `ADI05` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_pg** | `admin_istatistikler.ozet_pg` | `ADI06` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_pg_verisi** | `admin_istatistikler.ozet_pg_verisi` | `ADI07` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_proje** | `admin_istatistikler.ozet_proje` | `ADI08` | *Veri kaynağı yok* | Aktif |
| **admin_istatistikler.ozet_proje_task** | `admin_istatistikler.ozet_proje_task` | `ADI09` | *Veri kaynağı yok* | Aktif |


### 🎴 Kılavuz ve Video Oluşturucu Bileşeni Kartları (`admin_kilavuz_olusturucu`)
**Bileşen:** Kılavuz ve Video Oluşturucu | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_kilavuz_olusturucu.kontrol_paneli** | `admin_kilavuz_olusturucu.kontrol_paneli` | `ADK01` | *Veri kaynağı yok* | Aktif |
| **admin_kilavuz_olusturucu.calisma_loglari** | `admin_kilavuz_olusturucu.calisma_loglari` | `ADK02` | *Veri kaynağı yok* | Aktif |
| **admin_kilavuz_olusturucu.video_galerisi** | `admin_kilavuz_olusturucu.video_galerisi` | `ADK03` | *Veri kaynağı yok* | Aktif |
| **admin_kilavuz_olusturucu.yenitomofil_durumu** | `admin_kilavuz_olusturucu.yenitomofil_durumu` | `ADK04` | *Veri kaynağı yok* | Aktif |
| **admin_kilavuz_olusturucu.kilavuz_pdf_indirme** | `admin_kilavuz_olusturucu.kilavuz_pdf_indirme` | `ADK05` | *Veri kaynağı yok* | Aktif |


### 🎴 Giriş ve Aktivite Logları Bileşeni Kartları (`admin_giris_loglari`)
**Bileşen:** Giriş ve Aktivite Logları | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_loglar.toplam_giris** | `admin_loglar.toplam_giris` | `ADL01` | *Veri kaynağı yok* | Aktif |
| **admin_loglar.son_giris** | `admin_loglar.son_giris` | `ADL02` | *Veri kaynağı yok* | Aktif |
| **admin_loglar.son_veri_hareketi** | `admin_loglar.son_veri_hareketi` | `ADL03` | *Veri kaynağı yok* | Aktif |
| **admin_loglar.hic_giris_yapmamis** | `admin_loglar.hic_giris_yapmamis` | `ADL04` | *Veri kaynağı yok* | Aktif |
| **admin_loglar.kurum_bazinda** | `admin_loglar.kurum_bazinda` | `ADL05` | *Veri kaynağı yok* | Aktif |
| **admin_loglar.hic_giris_yapmamis_kullanicilar** | `admin_loglar.hic_giris_yapmamis_kullanicilar` | `ADL06` | *Veri kaynağı yok* | Aktif |
| **admin_loglar.son_hareketler** | `admin_loglar.son_hareketler` | `ADL07` | *Veri kaynağı yok* | Aktif |


### 🎴 Bildirim Yönetimi Bileşeni Kartları (`admin_bildirim_yonetimi`)
**Bileşen:** Bildirim Yönetimi | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_notifications.toplam_bildirim** | `admin_notifications.toplam_bildirim` | `ADN01` | *Veri kaynağı yok* | Aktif |
| **admin_notifications.okunmamis_bildirim** | `admin_notifications.okunmamis_bildirim` | `ADN02` | *Veri kaynağı yok* | Aktif |
| **admin_notifications.okunmus_bildirim** | `admin_notifications.okunmus_bildirim` | `ADN03` | *Veri kaynağı yok* | Aktif |
| **admin_notifications.yayin_bildirimi** | `admin_notifications.yayin_bildirimi` | `ADN04` | *Veri kaynağı yok* | Aktif |
| **admin_notifications.filtre** | `admin_notifications.filtre` | `ADN05` | *Veri kaynağı yok* | Aktif |
| **admin_notifications.bildirim_listesi** | `admin_notifications.bildirim_listesi` | `ADN06` | *Veri kaynağı yok* | Aktif |


### 🎴 Paket ve Modül Yönetimi Bileşeni Kartları (`admin_paket_modul_yonetimi`)
**Bileşen:** Paket ve Modül Yönetimi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_packages.abonelik_paketleri** | `admin_packages.abonelik_paketleri` | `ADP01` | *Veri kaynağı yok* | Aktif |
| **admin_packages.sistem_modulleri** | `admin_packages.sistem_modulleri` | `ADP02` | *Veri kaynağı yok* | Aktif |


### 🎴 Alt Kurum Yönetimi Bileşeni Kartları (`admin_alt_kurum_yonetimi`)
**Bileşen:** Alt Kurum Yönetimi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_sub_tenants.ozet_kart** | `admin_sub_tenants.ozet_kart` | `ADS01` | *Veri kaynağı yok* | Aktif |
| **admin_sub_tenants.alt_kurum_listesi** | `admin_sub_tenants.alt_kurum_listesi` | `ADS02` | *Veri kaynağı yok* | Aktif |


### 🎴 Alt Kurum Kullanım Raporu Bileşeni Kartları (`admin_alt_kurum_kullanim_raporu`)
**Bileşen:** Alt Kurum Kullanım Raporu | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_sub_tenants_usage.ozet_toplam** | `admin_sub_tenants_usage.ozet_toplam` | `ADSU01` | *Veri kaynağı yok* | Aktif |
| **admin_sub_tenants_usage.paket_dagilimi** | `admin_sub_tenants_usage.paket_dagilimi` | `ADSU02` | *Veri kaynağı yok* | Aktif |
| **admin_sub_tenants_usage.detay_tablosu** | `admin_sub_tenants_usage.detay_tablosu` | `ADSU03` | *Veri kaynağı yok* | Aktif |


### 🎴 Kurum Yönetimi Bileşeni Kartları (`admin_kurum_yonetimi`)
**Bileşen:** Kurum Yönetimi | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_tenants.toplam_kurum** | `admin_tenants.toplam_kurum` | `ADT01` | *Veri kaynağı yok* | Aktif |
| **admin_tenants.aktif_kurum** | `admin_tenants.aktif_kurum` | `ADT02` | *Veri kaynağı yok* | Aktif |
| **admin_tenants.arsivlenmis_kurum** | `admin_tenants.arsivlenmis_kurum` | `ADT03` | *Veri kaynağı yok* | Aktif |
| **admin_tenants.toplam_kullanici** | `admin_tenants.toplam_kullanici` | `ADT04` | *Veri kaynağı yok* | Aktif |
| **admin_tenants.kurum_listesi** | `admin_tenants.kurum_listesi` | `ADT05` | *Veri kaynağı yok* | Aktif |


### 🎴 Kullanıcı Yönetimi Bileşeni Kartları (`admin_kullanici_yonetimi`)
**Bileşen:** Kullanıcı Yönetimi | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_users.arama_filtre** | `admin_users.arama_filtre` | `ADU01` | *Veri kaynağı yok* | Aktif |
| **admin_users.toplam_kullanici** | `admin_users.toplam_kullanici` | `ADU02` | *Veri kaynağı yok* | Aktif |
| **admin_users.aktif_kullanici** | `admin_users.aktif_kullanici` | `ADU03` | *Veri kaynağı yok* | Aktif |
| **admin_users.pasif_kullanici** | `admin_users.pasif_kullanici` | `ADU04` | *Veri kaynağı yok* | Aktif |
| **admin_users.kullanici_listesi** | `admin_users.kullanici_listesi` | `ADU05` | *Veri kaynağı yok* | Aktif |


### 🎴 Yedekleme Aracı Bileşeni Kartları (`admin_yedekleme_araci`)
**Bileşen:** Yedekleme Aracı | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_yedekleme.manuel_yedek** | `admin_yedekleme.manuel_yedek` | `ADY201` | *Veri kaynağı yok* | Aktif |
| **admin_yedekleme.otomatik_yedek_durumu** | `admin_yedekleme.otomatik_yedek_durumu` | `ADY202` | *Veri kaynağı yok* | Aktif |
| **admin_yedekleme.yedek_listesi** | `admin_yedekleme.yedek_listesi` | `ADY203` | *Veri kaynağı yok* | Aktif |
| **admin_yedekleme.db_geri_yukleme** | `admin_yedekleme.db_geri_yukleme` | `ADY204` | *Veri kaynağı yok* | Aktif |


### 🎴 Yönetim Paneli Özeti Bileşeni Kartları (`admin_yonetim_paneli_ozet`)
**Bileşen:** Yönetim Paneli Özeti | **Kart Sayısı:** 10

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **admin_yonetim_paneli.bakim_modu** | `admin_yonetim_paneli.bakim_modu` | `ADYP01` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.kurum_secimi** | `admin_yonetim_paneli.kurum_secimi` | `ADYP02` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.cevrimici** | `admin_yonetim_paneli.cevrimici` | `ADYP03` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.aktif_hesap** | `admin_yonetim_paneli.aktif_hesap` | `ADYP04` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.son_24_saat** | `admin_yonetim_paneli.son_24_saat` | `ADYP05` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.son_7_gun** | `admin_yonetim_paneli.son_7_gun` | `ADYP06` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.son_30_gun** | `admin_yonetim_paneli.son_30_gun` | `ADYP07` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.tum_zamanlar** | `admin_yonetim_paneli.tum_zamanlar` | `ADYP08` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.kullanici_durumu** | `admin_yonetim_paneli.kullanici_durumu` | `ADYP09` | *Veri kaynağı yok* | Aktif |
| **admin_yonetim_paneli.son_aktiviteler** | `admin_yonetim_paneli.son_aktiviteler` | `ADYP10` | *Veri kaynağı yok* | Aktif |


### 🎴 E-posta Bildirim Ayarları Bileşeni Kartları (`eposta_bildirim_ayarlari`)
**Bileşen:** E-posta Bildirim Ayarları | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **ayarlar_eposta.bildirim_tercihleri** | `ayarlar_eposta.bildirim_tercihleri` | `AYE02` | *Veri kaynağı yok* | Aktif |
| **ayarlar.eposta_bildirimleri** | `ayarlar.eposta_bildirimleri` | `AY07` | *Veri kaynağı yok* | Aktif |


### 🎴 Hesap Ayarları Bileşeni Kartları (`hesap_ayarlari`)
**Bileşen:** Hesap Ayarları | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **ayarlar.hesap_ayarlari** | `ayarlar.hesap_ayarlari` | `AY05` | *Veri kaynağı yok* | Aktif |
| **ayarlar.profil_bilgileri** | `ayarlar.profil_bilgileri` | `AY06` | *Veri kaynağı yok* | Aktif |


### 🎴 Kurum Ayarları Bileşeni Kartları (`kurum_ayarlari`)
**Bileşen:** Kurum Ayarları | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **ayarlar.kurum_ayarlari** | `ayarlar.kurum_ayarlari` | `AY09` | *Veri kaynağı yok* | Aktif |


### 🎴 Yönetim Paneli (Admin) Bileşeni Kartları (`admin_yonetim_paneli`)
**Bileşen:** Yönetim Paneli (Admin) | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **ayarlar.yonetim_paneli** | `ayarlar.yonetim_paneli` | `AY10` | *Veri kaynağı yok* | Aktif |


### 🎴 Zamanlanmış Raporlar Bileşeni Kartları (`zamanlanmis_raporlar`)
**Bileşen:** Zamanlanmış Raporlar | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **ayarlar.zamanlanmis_rapor_ozeti** | `ayarlar.zamanlanmis_rapor_ozeti` | `AY04` | *Veri kaynağı yok* | Aktif |
| **ayarlar.zamanlanmis_raporlar** | `ayarlar.zamanlanmis_raporlar` | `AY08` | *Veri kaynağı yok* | Aktif |
| **ayarlar_zamanlanmis_raporlar.haftalik_strateji_ozeti** | `ayarlar_zamanlanmis_raporlar.haftalik_strateji_ozeti` | `AYZ01` | *Veri kaynağı yok* | Aktif |
| **ayarlar_zamanlanmis_raporlar.sabah_operasyonel_ozeti** | `ayarlar_zamanlanmis_raporlar.sabah_operasyonel_ozeti` | `AYZ02` | *Veri kaynağı yok* | Aktif |
| **ayarlar_zamanlanmis_raporlar.risk_anomali_uyarisi** | `ayarlar_zamanlanmis_raporlar.risk_anomali_uyarisi` | `AYZ03` | *Veri kaynağı yok* | Aktif |
| **ayarlar_zamanlanmis_raporlar.aylik_pg_raporu** | `ayarlar_zamanlanmis_raporlar.aylik_pg_raporu` | `AYZ04` | *Veri kaynağı yok* | Aktif |


### 🎴 Özel SMTP Yapılandırması Bileşeni Kartları (`ozel_smtp_yapilandirmasi`)
**Bileşen:** Özel SMTP Yapılandırması | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **ayarlar_eposta.ozel_smtp** | `ayarlar_eposta.ozel_smtp` | `AYE01` | *Veri kaynağı yok* | Aktif |


### 🎴 Bireysel Karne AI Özeti Bileşeni Kartları (`bireysel_karne_ai_ozet`)
**Bileşen:** Bireysel Karne AI Özeti | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **bireysel_karne.ai_ozet** | `bireysel_karne.ai_ozet` | `BR201` | *Veri kaynağı yok* | Aktif |


### 🎴 Bireysel Karne Özet Görselleri Bileşeni Kartları (`bireysel_karne_ozet_gorseller`)
**Bileşen:** Bireysel Karne Özet Görselleri | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **bireysel_karne.ilerleme_halkalari** | `bireysel_karne.ilerleme_halkalari` | `BR203` | *Veri kaynağı yok* | Aktif |
| **bireysel_karne.yil_ozeti** | `bireysel_karne.yil_ozeti` | `BR208` | *Veri kaynağı yok* | Aktif |


### 🎴 Bireysel Karne İstatistikleri Bileşeni Kartları (`bireysel_karne_istatistikleri`)
**Bileşen:** Bireysel Karne İstatistikleri | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **bireysel_karne.stat_toplam_pg** | `bireysel_karne.stat_toplam_pg` | `BR204` | *Veri kaynağı yok* | Aktif |
| **bireysel_karne.stat_veri_girilen** | `bireysel_karne.stat_veri_girilen` | `BR205` | *Veri kaynağı yok* | Aktif |
| **bireysel_karne.stat_faaliyetler** | `bireysel_karne.stat_faaliyetler` | `BR206` | *Veri kaynağı yok* | Aktif |
| **bireysel_karne.stat_tamamlanan** | `bireysel_karne.stat_tamamlanan` | `BR207` | *Veri kaynağı yok* | Aktif |


### 🎴 Bireysel Karne Zaman Çizelgesi Bileşeni Kartları (`bireysel_karne_zaman_cizelgesi`)
**Bileşen:** Bireysel Karne Zaman Çizelgesi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **bireysel_karne.zaman_cizelgesi** | `bireysel_karne.zaman_cizelgesi` | `BR209` | *Veri kaynağı yok* | Aktif |


### 🎴 Bireysel Karne Detay Tabloları Bileşeni Kartları (`bireysel_karne_detay_tablolari`)
**Bileşen:** Bireysel Karne Detay Tabloları | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **bireysel_karne.pg_tablosu** | `bireysel_karne.pg_tablosu` | `BR210` | *Veri kaynağı yok* | Aktif |
| **bireysel_karne.faaliyet_tablosu** | `bireysel_karne.faaliyet_tablosu` | `BR211` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Çapraz Risk Analizi Bileşeni Kartları (`k_radar_cross_risk_analizi`)
**Bileşen:** K-Radar Çapraz Risk Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_cross.risk_isi_haritasi** | `k_radar_cross.risk_isi_haritasi` | `KDC01` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar A3 Raporları Bileşeni Kartları (`k_radar_cross_a3`)
**Bileşen:** K-Radar A3 Raporları | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_cross_a3.a3_ozeti** | `k_radar_cross_a3.a3_ozeti` | `KDCA01` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Çapraz Anket Bileşeni Kartları (`k_radar_cross_anket`)
**Bileşen:** K-Radar Çapraz Anket | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_cross_anket.anket_ozeti** | `k_radar_cross_anket.anket_ozeti` | `KDCK01` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Paydaş Yönetimi Bileşeni Kartları (`k_radar_cross_paydas`)
**Bileşen:** K-Radar Paydaş Yönetimi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_cross_paydas.paydas_listesi** | `k_radar_cross_paydas.paydas_listesi` | `KDCP01` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Rekabet Analizi Bileşeni Kartları (`k_radar_cross_rekabet`)
**Bileşen:** K-Radar Rekabet Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_cross_rekabet.rekabet_ozeti** | `k_radar_cross_rekabet.rekabet_ozeti` | `KDCR01` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar Skoru Bileşeni Kartları (`k_radar_kp_skoru`)
**Bileşen:** KP-Radar Skoru | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp.toplam_skor** | `k_radar_kp.toplam_skor` | `KD21` | *Veri kaynağı yok* | Aktif |
| **k_radar_kp.band** | `k_radar_kp.band` | `KD22` | *Veri kaynağı yok* | Aktif |
| **k_radar_kp.kritik_pg** | `k_radar_kp.kritik_pg` | `KD23` | *Veri kaynağı yok* | Aktif |
| **k_radar_kp.hesaplanan_pg** | `k_radar_kp.hesaplanan_pg` | `KD24` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar Kıyaslama Bileşeni Kartları (`k_radar_kp_benchmark`)
**Bileşen:** KP-Radar Kıyaslama | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_benchmark.benchmark_ozeti** | `k_radar_kp_benchmark.benchmark_ozeti` | `KDB01` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar Darboğaz Analizi Bileşeni Kartları (`k_radar_kp_darbogaz`)
**Bileşen:** KP-Radar Darboğaz Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_darbogaz.ozet** | `k_radar_kp_darbogaz.ozet` | `KDD01` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar Kapasite Analizi Bileşeni Kartları (`k_radar_kp_kapasite`)
**Bileşen:** KP-Radar Kapasite Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_kapasite.kapasite_ozeti** | `k_radar_kp_kapasite.kapasite_ozeti` | `KDA01` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar OEE Analizi Bileşeni Kartları (`k_radar_kp_oee`)
**Bileşen:** KP-Radar OEE Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_oee.ozet** | `k_radar_kp_oee.ozet` | `KDO01` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar Süreç Olgunluğu Bileşeni Kartları (`k_radar_kp_olgunluk`)
**Bileşen:** KP-Radar Süreç Olgunluğu | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_olgunluk.olgunluk_takip** | `k_radar_kp_olgunluk.olgunluk_takip` | `KDM01` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar Pareto Analizi Bileşeni Kartları (`k_radar_kp_pareto`)
**Bileşen:** KP-Radar Pareto Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_pareto.ozet** | `k_radar_kp_pareto.ozet` | `KDPA01` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar SLA Analizi Bileşeni Kartları (`k_radar_kp_sla`)
**Bileşen:** KP-Radar SLA Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_sla.ozet** | `k_radar_kp_sla.ozet` | `KDSL01` | *Veri kaynağı yok* | Aktif |


### 🎴 KP-Radar Değer Akışı (VSM) Bileşeni Kartları (`k_radar_kp_vsm`)
**Bileşen:** KP-Radar Değer Akışı (VSM) | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kp_vsm.vsm_ozeti** | `k_radar_kp_vsm.vsm_ozeti` | `KDVS01` | *Veri kaynağı yok* | Aktif |


### 🎴 KPR Proje Radarı Bileşeni Kartları (`k_radar_kpr_proje_radari`)
**Bileşen:** KPR Proje Radarı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kpr.proje_radari** | `k_radar_kpr.proje_radari` | `KPR01` | *Veri kaynağı yok* | Aktif |


### 🎴 KPR Kritik Yol Analizi Bileşeni Kartları (`k_radar_kpr_cpm`)
**Bileşen:** KPR Kritik Yol Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kpr_cpm.cpm_analizi** | `k_radar_kpr_cpm.cpm_analizi` | `KPC01` | *Veri kaynağı yok* | Aktif |


### 🎴 KPR Kazanılmış Değer Analizi Bileşeni Kartları (`k_radar_kpr_evm`)
**Bileşen:** KPR Kazanılmış Değer Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kpr_evm.ozet** | `k_radar_kpr_evm.ozet` | `KPE01` | *Veri kaynağı yok* | Aktif |


### 🎴 KPR Gantt Takibi Bileşeni Kartları (`k_radar_kpr_gantt`)
**Bileşen:** KPR Gantt Takibi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kpr_gantt.gantt_ozeti** | `k_radar_kpr_gantt.gantt_ozeti` | `KPG01` | *Veri kaynağı yok* | Aktif |


### 🎴 KPR Kaynak Kapasitesi Bileşeni Kartları (`k_radar_kpr_kaynak_kapasite`)
**Bileşen:** KPR Kaynak Kapasitesi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kpr_kaynak_kapasite.ozet** | `k_radar_kpr_kaynak_kapasite.ozet` | `KPK01` | *Veri kaynağı yok* | Aktif |


### 🎴 KPR Risk Yönetimi Bileşeni Kartları (`k_radar_kpr_risk`)
**Bileşen:** KPR Risk Yönetimi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_kpr_risk.risk_ozeti** | `k_radar_kpr_risk.risk_ozeti` | `KPRI01` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Balanced Scorecard Bileşeni Kartları (`k_radar_ks_bsc`)
**Bileşen:** K-Radar Balanced Scorecard | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.bsc** | `k_radar_ks.bsc` | `KD10` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar EFQM Olgunluk Modeli Bileşeni Kartları (`k_radar_ks_efqm`)
**Bileşen:** K-Radar EFQM Olgunluk Modeli | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.efqm** | `k_radar_ks.efqm` | `KD11` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Hedef Gap Analizi Bileşeni Kartları (`k_radar_ks_gap_analizi`)
**Bileşen:** K-Radar Hedef Gap Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.gap_analizi** | `k_radar_ks.gap_analizi` | `KD08` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Kurumsal Strateji Skoru Bileşeni Kartları (`k_radar_ks_skoru`)
**Bileşen:** K-Radar Kurumsal Strateji Skoru | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.strateji_kapsami** | `k_radar_ks.strateji_kapsami` | `KD01` | *Veri kaynağı yok* | Aktif |
| **k_radar_ks.toplam_strateji** | `k_radar_ks.toplam_strateji` | `KD02` | *Veri kaynağı yok* | Aktif |
| **k_radar_ks.genel_pg_basarisi** | `k_radar_ks.genel_pg_basarisi` | `KD03` | *Veri kaynağı yok* | Aktif |
| **k_radar_ks.ks_skoru** | `k_radar_ks.ks_skoru` | `KD04` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar OKR Takibi Bileşeni Kartları (`k_radar_ks_okr`)
**Bileşen:** K-Radar OKR Takibi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.okr** | `k_radar_ks.okr` | `KD09` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Strateji-Süreç Kapsama Bileşeni Kartları (`k_radar_ks_strateji_surec_kapsama`)
**Bileşen:** K-Radar Strateji-Süreç Kapsama | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_ks.strateji_surec_kapsama_ozeti** | `k_radar_ks.strateji_surec_kapsama_ozeti` | `KD12` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Radar Risk Yönetimi Bileşeni Kartları (`k_radar_risk_yonetimi`)
**Bileşen:** K-Radar Risk Yönetimi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_radar_risk_management.risk_matrisi** | `k_radar_risk_management.risk_matrisi` | `KDR01` | *Veri kaynağı yok* | Aktif |
| **k_radar_risk_management.risk_listesi** | `k_radar_risk_management.risk_listesi` | `KDR02` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Aktivite Takvimi Bileşeni Kartları (`k_rapor_aktivite_takvim`)
**Bileşen:** K-Rapor Aktivite Takvimi | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_aktivite_takvim.gunluk_veri_giris_aktivitesi** | `k_rapor_aktivite_takvim.gunluk_veri_giris_aktivitesi` | `KR08` | *Veri kaynağı yok* | Aktif |
| **k_rapor_aktivite_takvim.son_30_gun_trend** | `k_rapor_aktivite_takvim.son_30_gun_trend` | `KR09` | *Veri kaynağı yok* | Aktif |
| **Toplam Giriş** | `k_rapor_aktivite_takvim.toplam_giris` | `KR72` | *Veri kaynağı yok* | Aktif |
| **Aktif Gün** | `k_rapor_aktivite_takvim.aktif_gun` | `KR73` | *Veri kaynağı yok* | Aktif |
| **Günlük Ort.** | `k_rapor_aktivite_takvim.gunluk_ort` | `KR74` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Anomali Tespiti Bileşeni Kartları (`k_rapor_anomali_tespiti`)
**Bileşen:** K-Rapor Anomali Tespiti | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_anomalies.tarama_filtreleri** | `k_rapor_anomalies.tarama_filtreleri` | `KRAN01` | *Veri kaynağı yok* | Aktif |
| **k_rapor_anomalies.ozet** | `k_rapor_anomalies.ozet` | `KRAN02` | *Veri kaynağı yok* | Aktif |
| **k_rapor_anomalies.anomali_listesi** | `k_rapor_anomalies.anomali_listesi` | `KRAN03` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Bildirim Analizi Bileşeni Kartları (`k_rapor_bildirim_analiz`)
**Bileşen:** K-Rapor Bildirim Analizi | **Kart Sayısı:** 8

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_bildirim_analiz.bildirim_turu_dagilimi** | `k_rapor_bildirim_analiz.bildirim_turu_dagilimi` | `KR10` | *Veri kaynağı yok* | Aktif |
| **k_rapor_bildirim_analiz.son_30_gun_bildirim_trendi** | `k_rapor_bildirim_analiz.son_30_gun_bildirim_trendi` | `KR13` | *Veri kaynağı yok* | Aktif |
| **k_rapor_bildirim_analiz.okunmayan_bildirimlerin_yaslanmasi** | `k_rapor_bildirim_analiz.okunmayan_bildirimlerin_yaslanmasi` | `KR12` | *Veri kaynağı yok* | Aktif |
| **k_rapor_bildirim_analiz.en_cok_bildirim_alan_kullanicilar** | `k_rapor_bildirim_analiz.en_cok_bildirim_alan_kullanicilar` | `KR11` | *Veri kaynağı yok* | Aktif |
| **Toplam Bildirim** | `k_rapor_bildirim_analiz.toplam_bildirim` | `KR78` | *Veri kaynağı yok* | Aktif |
| **Okunan** | `k_rapor_bildirim_analiz.okunan` | `KR79` | *Veri kaynağı yok* | Aktif |
| **Okunmayan** | `k_rapor_bildirim_analiz.okunmayan` | `KR80` | *Veri kaynağı yok* | Aktif |
| **Son 7 Gün** | `k_rapor_bildirim_analiz.son_7_gun` | `KR81` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Bireysel PG Analizi Bileşeni Kartları (`k_rapor_bireysel_pg`)
**Bileşen:** K-Rapor Bireysel PG Analizi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_bireysel.kullanici_bazli_pg_basari_tablosu** | `k_rapor_bireysel.kullanici_bazli_pg_basari_tablosu` | `KR15` | *Veri kaynağı yok* | Aktif |
| **k_rapor_bireysel.bireysel_pg_detay_listesi** | `k_rapor_bireysel.bireysel_pg_detay_listesi` | `KR14` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Denetim Analizi Bileşeni Kartları (`k_rapor_denetim`)
**Bileşen:** K-Rapor Denetim Analizi | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_denetim.islem_dagilimi** | `k_rapor_denetim.islem_dagilimi` | `KR17` | *Veri kaynağı yok* | Aktif |
| **k_rapor_denetim.en_aktif_kullanicilar** | `k_rapor_denetim.en_aktif_kullanicilar` | `KR16` | *Veri kaynağı yok* | Aktif |
| **k_rapor_denetim.son_islemler** | `k_rapor_denetim.son_islemler` | `KR18` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Kazanılmış Değer Analizi Bileşeni Kartları (`k_rapor_evm`)
**Bileşen:** K-Rapor Kazanılmış Değer Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_evm.kazanilmis_deger_evm_proje_snapshot_tablosu** | `k_rapor_evm.kazanilmis_deger_evm_proje_snapshot_tablosu` | `KR19` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Faaliyet Analizi Bileşeni Kartları (`k_rapor_faaliyet`)
**Bileşen:** K-Rapor Faaliyet Analizi | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_faaliyet.aylik_tamamlanan** | `k_rapor_faaliyet.aylik_tamamlanan` | `KR20` | *Veri kaynağı yok* | Aktif |
| **k_rapor_faaliyet.geciken_faaliyetler** | `k_rapor_faaliyet.geciken_faaliyetler` | `KR21` | *Veri kaynağı yok* | Aktif |
| **k_rapor_faaliyet.proje_portfoy_durumu** | `k_rapor_faaliyet.proje_portfoy_durumu` | `KR22` | *Veri kaynağı yok* | Aktif |
| **Tamamlanan** | `k_rapor_faaliyet.tamamlanan` | `KR58` | *Veri kaynağı yok* | Aktif |
| **Devam Ediyor** | `k_rapor_faaliyet.devam_ediyor` | `KR59` | *Veri kaynağı yok* | Aktif |
| **Geciken** | `k_rapor_faaliyet.geciken` | `KR60` | *Veri kaynağı yok* | Aktif |
| **Toplam** | `k_rapor_faaliyet.toplam` | `KR61` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor K-Vektör Ağırlıkları Bileşeni Kartları (`k_rapor_k_vektor`)
**Bileşen:** K-Rapor K-Vektör Ağırlıkları | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_k_vektor.ana_strateji_agirliklari** | `k_rapor_k_vektor.ana_strateji_agirliklari` | `KR25` | *Veri kaynağı yok* | Aktif |
| **k_rapor_k_vektor.agirlik_tablosu** | `k_rapor_k_vektor.agirlik_tablosu` | `KR23` | *Veri kaynağı yok* | Aktif |
| **k_rapor_k_vektor.alt_strateji_agirliklari** | `k_rapor_k_vektor.alt_strateji_agirliklari` | `KR24` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Kurum Karşılaştırma Bileşeni Kartları (`k_rapor_kurum_karsilastirma`)
**Bileşen:** K-Rapor Kurum Karşılaştırma | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_kurum_karsilastirma.kurum_performans_karsilastirmasi** | `k_rapor_kurum_karsilastirma.kurum_performans_karsilastirmasi` | `KR27` | *Veri kaynağı yok* | Aktif |
| **k_rapor_kurum_karsilastirma.kurum_detay_tablosu** | `k_rapor_kurum_karsilastirma.kurum_detay_tablosu` | `KR26` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Kurumsal Özet Bileşeni Kartları (`k_rapor_kurumsal_ozet`)
**Bileşen:** K-Rapor Kurumsal Özet | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_kurumsal.vizyon_skoru** | `k_rapor_kurumsal.vizyon_skoru` | `KR01` | *Veri kaynağı yok* | Aktif |
| **k_rapor_kurumsal.strateji_bazli_basari** | `k_rapor_kurumsal.strateji_bazli_basari` | `KR02` | *Veri kaynağı yok* | Aktif |
| **k_rapor_kurumsal.en_iyi_5_surec** | `k_rapor_kurumsal.en_iyi_5_surec` | `KR06` | *Veri kaynağı yok* | Aktif |
| **k_rapor_kurumsal.en_dusuk_5_surec** | `k_rapor_kurumsal.en_dusuk_5_surec` | `KR07` | *Veri kaynağı yok* | Aktif |
| **Hedefte** | `k_rapor_kurumsal.hedefte` | `KR03` | *Veri kaynağı yok* | Aktif |
| **Riskli** | `k_rapor_kurumsal.riskli` | `KR04` | *Veri kaynağı yok* | Aktif |
| **Kritik** | `k_rapor_kurumsal.kritik` | `KR05` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Paydaş Analizi Bileşeni Kartları (`k_rapor_paydas`)
**Bileşen:** K-Rapor Paydaş Analizi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_paydas.paydas_haritasi** | `k_rapor_paydas.paydas_haritasi` | `KR29` | *Veri kaynağı yok* | Aktif |
| **k_rapor_paydas.paydas_anket_ozeti** | `k_rapor_paydas.paydas_anket_ozeti` | `KR28` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor PG Dağılım Analizi Bileşeni Kartları (`k_rapor_pg_dagilim`)
**Bileşen:** K-Rapor PG Dağılım Analizi | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_pg_dagilim.basari_yuzdesi_dagilimi_histogram** | `k_rapor_pg_dagilim.basari_yuzdesi_dagilimi_histogram` | `KR30` | *Veri kaynağı yok* | Aktif |
| **k_rapor_pg_dagilim.pg_dagilim_grafigi** | `k_rapor_pg_dagilim.pg_dagilim_grafigi` | `KR32` | *Veri kaynağı yok* | Aktif |
| **k_rapor_pg_dagilim.en_dusuk_performansli_pg_ler** | `k_rapor_pg_dagilim.en_dusuk_performansli_pg_ler` | `KR31` | *Veri kaynağı yok* | Aktif |
| **Toplam PG** | `k_rapor_pg_dagilim.toplam_pg` | `KR68` | *Veri kaynağı yok* | Aktif |
| **Ort. Başarı** | `k_rapor_pg_dagilim.ort_basari` | `KR69` | *Veri kaynağı yok* | Aktif |
| **Hedefte (≥%80)** | `k_rapor_pg_dagilim.hedefte_80` | `KR70` | *Veri kaynağı yok* | Aktif |
| **Kritik (<%50)** | `k_rapor_pg_dagilim.kritik_50` | `KR71` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Rekabet ve A3 Analizi Bileşeni Kartları (`k_rapor_rekabet`)
**Bileşen:** K-Rapor Rekabet ve A3 Analizi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_rekabet.rekabetci_analiz** | `k_rapor_rekabet.rekabetci_analiz` | `KR34` | *Veri kaynağı yok* | Aktif |
| **k_rapor_rekabet.a3_raporlari** | `k_rapor_rekabet.a3_raporlari` | `KR33` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Risk ve Süreç Analizi Bileşeni Kartları (`k_rapor_risk`)
**Bileşen:** K-Rapor Risk ve Süreç Analizi | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_risk.risk_tablosu_rpn_sirali** | `k_rapor_risk.risk_tablosu_rpn_sirali` | `KR36` | *Veri kaynağı yok* | Aktif |
| **k_rapor_risk.surec_olgunluk_seviyeleri** | `k_rapor_risk.surec_olgunluk_seviyeleri` | `KR37` | *Veri kaynağı yok* | Aktif |
| **k_rapor_risk.darbogaz_gecmisi** | `k_rapor_risk.darbogaz_gecmisi` | `KR35` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Sorumlu Analizi Bileşeni Kartları (`k_rapor_sorumlu_analiz`)
**Bileşen:** K-Rapor Sorumlu Analizi | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_sorumlu_analiz.kisi_basina_faaliyet_yuku** | `k_rapor_sorumlu_analiz.kisi_basina_faaliyet_yuku` | `KR39` | *Veri kaynağı yok* | Aktif |
| **k_rapor_sorumlu_analiz.en_cok_geciken_kisiler** | `k_rapor_sorumlu_analiz.en_cok_geciken_kisiler` | `KR38` | *Veri kaynağı yok* | Aktif |
| **k_rapor_sorumlu_analiz.sorumlu_detay_tablosu** | `k_rapor_sorumlu_analiz.sorumlu_detay_tablosu` | `KR40` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Strateji Kapsama Analizi Bileşeni Kartları (`k_rapor_strateji_kapsama`)
**Bileşen:** K-Rapor Strateji Kapsama Analizi | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_strateji_kapsama.strateji_kapsama_durumu** | `k_rapor_strateji_kapsama.strateji_kapsama_durumu` | `KR42` | *Veri kaynağı yok* | Aktif |
| **k_rapor_strateji_kapsama.stratejisiz_surecler** | `k_rapor_strateji_kapsama.stratejisiz_surecler` | `KR43` | *Veri kaynağı yok* | Aktif |
| **k_rapor_strateji_kapsama.strateji_bazli_kapsama_tablosu** | `k_rapor_strateji_kapsama.strateji_bazli_kapsama_tablosu` | `KR41` | *Veri kaynağı yok* | Aktif |
| **Tam Kapsamlı** | `k_rapor_strateji_kapsama.tam_kapsamli` | `KR75` | *Veri kaynağı yok* | Aktif |
| **Kısmi** | `k_rapor_strateji_kapsama.kismi` | `KR76` | *Veri kaynağı yok* | Aktif |
| **Boş Strateji** | `k_rapor_strateji_kapsama.bos_strateji` | `KR77` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Süreç-PG Analizi Bileşeni Kartları (`k_rapor_surec_pg`)
**Bileşen:** K-Rapor Süreç-PG Analizi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_surec_pg.surec_donem_isi_haritasi** | `k_rapor_surec_pg.surec_donem_isi_haritasi` | `KR48` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor SWOT/TOWS Trend Analizi Bileşeni Kartları (`k_rapor_swot_trend`)
**Bileşen:** K-Rapor SWOT/TOWS Trend Analizi | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_swot_trend.swot_madde_sayisi_trendi** | `k_rapor_swot_trend.swot_madde_sayisi_trendi` | `KR49` | *Veri kaynağı yok* | Aktif |
| **k_rapor_swot_trend.tows_strateji_sayisi_trendi** | `k_rapor_swot_trend.tows_strateji_sayisi_trendi` | `KR50` | *Veri kaynağı yok* | Aktif |
| **k_rapor_swot_trend.yillik_swot_tows_ozet_tablosu** | `k_rapor_swot_trend.yillik_swot_tows_ozet_tablosu` | `KR51` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Uyarı Paneli Bileşeni Kartları (`k_rapor_uyari`)
**Bileşen:** K-Rapor Uyarı Paneli | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_uyari.kritik_performans_gostergeleri** | `k_rapor_uyari.kritik_performans_gostergeleri` | `KR53` | *Veri kaynağı yok* | Aktif |
| **k_rapor_uyari.yuksek_riskler** | `k_rapor_uyari.yuksek_riskler` | `KR54` | *Veri kaynağı yok* | Aktif |
| **k_rapor_uyari.geciken_faaliyetler** | `k_rapor_uyari.geciken_faaliyetler` | `KR52` | *Veri kaynağı yok* | Aktif |
| **Kritik PG** | `k_rapor_uyari.kritik_pg` | `KR65` | *Veri kaynağı yok* | Aktif |
| **Geciken Faaliyet** | `k_rapor_uyari.geciken_faaliyet` | `KR66` | *Veri kaynağı yok* | Aktif |
| **Yüksek Risk** | `k_rapor_uyari.yuksek_risk` | `KR67` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Strateji-Süreç Uyum Ağacı Bileşeni Kartları (`k_rapor_uyum`)
**Bileşen:** K-Rapor Strateji-Süreç Uyum Ağacı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_uyum.strateji_surec_katki_agaci** | `k_rapor_uyum.strateji_surec_katki_agaci` | `KR55` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Rapor Veri Durumu Bileşeni Kartları (`k_rapor_veri_durumu`)
**Bileşen:** K-Rapor Veri Durumu | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **k_rapor_veri_durumu.veri_girilen_pg_ler** | `k_rapor_veri_durumu.veri_girilen_pg_ler` | `KR56` | *Veri kaynağı yok* | Aktif |
| **k_rapor_veri_durumu.veri_girilmeyen_pg_ler** | `k_rapor_veri_durumu.veri_girilmeyen_pg_ler` | `KR57` | *Veri kaynağı yok* | Aktif |
| **Toplam PG** | `k_rapor_veri_durumu.toplam_pg` | `KR62` | *Veri kaynağı yok* | Aktif |
| **Veri Girilmiş** | `k_rapor_veri_durumu.veri_girilmis` | `KR63` | *Veri kaynağı yok* | Aktif |
| **Eksik** | `k_rapor_veri_durumu.eksik` | `KR64` | *Veri kaynağı yok* | Aktif |


### 🎴 Benim Görevlerim Kartı Bileşeni Kartları (`benim_gorevlerim_karti`)
**Bileşen:** Benim Görevlerim Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.benim_gorevlerim** | `masaustu.benim_gorevlerim` | `MA04` | *Veri kaynağı yok* | Aktif |


### 🎴 Benim Masam Kartı Bileşeni Kartları (`benim_masam_karti`)
**Bileşen:** Benim Masam Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.benim_masam** | `masaustu.benim_masam` | `MA08` | *Veri kaynağı yok* | Aktif |


### 🎴 Bildirimler Kartı Bileşeni Kartları (`bildirimler_karti`)
**Bileşen:** Bildirimler Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.bildirimler** | `masaustu.bildirimler` | `MA12` | *Veri kaynağı yok* | Aktif |


### 🎴 Mini İstatistik Şeridi Bileşeni Kartları (`mini_istatistik_seridi`)
**Bileşen:** Mini İstatistik Şeridi | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.bireysel_pg** | `masaustu.bireysel_pg` | `MA15` | *Veri kaynağı yok* | Aktif |
| **masaustu.mini_kartlar** | `masaustu.mini_kartlar` | `MA14` | *Veri kaynağı yok* | Aktif |
| **masaustu.devam_eden_faaliyet** | `masaustu.devam_eden_faaliyet` | `MA16` | *Veri kaynağı yok* | Aktif |
| **masaustu.surec_pg** | `masaustu.surec_pg` | `MA17` | *Veri kaynağı yok* | Aktif |
| **masaustu.okunmamis_bildirim** | `masaustu.okunmamis_bildirim` | `MA18` | *Veri kaynağı yok* | Aktif |


### 🎴 Bugünün Özeti Kartı Bileşeni Kartları (`bugunun_ozeti_karti`)
**Bileşen:** Bugünün Özeti Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.bugunun_ozeti** | `masaustu.bugunun_ozeti` | `MA03` | *Veri kaynağı yok* | Aktif |


### 🎴 Dikkat: Dönem Verisi Kartı Bileşeni Kartları (`dikkat_donem_verisi_karti`)
**Bileşen:** Dikkat: Dönem Verisi Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.dikkat_donem_verisi** | `masaustu.dikkat_donem_verisi` | `MA09` | *Veri kaynağı yok* | Aktif |


### 🎴 Favori PG'lerim Kartı Bileşeni Kartları (`favori_pglerim_karti`)
**Bileşen:** Favori PG'lerim Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.favori_pglerim** | `masaustu.favori_pglerim` | `MA19` | *Veri kaynağı yok* | Aktif |


### 🎴 Favori ve Son Ziyaretlerim Kartı Bileşeni Kartları (`favori_ve_son_ziyaretlerim_karti`)
**Bileşen:** Favori ve Son Ziyaretlerim Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.favori_ve_son_ziyaretlerim** | `masaustu.favori_ve_son_ziyaretlerim` | `MA05` | *Veri kaynağı yok* | Aktif |


### 🎴 Karalama Defteri Kartı Bileşeni Kartları (`karalama_defteri_karti`)
**Bileşen:** Karalama Defteri Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.karalama_defteri** | `masaustu.karalama_defteri` | `MA10` | *Veri kaynağı yok* | Aktif |


### 🎴 Kurumsal Olgunluk Endeksi Kartı Bileşeni Kartları (`kurumsal_olgunluk_endeksi_karti`)
**Bileşen:** Kurumsal Olgunluk Endeksi Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.kurumsal_olgunluk_endeksi** | `masaustu.kurumsal_olgunluk_endeksi` | `MA02` | *Veri kaynağı yok* | Aktif |


### 🎴 Özet Listeler Kartı Bileşeni Kartları (`ozet_listeler_karti`)
**Bileşen:** Özet Listeler Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.ozet_listeler** | `masaustu.ozet_listeler` | `MA11` | *Veri kaynağı yok* | Aktif |


### 🎴 Süreç PG'lerim Kartı Bileşeni Kartları (`surec_pglerim_karti`)
**Bileşen:** Süreç PG'lerim Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.surec_pglerim** | `masaustu.surec_pglerim` | `MA20` | *Veri kaynağı yok* | Aktif |


### 🎴 Takvimim Kartı Bileşeni Kartları (`takvimim_karti`)
**Bileşen:** Takvimim Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.takvimim** | `masaustu.takvimim` | `MA07` | *Veri kaynağı yok* | Aktif |


### 🎴 Yönetici Sabah Özeti Kartı Bileşeni Kartları (`yonetici_sabah_ozeti_karti`)
**Bileşen:** Yönetici Sabah Özeti Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **masaustu.yonetici_sabah_ozeti** | `masaustu.yonetici_sabah_ozeti` | `MA01` | *Veri kaynağı yok* | Aktif |


### 🎴 Süreç Özet İstatistikleri Bileşeni Kartları (`surec_ozet_istatistikleri`)
**Bileşen:** Süreç Özet İstatistikleri | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **process.toplam_surec** | `process.toplam_surec` | `PR01` | *Veri kaynağı yok* | Aktif |
| **process.toplam_pg** | `process.toplam_pg` | `PR02` | *Veri kaynağı yok* | Aktif |
| **process.yuksek_performans** | `process.yuksek_performans` | `PR04` | *Veri kaynağı yok* | Aktif |
| **process.kritik_surec** | `process.kritik_surec` | `PR05` | *Veri kaynağı yok* | Aktif |
| **process.k_vektor** | `process.k_vektor` | `PR06` | *Veri kaynağı yok* | Aktif |


### 🎴 Süreç Karnesi Genel Bilgiler Bileşeni Kartları (`surec_karnesi_genel_bilgiler`)
**Bileşen:** Süreç Karnesi Genel Bilgiler | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **process_karne.genel_bilgiler** | `process_karne.genel_bilgiler` | `PK02` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Özet İstatistikleri Bileşeni Kartları (`proje_ozet_istatistikleri`)
**Bileşen:** Proje Özet İstatistikleri | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project.toplam_proje** | `project.toplam_proje` | `PJ01` | *Veri kaynağı yok* | Aktif |
| **project.acik_gorev** | `project.acik_gorev` | `PJ02` | *Veri kaynağı yok* | Aktif |
| **project.gecikmis_gorev** | `project.gecikmis_gorev` | `PJ03` | *Veri kaynağı yok* | Aktif |
| **project.bu_hafta_biten** | `project.bu_hafta_biten` | `PJ04` | *Veri kaynağı yok* | Aktif |
| **project.acik_raid** | `project.acik_raid` | `PJ05` | *Veri kaynağı yok* | Aktif |
| **project.kritik_saglik** | `project.kritik_saglik` | `PJ06` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Operasyon Özeti Bileşeni Kartları (`proje_operasyon_ozeti`)
**Bileşen:** Proje Operasyon Özeti | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project.operasyon_ozeti** | `project.operasyon_ozeti` | `PJ08` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Listesi Yönetimi Bileşeni Kartları (`proje_listesi_yonetimi`)
**Bileşen:** Proje Listesi Yönetimi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project.proje_listesi** | `project.proje_listesi` | `PJ07` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Takvim Görünümü Bileşeni Kartları (`proje_takvim_gorunumu`)
**Bileşen:** Proje Takvim Görünümü | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_calendar.takvim** | `project_calendar.takvim` | `PJC01` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Detay Özeti Bileşeni Kartları (`proje_detay_ozeti`)
**Bileşen:** Proje Detay Özeti | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_detail.geciken_gorev_uyarisi** | `project_detail.geciken_gorev_uyarisi` | `PJD01` | *Veri kaynağı yok* | Aktif |
| **project_detail.proje_ozeti** | `project_detail.proje_ozeti` | `PJD02` | *Veri kaynağı yok* | Aktif |
| **project_detail.gorev_ozeti** | `project_detail.gorev_ozeti` | `PJD03` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Formu Bileşeni Kartları (`proje_formu`)
**Bileşen:** Proje Formu | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_form.sayfa** | `project_form.sayfa` | `PJF01` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Gantt Şeması Bileşeni Kartları (`proje_gantt_semasi`)
**Bileşen:** Proje Gantt Şeması | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_gantt.gantt_semasi** | `project_gantt.gantt_semasi` | `PJG01` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Kanban Panosu Bileşeni Kartları (`proje_kanban_panosu`)
**Bileşen:** Proje Kanban Panosu | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_kanban.yapilacak** | `project_kanban.yapilacak` | `PJK01` | *Veri kaynağı yok* | Aktif |
| **project_kanban.devam_beklemede** | `project_kanban.devam_beklemede` | `PJK02` | *Veri kaynağı yok* | Aktif |
| **project_kanban.tamamlandi** | `project_kanban.tamamlandi` | `PJK03` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Kapasite Yönetimi Bileşeni Kartları (`proje_kapasite_yonetimi`)
**Bileşen:** Proje Kapasite Yönetimi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_kapasite.sayfa** | `project_kapasite.sayfa` | `PJA01` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Portföy Yönetimi Bileşeni Kartları (`proje_portfoy_yonetimi`)
**Bileşen:** Proje Portföy Yönetimi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_portfolio.program_gantt** | `project_portfolio.program_gantt` | `PJP01` | *Veri kaynağı yok* | Aktif |
| **project_portfolio.portfoy_listesi** | `project_portfolio.portfoy_listesi` | `PJP02` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje RAID Yönetimi Bileşeni Kartları (`proje_raid_yonetimi`)
**Bileşen:** Proje RAID Yönetimi | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_raid.riskler** | `project_raid.riskler` | `PJR01` | *Veri kaynağı yok* | Aktif |
| **project_raid.varsayimlar** | `project_raid.varsayimlar` | `PJR02` | *Veri kaynağı yok* | Aktif |
| **project_raid.sorunlar** | `project_raid.sorunlar` | `PJR03` | *Veri kaynağı yok* | Aktif |
| **project_raid.bagimliliklar** | `project_raid.bagimliliklar` | `PJR04` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Stratejik İlişki Bileşeni Kartları (`proje_stratejik_iliski`)
**Bileşen:** Proje Stratejik İlişki | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_strategy_detail.proje_bilgisi** | `project_strategy_detail.proje_bilgisi` | `PJS01` | *Veri kaynağı yok* | Aktif |
| **project_strategy_detail.stratejik_skor** | `project_strategy_detail.stratejik_skor` | `PJS02` | *Veri kaynağı yok* | Aktif |
| **project_strategy_detail.bagli_surecler** | `project_strategy_detail.bagli_surecler` | `PJS03` | *Veri kaynağı yok* | Aktif |


### 🎴 Proje Görev Yönetimi Bileşeni Kartları (`proje_gorev_yonetimi`)
**Bileşen:** Proje Görev Yönetimi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **project_task_detail.sayfa** | `project_task_detail.sayfa` | `PJT01` | *Veri kaynağı yok* | Aktif |
| **project_task_form.sayfa** | `project_task_form.sayfa` | `PJTF01` | *Veri kaynağı yok* | Aktif |


### 🎴 AI Koç Raporu Bileşeni Kartları (`rapor_ai_coach_grubu`)
**Bileşen:** AI Koç Raporu | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_ai_coach.en_dusuk_performansli_3_strateji** | `raporlar_ai_coach.en_dusuk_performansli_3_strateji` | `RP153` | *Veri kaynağı yok* | Aktif |
| **raporlar_ai_coach.ai_onerisi** | `raporlar_ai_coach.ai_onerisi` | `RP154` | *Veri kaynağı yok* | Aktif |
| **Analiz Edilen Strateji** | `raporlar_ai_coach.analiz_edilen_strateji` | `RP151` | *Veri kaynağı yok* | Aktif |
| **En Düşük 3** | `raporlar_ai_coach.en_dusuk_3` | `RP152` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.ai_coach** | `raporlar_index.ai_coach` | `RPI24` | *Veri kaynağı yok* | Aktif |


### 🎴 AI Danışman Raporu Bileşeni Kartları (`rapor_ai_danisman_grubu`)
**Bileşen:** AI Danışman Raporu | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_ai_danisman.sayfa** | `raporlar_ai_danisman.sayfa` | `RPAD01` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.ai_danisman** | `raporlar_index.ai_danisman` | `RPI23` | *Veri kaynağı yok* | Aktif |


### 🎴 AI Sunum Oluşturucu Bileşeni Kartları (`rapor_ai_sunum_grubu`)
**Bileşen:** AI Sunum Oluşturucu | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_ai_sunum.sunum_hazir** | `raporlar_ai_sunum.sunum_hazir` | `RP155` | *Veri kaynağı yok* | Aktif |
| **raporlar_ai_sunum.sunumda_kullanilacak_veriler** | `raporlar_ai_sunum.sunumda_kullanilacak_veriler` | `RP156` | *Veri kaynağı yok* | Aktif |
| **raporlar_ai_sunum.slayt_yapisi** | `raporlar_ai_sunum.slayt_yapisi` | `RP157` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.ai_sunum** | `raporlar_index.ai_sunum` | `RPI11` | *Veri kaynağı yok* | Aktif |


### 🎴 Denetim Paketi Raporu Bileşeni Kartları (`rapor_audit_paketi_grubu`)
**Bileşen:** Denetim Paketi Raporu | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_audit_paketi.denetci_icin_hazir_pdf** | `raporlar_audit_paketi.denetci_icin_hazir_pdf` | `RP94` | *Veri kaynağı yok* | Aktif |
| **raporlar_audit_paketi.pdf_bolumleri** | `raporlar_audit_paketi.pdf_bolumleri` | `RP95` | *Veri kaynağı yok* | Aktif |
| **raporlar_audit_paketi.kullanim_amaci** | `raporlar_audit_paketi.kullanim_amaci` | `RP96` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.audit_paketi** | `raporlar_index.audit_paketi` | `RPI34` | *Veri kaynağı yok* | Aktif |


### 🎴 BI Bağlayıcı Bileşeni Kartları (`rapor_bi_connector_grubu`)
**Bileşen:** BI Bağlayıcı | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_bi_connector.tableau_baglanti_rehberi** | `raporlar_bi_connector.tableau_baglanti_rehberi` | `RP163` | *Veri kaynağı yok* | Aktif |
| **raporlar_bi_connector.excel_google_sheets** | `raporlar_bi_connector.excel_google_sheets` | `RP164` | *Veri kaynağı yok* | Aktif |
| **raporlar_bi_connector.power_bi_baglanti_rehberi** | `raporlar_bi_connector.power_bi_baglanti_rehberi` | `RP162` | *Veri kaynağı yok* | Aktif |
| **KPI Ölçümleri (CSV)** | `raporlar_bi_connector.kpi_olcumleri_csv` | `RP160` | *Veri kaynağı yok* | Aktif |
| **Stratejiler (JSON)** | `raporlar_bi_connector.stratejiler_json` | `RP161` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.bi_connector** | `raporlar_index.bi_connector` | `RPI40` | *Veri kaynağı yok* | Aktif |


### 🎴 Bireysel Hizalama Raporu Bileşeni Kartları (`rapor_bireysel_hizalama_grubu`)
**Bileşen:** Bireysel Hizalama Raporu | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_bireysel_hizalama.bireysel_pg_ler** | `raporlar_bireysel_hizalama.bireysel_pg_ler` | `RP23` | *Veri kaynağı yok* | Aktif |
| **Genel Hizalama** | `raporlar_bireysel_hizalama.genel_hizalama` | `RP20` | *Veri kaynağı yok* | Aktif |
| **PG'si Olan Kullanıcı** | `raporlar_bireysel_hizalama.pg_si_olan_kullanici` | `RP21` | *Veri kaynağı yok* | Aktif |
| **Toplam Kullanıcı** | `raporlar_bireysel_hizalama.toplam_kullanici` | `RP22` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.bireysel_hizalama** | `raporlar_index.bireysel_hizalama` | `RPI19` | *Veri kaynağı yok* | Aktif |


### 🎴 Toplu Bireysel Karne Üretimi Bileşeni Kartları (`rapor_bireysel_karne_batch_grubu`)
**Bileşen:** Toplu Bireysel Karne Üretimi | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_bireysel_karne_batch.toplu_uretim_zip** | `raporlar_bireysel_karne_batch.toplu_uretim_zip` | `RP177` | *Veri kaynağı yok* | Aktif |
| **raporlar_bireysel_karne_batch.her_karne_icerigi** | `raporlar_bireysel_karne_batch.her_karne_icerigi` | `RP178` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.bireysel_karne_batch** | `raporlar_index.bireysel_karne_batch` | `RPI35` | *Veri kaynağı yok* | Aktif |


### 🎴 Karbon Trend Raporu Bileşeni Kartları (`rapor_carbon_trend_grubu`)
**Bileşen:** Karbon Trend Raporu | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_carbon_trend.yillik_trend** | `raporlar_carbon_trend.yillik_trend` | `RP150` | *Veri kaynağı yok* | Aktif |
| **Metrik Sayısı** | `raporlar_carbon_trend.metrik_sayisi` | `RP146` | *Veri kaynağı yok* | Aktif |
| **Veri Yılı** | `raporlar_carbon_trend.veri_yili` | `RP147` | *Veri kaynağı yok* | Aktif |
| **Son Yıl Toplam** | `raporlar_carbon_trend.son_yil_toplam` | `RP148` | *Veri kaynağı yok* | Aktif |
| **İlk Yıla Göre** | `raporlar_carbon_trend.ilk_yila_gore` | `RP149` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.carbon_trend** | `raporlar_index.carbon_trend` | `RPI22` | *Veri kaynağı yok* | Aktif |


### 🎴 CFO Panosu Bileşeni Kartları (`rapor_cfo_dashboard_grubu`)
**Bileşen:** CFO Panosu | **Kart Sayısı:** 10

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_cfo_dashboard.en_buyuk_5_stratejik_girisim** | `raporlar_cfo_dashboard.en_buyuk_5_stratejik_girisim` | `RP119` | *Veri kaynağı yok* | Aktif |
| **raporlar_cfo_dashboard.durum_dagilimi** | `raporlar_cfo_dashboard.durum_dagilimi` | `RP120` | *Veri kaynağı yok* | Aktif |
| **raporlar_cfo_dashboard.strateji_bazli_butce_atifi** | `raporlar_cfo_dashboard.strateji_bazli_butce_atifi` | `RP121` | *Veri kaynağı yok* | Aktif |
| **Toplam Bütçe** | `raporlar_cfo_dashboard.toplam_butce` | `RP113` | *Veri kaynağı yok* | Aktif |
| **Harcanan** | `raporlar_cfo_dashboard.harcanan` | `RP114` | *Veri kaynağı yok* | Aktif |
| **Kalan** | `raporlar_cfo_dashboard.kalan` | `RP115` | *Veri kaynağı yok* | Aktif |
| **Bütçe Aşan** | `raporlar_cfo_dashboard.butce_asan` | `RP116` | *Veri kaynağı yok* | Aktif |
| **LLM Maliyet (30g)** | `raporlar_cfo_dashboard.llm_maliyet_30g` | `RP117` | *Veri kaynağı yok* | Aktif |
| **Recurring Task** | `raporlar_cfo_dashboard.recurring_task` | `RP118` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.cfo_dashboard** | `raporlar_index.cfo_dashboard` | `RPI26` | *Veri kaynağı yok* | Aktif |


### 🎴 CHRO Panosu Bileşeni Kartları (`rapor_chro_dashboard_grubu`)
**Bileşen:** CHRO Panosu | **Kart Sayısı:** 10

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_chro_dashboard.departman_dagilimi** | `raporlar_chro_dashboard.departman_dagilimi` | `RP135` | *Veri kaynağı yok* | Aktif |
| **raporlar_chro_dashboard.rol_dagilimi** | `raporlar_chro_dashboard.rol_dagilimi` | `RP136` | *Veri kaynağı yok* | Aktif |
| **raporlar_chro_dashboard.en_cok_bireysel_pg_sahibi_top_10** | `raporlar_chro_dashboard.en_cok_bireysel_pg_sahibi_top_10` | `RP137` | *Veri kaynağı yok* | Aktif |
| **raporlar_chro_dashboard.en_cok_surec_uyeligi_top_5** | `raporlar_chro_dashboard.en_cok_surec_uyeligi_top_5` | `RP138` | *Veri kaynağı yok* | Aktif |
| **Çalışan** | `raporlar_chro_dashboard.calisan` | `RP130` | *Veri kaynağı yok* | Aktif |
| **Departman** | `raporlar_chro_dashboard.departman` | `RP131` | *Veri kaynağı yok* | Aktif |
| **Bireysel PG** | `raporlar_chro_dashboard.bireysel_pg` | `RP132` | *Veri kaynağı yok* | Aktif |
| **Ort. PG / Kişi** | `raporlar_chro_dashboard.ort_pg_kisi` | `RP133` | *Veri kaynağı yok* | Aktif |
| **2FA Oranı** | `raporlar_chro_dashboard.2fa_orani` | `RP134` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.chro_dashboard** | `raporlar_index.chro_dashboard` | `RPI28` | *Veri kaynağı yok* | Aktif |


### 🎴 CMMI Isı Haritası Bileşeni Kartları (`rapor_cmmi_heatmap_grubu`)
**Bileşen:** CMMI Isı Haritası | **Kart Sayısı:** 9

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_cmmi_heatmap.ortalama_olgunluk** | `raporlar_cmmi_heatmap.ortalama_olgunluk` | `RP12` | *Veri kaynağı yok* | Aktif |
| **raporlar_cmmi_heatmap.seviye_dagilimi_ve_aciklamalar** | `raporlar_cmmi_heatmap.seviye_dagilimi_ve_aciklamalar` | `RP13` | *Veri kaynağı yok* | Aktif |
| **raporlar_cmmi_heatmap.surec_bazli_olgunluk** | `raporlar_cmmi_heatmap.surec_bazli_olgunluk` | `RP14` | *Veri kaynağı yok* | Aktif |
| **Ölçülen Süreç** | `raporlar_cmmi_heatmap.olculen_surec` | `RP07` | *Veri kaynağı yok* | Aktif |
| **Ölçülmemiş** | `raporlar_cmmi_heatmap.olculmemis` | `RP08` | *Veri kaynağı yok* | Aktif |
| **Ortalama Seviye** | `raporlar_cmmi_heatmap.ortalama_seviye` | `RP09` | *Veri kaynağı yok* | Aktif |
| **Optimize Eden (L5)** | `raporlar_cmmi_heatmap.optimize_eden_l5` | `RP10` | *Veri kaynağı yok* | Aktif |
| **Düşük Seviye (L1-L2)** | `raporlar_cmmi_heatmap.dusuk_seviye_l1_l2` | `RP11` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.cmmi_heatmap** | `raporlar_index.cmmi_heatmap` | `RPI17` | *Veri kaynağı yok* | Aktif |


### 🎴 COO Panosu Bileşeni Kartları (`rapor_coo_dashboard_grubu`)
**Bileşen:** COO Panosu | **Kart Sayısı:** 9

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_coo_dashboard.surec_saglik_dagilimi** | `raporlar_coo_dashboard.surec_saglik_dagilimi` | `RP127` | *Veri kaynağı yok* | Aktif |
| **raporlar_coo_dashboard.surecler_saglik_skoru** | `raporlar_coo_dashboard.surecler_saglik_skoru` | `RP128` | *Veri kaynağı yok* | Aktif |
| **raporlar_coo_dashboard.aktif_darbogazlar** | `raporlar_coo_dashboard.aktif_darbogazlar` | `RP129` | *Veri kaynağı yok* | Aktif |
| **Süreç** | `raporlar_coo_dashboard.surec` | `RP122` | *Veri kaynağı yok* | Aktif |
| **Ort. Sağlık** | `raporlar_coo_dashboard.ort_saglik` | `RP123` | *Veri kaynağı yok* | Aktif |
| **Geciken Faaliyet** | `raporlar_coo_dashboard.geciken_faaliyet` | `RP124` | *Veri kaynağı yok* | Aktif |
| **Aktif Darboğaz** | `raporlar_coo_dashboard.aktif_darbogaz` | `RP125` | *Veri kaynağı yok* | Aktif |
| **Ort. CMMI** | `raporlar_coo_dashboard.ort_cmmi` | `RP126` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.coo_dashboard** | `raporlar_index.coo_dashboard` | `RPI27` | *Veri kaynağı yok* | Aktif |


### 🎴 Departman Performans Raporu Bileşeni Kartları (`rapor_departman_performans_grubu`)
**Bileşen:** Departman Performans Raporu | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **Departman** | `raporlar_departman_performans.departman` | `RP01` | *Veri kaynağı yok* | Aktif |
| **raporlar_departman_performans.departman_karti** | `raporlar_departman_performans.departman_karti` | `RP04` | *Veri kaynağı yok* | Aktif |
| **Toplam Çalışan** | `raporlar_departman_performans.toplam_calisan` | `RP02` | *Veri kaynağı yok* | Aktif |
| **Toplam Bireysel PG** | `raporlar_departman_performans.toplam_bireysel_pg` | `RP03` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.departman_performans** | `raporlar_index.departman_performans` | `RPI06` | *Veri kaynağı yok* | Aktif |


### 🎴 Erken Uyarı Raporu Bileşeni Kartları (`rapor_early_warning_grubu`)
**Bileşen:** Erken Uyarı Raporu | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **Kontrol Edilen PG** | `raporlar_early_warning.kontrol_edilen_pg` | `RP72` | *Veri kaynağı yok* | Aktif |
| **Uyarı Sayısı** | `raporlar_early_warning.uyari_sayisi` | `RP73` | *Veri kaynağı yok* | Aktif |
| **raporlar_early_warning.uyari_listesi** | `raporlar_early_warning.uyari_listesi` | `RP75` | *Veri kaynağı yok* | Aktif |
| **Yüksek Öncelik** | `raporlar_early_warning.yuksek_oncelik` | `RP74` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.early_warning** | `raporlar_index.early_warning` | `RPI25` | *Veri kaynağı yok* | Aktif |


### 🎴 ESG Raporu Bileşeni Kartları (`rapor_esg_rapor_grubu`)
**Bileşen:** ESG Raporu | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_esg_rapor.yatirimci_denetci_hazir_pdf** | `raporlar_esg_rapor.yatirimci_denetci_hazir_pdf` | `RP175` | *Veri kaynağı yok* | Aktif |
| **raporlar_esg_rapor.rapor_icerigi** | `raporlar_esg_rapor.rapor_icerigi` | `RP176` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.esg_rapor** | `raporlar_index.esg_rapor` | `RPI33` | *Veri kaynağı yok* | Aktif |


### 🎴 ESG Yönetim Sayfası Bileşeni Kartları (`rapor_esg_yonetim_grubu`)
**Bileşen:** ESG Yönetim Sayfası | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_esg_yonetim.sayfa** | `raporlar_esg_yonetim.sayfa` | `RPEY01` | *Veri kaynağı yok* | Aktif |


### 🎴 Yıllar Arası Evrim Filmi Bileşeni Kartları (`rapor_evrim_filmi_grubu`)
**Bileşen:** Yıllar Arası Evrim Filmi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_evrim_filmi.yillar_arasi_evrim_filmi** | `raporlar_evrim_filmi.yillar_arasi_evrim_filmi` | `RP139` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.evrim_filmi** | `raporlar_index.evrim_filmi` | `RPI10` | *Veri kaynağı yok* | Aktif |


### 🎴 Hedef Revizyon Raporu Bileşeni Kartları (`rapor_hedef_revizyon_grubu`)
**Bileşen:** Hedef Revizyon Raporu | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_hedef_revizyon.yillara_gore_revizyon** | `raporlar_hedef_revizyon.yillara_gore_revizyon` | `RP18` | *Veri kaynağı yok* | Aktif |
| **raporlar_hedef_revizyon.revize_edilen_pg_ler** | `raporlar_hedef_revizyon.revize_edilen_pg_ler` | `RP19` | *Veri kaynağı yok* | Aktif |
| **Toplam Plan Dönemi** | `raporlar_hedef_revizyon.toplam_plan_donemi` | `RP15` | *Veri kaynağı yok* | Aktif |
| **Revizyon Yapılan Yıl** | `raporlar_hedef_revizyon.revizyon_yapilan_yil` | `RP16` | *Veri kaynağı yok* | Aktif |
| **Toplam Revizyon** | `raporlar_hedef_revizyon.toplam_revizyon` | `RP17` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.hedef_revizyon** | `raporlar_index.hedef_revizyon` | `RPI05` | *Veri kaynağı yok* | Aktif |


### 🎴 Hizalama Sankey Diyagramı Bileşeni Kartları (`rapor_hizalama_sankey_grubu`)
**Bileşen:** Hizalama Sankey Diyagramı | **Kart Sayısı:** 8

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **Ana Strateji** | `raporlar_hizalama_sankey.ana_strateji` | `RP165` | *Veri kaynağı yok* | Aktif |
| **Alt Strateji** | `raporlar_hizalama_sankey.alt_strateji` | `RP166` | *Veri kaynağı yok* | Aktif |
| **Süreç** | `raporlar_hizalama_sankey.surec` | `RP167` | *Veri kaynağı yok* | Aktif |
| **PG** | `raporlar_hizalama_sankey.pg` | `RP168` | *Veri kaynağı yok* | Aktif |
| **Bağlantı** | `raporlar_hizalama_sankey.baglanti` | `RP169` | *Veri kaynağı yok* | Aktif |
| **Hizalanmamış** | `raporlar_hizalama_sankey.hizalanmamis` | `RP170` | *Veri kaynağı yok* | Aktif |
| **raporlar_hizalama_sankey.akis_gorseli** | `raporlar_hizalama_sankey.akis_gorseli` | `RPHS01` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.hizalama_sankey** | `raporlar_index.hizalama_sankey` | `RPI04` | *Veri kaynağı yok* | Aktif |


### 🎴 2FA Güvenlik Raporu Bileşeni Kartları (`rapor_iki_fa_grubu`)
**Bileşen:** 2FA Güvenlik Raporu | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_iki_fa.2fa_dagilim** | `raporlar_iki_fa.2fa_dagilim` | `RP92` | *Veri kaynağı yok* | Aktif |
| **raporlar_iki_fa.2fa_si_olmayan_yoneticiler_kritik_guvenlik_acigi** | `raporlar_iki_fa.2fa_si_olmayan_yoneticiler_kritik_guvenlik_acigi` | `RP93` | *Veri kaynağı yok* | Aktif |
| **Toplam Kullanıcı** | `raporlar_iki_fa.toplam_kullanici` | `RP88` | *Veri kaynağı yok* | Aktif |
| **2FA Etkin** | `raporlar_iki_fa.2fa_etkin` | `RP89` | *Veri kaynağı yok* | Aktif |
| **2FA Yok** | `raporlar_iki_fa.2fa_yok` | `RP90` | *Veri kaynağı yok* | Aktif |
| **Etkinlik %** | `raporlar_iki_fa.etkinlik` | `RP91` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.iki_fa** | `raporlar_index.iki_fa` | `RPI21` | *Veri kaynağı yok* | Aktif |


### 🎴 Girişim Balon Grafiği Bileşeni Kartları (`rapor_initiative_bubble_grubu`)
**Bileşen:** Girişim Balon Grafiği | **Kart Sayısı:** 12

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_initiative_bubble.yatay_eksen_x** | `raporlar_initiative_bubble.yatay_eksen_x` | `RP24` | *Veri kaynağı yok* | Aktif |
| **raporlar_initiative_bubble.dikey_eksen_y** | `raporlar_initiative_bubble.dikey_eksen_y` | `RP25` | *Veri kaynağı yok* | Aktif |
| **raporlar_initiative_bubble.daire_boyutu** | `raporlar_initiative_bubble.daire_boyutu` | `RP26` | *Veri kaynağı yok* | Aktif |
| **raporlar_initiative_bubble.daire_rengi** | `raporlar_initiative_bubble.daire_rengi` | `RP27` | *Veri kaynağı yok* | Aktif |
| **raporlar_initiative_bubble.4_kadran_nasil_yorumlanir** | `raporlar_initiative_bubble.4_kadran_nasil_yorumlanir` | `RP28` | *Veri kaynağı yok* | Aktif |
| **raporlar_initiative_bubble.portfoy_balon_grafigi** | `raporlar_initiative_bubble.portfoy_balon_grafigi` | `RP33` | *Veri kaynağı yok* | Aktif |
| **raporlar_initiative_bubble.detay_tablosu** | `raporlar_initiative_bubble.detay_tablosu` | `RP34` | *Veri kaynağı yok* | Aktif |
| **Toplam Girişim** | `raporlar_initiative_bubble.toplam_girisim` | `RP29` | *Veri kaynağı yok* | Aktif |
| **Toplam Bütçe** | `raporlar_initiative_bubble.toplam_butce` | `RP30` | *Veri kaynağı yok* | Aktif |
| **Harcanan Bütçe** | `raporlar_initiative_bubble.harcanan_butce` | `RP31` | *Veri kaynağı yok* | Aktif |
| **Ortalama İlerleme** | `raporlar_initiative_bubble.ortalama_ilerleme` | `RP32` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.initiative_bubble** | `raporlar_index.initiative_bubble` | `RPI08` | *Veri kaynağı yok* | Aktif |


### 🎴 Girişim Yol Haritası Bileşeni Kartları (`rapor_initiative_roadmap_grubu`)
**Bileşen:** Girişim Yol Haritası | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_initiative_roadmap.stratejik_girisimler** | `raporlar_initiative_roadmap.stratejik_girisimler` | `RP38` | *Veri kaynağı yok* | Aktif |
| **Toplam Stratejik Girişim** | `raporlar_initiative_roadmap.toplam_stratejik_girisim` | `RP35` | *Veri kaynağı yok* | Aktif |
| **Yıl Aralığı** | `raporlar_initiative_roadmap.yil_araligi` | `RP36` | *Veri kaynağı yok* | Aktif |
| **Milestone** | `raporlar_initiative_roadmap.milestone` | `RP37` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.initiative_roadmap** | `raporlar_index.initiative_roadmap` | `RPI15` | *Veri kaynağı yok* | Aktif |


### 🎴 KV Çarpıklık Raporu Bileşeni Kartları (`rapor_kv_carpiklik_grubu`)
**Bileşen:** KV Çarpıklık Raporu | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_kv_carpiklik.ozet_kartlari** | `raporlar_kv_carpiklik.ozet_kartlari` | `RPKV01` | *Veri kaynağı yok* | Aktif |
| **raporlar_kv_carpiklik.agirlik_skor_karsilastirma** | `raporlar_kv_carpiklik.agirlik_skor_karsilastirma` | `RPKV02` | *Veri kaynağı yok* | Aktif |
| **raporlar_kv_carpiklik.detay_tablosu** | `raporlar_kv_carpiklik.detay_tablosu` | `RPKV03` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.kv_carpiklik** | `raporlar_index.kv_carpiklik` | `RPI03` | *Veri kaynağı yok* | Aktif |


### 🎴 ML Anomali Tespiti Bileşeni Kartları (`rapor_ml_anomaly_grubu`)
**Bileşen:** ML Anomali Tespiti | **Kart Sayısı:** 5

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_ml_anomaly.tespit_edilen_anomaliler** | `raporlar_ml_anomaly.tespit_edilen_anomaliler` | `RP79` | *Veri kaynağı yok* | Aktif |
| **Analiz Edilen PG** | `raporlar_ml_anomaly.analiz_edilen_pg` | `RP76` | *Veri kaynağı yok* | Aktif |
| **Yetersiz Veri (Atlandı)** | `raporlar_ml_anomaly.yetersiz_veri_atlandi` | `RP77` | *Veri kaynağı yok* | Aktif |
| **Anomali Tespit Edildi** | `raporlar_ml_anomaly.anomali_tespit_edildi` | `RP78` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.ml_anomaly** | `raporlar_index.ml_anomaly` | `RPI41` | *Veri kaynağı yok* | Aktif |


### 🎴 Mobile Hub Raporu Bileşeni Kartları (`rapor_mobile_grubu`)
**Bileşen:** Mobile Hub Raporu | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_mobile.mobile_hub** | `raporlar_mobile.mobile_hub` | `RP179` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.mobile** | `raporlar_index.mobile` | `RPI39` | *Veri kaynağı yok* | Aktif |


### 🎴 Muda (İsraf) Analizi Bileşeni Kartları (`rapor_muda_analizi_grubu`)
**Bileşen:** Muda (İsraf) Analizi | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_muda_analizi.7_muda_turu_bulgu_sayilari_aciklamalar** | `raporlar_muda_analizi.7_muda_turu_bulgu_sayilari_aciklamalar` | `RP64` | *Veri kaynağı yok* | Aktif |
| **raporlar_muda_analizi.bulgu_saptanan_surecler** | `raporlar_muda_analizi.bulgu_saptanan_surecler` | `RP65` | *Veri kaynağı yok* | Aktif |
| **Analiz Edilen Süreç** | `raporlar_muda_analizi.analiz_edilen_surec` | `RP61` | *Veri kaynağı yok* | Aktif |
| **Bulgu Olan Süreç** | `raporlar_muda_analizi.bulgu_olan_surec` | `RP62` | *Veri kaynağı yok* | Aktif |
| **Toplam Bulgu** | `raporlar_muda_analizi.toplam_bulgu` | `RP63` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.muda_analizi** | `raporlar_index.muda_analizi` | `RPI16` | *Veri kaynağı yok* | Aktif |


### 🎴 Doğal Dil Sorgulama Bileşeni Kartları (`rapor_nlp_query_grubu`)
**Bileşen:** Doğal Dil Sorgulama | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_nlp_query.hazir_sorular** | `raporlar_nlp_query.hazir_sorular` | `RP158` | *Veri kaynağı yok* | Aktif |
| **raporlar_nlp_query.cevap** | `raporlar_nlp_query.cevap` | `RP159` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.nlp_query** | `raporlar_index.nlp_query` | `RPI37` | *Veri kaynağı yok* | Aktif |


### 🎴 OKR Kademelendirme Raporu Bileşeni Kartları (`rapor_okr_cascade_grubu`)
**Bileşen:** OKR Kademelendirme Raporu | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **Objective** | `raporlar_okr_cascade.objective` | `RP50` | *Veri kaynağı yok* | Aktif |
| **Key Result** | `raporlar_okr_cascade.key_result` | `RP51` | *Veri kaynağı yok* | Aktif |
| **Ort. Tamamlanma** | `raporlar_okr_cascade.ort_tamamlanma` | `RP52` | *Veri kaynağı yok* | Aktif |
| **Plan Yılı** | `raporlar_okr_cascade.plan_yili` | `RP53` | *Veri kaynağı yok* | Aktif |
| **raporlar_okr_cascade.okr_aciklama** | `raporlar_okr_cascade.okr_aciklama` | `RPOC01` | *Veri kaynağı yok* | Aktif |
| **raporlar_okr_cascade.hizalama_listesi** | `raporlar_okr_cascade.hizalama_listesi` | `RPOC02` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.okr_cascade** | `raporlar_index.okr_cascade` | `RPI14` | *Veri kaynağı yok* | Aktif |


### 🎴 Onay Zinciri Raporu Bileşeni Kartları (`rapor_onay_zinciri_grubu`)
**Bileşen:** Onay Zinciri Raporu | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_onay_zinciri.stratejik_girisim_ler** | `raporlar_onay_zinciri.stratejik_girisim_ler` | `RP101` | *Veri kaynağı yok* | Aktif |
| **Toplam** | `raporlar_onay_zinciri.toplam` | `RP97` | *Veri kaynağı yok* | Aktif |
| **Onay Bekliyor** | `raporlar_onay_zinciri.onay_bekliyor` | `RP98` | *Veri kaynağı yok* | Aktif |
| **Onaylanmış** | `raporlar_onay_zinciri.onaylanmis` | `RP99` | *Veri kaynağı yok* | Aktif |
| **Reddedilen** | `raporlar_onay_zinciri.reddedilen` | `RP100` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.onay_zinciri** | `raporlar_index.onay_zinciri` | `RPI42` | *Veri kaynağı yok* | Aktif |


### 🎴 PG-Proje Etki Raporu Bileşeni Kartları (`rapor_pg_proje_etki_grubu`)
**Bileşen:** PG-Proje Etki Raporu | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_pg_proje_etki.nasil_okunur** | `raporlar_pg_proje_etki.nasil_okunur` | `RPPE01` | *Veri kaynağı yok* | Aktif |
| **raporlar_pg_proje_etki.ozet_kartlari** | `raporlar_pg_proje_etki.ozet_kartlari` | `RPPE02` | *Veri kaynağı yok* | Aktif |
| **raporlar_pg_proje_etki.proje_listesi** | `raporlar_pg_proje_etki.proje_listesi` | `RPPE03` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.pg_proje_etki** | `raporlar_index.pg_proje_etki` | `RPI02` | *Veri kaynağı yok* | Aktif |


### 🎴 Çeyreklik Review Raporu Bileşeni Kartları (`rapor_quarterly_review_grubu`)
**Bileşen:** Çeyreklik Review Raporu | **Kart Sayısı:** 8

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_quarterly_review.ceyreklik_review_toplantisi** | `raporlar_quarterly_review.ceyreklik_review_toplantisi` | `RP39` | *Veri kaynağı yok* | Aktif |
| **raporlar_quarterly_review.ai_yonetici_ozeti** | `raporlar_quarterly_review.ai_yonetici_ozeti` | `RP43` | *Veri kaynağı yok* | Aktif |
| **raporlar_quarterly_review.onerilen_agenda** | `raporlar_quarterly_review.onerilen_agenda` | `RP44` | *Veri kaynağı yok* | Aktif |
| **raporlar_quarterly_review.on_calisma_sorulari** | `raporlar_quarterly_review.on_calisma_sorulari` | `RP45` | *Veri kaynağı yok* | Aktif |
| **Ölçüm Hacmi (Q)** | `raporlar_quarterly_review.olcum_hacmi_q` | `RP40` | *Veri kaynağı yok* | Aktif |
| **Yeni Stratejik Girişim** | `raporlar_quarterly_review.yeni_stratejik_girisim` | `RP41` | *Veri kaynağı yok* | Aktif |
| **Tamamlanan Stratejik Girişim** | `raporlar_quarterly_review.tamamlanan_stratejik_girisim` | `RP42` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.quarterly_review** | `raporlar_index.quarterly_review` | `RPI29` | *Veri kaynağı yok* | Aktif |


### 🎴 Risk Isı Haritası Bileşeni Kartları (`rapor_risk_heatmap_grubu`)
**Bileşen:** Risk Isı Haritası | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **Kritik (≥15)** | `raporlar_risk_heatmap.kritik_15` | `RP69` | *Veri kaynağı yok* | Aktif |
| **raporlar_risk_heatmap.5_5_risk_matrisi** | `raporlar_risk_heatmap.5_5_risk_matrisi` | `RP70` | *Veri kaynağı yok* | Aktif |
| **raporlar_risk_heatmap.en_yuksek_rpn_ilk_10** | `raporlar_risk_heatmap.en_yuksek_rpn_ilk_10` | `RP71` | *Veri kaynağı yok* | Aktif |
| **Toplam Risk** | `raporlar_risk_heatmap.toplam_risk` | `RP66` | *Veri kaynağı yok* | Aktif |
| **Açık** | `raporlar_risk_heatmap.acik` | `RP67` | *Veri kaynağı yok* | Aktif |
| **Azaltıldı** | `raporlar_risk_heatmap.azaltildi` | `RP68` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.risk_heatmap** | `raporlar_index.risk_heatmap` | `RPI20` | *Veri kaynağı yok* | Aktif |


### 🎴 Sabah Özeti Raporu Bileşeni Kartları (`rapor_sabah_ozeti_grubu`)
**Bileşen:** Sabah Özeti Raporu | **Kart Sayısı:** 8

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_sabah_ozeti.son_veri_girisleri** | `raporlar_sabah_ozeti.son_veri_girisleri` | `RP60` | *Veri kaynağı yok* | Aktif |
| **Geciken Faaliyet** | `raporlar_sabah_ozeti.geciken_faaliyet` | `RP54` | *Veri kaynağı yok* | Aktif |
| **Bugün Bitiş** | `raporlar_sabah_ozeti.bugun_bitis` | `RP55` | *Veri kaynağı yok* | Aktif |
| **Önümüzdeki 7 Gün** | `raporlar_sabah_ozeti.onumuzdeki_7_gun` | `RP56` | *Veri kaynağı yok* | Aktif |
| **Son 7 Gün Tamamlanan** | `raporlar_sabah_ozeti.son_7_gun_tamamlanan` | `RP57` | *Veri kaynağı yok* | Aktif |
| **Bugün Ölçüm** | `raporlar_sabah_ozeti.bugun_olcum` | `RP58` | *Veri kaynağı yok* | Aktif |
| **Son 7 Gün Ölçüm** | `raporlar_sabah_ozeti.son_7_gun_olcum` | `RP59` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.sabah_ozeti** | `raporlar_index.sabah_ozeti` | `RPI09` | *Veri kaynağı yok* | Aktif |


### 🎴 Sektör Kıyaslama Raporu Bileşeni Kartları (`rapor_sektor_benchmark_grubu`)
**Bileşen:** Sektör Kıyaslama Raporu | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_sektor_benchmark.sektor_otomotiv_yan_sanayi** | `raporlar_sektor_benchmark.sektor_otomotiv_yan_sanayi` | `RP143` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektor_benchmark.sektor_ortalamalari** | `raporlar_sektor_benchmark.sektor_ortalamalari` | `RP144` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektor_benchmark.ai_sektor_degerlendirmesi** | `raporlar_sektor_benchmark.ai_sektor_degerlendirmesi` | `RP145` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.sektor_benchmark** | `raporlar_index.sektor_benchmark` | `RPI38` | *Veri kaynağı yok* | Aktif |


### 🎴 Sektörel Plan Paketleri Bileşeni Kartları (`rapor_sektorel_grubu`)
**Bileşen:** Sektörel Plan Paketleri | **Kart Sayısı:** 9

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_index.sektorel** | `raporlar_index.sektorel` | `RPI36` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel.sektor_otomotiv** | `raporlar_sektorel.sektor_otomotiv` | `RPSK01` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel.sektor_saglik** | `raporlar_sektorel.sektor_saglik` | `RPSK02` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel.sektor_finans** | `raporlar_sektorel.sektor_finans` | `RPSK03` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel.sektor_egitim** | `raporlar_sektorel.sektor_egitim` | `RPSK04` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel.sektor_kamu** | `raporlar_sektorel.sektor_kamu` | `RPSK05` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel.sektor_perakende** | `raporlar_sektorel.sektor_perakende` | `RPSK06` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel.sektor_insaat** | `raporlar_sektorel.sektor_insaat` | `RPSK07` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel.sektor_hizmet** | `raporlar_sektorel.sektor_hizmet` | `RPSK08` | *Veri kaynağı yok* | Aktif |


### 🎴 Strateji Hikayesi Raporu Bileşeni Kartları (`rapor_strateji_hikayesi_grubu`)
**Bileşen:** Strateji Hikayesi Raporu | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_strateji_hikayesi.hikaye** | `raporlar_strateji_hikayesi.hikaye` | `RP140` | *Veri kaynağı yok* | Aktif |
| **raporlar_strateji_hikayesi.yillik_snapshot** | `raporlar_strateji_hikayesi.yillik_snapshot` | `RP141` | *Veri kaynağı yok* | Aktif |
| **raporlar_strateji_hikayesi.kirilim_noktalari** | `raporlar_strateji_hikayesi.kirilim_noktalari` | `RP142` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.strateji_hikayesi** | `raporlar_index.strateji_hikayesi` | `RPI30` | *Veri kaynağı yok* | Aktif |


### 🎴 Stratejik Yıllık Rapor Bileşeni Kartları (`rapor_stratejik_yillik_grubu`)
**Bileşen:** Stratejik Yıllık Rapor | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_stratejik_yillik.premium_pdf_35_sayfa** | `raporlar_stratejik_yillik.premium_pdf_35_sayfa` | `RP173` | *Veri kaynağı yok* | Aktif |
| **raporlar_stratejik_yillik.bolum_yapisi** | `raporlar_stratejik_yillik.bolum_yapisi` | `RP174` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.stratejik_yillik** | `raporlar_index.stratejik_yillik` | `RPI31` | *Veri kaynağı yok* | Aktif |


### 🎴 Stratejik Hiyerarşi Sunburst Bileşeni Kartları (`rapor_sunburst_grubu`)
**Bileşen:** Stratejik Hiyerarşi Sunburst | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_sunburst.stratejik_hiyerarsi_sunburst** | `raporlar_sunburst.stratejik_hiyerarsi_sunburst` | `RP112` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.sunburst** | `raporlar_index.sunburst` | `RPI12` | *Veri kaynağı yok* | Aktif |


### 🎴 Veri Kalitesi Raporu Bileşeni Kartları (`rapor_veri_kalitesi_grubu`)
**Bileşen:** Veri Kalitesi Raporu | **Kart Sayısı:** 9

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_veri_kalitesi.kritik_pg_ler** | `raporlar_veri_kalitesi.kritik_pg_ler` | `RP85` | *Veri kaynağı yok* | Aktif |
| **raporlar_veri_kalitesi.orta_risk_pg_ler** | `raporlar_veri_kalitesi.orta_risk_pg_ler` | `RP86` | *Veri kaynağı yok* | Aktif |
| **raporlar_veri_kalitesi.surec_bazli_doluluk** | `raporlar_veri_kalitesi.surec_bazli_doluluk` | `RP87` | *Veri kaynağı yok* | Aktif |
| **Genel Skor** | `raporlar_veri_kalitesi.genel_skor` | `RP80` | *Veri kaynağı yok* | Aktif |
| **Toplam PG** | `raporlar_veri_kalitesi.toplam_pg` | `RP81` | *Veri kaynağı yok* | Aktif |
| **Kritik** | `raporlar_veri_kalitesi.kritik` | `RP82` | *Veri kaynağı yok* | Aktif |
| **Orta Risk** | `raporlar_veri_kalitesi.orta_risk` | `RP83` | *Veri kaynağı yok* | Aktif |
| **Sağlıklı** | `raporlar_veri_kalitesi.saglikli` | `RP84` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.veri_kalitesi** | `raporlar_index.veri_kalitesi` | `RPI01` | *Veri kaynağı yok* | Aktif |


### 🎴 VRIO Portföy Raporu Bileşeni Kartları (`rapor_vrio_portfoy_grubu`)
**Bileşen:** VRIO Portföy Raporu | **Kart Sayısı:** 12

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **Sürdürülebilir Rekabet Avantajı 0** | `raporlar_vrio_portfoy.surdurulebilir_rekabet_avantaji_0` | `RP107` | *Veri kaynağı yok* | Aktif |
| **Geçici Rekabet Avantajı 0** | `raporlar_vrio_portfoy.gecici_rekabet_avantaji_0` | `RP108` | *Veri kaynağı yok* | Aktif |
| **Kullanılmayan Avantaj 0** | `raporlar_vrio_portfoy.kullanilmayan_avantaj_0` | `RP109` | *Veri kaynağı yok* | Aktif |
| **Rekabet Paritesi 0** | `raporlar_vrio_portfoy.rekabet_paritesi_0` | `RP110` | *Veri kaynağı yok* | Aktif |
| **Rekabetçi Dezavantaj 0** | `raporlar_vrio_portfoy.rekabetci_dezavantaj_0` | `RP111` | *Veri kaynağı yok* | Aktif |
| **Toplam Kaynak** | `raporlar_vrio_portfoy.toplam_kaynak` | `RP102` | *Veri kaynağı yok* | Aktif |
| **Sürdürülebilir** | `raporlar_vrio_portfoy.surdurulebilir` | `RP103` | *Veri kaynağı yok* | Aktif |
| **Geçici** | `raporlar_vrio_portfoy.gecici` | `RP104` | *Veri kaynağı yok* | Aktif |
| **Kullanılmayan** | `raporlar_vrio_portfoy.kullanilmayan` | `RP105` | *Veri kaynağı yok* | Aktif |
| **Dezavantaj** | `raporlar_vrio_portfoy.dezavantaj` | `RP106` | *Veri kaynağı yok* | Aktif |
| **raporlar_vrio_portfoy.sayfa** | `raporlar_vrio_portfoy.sayfa` | `RPVP01` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.vrio_portfoy** | `raporlar_index.vrio_portfoy` | `RPI13` | *Veri kaynağı yok* | Aktif |


### 🎴 Yatırımcı Sunumu Bileşeni Kartları (`rapor_yatirimci_sunum_grubu`)
**Bileşen:** Yatırımcı Sunumu | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_yatirimci_sunum.pptx_sunum_16_9** | `raporlar_yatirimci_sunum.pptx_sunum_16_9` | `RP171` | *Veri kaynağı yok* | Aktif |
| **raporlar_yatirimci_sunum.slayt_yapisi** | `raporlar_yatirimci_sunum.slayt_yapisi` | `RP172` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.yatirimci_sunum** | `raporlar_index.yatirimci_sunum` | `RPI32` | *Veri kaynağı yok* | Aktif |


### 🎴 Yönetici Liderlik Raporu Bileşeni Kartları (`rapor_yonetici_liderlik_grubu`)
**Bileşen:** Yönetici Liderlik Raporu | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_yonetici_liderlik.yoneticiler_karti** | `raporlar_yonetici_liderlik.yoneticiler_karti` | `RP06` | *Veri kaynağı yok* | Aktif |
| **Yönetici Sayısı** | `raporlar_yonetici_liderlik.yonetici_sayisi` | `RP05` | *Veri kaynağı yok* | Aktif |
| **raporlar_index.yonetici_liderlik** | `raporlar_index.yonetici_liderlik` | `RPI07` | *Veri kaynağı yok* | Aktif |


### 🎴 Operasyon İstatistikleri Bileşeni Kartları (`rapor_operasyon_istatistik_grubu`)
**Bileşen:** Operasyon İstatistikleri | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_operasyon_istatistik.surecler** | `raporlar_operasyon_istatistik.surecler` | `RP49` | *Veri kaynağı yok* | Aktif |
| **Toplam Süreç** | `raporlar_operasyon_istatistik.toplam_surec` | `RP46` | *Veri kaynağı yok* | Aktif |
| **Toplam PG** | `raporlar_operasyon_istatistik.toplam_pg` | `RP47` | *Veri kaynağı yok* | Aktif |
| **Toplam Faaliyet** | `raporlar_operasyon_istatistik.toplam_faaliyet` | `RP48` | *Veri kaynağı yok* | Aktif |


### 🎴 Sektörel Paket Detayı Bileşeni Kartları (`rapor_sektorel_detay_grubu`)
**Bileşen:** Sektörel Paket Detayı | **Kart Sayısı:** 7

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **raporlar_sektorel_detay.ozet_istatistik** | `raporlar_sektorel_detay.ozet_istatistik` | `RPSD01` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel_detay.uyum_standartlari** | `raporlar_sektorel_detay.uyum_standartlari` | `RPSD02` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel_detay.stratejiler** | `raporlar_sektorel_detay.stratejiler` | `RPSD03` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel_detay.surecler** | `raporlar_sektorel_detay.surecler` | `RPSD04` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel_detay.riskler** | `raporlar_sektorel_detay.riskler` | `RPSD05` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel_detay.performans_gostergeleri** | `raporlar_sektorel_detay.performans_gostergeleri` | `RPSD06` | *Veri kaynağı yok* | Aktif |
| **raporlar_sektorel_detay.paketi_uygula_bilgi** | `raporlar_sektorel_detay.paketi_uygula_bilgi` | `RPSD07` | *Veri kaynağı yok* | Aktif |


### 🎴 Yapay Zeka Ayarları Bileşeni Kartları (`ai_ayarlari`)
**Bileşen:** Yapay Zeka Ayarları | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_ai_settings.kaynak_modu** | `sp_ai_settings.kaynak_modu` | `SPAI01` | *Veri kaynağı yok* | Aktif |
| **sp_ai_settings.api_anahtari_bilgileri** | `sp_ai_settings.api_anahtari_bilgileri` | `SPAI02` | *Veri kaynağı yok* | Aktif |


### 🎴 Mavi Okyanus Analizi Bileşeni Kartları (`mavi_okyanus_analizi`)
**Bileşen:** Mavi Okyanus Analizi | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_blue_ocean.tuval_listesi** | `sp_blue_ocean.tuval_listesi` | `SPBO01` | *Veri kaynağı yok* | Aktif |
| **sp_blue_ocean.tuval_detay** | `sp_blue_ocean.tuval_detay` | `SPBO02` | *Veri kaynağı yok* | Aktif |
| **sp_blue_ocean.deger_egrisi** | `sp_blue_ocean.deger_egrisi` | `SPBO03` | *Veri kaynağı yok* | Aktif |
| **sp_blue_ocean.errc_tablosu** | `sp_blue_ocean.errc_tablosu` | `SPBO04` | *Veri kaynağı yok* | Aktif |


### 🎴 Dengeli Karne (BSC) Bileşeni Kartları (`dengeli_karne_bsc`)
**Bileşen:** Dengeli Karne (BSC) | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_bsc.sayfa** | `sp_bsc.sayfa` | `SPBS01` | *Veri kaynağı yok* | Aktif |
| **sp_bsc.atanmamis_gostergeler** | `sp_bsc.atanmamis_gostergeler` | `SPBS02` | *Veri kaynağı yok* | Aktif |


### 🎴 Çeyreklik Değerlendirme Bileşeni Kartları (`ceyreklik_degerlendirme`)
**Bileşen:** Çeyreklik Değerlendirme | **Kart Sayısı:** 8

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_ceyreklik_review.donem_secici** | `sp_ceyreklik_review.donem_secici` | `SPQR01` | *Veri kaynağı yok* | Aktif |
| **sp_ceyreklik_review.pg_durumu** | `sp_ceyreklik_review.pg_durumu` | `SPQR02` | *Veri kaynağı yok* | Aktif |
| **sp_ceyreklik_review.strateji** | `sp_ceyreklik_review.strateji` | `SPQR03` | *Veri kaynağı yok* | Aktif |
| **sp_ceyreklik_review.okr_ilerleme** | `sp_ceyreklik_review.okr_ilerleme` | `SPQR04` | *Veri kaynağı yok* | Aktif |
| **sp_ceyreklik_review.faaliyet** | `sp_ceyreklik_review.faaliyet` | `SPQR05` | *Veri kaynağı yok* | Aktif |
| **sp_ceyreklik_review.risk** | `sp_ceyreklik_review.risk` | `SPQR06` | *Veri kaynağı yok* | Aktif |
| **sp_ceyreklik_review.anomali** | `sp_ceyreklik_review.anomali` | `SPQR07` | *Veri kaynağı yok* | Aktif |
| **sp_ceyreklik_review.aksiyon_onerileri** | `sp_ceyreklik_review.aksiyon_onerileri` | `SPQR08` | *Veri kaynağı yok* | Aktif |


### 🎴 Stratejik Plan Dönemleri Bileşeni Kartları (`sp_plan_donemleri`)
**Bileşen:** Stratejik Plan Dönemleri | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_donemler.bos_durum** | `sp_donemler.bos_durum` | `SPDN01` | *Veri kaynağı yok* | Aktif |
| **sp_donemler.aktif_donem** | `sp_donemler.aktif_donem` | `SPDN02` | *Veri kaynağı yok* | Aktif |
| **sp_donemler.tum_donemler** | `sp_donemler.tum_donemler` | `SPDN03` | *Veri kaynağı yok* | Aktif |
| **sp_donemler.donem_karsilastir** | `sp_donemler.donem_karsilastir` | `SPDN04` | *Veri kaynağı yok* | Aktif |


### 🎴 SP Yönetici Paneli Bileşeni Kartları (`sp_yonetici_paneli`)
**Bileşen:** SP Yönetici Paneli | **Kart Sayısı:** 13

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_exec_dashboard.ai_yonetici_ozeti** | `sp_exec_dashboard.ai_yonetici_ozeti` | `SPED01` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.saglik_skoru** | `sp_exec_dashboard.saglik_skoru` | `SPED02` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.pg_hedef_ustu** | `sp_exec_dashboard.pg_hedef_ustu` | `SPED03` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.girisim_sagligi** | `sp_exec_dashboard.girisim_sagligi` | `SPED04` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.gecikmis_faaliyet** | `sp_exec_dashboard.gecikmis_faaliyet` | `SPED05` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.kritik_risk** | `sp_exec_dashboard.kritik_risk` | `SPED06` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.yuksek_anomali** | `sp_exec_dashboard.yuksek_anomali` | `SPED07` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.aktif_tetikleyici** | `sp_exec_dashboard.aktif_tetikleyici` | `SPED08` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.kvektor_gelisimi** | `sp_exec_dashboard.kvektor_gelisimi` | `SPED09` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.aylik_saglik_trendi** | `sp_exec_dashboard.aylik_saglik_trendi` | `SPED10` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.strateji_siralamasi** | `sp_exec_dashboard.strateji_siralamasi` | `SPED11` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.otomatik_vurgular** | `sp_exec_dashboard.otomatik_vurgular` | `SPED12` | *Veri kaynağı yok* | Aktif |
| **sp_exec_dashboard.ai_pivot_onerileri** | `sp_exec_dashboard.ai_pivot_onerileri` | `SPED13` | *Veri kaynağı yok* | Aktif |


### 🎴 Stratejik Girişimler Bileşeni Kartları (`stratejik_girisimler`)
**Bileşen:** Stratejik Girişimler | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_initiatives.girisim_listesi** | `sp_initiatives.girisim_listesi` | `SPIN01` | *Veri kaynağı yok* | Aktif |


### 🎴 Yapay Zeka Kullanım Raporu Bileşeni Kartları (`ai_kullanim_raporu`)
**Bileşen:** Yapay Zeka Kullanım Raporu | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_llm_usage.kota_ozeti** | `sp_llm_usage.kota_ozeti` | `SPLU01` | *Veri kaynağı yok* | Aktif |
| **sp_llm_usage.son_cagrilar** | `sp_llm_usage.son_cagrilar` | `SPLU02` | *Veri kaynağı yok* | Aktif |


### 🎴 OKR Yönetimi Bileşeni Kartları (`okr_yonetimi`)
**Bileşen:** OKR Yönetimi | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_okr.ozet** | `sp_okr.ozet` | `SPOK01` | *Veri kaynağı yok* | Aktif |
| **sp_okr.hedef_karti** | `sp_okr.hedef_karti` | `SPOK02` | *Veri kaynağı yok* | Aktif |


### 🎴 Yeniden Planlama Tetikleyicileri Bileşeni Kartları (`yeniden_planlama_tetikleyicileri`)
**Bileşen:** Yeniden Planlama Tetikleyicileri | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_replan_triggers.aktif_tetikleyiciler** | `sp_replan_triggers.aktif_tetikleyiciler` | `SPRT01` | *Veri kaynağı yok* | Aktif |
| **sp_replan_triggers.son_ateslemeler** | `sp_replan_triggers.son_ateslemeler` | `SPRT02` | *Veri kaynağı yok* | Aktif |


### 🎴 Senaryo Planlama Bileşeni Kartları (`senaryo_planlama`)
**Bileşen:** Senaryo Planlama | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_scenarios.senaryo_olustur** | `sp_scenarios.senaryo_olustur` | `SPSC01` | *Veri kaynağı yok* | Aktif |
| **sp_scenarios.senaryo_listesi** | `sp_scenarios.senaryo_listesi` | `SPSC02` | *Veri kaynağı yok* | Aktif |
| **sp_scenarios_kiyas.secim_listesi** | `sp_scenarios_kiyas.secim_listesi` | `SPSK01` | *Veri kaynağı yok* | Aktif |
| **sp_scenarios_kiyas.vizyon_skoru_karsilastirma** | `sp_scenarios_kiyas.vizyon_skoru_karsilastirma` | `SPSK02` | *Veri kaynağı yok* | Aktif |


### 🎴 Yeni Plan Yılı Sihirbazı Bileşeni Kartları (`yeni_plan_yili_sihirbazi`)
**Bileşen:** Yeni Plan Yılı Sihirbazı | **Kart Sayısı:** 3

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_sihirbaz_yeni_yil.yil_secimi** | `sp_sihirbaz_yeni_yil.yil_secimi` | `SPWZ01` | *Veri kaynağı yok* | Aktif |
| **sp_sihirbaz_yeni_yil.onizleme** | `sp_sihirbaz_yeni_yil.onizleme` | `SPWZ02` | *Veri kaynağı yok* | Aktif |
| **sp_sihirbaz_yeni_yil.sonuc** | `sp_sihirbaz_yeni_yil.sonuc` | `SPWZ03` | *Veri kaynağı yok* | Aktif |


### 🎴 Strateji-Proje Hizalama Matrisi Bileşeni Kartları (`strateji_proje_hizalama_matrisi`)
**Bileşen:** Strateji-Proje Hizalama Matrisi | **Kart Sayısı:** 8

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_strategy_project_matrix.nasil_okunur** | `sp_strategy_project_matrix.nasil_okunur` | `SPSM01` | *Veri kaynağı yok* | Aktif |
| **sp_strategy_project_matrix.hizalama_matrisi** | `sp_strategy_project_matrix.hizalama_matrisi` | `SPSM02` | *Veri kaynağı yok* | Aktif |
| **sp_strategy_project_matrix.ozet_strateji** | `sp_strategy_project_matrix.ozet_strateji` | `SPSM03` | *Veri kaynağı yok* | Aktif |
| **sp_strategy_project_matrix.ozet_proje** | `sp_strategy_project_matrix.ozet_proje` | `SPSM04` | *Veri kaynağı yok* | Aktif |
| **sp_strategy_project_matrix.ozet_en_guclu_hizalama** | `sp_strategy_project_matrix.ozet_en_guclu_hizalama` | `SPSM05` | *Veri kaynağı yok* | Aktif |
| **sp_strategy_project_matrix.ozet_hizalama_kapsama** | `sp_strategy_project_matrix.ozet_hizalama_kapsama` | `SPSM06` | *Veri kaynağı yok* | Aktif |
| **sp_strategy_project_matrix.hizalanmamis_projeler** | `sp_strategy_project_matrix.hizalanmamis_projeler` | `SPSM07` | *Veri kaynağı yok* | Aktif |
| **sp_strategy_project_matrix.stratejisi_olmayan_projeler** | `sp_strategy_project_matrix.stratejisi_olmayan_projeler` | `SPSM08` | *Veri kaynağı yok* | Aktif |


### 🎴 Strateji Haritası Bileşeni Kartları (`strateji_haritasi`)
**Bileşen:** Strateji Haritası | **Kart Sayısı:** 6

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_strateji_haritasi.ana_strateji** | `sp_strateji_haritasi.ana_strateji` | `SP14` | *Veri kaynağı yok* | Aktif |
| **sp_strateji_haritasi.alt_strateji** | `sp_strateji_haritasi.alt_strateji` | `SP15` | *Veri kaynağı yok* | Aktif |
| **sp_strateji_haritasi.surec** | `sp_strateji_haritasi.surec` | `SP16` | *Veri kaynağı yok* | Aktif |
| **sp_strateji_haritasi.pg** | `sp_strateji_haritasi.pg` | `SP17` | *Veri kaynağı yok* | Aktif |
| **sp_strateji_haritasi.str_girisim** | `sp_strateji_haritasi.str_girisim` | `SP18` | *Veri kaynağı yok* | Aktif |
| **sp_strateji_haritasi.strateji_haritasi** | `sp_strateji_haritasi.strateji_haritasi` | `SP19` | *Veri kaynağı yok* | Aktif |


### 🎴 Plan Şablonları Bileşeni Kartları (`plan_sablonlari`)
**Bileşen:** Plan Şablonları | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_templates.sablon_karti** | `sp_templates.sablon_karti` | `SPTM01` | *Veri kaynağı yok* | Aktif |


### 🎴 Savaş Odası TV Panosu Bileşeni Kartları (`savas_odasi_tv_panosu`)
**Bileşen:** Savaş Odası TV Panosu | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_tv.sayfa** | `sp_tv.sayfa` | `SPTV01` | *Veri kaynağı yok* | Aktif |


### 🎴 Hoshin X-Matrix Bileşeni Kartları (`hoshin_x_matrix`)
**Bileşen:** Hoshin X-Matrix | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp_xmatrix.sayfa** | `sp_xmatrix.sayfa` | `SPXM01` | *Veri kaynağı yok* | Aktif |


### 🎴 Anomali Tespiti Bileşeni Kartları (`anomali_tespiti`)
**Bileşen:** Anomali Tespiti | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **analiz.anomali_ozet** | `analiz.anomali_ozet` | `AN05` | *Veri kaynağı yok* | Aktif |
| **analiz.anomali_listesi** | `analiz.anomali_listesi` | `AN08` | *Veri kaynağı yok* | Aktif |


### 🎴 Süreç Sağlık Skoru Bileşeni Kartları (`surec_saglik_skoru`)
**Bileşen:** Süreç Sağlık Skoru | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **analiz.saglik_skoru** | `analiz.saglik_skoru` | `AN02` | *Veri kaynağı yok* | Aktif |


### 🎴 Trend ve Tahmin Analizi Bileşeni Kartları (`trend_tahmin_analizi`)
**Bileşen:** Trend ve Tahmin Analizi | **Kart Sayısı:** 4

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **analiz.trend_yonu** | `analiz.trend_yonu` | `AN03` | *Veri kaynağı yok* | Aktif |
| **analiz.tahmin_ozet** | `analiz.tahmin_ozet` | `AN04` | *Veri kaynağı yok* | Aktif |
| **analiz.trend_grafigi** | `analiz.trend_grafigi` | `AN06` | *Veri kaynağı yok* | Aktif |
| **analiz.tahmin_grafigi** | `analiz.tahmin_grafigi` | `AN07` | *Veri kaynağı yok* | Aktif |


### 🎴 API Erişimi Bileşeni Kartları (`api_erisimi`)
**Bileşen:** API Erişimi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **api_docs.endpoint_listesi** | `api_docs.endpoint_listesi` | `APD01` | *Veri kaynağı yok* | Aktif |


### 🎴 Kurum Takvimi Bileşeni Kartları (`kurum_takvimi`)
**Bileşen:** Kurum Takvimi | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **calendar.kurum_takvimi** | `calendar.kurum_takvimi` | `CA01` | *Veri kaynağı yok* | Aktif |


### 🎴 K-Vektör Vizyon Skoru Bileşeni Kartları (`k_vektor_vizyon_skoru`)
**Bileşen:** K-Vektör Vizyon Skoru | **Kart Sayısı:** 2

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp.k_vektor_vizyon** | `sp.k_vektor_vizyon` | `SP03` | *Veri kaynağı yok* | Aktif |
| **kurum_ayarlar.k_vektor** | `kurum_ayarlar.k_vektor` | `KUA03` | *Veri kaynağı yok* | Aktif |


### 🎴 Bireysel Hedef Hizalama Bileşeni Kartları (`bireysel_hedef_hizalama`)
**Bileşen:** Bireysel Hedef Hizalama | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp.bireysel_hedefler** | `sp.bireysel_hedefler` | `SP13` | *Veri kaynağı yok* | Aktif |


### 🎴 Vizyon Kartı Bileşeni Kartları (`vizyon_karti`)
**Bileşen:** Vizyon Kartı | **Kart Sayısı:** 1

| Kart Adı | Kart Kodu | Kısa Kod (Short ID) | Veri Kaynakları (Data Sources) | Durum |
| :--- | :--- | :--- | :--- | :--- |
| **sp.vizyon** | `sp.vizyon` | `SP08` | *Veri kaynağı yok* | Aktif |

