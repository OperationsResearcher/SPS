# 03 - Güvenlik ve Veri Koruma Denetimi

Tarih: 2026-10-10 | Kapsam: salt okunur statik inceleme (Yerel kod tabanı). Canlı sunuculara istek yapılmadı. Gizli anahtar değeri rapora yazılmadı.
Yöntem: grep/AST taraması, kritik route'ların elle okunması, `pip-audit -l` (yerel .venv; yalnızca PyPI/OSV advisory sorgusu).
Kapsanmayan: 176 `get_or_404/query.get` çağrısının tamamı (örneklem yapıldı), 365 JS `innerHTML` kullanımı (örneklenmedi), Test/Yayın ortamının gerçek env değerleri.

## Olumlu gözlemler
- `config.py`: SECRET_KEY varsayılanı yok, tanımsızsa uygulama başlamıyor. Çerezler Secure/HttpOnly/SameSite=Strict. CSRF açık.
- Repo'da `.env`/`*.pem`/`*.key`/`*.dump` izlenmiyor (`git ls-files`); yalnızca `.env.example`, `.env.template`, `.env.production.example` var. Anahtar benzeri satırlar placeholder kalıbı taşıyor (gerçek anahtar kalıbı `AIza...` bulunmadı).
- Login throttle: e-posta+IP bazlı, Redis destekli. `/demo/end` GET ile sıfırlama kapatılmış. `next` parametresi kısmen doğrulanıyor.
- Oturum gerektirmeyen route AST taraması: kalanlar pazarlama, demo, health, SSO, TOTP challenge, legacy yönlendirmeler - beklenen kamusal yüzey; korumasız veri route'u bulunmadı.
- Admin route'larında (kullanıcı düzenleme, logo, bildirim silme) tenant kontrolü var. SocketIO oda katılımı `_can_access_process` ile kontrollü.

## Bulgular

### GV-001 - Kurumsal doküman merkezi: kiracılar arası listeleme ve indirme (IDOR)
- Dosya:satır: `api/routes_files.py:289-297` (liste), `:413-430` (indirme)
- Kanıt: Liste sorgusu `scope=='CORPORATE'` ve `is_active` filtreler, kurum/tenant filtresi yok. İndirme `ProjectFile.query.get_or_404(file_id)` sonrası yalnızca `scope` kontrol eder, kurum karşılaştırması yok; ardından `send_file(corporate_file.file_path.lstrip('/'))`. Proje dosyası indirmesi (`:469-486`) ise `project.kurum_id` kontrolü yapıyor - tutarsızlık.
- Açıklama: Oturum açmış herhangi bir kullanıcı başka kurumların "kurumsal" dosyalarını listeleyip `file_id` tahminiyle indirebilir.
- Koşul: `api_bp` kayıtlı (`app/__init__.py:615-620`), geçerli oturum yeterli; ID'ler sıralı tam sayı.
- Etki: Kiracılar arası gizli doküman sızıntısı.
- Önem: Yüksek | Etiket: kesin (kod okumasıyla; çalışma zamanında denenmedi)
- Çözüm: ProjectFile'ı kuruma bağla (kolon yoksa kullanıcı->kurum üzerinden); liste ve indirmede `current_user` kurumuyla filtrele; indirmede yolu sabit klasöre `basename` ile kilitle.
- Efor: 0.5-1 gün | Doğrulama: iki kurumlu test; B kullanıcısı A'nın file_id'sini indirince 403/404.

### GV-002 - Tenant LLM `base_url` doğrulanmadan kullanılıyor (SSRF)
- Dosya:satır: `micro/modules/sp/routes_tenant_ai.py:67` (kayıt), `app/services/llm_gateway.py:107` (OpenAI istemcisi `base_url`), `:256`
- Kanıt: `cfg.base_url = (d.get("base_url") or "").strip() or None`; şema/host allowlist yok; `/ai-config/test` ucu da var.
- Açıklama: `_can()` yetkili kurum yöneticisi, sunucunun iç ağ/metadata/loopback adreslerine istek yaptırabilir; hata mesajlarıyla yanıt sızabilir; ayrıca API anahtarı keyfi hosta gider.
- Koşul: Kurum yöneticisi hesabı + OpenAI uyumlu sağlayıcı. | Etki: iç servis keşfi. | Önem: Orta-Yüksek | Etiket: olası
- Çözüm: https zorunlu, host allowlist veya çözümlenen IP'nin özel/loopback/link-local olmasını reddet.
- Efor: 0.5 gün | Doğrulama: `http://127.0.0.1:5001` ve link-local adres kayıtta reddedilmeli.

