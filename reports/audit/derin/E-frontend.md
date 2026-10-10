# ALAN E — Frontend Derin Analiz (JS, Jinja, CSS, XSS, a11y, i18n)

Tarih: 2026-10-10 · Salt okunur analiz · Kapsam: `ui/static/**/*.js`, `static/**/*.js` (vendor/min hariç, 134 dosya), `templates/` (65) + `ui/templates/` (168) = 233 şablon.

Yöntem notu: İstatistikler Node tabanlı heuristik tarayıcılarla çıkarıldı (template-literal `${}` enterpolasyonu, innerHTML/insertAdjacentHTML/.html sink'leri). "Doğrulandı" etiketi, sink satırı + veri kaynağı (kullanıcı girdisi -> API -> JS) okunarak verildi; exploit çalıştırılarak denenmedi. Heuristiğin kaçırabileceği kalıplar (string-concat HTML) örneklemle tarandı; ek bulgu çıkmadı. Satır numaraları sink ifadesinin başladığı satırdır; enterpolasyon birkaç satır aşağıda olabilir.

## Sayısal özet

| Metrik | Değer |
|---|---|
| Taranan JS / şablon | 134 / 233 |
| innerHTML/insertAdjacentHTML/.html( sink (JS) | 611 (şablon içi inline: 198 innerHTML) |
| Kaçışsız enterpolasyon adayı (heuristik) | ~325 JS + ~79 legacy şablon; çoğu sayı/renk/sabit |
| **DOĞRULANMIŞ XSS (canlı yüzey, saklı)** | **7** (E-001..E-007) |
| Olası XSS (kaynak doğrulanamadı) | 2 grup (E-008) |
| Legacy/ulaşılamaz yüzeyde XSS deseni | ~30 sink (E-009) |
| Jinja `\|safe` | 6 (hepsi sabit/`_()`+url_for, güvenli; 1 ölü şablon) |
| Inline script içi `{{ }}` (tojson'suz) | 68 (hepsi int id / bool / tarih; güvenli) |
| Inline `<script>` (içerikli) | 99 blok / 76 dosya |
| Inline `<style>` / `style=""` | 27 blok / 4734 öznitelik |
| Inline event handler (`on*=`) | 190 / 38 dosya |
| `alert()/confirm()` gerçek çağrı | JS ~20 (ui 8 + static/js ~12); şablon 27 alert + 19 confirm (çoğu legacy) |
| CSRF header'ı olmayan mutasyon fetch | 3 dosya (E-010) |
| Sessiz catch (`.catch(()=>{})`, boş catch) | 31 |
| Şablonda `_()` dışı Türkçe metin | 110 dosya / ~1387 düğüm (modern ui: 20 dosya/103; legacy `templates/`: 90/1284) |
| JS'de t() dışı Türkçe literal (ham, gürültülü) | ~1500 / 91 dosya |
| `reports/*.js` içinde hiç `t()` olmayan | 33 / 39 |
| `mc-modal-overlay` role/aria-modal yok | 44 / 44 |
| Etiketsiz ikon-only buton | 22 kesin, ~275 heuristik |
| Ölü JS (hiçbir yerde adı geçmeyen) | 34 |
| Ölü şablon (legacy `templates/`) | ~40 / 65 |
| console.log kalıntısı | 77 |

---

## XSS — doğrulanmış

Çarpan: Üretim CSP'si `script-src 'self' 'unsafe-inline'` (`app/__init__.py:113-117`) -> CSP bu bulguları HAFİFLETMEZ.

### E-001 — Kule bilet detayı modalı: saklı XSS (kullanıcı -> Admin, kurumlar arası)
- Dosya: `static/js/admin_kule.js:20-44`; kaynak `app/routes/admin.py:269-290`; yazım `app/routes/core.py:19-44` (`/kule/send`).
- Kanıt: `${ticket.user_name}`, `${ticket.tenant_name}`, `${ticket.subject}`, `${ticket.status}`, `${ticket.message}`, `<a href="${ticket.page_url}">` -> `contentDiv.innerHTML`. `message` sanitizasyonsuz DB'ye yazılıyor (`message=message`); `page_url` form alanı, `javascript:` URL'ye açık. `templates/admin/kule_iletisim.html:198` bu JS'i yüklüyor, `app/routes/admin.py:240` render ediyor.
- Etki: Giriş yapmış herhangi bir kullanıcı (her kurum) bilet gönderir; Admin "detay" tıklayınca script Admin oturumunda çalışır -> hesap ele geçirme, tüm kurum verisi.
- Önem: **Kritik** · Etiket: [Güvenlik][XSS][Saklı][Yetki yükseltme]
- Çözüm: DOM'u `textContent` ile kur veya tüm alanları escape et; `page_url`'i `new URL()` ile `http(s):` doğrula; sunucuda HTML-strip.
- Efor: S · Doğrulama: `<img src=x onerror=alert(1)>` mesajı gönder, Admin detayı aç; alert tetiklenmemeli, `javascript:` link olmamalı.

### E-002 — Girişim listesi
- `ui/templates/platform/sp/initiatives.html:120-135` (`${i.name}`, `${i.code}`); sayfada esc yok. Kullanıcı girdili ad.
- Önem: **Yüksek** (aynı kurumda düşük yetkili -> yönetici saklı XSS) · [Güvenlik][XSS][Saklı] · Çözüm: `${esc(i.name)}` · Efor: S · Doğrulama: ad olarak payload gir, listeyi aç.

### E-003 — VRIO listesi
- `ui/templates/platform/sp/vrio.html:113-115` (`${r.name}`, `${r.description}`). Önem Yüksek; çözüm/efor/doğrulama E-002 gibi.

### E-004 — Yeniden planlama tetikleyicileri
- `ui/templates/platform/sp/replan_triggers.html:129` (`${i.name}`), `:146` (`${e.action_taken}` serbest metin). Önem Yüksek.

### E-005 — Senaryo seçimi
- `ui/templates/platform/sp/scenarios.html:78-79,96-101` (`${i.name}`, `${p.name}` option/innerHTML; `</option>` ile çıkış mümkün). Önem Yüksek.

### E-006 — Mavi Okyanus tuval listesi
- `ui/templates/platform/sp/blue_ocean.html:162-166` (`${c.name}`, `${c.industry}`). Önem Yüksek.

### E-007 — Yönetim özeti "en düşük 5"
- `ui/templates/platform/masaustu/yonetim_ozeti.html:180-183` (`${s.code}`, `${s.title}`). Aynı dosyada `escHtml` (satır 234) tanımlı ama burada kullanılmıyor. Hedef kitle yönetici masaüstü. Önem Yüksek; çözüm `escHtml(s.title)`; Efor XS.

Ortak kök neden (E-002..E-007): her sayfa kendi inline script'inde esc yazıyor ya da yazmıyor; ortak `mcEsc` yok. Kalıcı çözüm: `base.html`'de tek `window.mcEsc()` + lint (`no-unsanitized`) — Efor M.

## XSS — olası / düşük

### E-008 — Kaynağı doğrulanamayan
- `sp/exec_dashboard.html:548-551` `${it.text}` — sunucu/LLM metni olabilir (dolaylı enjeksiyon). Orta.
- `sp/templates.html:65-72` `${it.name}`, `${it.description}` — kullanıcı oluşturabiliyorsa saklı XSS. Orta.
- `sp/ai_settings.html:165,199-209` `${j.message}`, `last_test_message` — sağlayıcı hata metni yansıtılıyor. Düşük-Orta.
- `admin/holding_dashboard.html:207-242`, `sub_tenants.html:288`, `sub_tenants_usage.html:184` `j.message`/`e.message` innerHTML. Düşük.
- `ui/static/platform/js/calendar_quick_create.js:540` `err.message` innerHTML. Düşük.
- `ui/static/platform/js/k_rapor.js:126` `card.dataset.name` innerHTML (sunucu sabiti; savunma için düzelt). Düşük.
- Çözüm: esc()/textContent · Efor S · Doğrulama: alana payload.
- Güvenli bulunan: `k_radar_ks.js:1172` (`recommendations` sunucuda sabit metin; ama Türkçe `_()`'sız, bkz. E-017), `reports/*.js` (hepsi `esc()` kullanıyor), SVG enterpolasyonları (sayı), `sp/okr.html` (`textContent`).

### E-009 — Legacy `static/js/*` (ulaşılamaz) — ~30 sink
- `static/js/surec_panel.js:458,480,642,1182,2187,2799,2821` (`strategy.name`, `surec.ad`), `surec_karnesi.js:950,3725` (`pg.ad`, `uye.ad_soyad`), `process_karne.js:259,941,1099-1104`, `process_panel.js:55,96,282`, `admin_panel.js:1029,1045,2295,3334`, `modules/notification-manager.js:178-182`, `strategy_dynamic_flow.js:106`.
- Bağlam: `templates/process/{karne,panel,detail}.html` hiçbir `render_template`'te geçmiyor; `surec_panel.js`, `surec_karnesi.js`, `admin_panel.js`, `notification-manager.js` hiçbir şablonda yüklenmiyor. Şu an ulaşılamaz; geri bağlanırsa doğrudan saklı XSS. Önem Orta (latent). Çözüm: sil/arşivle (E-021). Efor S.

### Jinja tarafı (temiz)
- `|safe`: `marketing/blog/post.html:12` (`html_content`; render eden route yok, ölü), `kurum/ayarlar.html:94-95`, `kurum/index.html:427,671`, `_hierarchy_help.html:34` -> sabit çeviri metni + `url_for`; kullanıcı verisi değil. (`_()` çıktısına `|safe`: .po üzerinden enjeksiyon yüzeyi, Düşük.)
- `Markup(`/`mark_safe`/`autoescape false`: yok. `render_template_string`: yalnız e-posta digest (`app/services/email_digest_service.py:127,163`, `weekly_digest_service.py:201`), şablon sabit; alan escape'i alan dışı, teyit edilmedi.
- Inline script içi `{{ }}` (115 adet): `tojson`suz 68 kullanım yalnız int id / bool / tarih / sayı -> güvenli. `project/gantt.html:54` ad `|tojson` ile yapılmış (doğru örnek).

---

## Diğer bulgular

### E-010 — CSRF token'sız mutasyon fetch'leri
- `ui/static/platform/js/sp_projeler.js:22-26` (`apiFetch` header'ında `X-CSRFToken` yok; POST `:187,:269`), `:151-152` (DELETE); `ui/static/platform/js/reports/sektor_benchmark.js:149-153` (POST); `ui/static/platform/js/admin_setup_import.js:34` (POST FormData).
- Kanıt: `CSRFProtect` aktif (`app/__init__.py:61`), global fetch yaması yok (yalnız `meta csrf-token` ve `app.js:204` helper'ı). `X-Requested-With` CSRF'i geçmez. `csrf.exempt` yalnız `micro/modules/admin/routes_admin_tools.py`'de.
- Etki: Büyük olasılıkla 400 -> SP proje CRUD, sektör AI yorumu, kurulum import KIRIK (veya muaf ise CSRF açığı). Önem: **Yüksek**. Runtime'da doğrulanmadı.
- Etiket: [Fonksiyonel][Güvenlik] · Çözüm: tek `window.mcFetch` (CSRF + ok kontrolü + hata toast) · Efor M · Doğrulama: proje oluştur/sil 200 dönmeli.

### E-011 — Sessiz hata yutma (31)
- `k_radar_ks.js:105,119,133,164,181,212,587,617`, `sp_analiz.js:121,155,188`, `ayarlar_index.js:17`, `masaustu.js:343`, `dark_mode.js:31,56`, `command_palette.js:66,231`, `reports/{cmmi_heatmap:120,hizalama_sankey:249,kv_carpiklik:112,muda_analizi:74,op_istatistik:48,sektor_benchmark:133}`, `surec.js:568`, `yonetim_paneli.js:267`.
- Etki: veri yüklenemezse boş/yanlış ekran; §3 "except: pass yasak"ın JS karşılığı. Orta · Çözüm: en az console.error + toast · Efor S-M.

### E-012 — `res.json()` öncesi `res.ok` yok / catch'siz fetch
- ui/static'te 21 `.then(r => r.json())` zinciri vs 24 `ok` kontrolü; `reports/nlp_query.js:27,36,42`, `sp_projeler.js:151` (catch yok), `static/js/process_panel.js:230,253`. 4xx/5xx HTML yanıt JSON parse hatasına düşüp yutuluyor. Orta · Çözüm: ortak mcFetch · Efor M.

### E-013 — Hardcoded URL (JS)
- 189 literal `fetch('/...')`: legacy `admin_panel.js` (50), `surec_karnesi.js` (26), `surec_panel.js` (9), `tenant_dashboard.js` (5), `process_karne.js` (5); modern: `reports/nlp_query.js` (3), `yatirimci_sunum.js`, `stratejik_yillik.js`, `sektor_benchmark.js`, `bireysel_karne_batch.js`, `ai_sunum.js` (2'şer). Modern JS çoğunlukla `data-*` ile temiz. §3 ihlali. Düşük-Orta · Çözüm: `data-*-url` · Efor M.

### E-014 — Inline script/style yoğunluğu ve CSP
- 99 inline script (en çok `platform/base.html` 5, `sp/exec_dashboard.html` 4, `surec/karne.html` 3, `surec/index.html` 3), 27 `<style>`, 4734 `style=""`, 190 inline `on*=`. CSP `unsafe-inline` zorunluluğu (`app/__init__.py:105-112` kendi notu) XSS hafifletmesini yok ediyor -> E-001..E-007 etkisini artırıyor. Orta (mimari borç) · Çözüm: nonce'lu CSP + harici JS göçü, `mcEsc` ile birlikte · Efor L.
- `console.log` 77 kalıntı (Düşük). Jinja-in-JS: `static/js/components/dashboard-builder.js:157-211` Vue şablonunda `{{ }}` (dosya ölü).

### E-015 — alert()/confirm() kalıntıları
- Modern: `ui/static/platform/js/sp_analiz.js:71`, `totp_setup.js:33`, `twofa.js:70`, `reports/veri_kalitesi.js:98` (alert); `sp_projeler.js:124` (Swal yoksa confirm); `ui/templates/platform/surec/index.html:684`; `admin/yedekleme.html:144-145` (DB geri yükleme fallback'i confirm); `admin/sub_tenants.html:393,412` (confirm: parola sıfırlama, pasifleştirme — Swal yok).
- Legacy: `templates/admin/feedback_management.html` 12, `bsc/strategy_map.html` 5, `projects/*.html`, `static/js/kurum_panel.js` 10, `surec_karnesi.js` 2.
- Orta (kural ihlali; yıkıcı işlemde native confirm) · Çözüm: Swal onay · Efor S · Doğrulama: grep sıfır.

### E-016 — i18n: şablonlarda `_()` dışı Türkçe
- Modern `ui/templates`: 20 dosya / 103 düğüm; `platform/k_rapor/index.html` (47), `surec/index.html` (17 + 8 attr "Ağaç görünümü"), `kurum/index.html` (9 attr "Düzenle"), `masaustu/index.html`, `surec/karne.html`. (`base.html` dil menüsü bilinçli.)
- Legacy `templates/`: 90 dosya / 1284 düğüm (`process/karne.html` 190, `process/panel.html` 73, ...) çoğu ölü.
- EN arayüzde Türkçe. Orta · Çözüm: `_()` + `.po` + compile (§5.1) · Efor M · Doğrulama: EN'de gezinti.

### E-017 — i18n: JS hardcoded metin
- `ui/static/platform/js/reports/*.js`: 39 dosyanın 33'ünde hiç `t()` yok (`sektor_benchmark.js:12` 'Veri alınamadı', `veri_kalitesi.js:31,78` 'Hata: ', `coo_dashboard.js:21` ' iyi'/' orta', `hedef_revizyon.js`, `vrio_portfoy.js`, `initiative_bubble.js:7` 'Planlandı', `ai_sunum.js`). Ayrıca `tool_info_modal.js:10` (başlık + gövde), `k_radar_ks.js`, `calendar_quick_create.js:126`, `pg_tablo_modal.js:69`, `surec.js`, `bireysel.js`.
- Sunucudan gelen Türkçe: `micro/modules/sp/routes_analysis.py:1076-1090` (BSC önerileri `_()`'sız; `k_radar_ks.js:1172` EN'de Türkçe basar).
- Ham ~1500 literal / 91 dosya (iç içe t() false-positive içerir; legacy `static/js` ~700). Orta · Efor L (reports M).

### E-018 — Erişilebilirlik: modal
- 44 `mc-modal-overlay`'in hiçbiri `role="dialog"`/`aria-modal`/`aria-labelledby` taşımıyor (yalnız `base.html:912` doğru). Focus-trap yok, açılışta odak taşınmıyor/kapanışta geri dönmüyor; yalnız Escape var (`app.js:100`, `mc-modal-form.js:80`). Çoğu: `k_radar/ks.html` 10, `surec/karne.html` 8, `auth/profil.html` 3, `sp/blue_ocean.html` 3. Orta · Çözüm: ortak modal yardımcısı (role, trap, restore) · Efor M.

### E-019 — Erişilebilirlik: ikon buton ve form
- `×`/ikon-only buton etiketsiz: 22 kesin (`sp/okr.html` 4, `blue_ocean` 3, `k_radar/risk_management` 3, `sp/projeler`, `sp/donemler`, `admin/hata_kontrolu`), `mc-modal-close` 18 yerde `aria-label`'sız; heuristik ~275. 75 input `id`'siz (label bağlanamaz), ~47 etiketsiz. Orta · Çözüm: `aria-label="{{ _('Kapat') }}"`, label for · Efor M.

### E-020 — Tutarsız kaçış yardımcıları
- 12+ kopya: `esc/escHtml/escapeHtml/escAttr/escapeHtmlKoe` (admin.js:55, admin_hierarchy.js:28, analiz.js:225, bireysel.js:125, command_palette.js:82, kule.js:263, kurum.js:59, k_radar.js:33, masaustu.js:102,439 ...). `reports/nlp_query.js:3` `[&<>"]` tek tırnağı kaçırmıyor (öznitelik bağlamı). Düşük-Orta · Çözüm: tek `mcEsc` · Efor S.

### E-021 — Ölü JS (34)
- `ui/static/platform/js/`: `launcher_plan_year.js`, `masaustu_plan_year.js`, `sp_analiz.js`, `reports/early_warning.js`, `reports/ml_anomaly.js`, `reports/risk_heatmap.js` (bu raporlar şablonda inline script kullanıyor -> mükerrer).
- `static/js/`: `admin_confirm.js`, `admin_packages.js`, `admin_panel.js`, `admin_tenants.js`, `admin_users.js`, `bireysel_panel.js`, `components/dashboard-builder.js`, `components/kpi-card.js`, `dashboard_classic.js`, `dashboard_sideview.js`, `kpi_panel_modern.js`, `kurum_panel.js`, `modules/chart-utils.js`, `modules/notification-manager.js`, `modules/process_karne/api.js`, `modules/process_karne/calculations.js`, `project_list.js`, `strategy.js`, `strategy_dynamic_flow.js`, `strategy_planning_flow.js`, `surec_panel.js`, `tenant_dashboard.js`, `vue-app.js`.
- `static/prototypes/`: `kontrol-common.js`, `kontrol-index.js`, `modul-karne.js`, `modul-pg.js`, `modul-surec.js`. Kökte: `tmp_admin_panel.js`, `deleteOrganization_extracted.js`, `kontrol-common.js`, `kontrol.html`.
- Yöntem: dosya adı `templates ui/templates app main micro api` içinde (py/html/js) geçmiyor; dinamik yükleme false-positive olabilir -> silmeden `git log -S` + grep. Düşük (E-009'u kapatır) · Çözüm: `scripts/_arsiv/` · Efor S.

### E-022 — Ölü legacy şablonlar (~40/65)
- `templates/process/{karne,panel,detail,index}.html`, `strategy/project_portfolio.html`, `marketing/blog/post.html` (`|safe` içerir), `projects/*.html` vb.: `render_template` referansı bulunamadı (heuristik; dinamik ad false-positive olabilir). Düşük · Çözüm: doğrula + arşivle (route-silme refleksi: `url_for` taraması) · Efor M.

---

## En önemli 5
1. E-001 Kule bilet modalı saklı XSS (kullanıcı -> Admin, CSP korumasız).
2. E-002..E-007 SP/masaüstü şablonlarında 6 ek saklı XSS (kullanıcı girdili ad alanları kaçışsız) — ortak çözüm `mcEsc`.
3. E-014 CSP `unsafe-inline` + 99 inline script / 190 inline handler: XSS hafifletmesi yok.
4. E-010 CSRF header'sız POST/DELETE (SP proje CRUD, sektör AI yorumu, kurulum import).
5. E-017/E-016 i18n (reports JS'lerinin 33/39'unda t() yok) ve E-018 modal a11y.

Önerilen sıra: Hafta 1 E-001..E-007 (+mcEsc) ve E-010; sonra E-021/E-022 temizliği, E-015, E-018; i18n paket paket.
