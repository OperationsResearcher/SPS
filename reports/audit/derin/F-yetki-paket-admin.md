# ALAN F — Yetkilendirme, Paket Gating, Admin, Bireysel, Proje (derin analiz)

Tarih: 2026-10-10 · Salt okunur analiz (kod değiştirilmedi). Kapsam: micro/modules/admin, bireysel, proje, kurum, shared/*, api/routes_projects.py, platform_core (gating), app/utils (decorators, tenant_scope, project_rbac), app/routes (auth, totp).

Etiketler: [DOĞRULANDI] kod yolu okunarak teyit edildi · [KOŞULLU] belirli veri/konfig koşuluna bağlı · [TASARIM] ürün kararı gerektirir.

## Özet tablo

| ID | Başlık | Önem | Etiket |
|----|--------|------|--------|
| F-001 | Kurum Yöneticisi/Üst Yönetim kendi kurumunun paketini, lisans bitişini ve kullanıcı kotasını değiştirebiliyor | Kritik | DOĞRULANDI |
| F-002 | Paket kapısı yalnız GET + "sayfa" isteklerinde; XHR başlığı/POST/API ile atlanıyor | Yüksek | DOĞRULANDI |
| F-003 | Legacy `api_bp` `/api/projeler*` rol kontrolü yok: standart kullanıcı proje oluşturur/düzenler/klonlar | Yüksek | DOĞRULANDI |
| F-004 | Paket kapısının kapsamadığı yüzeyler (/api/v1, /api/projeler, /organization, /holding, ayrı blueprint'ler) | Yüksek | DOĞRULANDI |
| F-005 | Hedef rol kontrolü eksik: Üst Yönetim aynı kurumdaki hesapların parola/2FA'sını sıfırlayıp devralabiliyor | Yüksek | DOĞRULANDI |
| F-006 | DB geri yükleme (`pg_restore --clean`) Yayın'da açık, denetim kaydı yok | Yüksek | DOĞRULANDI |
| F-007 | Arşivli/pasif kurum, lisans süresi ve kullanıcı kotası uygulanmıyor | Orta-Yüksek | DOĞRULANDI |
| F-008 | Üst Yönetim, bayi/holding kurumunda alt kurum açıp alt kurum yöneticisini devralabiliyor | Orta-Yüksek | DOĞRULANDI |
| F-009 | Tehlikeli yönetim işlemlerinde denetim kaydı yok | Orta | DOĞRULANDI |
| F-010 | Admin kullanıcı oluşturma/düzenlemede parola politikası yok | Orta | DOĞRULANDI |
| F-011 | Paket kısıtı fail-open (paketsiz kurum, çözümleme hatası) | Orta | DOĞRULANDI |
| F-012 | Kart düzeyi paket gating yalnız istemci tarafı | Orta | TASARIM |
| F-013 | TOTP: replay koruması yok, yedek kod ve secret düz metin, oturum sabitleme | Orta | DOĞRULANDI |
| F-014 | 2FA bekleyen oturum süresiz; e-posta değişimi yeniden kimlik doğrulamasız | Orta-Düşük | DOĞRULANDI |
| F-015 | `Admin` rollü kullanıcı kurum yöneticisince değiştirilebilir (aynı tenant_id ise) | Orta (koşullu Kritik) | KOŞULLU |
| F-016 | Geçersiz `role_id` atama kontrolünü atlıyor | Düşük | DOĞRULANDI |
| F-017 | Bildirim yayınında `link`/`type` doğrulaması yok | Düşük | KOŞULLU |
| F-018 | Demo modu yalnız konfig bayrağına bağlı | Düşük | KOŞULLU |
| F-019 | CSRF muafiyetli yıkıcı admin uçları | Düşük | DOĞRULANDI |
| F-020 | Görev atama doğrulaması Platform Admin için yanlış tenant'a bağlı | Düşük | DOĞRULANDI |

---

## F-001 — Kurum içi roller kendi paketini/lisansını/kotasını değiştirebilir
- Dosya: `micro/modules/admin/routes.py:1009-1037`
- Kanıt: `admin_tenants_edit` yalnızca `_is_manager()` (Admin, tenant_admin, executive_manager) ve `tenant_id == current_user.tenant_id` ister. Ardından `max_user_count` (1031), `license_end_date` (1032-1034) ve `package_id` (1035-1036) gövdeden koşulsuz yazılır. `tenant_type`/`sub_tenant_limit` için `_is_admin()` konmuş, bu üç alan için konmamış.
- Etki: Kurum Yöneticisi (ve Üst Yönetim) `POST /admin/tenants/edit/<kendi_id>` ile `{"package_id": <Master>}` göndererek paketi kendi kendine yükseltir; lisans bitişini uzatır; kullanıcı kotasını artırır. Ticari model (paket->modül) aşılır. Denetim kaydında bu alanlar da yok (F-009).
- Önem: Kritik · Etiket: DOĞRULANDI
- Çözüm: Bu üç alanı `if _is_admin():` bloğuna al (tenant_type ile aynı desen); audit'e eski/yeni paket yaz.
- Efor: 0.5 saat
- Doğrulama testi: executive_manager ve tenant_admin oturumuyla `package_id`, `license_end_date`, `max_user_count` gönder -> 403 veya alanlar değişmemeli; Admin ile değişmeli (pytest, Flask test client).

## F-002 — Paket kapısı atlanabiliyor
- Dosya: `platform_core/__init__.py:119-139`
- Kanıt: `is_api = ("/api/" in path) or request.headers.get("X-Requested-With") == "XMLHttpRequest"`; paket kapısı `if pkg_mid is not None and not is_api and request.method == "GET"` (satır 131). Sonuç: (a) istemci `X-Requested-With: XMLHttpRequest` ekleyince GET sayfa kapısı atlanır, (b) tüm POST/PUT/DELETE istekleri paket kapısına girmez (ör. `POST /k-plan/individual/api/pi/add`, `/k-plan/project/new`), (c) yolu `/api/` içeren her şey atlanır. Yorum "API/AJAX kendi 403'ünü verir" diyor; ancak modül route'ları `require_module` kullanmıyor (yalnız raporlar ve sp/routes_exec_advisor kullanıyor).
- Etki: Paketinde `bireysel`/`proje`/`surec`/`analiz`/`k_radar`/`k_rapor` olmayan kurum kullanıcısı, menüde görünmeyen modülün verisini ve yazma uçlarını doğrudan çağırır. Rol kapısı bu atlamayı yapmıyor ama yalnız sp/k_radar/analiz içindir.
- Önem: Yüksek · Etiket: DOĞRULANDI
- Çözüm: Paket kapısı HER yöntemde ve her istek tipinde çalışsın; `is_api` yalnızca ret biçimini (redirect vs JSON 403) seçsin. İstemci başlığına güvenme.
- Efor: 2 saat (+ regresyon testleri)
- Doğrulama testi: paketinde `bireysel` olmayan kullanıcıyla (1) `GET /k-plan/individual/scorecard` + `X-Requested-With`, (2) `POST /k-plan/individual/api/pi/add` -> 403 beklenir.

## F-003 — Legacy proje REST API'sinde rol/üyelik kontrolü yok
- Dosya: `api/routes_projects.py:71-215` (POST), `:218-337` (PUT), `:1197` (klonla), `:986`/`:1049`/`:1100` (risk ekle/güncelle/sil); blueprint `/api` önekiyle kayıtlı (`app/__init__.py:621-626`)
- Kanıt: Bu uçlar yalnızca `@login_required` ve `project.kurum_id != current_user.kurum_id` kontrolü yapar. Modern yüzeydeki `can_crud_project_portfolio` ve `user_is_project_leader` yok. Aynı dosyada görev uçları `@project_observer_allowed` ile korunmuş, proje oluştur/güncelle/klonla/risk uçları korunmamış.
- Etki: Kurum Kullanıcısı `POST /api/projeler` ile proje oluşturur, kurumdaki HERHANGİ bir projeyi `PUT /api/projeler/<id>` ile (ad, lider, üyeler, süreç bağları) değiştirir, klonlar, risk ekler/siler. Modern arayüzdeki "Yeni proje oluşturma yetkiniz yok" kuralı API'den aşılır. `/api/` olduğu için F-002 nedeniyle paket kapısı da yok.
- Önem: Yüksek · Etiket: DOĞRULANDI
- Çözüm: Bu uçlara `micro.modules.proje.permissions` fonksiyonlarını bağla (oluştur -> `can_crud_project_portfolio`; güncelle/klonla -> `user_is_project_leader`; risk -> `user_can_edit_tasks`); uzun vadede uçları modern modüle taşı/kaldır (strangler).
- Efor: 3 saat
- Doğrulama testi: standard_user ile `POST /api/projeler` ve başkasına ait projede `PUT` -> 403.

## F-004 — Paket kapısının görmediği yüzeyler
- Dosya: `platform_core/__init__.py:46-60` (`_GATED_PREFIX_MODULE`), `app/__init__.py:592-626`
- Kanıt: Tabloda yalnız `/k-plan/process|individual|project`, `/process|/individual|/project`, `/k-radar*`, `/analysis`, `/k-report`, `/k-rapor` var. Kapsam dışı: `/api/v1/*` (14 route, micro/modules/api), `/api/projeler*` (legacy `api_bp`, ayrı blueprint), `app/api` v1 blueprint'i ve `process_performance_bp`, `/organization/api/*`, `/holding/api/*`, `/reports`, `/surec`, `/proje`. Kapı `@app_bp.before_request` olduğundan ayrı blueprint'lere hiç uygulanmaz.
- Etki: Paket kapsamı yeni/ayrı blueprint'e eklenen her route'ta sessizce yok olur (kodun kendi yorumu da bunu söylüyor). Mevcut açıklar: /api/v1 veri API'si ve `/api/projeler`.
- Önem: Yüksek · Etiket: DOĞRULANDI
- Çözüm: Önek tablosu yerine blueprint-bağımsız `app.before_request` kapısı; endpoint->modül eşlemesi; CI testi: tüm `url_map` route'ları bir modüle ya da açık "gate-exempt" listesine düşmeli.
- Efor: 1 gün
- Doğrulama testi: `url_map` taraması — eşlenmemiş ve muaf listesinde olmayan route varsa test kırmızı.

## F-005 — Hedef rol kontrolü eksik: Üst Yönetim hesapları devralabilir
- Dosya: `micro/modules/admin/routes.py:594-646` (edit), `:648-676` (toggle), `:679-730` (2fa-reset)
- Kanıt: `_is_manager()` executive_manager'ı kapsar. Hedefte yalnızca "tenant_admin değilse" engeli var (602-608). Üst Yönetim, aynı kurumdaki herhangi bir kullanıcının (diğer executive_manager dahil) `password` alanını `admin_users_edit`'te (623-624) doğrudan atar; `2fa-reset` ile TOTP'sini siler.
- Etki: Üst Yönetim rolündeki bir kullanıcı (ele geçirilmiş hesap veya kötü niyetli iç kullanıcı) aynı kurumdaki diğer Üst Yönetim hesabına 2FA'yı sıfırlayıp parolayı değiştirerek geçer; denetimde yalnız "2FA sıfırlandı" kaydı var, parola atama kaydı yok. Yatay devralma + 2FA atlatma yolu.
- Önem: Yüksek · Etiket: DOĞRULANDI
- Çözüm: Rol hiyerarşisi (Admin > tenant_admin > executive_manager > standard_user): işlem yapan yalnızca KENDİSİNDEN DÜŞÜK rolü yönetsin; parola atamayı kaldırıp "sıfırlama bağlantısı gönder" akışı; her iki işlem için audit.
- Efor: 3 saat
- Doğrulama testi: executive_manager A ile executive_manager B için `edit` (password) ve `2fa-reset` -> 403.

## F-006 — DB geri yükleme Yayın'da açık, denetimsiz
- Dosya: `micro/modules/admin/routes_admin_tools.py:248-299`
- Kanıt: Aynı dosyada `indir/db`, `indir/kod`, `indir-dosya` uçları `_is_local()` ile Yayın/Test/Demo'da kilitli (GUV-08); `geri-yukle/db` kilitli değil: yalnız `_is_admin()` + parola + sabit onay metni (`_RESTORE_CONFIRM`, satır 138). `restore_db` `pg_restore --clean --if-exists` çalıştırır (`app/services/yedekleme_service.py:170-185`). Fonksiyonda `AuditLogger` çağrısı yok, TOTP yeniden doğrulaması yok, bakım modu şartı yok. `@csrf.exempt`.
- Etki: Ele geçirilmiş Admin oturumu + sızmış parola ile tüm müşteri verisi silinip saldırgan dump'ıyla değiştirilir; dump kullanıcı/yetki tablolarını da içerir (kalıcı arka kapı). İz bırakmaz.
- Önem: Yüksek · Etiket: DOĞRULANDI
- Çözüm: Yayın/Test/Demo'da `_is_local()` ile kilitle (diğer yedek uçlarıyla tutarlı); açık kalacaksa bakım modu zorunluluğu + TOTP + audit + otomatik pre-restore yedek.
- Efor: 1 saat (kilit) / 4 saat (tam koruma)
- Doğrulama testi: `FLASK_ENV=production` iken Admin ile `POST .../geri-yukle/db` -> 403 "bu ortamda kilitli".

## F-007 — Pasif kurum / lisans süresi / kota uygulanmıyor
- Dosya: `app/routes/auth.py:70`, `app/__init__.py:162-175` (`load_user`), `micro/modules/admin/routes.py:1147-1164`
- Kanıt: login yalnız `User.is_active` filtreler, `load_user` yalnız `User.is_active` + `session_version` bakar. `tenant.is_active` ve `license_end_date` kod yolunda (admin ekranları ve rapor servisleri dışında) hiçbir yerde denetlenmiyor (grep ile doğrulandı). `max_user_count` yalnız yazılıyor/gösteriliyor; `admin_users_add`, `admin_users_bulk_import`, sub-tenant oluşturma kota denetlemiyor.
- Etki: "Arşivle" ile kapatılan kurumun kullanıcıları girişe devam eder; lisansı biten kurum çalışır; kullanıcı kotası (satış limiti) uygulanmaz.
- Önem: Orta-Yüksek · Etiket: DOĞRULANDI
- Çözüm: `load_user`'da kurum aktif + lisans geçerli kontrolü (Admin hariç); kullanıcı ekleme uçlarında `count(active) < max_user_count`.
- Efor: 3 saat
- Doğrulama testi: `tenant.is_active=False` -> o kurum kullanıcısıyla login/istek reddedilmeli; kota dolunca `users/add` -> 400.

## F-008 — Üst Yönetim alt kurum açıp alt kurum yöneticisini devralabilir
- Dosya: `app/utils/tenant_scope.py:197-212` (`is_dealer_admin`/`is_holding_admin` executive_manager dahil), `micro/modules/admin/routes_sub_tenants.py:134-250`, `:257-310`
- Kanıt: `can_manage_sub_tenants` executive_manager'a izin verir. Alt kurum oluştururken yönetici e-postası/parolası gövdeden gelir; `admin/reset-password` alt kurum tenant_admin parolasını sıfırlar. Paket seçimi opsiyonel ve herhangi aktif paket olabilir (183-196).
- Etki: Bayi/Holding kurumundaki Üst Yönetim kullanıcısı alt kurumların yönetici hesabını yeniden oluşturup devralır; alt kuruma istediği (en pahalı) paketi verir.
- Önem: Orta-Yüksek · Etiket: DOĞRULANDI (rol politikası TASARIM)
- Çözüm: Sub-tenant işlemlerini `tenant_admin` + Admin ile sınırla veya açık ürün kararı; paket seçimini bayiye tanımlı izinli listeye bağla.
- Efor: 2 saat
- Doğrulama testi: dealer tenant executive_manager -> `POST /admin/api/sub-tenants` -> 403.
- Not: Parola sıfırlama yanıtı "e-posta ile gönderildi" diyor; gönderen kod bu dosyada yok. Doğrulanmadı; mail yoksa yönetici yeni parolayı öğrenemez (işlevsel kusur).

## F-009 — Denetim kaydı eksik tehlikeli işlemler
- Dosya: `micro/modules/admin/routes.py`
- Kanıt (AuditLogger çağrısı OLMAYAN uçlar): `admin_users_toggle` 648-676, `admin_users_bulk_import` 735-808, `admin_tenants_toggle` 1147-1164 (kurum arşivleme), `admin_packages_add/edit/toggle` 1638-1700, `admin_package_module_toggle` 1739-1762 (tüm kurumların erişimini değiştirir), `admin_modules_add/toggle`, `admin_notifications_broadcast` 1555-1600, `admin_k_radar_weights_save`. `admin_users_edit` audit'i eski değer (`{}`) ve parola değişimi içermiyor (619-640); `admin_tenants_edit` audit'i paket/lisans/kota alanlarını içermiyor (1055-1066). DB geri yükleme için F-006. Tenant klonlama / toplu silme aracı bu kapsamda bulunamadı.
- Etki: Paket-modül değişimi ve kurum kapatma gibi geri dönüşü zor işlemlerin kim/ne zaman izi yok; F-001 gibi suistimal tespit edilemez.
- Önem: Orta · Etiket: DOĞRULANDI
- Çözüm: Ortak `@audited(action)` dekoratörü veya ilgili uçlara `AuditLogger.log_update(old,new)`; parola alanı "password_changed" olarak (değer yazılmadan).
- Efor: 4 saat
- Doğrulama testi: her uç sonrası `audit_logs` satır sayısı artmalı.

## F-010 — Parola politikası admin uçlarında uygulanmıyor
- Dosya: `micro/modules/admin/routes.py:542, 568, 623-624`
- Kanıt: Profil ekranı `validate_password` kullanıyor (`micro/modules/shared/auth/routes.py:38-44`); `admin_users_add` ve `admin_users_edit` gövdedeki `password`'u uzunluk/karmaşıklık denetimsiz hash'ler (bulk-import en az 8 karakter istiyor).
- Etki: `1` gibi parolalar atanabilir; yönetici bilinen parola atayabilir (F-005 ile birleşir).
- Önem: Orta · Etiket: DOĞRULANDI
- Çözüm: Aynı `validate_password`'ı uygula; yönetici-parola atama yerine tek kullanımlık bağlantı.
- Efor: 1 saat
- Doğrulama testi: `users/add` ile `password:"1"` -> 400.

## F-011 — Paket kısıtı fail-open
- Dosya: `app/utils/package_gating.py:12-34`, `micro/core/module_registry.py:226-250`, `platform_core/__init__.py:136, 146`, `app/utils/decorators.py:86`
- Kanıt: paketsiz tenant -> `allowed_component_slugs` None (kısıtsız); `module_registry` paketsizde kurum yöneticisi/Üst Yönetim için tam launcher; üç yerde `except -> fail-open`. Alt kurum `package_id=None` ile açılabilir (routes_sub_tenants.py:183-196, 209-217); `admin_tenants_add` de paketsiz mümkün.
- Etki: Paket atanmamış (veya çözümleme sırasında DB hatası oluşan) kurum tüm modülleri kullanır.
- Önem: Orta · Etiket: DOĞRULANDI (paketsiz = tam erişim bir TASARIM kararı olabilir; hata yolunda fail-open düzeltilmeli)
- Çözüm: Hata yolunda fail-closed (log + 403), paketsiz kurum için açık "varsayılan paket"; alt kurum paketini zorunlu kıl.
- Efor: 3 saat
- Doğrulama testi: `get_accessible_modules` istisna fırlatınca modül sayfası reddedilmeli.

## F-012 — Kart düzeyi paket gating yalnız istemcide
- Dosya: `micro/modules/admin/routes.py:1312-1338`, `app/utils/package_gating.py:37-70`
- Kanıt: Sunucu yalnız gizlenecek kart kodlarını döner; "base.html merkezî JS'i bunları gizler". Kartın verisi aynı sayfa/API yanıtında zaten gelir.
- Etki: Paket dışı kart içeriği DOM/ağ yanıtında okunabilir; yalnız görsel gizleme.
- Önem: Orta · Etiket: TASARIM
- Çözüm: Kart veri uçlarını `require_component(slug)` ile koru (decorator mevcut, `app/utils/decorators.py:10`).
- Efor: 1-2 gün
- Doğrulama testi: paket dışı kartın veri API'sine doğrudan istek -> 403.

## F-013 — TOTP sertleştirme eksikleri
- Dosya: `app/services/totp_service.py:61-101`, `app/routes/totp.py:170-223`, `app/routes/auth.py:95-98`
- Kanıt: (a) `verify_totp_code` kullanılan zaman diliminin kaydını tutmaz; `valid_window=1` ile aynı kod yaklaşık 90 sn tekrar kullanılabilir. (b) Yedek kodlar `totp_backup_codes_json`'da düz metin, `in` karşılaştırması zamanlama-güvenli değil, 32 bit; `totp_secret` düz metin. (c) `totp_challenge` başarıda `session.clear()` yapmıyor; normal login yolu yapıyor (oturum sabitleme).
- Etki: DB sızıntısında tüm 2FA sırları ve yedek kodlar doğrudan kullanılabilir; yakalanan kod kısa süre yeniden kullanılır.
- Önem: Orta · Etiket: DOĞRULANDI
- Çözüm: `last_used_step` sakla; yedek kodları hash'le (`secrets.compare_digest`); secret'ı şifreli sakla; challenge sonrası `session.clear()` + `login_user`.
- Efor: 4 saat
- Doğrulama testi: aynı TOTP kodunu iki kez gönder -> ikincisi reddedilmeli.

## F-014 — 2FA bekleyen oturum ve e-posta değişimi
- Dosya: `app/routes/auth.py:90-92`, `micro/modules/shared/auth/routes.py:49-53`
- Kanıt: `_pending_2fa_user_id` zaman damgasız, süresiz. Kilit anahtarı e-posta+IP olduğundan saldırgan hedefin e-postasını kilitleyebilir (hesap kilitleme DoS). Profilde e-posta, parola doğrulaması istenmeden değiştirilir (parola değişimi `current_password` ister, e-posta istemez).
- Etki: Oturumu çalınmış hesapta e-posta değiştirilip parola sıfırlama zinciriyle kalıcı devralma.
- Önem: Orta-Düşük · Etiket: DOĞRULANDI
- Çözüm: Pending 2FA için 5 dk TTL; e-posta değişiminde `current_password` + eski adrese bildirim.
- Efor: 2 saat
- Doğrulama testi: e-posta değişimi parolasız -> 400.

## F-015 — Admin rollü kullanıcı kurum yöneticisince değiştirilebilir
- Dosya: `micro/modules/admin/routes.py:596-646, 650-676, 681-705`
- Kanıt: Kontroller `u.tenant_id != current_user.tenant_id` ve `u.role.name == "tenant_admin"`; hedef `Admin` ise engel yok. Platform Admin kullanıcıları bir müşteri kurumuna bağlıysa o kurumun tenant_admin'i Admin'in parolasını/2FA'sını sıfırlayıp platform yetkisi alır.
- Etki: KOŞULLU — Admin kullanıcıların `tenant_id`'si müşteri kurumuysa tam dikey yükseltme. Veritabanında teyit edilmedi.
- Önem: Orta (koşullu Kritik) · Etiket: KOŞULLU
- Çözüm: Hedef rol `Admin` ise yalnız Admin işlem yapabilsin (F-005 hiyerarşisinin parçası).
- Efor: 0.5 saat
- Doğrulama testi: SQL `select u.id,u.tenant_id from users u join roles r on r.id=u.role_id where r.name='Admin'`; test: tenant_admin -> Admin hedefi `edit` -> 403.

## F-016 — Geçersiz `role_id` atama kontrolünü atlıyor
- Dosya: `micro/modules/admin/routes.py:613-622`
- Kanıt: `new_role = Role.query.get(...)`; yetki kontrolü `if new_role:` içinde, dışında `u.role_id = int(data["role_id"])` koşulsuz. `users/add` doğru yapıyor (516-524).
- Önem: Düşük · Etiket: DOĞRULANDI
- Çözüm: `if not new_role: return 400`. Efor: 15 dk. Test: `role_id=999999` -> 400.

## F-017 — Bildirim yayını girdi doğrulaması
- Dosya: `micro/modules/admin/routes.py:1555-1590`
- Kanıt: `link` ve `type` doğrulamasız saklanır. Şablonda `href` olarak basılıp basılmadığı bu analizde doğrulanmadı.
- Etki: `javascript:` şemalı link tüm kurum kullanıcılarında tıklamada çalışabilir (stored XSS).
- Önem: Düşük · Etiket: KOŞULLU
- Çözüm: Yalnız `/` ile başlayan yerel yollar (login'deki GV-006 mantığı); `type` beyaz liste.
- Efor: 30 dk. Test: `link:"javascript:alert(1)"` -> 400.

## F-018 — Demo modu konfig bağımlılığı
- Dosya: `micro/modules/demo/routes.py:73-165`
- Kanıt: `/demo/start/<key>` yalnız `KOKPITIM_DEMO_MODE` bayrağına bakıp kurumun tenant_admin kullanıcısıyla kimlik bilgisiz oturum açar.
- Etki: Bayrağın Yayın/Test ortamına yanlış taşınması = anonim tenant_admin girişi. Tek savunma konfig.
- Önem: Düşük · Etiket: KOŞULLU
- Çözüm: Ortam adı/host kontrolü; Yayın'da bayrak açıksa başlatmayı reddet.
- Efor: 1 saat. Test: production config + bayrak -> uygulama init hata vermeli.

## F-019 — CSRF muafiyetli admin uçları
- Dosya: `micro/modules/admin/routes_admin_tools.py:171,193,233,249,361,406,447,490,537`; `routes_setup_import.py:58,74`
- Kanıt: Durum değiştiren uçlar `@csrf.exempt`. Çerez `SameSite=Strict` (config.py:100) olduğundan istismar zor; savunma tek katmana düşüyor. Yerel olmayan ortamda geçerli olanlar: `otomatik-calistir`, `geri-yukle/db`, `setup-import/apply`.
- Önem: Düşük · Etiket: DOĞRULANDI
- Çözüm: Muafiyeti kaldır, `X-CSRFToken` başlığı gönder. Efor: 2 saat.

## F-020 — Görev atama doğrulaması Platform Admin için yanlış tenant'a bağlı
- Dosya: `micro/modules/proje/routes_tasks.py:60-67, 92, 158-170, 190, 270, 280`
- Kanıt: Atanan/KPI doğrulaması `current_user.tenant_id`'ye karşı; Platform Admin başka kurum projesinde görev eklerken geçerli atama reddedilir. Güvenlik açığı değil (daha kısıtlayıcı), işlevsel tutarsızlık; doğru karşılaştırma `proj.kurum_id`.
- Önem: Düşük · Etiket: DOĞRULANDI
- Çözüm: `current_user.tenant_id` -> `proj.kurum_id`. Efor: 30 dk.

---

## Olumlu bulgular (kanıtlı, sorun yok)
- Bireysel karne (`micro/modules/bireysel/routes.py`): tüm CRUD/okuma uçları `user_id=current_user.id` ile sorgulanıyor (244, 274, 298, 395, 419, 436, 502, 677); başka kullanıcının verisine id ile erişim yolu bulunamadı. `team-alignment` yalnız yönetici rolleri ve kendi tenant'ı (733-741).
- Modern proje yüzeyi (`micro/modules/proje/permissions.py`, `routes_project_crud.py`, `routes_tasks.py`): `_same_tenant` ile kurum izolasyonu, lider/üye/gözlemci ayrımı, `Project` sorguları `kurum_id` filtreli.
- Kurum modülü (`micro/modules/kurum/routes.py`): tüm yazma uçları `_check_kurum_role()` ve `tenant_id == current_user.tenant_id` filtreli.
- Platform düzeyi admin uçları (paket, modül, kart, bakım, tenant add/toggle, araçlar) `_is_admin()` (yalnız `Admin`) ile korunuyor; yedek indirme uçları `_is_local()` kilitli.
- Kendi rolünü değiştirme: profil POST'u `role` alanı yazmıyor; `ASSIGNABLE_ROLES` atanabilir rolleri sınırlıyor (tenant_admin hedefi tenant_admin olmayanlarca düzenlenemez; executive_manager yalnız executive_manager/standard_user atayabilir). Kurum Yöneticisi -> Sistem Yöneticisi rolü atama: engelli (`ASSIGNABLE_ROLES["tenant_admin"]`).
- Oturum: `session_version` artışı (`app/models/core.py:309-312`) + `load_user` (`app/__init__.py:162-175`) parola değişince (profil, admin, sıfırlama) diğer oturumları düşürüyor; pasif kullanıcı oturumu da düşüyor. "Parola değişince diğer oturumlar düşmüyor" riski YOK.
- Login açık yönlendirme (GV-006) ve kaba kuvvet kilidi mevcut; SMTP hedefi `outbound_guard` ile korunuyor (hem kayıt hem test); DB restore PGDMP sihirli bayt kontrolü var.
- Onay akışlarında kendi kendini onaylama: bu kapsamdaki modüllerde onay/onaylama route'u bulunamadı (yalnız `raporlar_onay_zinciri` salt okunur); uygulanamaz.
- Alt kurum izolasyonu: `accessible_tenant_ids` bayi/normal için yalnız kendi tenant'ı, holding için kendi + alt kurumlar; sub-tenant işlemleri `parent.id == current_user.tenant_id` ile sınırlı (kardeş/üst kuruma erişim yolu bulunamadı).
- 2FA bekleyen oturumla başka route'a erişim: `_pending_2fa_user_id` `login_user` çağrılmadan hiçbir korumalı route'u açmıyor; atlatma yolu bulunamadı.

## Öncelik sırası (öneri)
F-001 -> F-002/F-004 (birlikte) -> F-003 -> F-005/F-015 -> F-006 -> F-007 -> F-009 -> geri kalanlar.