### GV-003 - CSRF muafiyeti (63 kullanım)
- Dosya:satır: `micro/modules/sp/routes_tenant_ai.py:48-50` (API anahtarı/base_url yazan POST `@csrf.exempt`); diğerleri `sp/routes_*`, `admin/routes_setup_import.py`, `admin/routes_admin_tools.py`, `raporlar/routes_faz4.py`, `shared/kule/routes.py`
- Açıklama: SameSite=Strict hafifletici, ancak muafiyet savunma derinliğini kaldırır; `SESSION_COOKIE_SAMESITE` env ile gevşetilebiliyor (`config.py:97`); GV-002 ile zincirlenebilir.
- Önem: Orta | Etiket: iyileştirme/olası | Çözüm: muafiyetleri kaldırıp fetch'lerde `X-CSRFToken` gönder. Efor: 2-3 gün | Doğrulama: tokensız POST 400.

### GV-004 - Bağımlılık açıkları (pip-audit: 185 bulgu, yerel .venv)
- Dosya: `requirements.txt` (çoğu `>=`, kilit dosyası yok; `Flask-SocketIO==5.3.5`, `python-socketio==5.10.0`, `marshmallow==3.20.1` sabit).
- Kanıt: python-socketio 5.10.0 (düzeltme 5.14.0/5.16.2), python-engineio 4.13.1 (4.13.2), werkzeug 3.1.7 (3.1.9), urllib3 2.6.3 (2.8.0), pypdf 6.12.1, weasyprint 68.1 (70.0), ayrıca cryptography, pillow, pyjwt 2.8.0, aiohttp, idna, mako, oauthlib, pyasn1. `eventlet 0.33.3` yüklü ama kullanılmıyor. Advisory uygulanabilirliği tek tek doğrulanmadı.
- Önem: Orta | Etiket: kesin (sürüm), etki olası
- Çözüm: pip-compile ile kilit + güncelleme, regresyon testi. Efor: 1-2 gün | Doğrulama: `pip-audit` temiz/kabul listesi. Not: Yayın image sürümleri yerelden farklı olabilir; doğrulanamadı.

### GV-005 - CSP `script-src 'unsafe-inline'`
- Dosya:satır: `app/__init__.py:111,115`
- Açıklama: ~76 inline script/55 inline handler nedeniyle gerekçeli; XSS bulunursa CSP engellemez. `|safe` kullanımları (`ui/templates/platform/kurum/ayarlar.html:94-95`, `index.html:427,671`, `_hierarchy_help.html:34`) sabit/çeviri metni, kullanıcı girdisi görünmüyor. 365 `innerHTML` kullanımı örneklenmedi.
- Önem: Orta | Etiket: iyileştirme | Çözüm: nonce tabanlı CSP'ye aşamalı geçiş; innerHTML'de kullanıcı verisi için `textContent`. Efor: 1-2 hafta.

### GV-006 - Açık yönlendirme (kısmi)
- Dosya:satır: `app/routes/auth.py:95-106`
- Kanıt: `not parsed.netloc and not parsed.scheme` kontrolü; `/\evil.com` gibi değerler netloc üretmez, tarayıcı `//` gibi yorumlayabilir. `session['next']` kontrolsüz saklanıyor (kullanımı doğrulanmadı).
- Önem: Düşük-Orta | Etiket: olası | Çözüm: `startswith('/') and not startswith('//') and '\\' not in raw_next`. Efor: 15 dk | Doğrulama: `?next=/\evil.com` yerel landing'e düşmeli.

### GV-007 - Demo modu: parolasız tenant_admin girişi
- Dosya:satır: `micro/modules/demo/routes.py:120-160`
- Açıklama: `KOKPITIM_DEMO_MODE=1` ise herkes GET ile kurum admin'i olarak girer (tasarım gereği, KURALLAR §8.4). Bayrağın Test/Yayın'a sızması tam hesap ele geçirmedir; GET ile tetiklenir, rate limit görünmüyor; `_demo_admin_for_tenant` son çare olarak tenant'taki herhangi bir kullanıcıyı seçiyor. Yayın'da kapalı olduğu koddan doğrulanamadı.
- Önem: Orta (Demo), Yayın'da sızarsa Kritik | Etiket: olası
- Çözüm: Yayın ortamında bayrak açıksa başlatmayı reddet; demo_start'a limiter, yalnız POST+CSRF. Efor: 0.5 gün.

