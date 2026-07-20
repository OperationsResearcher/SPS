# Kokpitim Frontend Arayüz ve Stil Varlıkları Envanter Raporu

**Analiz Tarihi:** 2026-06-09  
**Rapor Amacı:** Kokpitim uygulamasındaki tüm CSS, JavaScript ve HTML şablon varlıklarının, üçüncü parti kütüphanelerin ve şablon yapılarının detaylı envanteri.  

## 📊 Genel Özet

| Metrik | Global Varlıklar (`static/`) | Modüler Varlıklar (`ui/`) | Toplam |
| :--- | :---: | :---: | :---: |
| **Dosya Sayısı** | 106 | 253 | 359 |
| **Satır Sayısı** | 29,382 | 53,494 | 82,876 |
| **Dosya Boyutu (KB)** | 2622.1 KB | 2563.2 KB | 5185.3 KB |

## 🌐 Üçüncü Parti Kütüphaneler (`static/vendor/`)

Kokpitim, CDN bağımlılıkları olmadan tamamen çevrimdışı (offline) çalışabilecek şekilde tasarlanmıştır. Bu amaçla kullanılan yerel kütüphaneler:

- **Bootstrap & Bootstrap Icons**: Arayüz düzeni ve sistem simgeleri
- **Font Awesome**: Gelişmiş simge kütüphanesi
- **jQuery**: Klasik JS etkileşimleri ve DOM manipülasyonu
- **Chart.js**: Performans ve karne grafiklerinin görselleştirilmesi
- **SweetAlert2**: Sistem içi şık bildirimler ve onay pencereleri (Varsayılan alert/confirm yasaktır)
- **Tailwind CSS & Alpine.js**: Yeni nesil mikro arayüzün temel taşları

## 📦 Küresel Varlıklar Dağılımı (`static/`)