### GV-008 - Rate limit depolaması `memory://` varsayılanı
- Dosya:satır: `config.py:136`; `app/utils/security.py:15`; `app/utils/login_throttle.py` (Redis yoksa bellek)
- Açıklama: Redis yoksa çok işçili gunicorn'da limitler işçi başına sayılır (KURALLAR §7 S3). 
- Önem: Orta | Etiket: kesin (yapılandırma), Yayın etkisi doğrulanamadı | Çözüm: Yayın'da `REDIS_URL` zorunlu. Efor: 0.5 gün.

### GV-009 - SocketIO CORS ve `debug=True`
- Dosya:satır: `app/extensions.py:50` (`SOCKETIO_CORS_ORIGINS=*` mümkün), `app.py:56` (`debug=True`, 127.0.0.1)
- Açıklama: `*` env ile açılabilir; debug yalnız yerel bağlı. Önem: Düşük | Etiket: iyileştirme | Çözüm: üretimde `*` reddet, debug'ı env'e bağla.

### GV-010 - Yükleme ve dosya yolu güveni
- Dosya:satır: `api/routes_files.py:136-180, 336-375`, indirme `:425`
- Açıklama: Uzantı+MIME doğrulaması ve `secure_filename` var (olumlu). Zayıflıklar: `.zip/.rar/.doc/.xls` kabul, antivirüs yok; dosyalar `static/uploads/...` altında - doğrudan statik servis ediliyorsa GV-001 kontrolü bypass olur (nginx/static yapılandırması incelenmedi); indirmede DB'deki `file_path` doğrudan `send_file`'a gider.
- Önem: Orta | Etiket: olası | Çözüm: yüklemeleri statik kök dışına al, yalnızca yetkili route ile sun. Efor: 1 gün.

### GV-011 - f-string SQL
- Dosya:satır: `app/services/tenant_clone_service.py:168,341`, `services/tenant_backup_service.py:342`, `app/services/hoshin_xmatrix_service.py:30`, `quarterly_review_service.py:143`, `demo_reset_service.py:139-235`, `app/utils/db_sequence.py:178`
- Açıklama: Tablo/sütun adları koddan/kataloğdan geliyor; kullanıcı girdisi gözlenmedi. hoshin/quarterly f-string parçalarının kaynağı tam doğrulanmadı.
- Önem: Düşük | Etiket: iyileştirme | Çözüm: tablo adı allowlist/quote_ident. Efor: 0.5 gün.

### GV-012 - Şifreleme anahtarı yönetimi
- Dosya:satır: `app/utils/encryption.py:26-45`, `app/models/tenant_llm_config.py:19`
- Açıklama: Üretimde ENCRYPTION_KEY zorunlu (olumlu). İki ayrı anahtar (ENCRYPTION_KEY / LLM_ENCRYPTION_KEY), rotasyon (MultiFernet) ve anahtar yedeği belgesiz; kayıp = BYOK anahtarları kaybı.
- Önem: Düşük-Orta | Etiket: iyileştirme | Efor: 1 gün.

### GV-013 - Parola politikası ve eski kod kopyası
- Dosya:satır: `micro/modules/admin/routes.py:620-622` (yönetici parola atamasında karmaşıklık kontrolü görülmedi). `Kalder/` dizini git'te izlenmiyor (0 dosya) ama içinde `csrf.exempt` içeren kopya kod var; dağıtıma girmediğini doğrula.
- Önem: Düşük | Etiket: olası | Efor: 0.5 gün.

### GV-014 - HSTS/HTTPS
- `Talisman force_https=False` (`app/__init__.py`); HSTS `security.py:75` koşullu. TLS nginx'te (kod dışı), doğrulanamadı. Önem: Düşük | Etiket: iyileştirme.

## Doğrulanamayanlar
Canlı yapılandırma (Redis, demo bayrağı, nginx static alias), CVE uygulanabilirliği, JS innerHTML XSS, 176 `get_or_404` çağrısının tamamı (özellikle `api/` ve `main/` legacy).

## Öncelik listesi
- P0: GV-001
- P1: GV-002, GV-004, GV-007, GV-010
- P2: GV-003, GV-005, GV-006, GV-008, GV-012
- P3: GV-009, GV-011, GV-013, GV-014