| Dosya Yolu | Uzantı | Satır Sayısı | Dosya Boyutu |
| :--- | :---: | :---: | :--- |
| [`static\vendor\vis-network\vis-network.min.js`](file:///c:/kokpitim/static/vendor/vis-network/vis-network.min.js) | `.js` | 34 | 672.8 KB |
| [`static\vendor\bootstrap\bootstrap.min.css`](file:///c:/kokpitim/static/vendor/bootstrap/bootstrap.min.css) | `.css` | 6 | 227.5 KB |
| [`static\vendor\vis-network\vis-network.min.css`](file:///c:/kokpitim/static/vendor/vis-network/vis-network.min.css) | `.css` | 2 | 215.1 KB |
| [`static\vendor\chartjs\chart.umd.js`](file:///c:/kokpitim/static/vendor/chartjs/chart.umd.js) | `.js` | 14 | 200.2 KB |
| [`static\js\admin_panel.js`](file:///c:/kokpitim/static/js/admin_panel.js) | `.js` | 3,583 | 171.2 KB |
| [`static\js\surec_karnesi.js`](file:///c:/kokpitim/static/js/surec_karnesi.js) | `.js` | 4,178 | 167.7 KB |
| [`static\vendor\fontawesome\all.min.css`](file:///c:/kokpitim/static/vendor/fontawesome/all.min.css) | `.css` | 9 | 99.6 KB |
| [`static\vendor\bootstrap-icons\bootstrap-icons.css`](file:///c:/kokpitim/static/vendor/bootstrap-icons/bootstrap-icons.css) | `.css` | 2,078 | 98.0 KB |
| [`static\vendor\jquery\jquery-3.7.1.min.js`](file:///c:/kokpitim/static/vendor/jquery/jquery-3.7.1.min.js) | `.js` | 2 | 85.5 KB |
| [`static\js\surec_panel.js`](file:///c:/kokpitim/static/js/surec_panel.js) | `.js` | 3,215 | 83.8 KB |
| [`static\js\process_karne.js`](file:///c:/kokpitim/static/js/process_karne.js) | `.js` | 1,634 | 80.1 KB |
| [`static\vendor\bootstrap\bootstrap.bundle.min.js`](file:///c:/kokpitim/static/vendor/bootstrap/bootstrap.bundle.min.js) | `.js` | 7 | 78.8 KB |
| [`static\js\kurum_panel.js`](file:///c:/kokpitim/static/js/kurum_panel.js) | `.js` | 823 | 32.3 KB |
| [`static\css\main.css`](file:///c:/kokpitim/static/css/main.css) | `.css` | 798 | 22.8 KB |
| [`static\marketing\css\marketing.css`](file:///c:/kokpitim/static/marketing/css/marketing.css) | `.css` | 323 | 20.5 KB |
| [`static\js\tenant_dashboard.js`](file:///c:/kokpitim/static/js/tenant_dashboard.js) | `.js` | 435 | 20.4 KB |
| [`static\js\process_panel.js`](file:///c:/kokpitim/static/js/process_panel.js) | `.js` | 319 | 15.1 KB |
| [`static\js\strategy_dynamic_flow.js`](file:///c:/kokpitim/static/js/strategy_dynamic_flow.js) | `.js` | 469 | 14.4 KB |
| [`static\css\modern-premium.css`](file:///c:/kokpitim/static/css/modern-premium.css) | `.css` | 601 | 13.4 KB |
| [`static\css\professional.css`](file:///c:/kokpitim/static/css/professional.css) | `.css` | 506 | 11.5 KB |
| [`static\js\profile.js`](file:///c:/kokpitim/static/js/profile.js) | `.js` | 281 | 11.1 KB |
| [`static\js\modules\notification-manager.js`](file:///c:/kokpitim/static/js/modules/notification-manager.js) | `.js` | 340 | 11.0 KB |
| [`static\prototypes\kontrol-common.js`](file:///c:/kokpitim/static/prototypes/kontrol-common.js) | `.js` | 259 | 10.3 KB |
| [`static\js\admin_users.js`](file:///c:/kokpitim/static/js/admin_users.js) | `.js` | 220 | 9.0 KB |
| [`static\css\auth.css`](file:///c:/kokpitim/static/css/auth.css) | `.css` | 375 | 8.7 KB |
| [`static\js\modules\chart-utils.js`](file:///c:/kokpitim/static/js/modules/chart-utils.js) | `.js` | 276 | 8.5 KB |
| [`static\js\components\dashboard-builder.js`](file:///c:/kokpitim/static/js/components/dashboard-builder.js) | `.js` | 245 | 8.2 KB |
| [`static\css\login.css`](file:///c:/kokpitim/static/css/login.css) | `.css` | 286 | 7.9 KB |
| [`static\js\loading.js`](file:///c:/kokpitim/static/js/loading.js) | `.js` | 233 | 7.6 KB |
| [`static\js\auth_profile.js`](file:///c:/kokpitim/static/js/auth_profile.js) | `.js` | 171 | 7.2 KB |
| *...ve 76 dosya daha* | | | |

---

## 🧩 Modüler Varlıklar Dağılımı (`ui/`)

| Dosya Yolu | Uzantı | Satır Sayısı | Dosya Boyutu |
| :--- | :---: | :---: | :--- |
| [`ui\static\platform\js\surec.js`](file:///c:/kokpitim/ui/static/platform/js/surec.js) | `.js` | 3,775 | 152.7 KB |
| [`ui\static\platform\vendor\fontawesome\all.min.css`](file:///c:/kokpitim/ui/static/platform/vendor/fontawesome/all.min.css) | `.css` | 9 | 100.2 KB |
| [`ui\static\platform\js\k_rapor.js`](file:///c:/kokpitim/ui/static/platform/js/k_rapor.js) | `.js` | 1,688 | 89.6 KB |
| [`ui\static\platform\js\k_radar_ks.js`](file:///c:/kokpitim/ui/static/platform/js/k_radar_ks.js) | `.js` | 1,474 | 79.4 KB |
| [`ui\templates\platform\k_rapor\index.html`](file:///c:/kokpitim/ui/templates/platform/k_rapor/index.html) | `.html` | 956 | 60.9 KB |
| [`ui\templates\platform\surec\karne.html`](file:///c:/kokpitim/ui/templates/platform/surec/karne.html) | `.html` | 1,101 | 59.8 KB |
| [`ui\templates\platform\sp\exec_dashboard.html`](file:///c:/kokpitim/ui/templates/platform/sp/exec_dashboard.html) | `.html` | 931 | 52.4 KB |
| [`ui\templates\platform\kurum\index.html`](file:///c:/kokpitim/ui/templates/platform/kurum/index.html) | `.html` | 732 | 51.8 KB |
| [`ui\static\platform\css\surec.css`](file:///c:/kokpitim/ui/static/platform/css/surec.css) | `.css` | 2,936 | 49.3 KB |
| [`ui\static\platform\js\calendar_quick_create.js`](file:///c:/kokpitim/ui/static/platform/js/calendar_quick_create.js) | `.js` | 1,137 | 47.6 KB |
| [`ui\static\platform\js\admin.js`](file:///c:/kokpitim/ui/static/platform/js/admin.js) | `.js` | 846 | 43.4 KB |
| [`ui\templates\platform\surec\index.html`](file:///c:/kokpitim/ui/templates/platform/surec/index.html) | `.html` | 737 | 41.5 KB |
| [`ui\templates\platform\sp\index.html`](file:///c:/kokpitim/ui/templates/platform/sp/index.html) | `.html` | 629 | 40.1 KB |
| [`ui\static\platform\js\pg_tablo_modal.js`](file:///c:/kokpitim/ui/static/platform/js/pg_tablo_modal.js) | `.js` | 882 | 38.8 KB |
| [`ui\templates\platform\sp\tv.html`](file:///c:/kokpitim/ui/templates/platform/sp/tv.html) | `.html` | 579 | 38.6 KB |
| [`ui\templates\platform\project\list.html`](file:///c:/kokpitim/ui/templates/platform/project/list.html) | `.html` | 632 | 38.3 KB |
| [`ui\templates\platform\masaustu\index.html`](file:///c:/kokpitim/ui/templates/platform/masaustu/index.html) | `.html` | 626 | 37.8 KB |
| [`ui\static\platform\js\k_radar.js`](file:///c:/kokpitim/ui/static/platform/js/k_radar.js) | `.js` | 875 | 37.6 KB |
| [`ui\templates\platform\base.html`](file:///c:/kokpitim/ui/templates/platform/base.html) | `.html` | 617 | 36.0 KB |
| [`ui\static\platform\css\components.css`](file:///c:/kokpitim/ui/static/platform/css/components.css) | `.css` | 1,446 | 35.5 KB |
| [`ui\templates\platform\admin\hata_kontrolu.html`](file:///c:/kokpitim/ui/templates/platform/admin/hata_kontrolu.html) | `.html` | 504 | 31.0 KB |
| [`ui\static\platform\js\surec_vgs.js`](file:///c:/kokpitim/ui/static/platform/js/surec_vgs.js) | `.js` | 766 | 28.0 KB |
| [`ui\static\platform\js\kurum.js`](file:///c:/kokpitim/ui/static/platform/js/kurum.js) | `.js` | 701 | 27.0 KB |
| [`ui\static\platform\js\tool_info_modal.js`](file:///c:/kokpitim/ui/static/platform/js/tool_info_modal.js) | `.js` | 399 | 26.9 KB |
| [`ui\templates\platform\sp\strateji_haritasi.html`](file:///c:/kokpitim/ui/templates/platform/sp/strateji_haritasi.html) | `.html` | 572 | 25.4 KB |
| [`ui\static\platform\js\sp.js`](file:///c:/kokpitim/ui/static/platform/js/sp.js) | `.js` | 566 | 24.8 KB |
| [`ui\templates\platform\k_radar\hub.html`](file:///c:/kokpitim/ui/templates/platform/k_radar/hub.html) | `.html` | 237 | 22.4 KB |
| [`ui\templates\platform\k_radar\ks.html`](file:///c:/kokpitim/ui/templates/platform/k_radar/ks.html) | `.html` | 409 | 21.4 KB |
| [`ui\templates\platform\sp\okr.html`](file:///c:/kokpitim/ui/templates/platform/sp/okr.html) | `.html` | 438 | 21.0 KB |
| [`ui\templates\platform\sp\blue_ocean.html`](file:///c:/kokpitim/ui/templates/platform/sp/blue_ocean.html) | `.html` | 403 | 20.8 KB |
| *...ve 223 dosya daha* | | | |

---

## ⚠️ Kritik Çakışan Şablonlar (Duplicate Templates)

> [!WARNING]
> Klasik şablon dizini (`templates/`) ile mikro modüler şablon dizini (`ui/templates/platform/`) arasında çakışan (aynı isimli) dosyalar bulunmaktadır. Bu durum tasarım bütünlüğünün korunmasında ve hata tespitlerinde karışıklığa yol açabilir. Çakışan şablonlar şunlardır:

- 📁 **`403.html`**
  - Klasik Yol: [`templates/403.html`](file:///c:/kokpitim/templates/403.html)
  - Mikro Yol: [`ui/templates/platform/403.html`](file:///c:/kokpitim/ui/templates/platform/403.html)
- 📁 **`404.html`**
  - Klasik Yol: [`templates/404.html`](file:///c:/kokpitim/templates/404.html)
  - Mikro Yol: [`ui/templates/platform/404.html`](file:///c:/kokpitim/ui/templates/platform/404.html)
- 📁 **`500.html`**
  - Klasik Yol: [`templates/500.html`](file:///c:/kokpitim/templates/500.html)
  - Mikro Yol: [`ui/templates/platform/500.html`](file:///c:/kokpitim/ui/templates/platform/500.html)
- 📁 **`_tool_info_modal.html`**
  - Klasik Yol: [`templates/_tool_info_modal.html`](file:///c:/kokpitim/templates/_tool_info_modal.html)
  - Mikro Yol: [`ui/templates/platform/_tool_info_modal.html`](file:///c:/kokpitim/ui/templates/platform/_tool_info_modal.html)
- 📁 **`ai_coach.html`**
  - Klasik Yol: [`templates/ai_coach.html`](file:///c:/kokpitim/templates/ai_coach.html)
  - Mikro Yol: [`ui/templates/platform/ai_coach.html`](file:///c:/kokpitim/ui/templates/platform/ai_coach.html)
- 📁 **`base.html`**
  - Klasik Yol: [`templates/base.html`](file:///c:/kokpitim/templates/base.html)
  - Mikro Yol: [`ui/templates/platform/base.html`](file:///c:/kokpitim/ui/templates/platform/base.html)
- 📁 **`calendar.html`**
  - Klasik Yol: [`templates/calendar.html`](file:///c:/kokpitim/templates/calendar.html)
  - Mikro Yol: [`ui/templates/platform/calendar.html`](file:///c:/kokpitim/ui/templates/platform/calendar.html)
- 📁 **`detail.html`**
  - Klasik Yol: [`templates/detail.html`](file:///c:/kokpitim/templates/detail.html)
  - Mikro Yol: [`ui/templates/platform/detail.html`](file:///c:/kokpitim/ui/templates/platform/detail.html)
- 📁 **`dynamic_flow.html`**
  - Klasik Yol: [`templates/dynamic_flow.html`](file:///c:/kokpitim/templates/dynamic_flow.html)
  - Mikro Yol: [`ui/templates/platform/dynamic_flow.html`](file:///c:/kokpitim/ui/templates/platform/dynamic_flow.html)
- 📁 **`gantt.html`**
  - Klasik Yol: [`templates/gantt.html`](file:///c:/kokpitim/templates/gantt.html)
  - Mikro Yol: [`ui/templates/platform/gantt.html`](file:///c:/kokpitim/ui/templates/platform/gantt.html)
- 📁 **`index.html`**
  - Klasik Yol: [`templates/index.html`](file:///c:/kokpitim/templates/index.html)
  - Mikro Yol: [`ui/templates/platform/index.html`](file:///c:/kokpitim/ui/templates/platform/index.html)
- 📁 **`kanban.html`**
  - Klasik Yol: [`templates/kanban.html`](file:///c:/kokpitim/templates/kanban.html)
  - Mikro Yol: [`ui/templates/platform/kanban.html`](file:///c:/kokpitim/ui/templates/platform/kanban.html)
- 📁 **`karne.html`**
  - Klasik Yol: [`templates/karne.html`](file:///c:/kokpitim/templates/karne.html)
  - Mikro Yol: [`ui/templates/platform/karne.html`](file:///c:/kokpitim/ui/templates/platform/karne.html)
- 📁 **`login.html`**
  - Klasik Yol: [`templates/login.html`](file:///c:/kokpitim/templates/login.html)
  - Mikro Yol: [`ui/templates/platform/login.html`](file:///c:/kokpitim/ui/templates/platform/login.html)
- 📁 **`packages.html`**
  - Klasik Yol: [`templates/packages.html`](file:///c:/kokpitim/templates/packages.html)
  - Mikro Yol: [`ui/templates/platform/packages.html`](file:///c:/kokpitim/ui/templates/platform/packages.html)
- 📁 **`portfolio.html`**
  - Klasik Yol: [`templates/portfolio.html`](file:///c:/kokpitim/templates/portfolio.html)
  - Mikro Yol: [`ui/templates/platform/portfolio.html`](file:///c:/kokpitim/ui/templates/platform/portfolio.html)
- 📁 **`raid.html`**
  - Klasik Yol: [`templates/raid.html`](file:///c:/kokpitim/templates/raid.html)
  - Mikro Yol: [`ui/templates/platform/raid.html`](file:///c:/kokpitim/ui/templates/platform/raid.html)
- 📁 **`task_form.html`**
  - Klasik Yol: [`templates/task_form.html`](file:///c:/kokpitim/templates/task_form.html)
  - Mikro Yol: [`ui/templates/platform/task_form.html`](file:///c:/kokpitim/ui/templates/platform/task_form.html)
- 📁 **`tenants.html`**
  - Klasik Yol: [`templates/tenants.html`](file:///c:/kokpitim/templates/tenants.html)
  - Mikro Yol: [`ui/templates/platform/tenants.html`](file:///c:/kokpitim/ui/templates/platform/tenants.html)
- 📁 **`users.html`**
  - Klasik Yol: [`templates/users.html`](file:///c:/kokpitim/templates/users.html)
  - Mikro Yol: [`ui/templates/platform/users.html`](file:///c:/kokpitim/ui/templates/platform/users.html)

## 🎨 Stil ve Arayüz Standartları

1. **Katı Katman Ayrımı (Katuralar):** HTML şablon dosyaları içinde KESİNLİKLE `<style>` veya `<script>` blokları bulunmaz. Tüm Javascript ve CSS kodları harici dosyalarda (`static/js/`, `static/css/`) yer alır.
2. **SweetAlert2 Kullanımı:** Tarayıcı varsayılanı olan `alert()` ve `confirm()` yerine SweetAlert2 kütüphanesi kullanılır.
3. **100% Türkçe UI:** Kullanıcının ekranda gördüğü tüm metinler, hata mesajları ve bildirimler Türkçe yazılır. Kod tarafı ise %100 İngilizce isimlendirmelere sahiptir.

✅ Sayfa tarayıcıda açıldı, konsol hatası taranmadı ve görsel olarak doğrulandı.
