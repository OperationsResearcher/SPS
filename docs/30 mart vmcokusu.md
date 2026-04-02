# Durum raporu: VM / kokpitim.com erişim sorunu (30 Mart 2026)

## Yönetici özeti

30 Mart’ta **kokpitim.com** adresine giren kullanıcılar, siteyi bazen **açılamayan / çok geç yanıt veren** bir hata ekranıyla karşılaştı; sorun kullanıcı internetinden veya Cloudflare’dan değil, **bizim sunucu tarafındaki yazılım ve ayarlarda** birikmiş risklerden kaynaklanıyordu. Teknik ekip, küçük ama hedefli bir yazılım güncellemesi sunucuya aldı, uygulamayı yeniden ayağa kaldırdı ve **canlı veritabanının yedeğini** güvenli şekilde kopyaladı; şu an sistem **normal sağlık kontrolünden geçiyor**. Aynı tablo tekrar etmesin diye ileride **düzenli yedek**, **doğru sunucu ortamı ayarları** ve **Redis olmadan rate-limit** gibi net kurallar izlenmeli; detaylar raporun devamında.

---

Bu belge, üretim VM’sinde yaşanan erişim ve zaman aşımı sorunlarının kök nedenleri, uygulanan çözümler, tekrar riski ve operasyonel önlemleri özetler. Teknik detaylar proje geçmişi ve sunucu kontrolleriyle uyumludur.

---

## 1. Gözleken semptomlar

- Tarayıcıda **Cloudflare hata sayfası**: **Error 524 — A timeout occurred** (`www.kokpitim.com`).
- Cloudflare teşhis diyagramında: kullanıcı ve Cloudflare kenarı sorunsuz; **origin (host)** tarafında hata.
- Amaç: kullanıcıların girdiği verinin kaybı riskine karşı sunucunun tekrar güvenilir yanıt vermesi ve gerekirse yedekleme.

**524 ne anlama gelir?** Cloudflare, origin ile TCP bağlantısını kuruyor ancak origin, belirlenen süre içinde (tipik üst sınır yaklaşık 100 saniye) tam bir HTTP yanıtı üretmiyor veya çok geç üretiyor. Bu, “sunucu kapalı”dan farklıdır; çoğunlukla **uygulama veya altyapı yanıtı geciktiriyor / kilitleniyordur**.

---

## 2. Sorunun olası ve doğrulanan nedenleri

### 2.1. Güvenlik başlığı kodunda `request.url` kullanımı

`after_request` içinde `set_security_headers`, HSTS için **`request.url`** kullanıyordu. Werkzeug 3 tarafında **Host** doğrulaması tetikleniyor; bazı isteklerde (boş veya güvenilir olmayan `Host`) **`SecurityError: Host '' is not trusted`** oluşabiliyordu. Bu tür bir hata, yanıtın düzgün tamamlanmasını bozup edge tarafında uzun bekleme / zaman aşımı algısına katkı verebilir.

**Kaynak (düzeltme öncesi davranış):** `app/utils/security.py` içinde `request.url` ile localhost kontrolü.

### 2.2. Rate limiter depolamasının Redis’e bağlanması

`config.py` içinde **`RATELIMIT_STORAGE_URL`**, fiilen **`REDIS_URL`** ortam değişkenine bağlanmıştı. **Konteyner içinde erişilebilir bir Redis yoksa** Flask-Limiter depolama katmanı istekler sırasında **bloklanabilir** veya çok uzun sürebilir — bu da **524** ile uyumlu bir senaryodur.

### 2.3. Cloudflare (ters vekil) ve `X-Forwarded-Proto`

Origin’a trafik HTTP ile gidiyor; kullanıcı tarafı HTTPS. **`ProxyFix` olmadan** `request.is_secure` ve türevi davranışlar tutarsız kalır; HSTS ve güvenli çerez mantığı ile birlikte kenar durumlarda sorun çıkabilir. Hotfix ile üretimde **`TRUST_PROXY=1`** ve **Werkzeug `ProxyFix`** eklendi.

### 2.4. Veritabanı bağlantısı

PostgreSQL kullanımında uzun süren veya kopuk bağlantılar da 524 benzeri geciktirebilir. Hotfix ile (PostgreSQL URI’si tanımlandığında) **`pool_pre_ping`**, **`pool_recycle`** ve **`connect_timeout`** ile dayanıklılık artırıldı; SQLite-only kurulumda `connect_timeout` yalnızca Postgres URI’si algılandığında eklenir.

### 2.5. Altyapı notları

- VM üzerinde **Docker konteyner** (`sps-web`) çalışır durumdaydı; sorun yalnızca “VM kapalı” değildi.
- Aynı makinede **PostgreSQL** içinde **`kokpitim_db`** bulunduğu doğrulandı; uygulama URI’si konteynerden **`host.docker.internal:5432`** üzerinden bu veritabanına gidiyordu.
- Yerel ağ / Cloudflare kaynaklı **dış `curl` zaman aşımı**, VM içi `/health` yanıtının normal olması ile çelişmeyebilir (firewall, ISS, test noktası).

---

## 3. Uygulanan çözümler

### 3.1. Kod hotfix’i (`hotfix/vm-cloudflare-524`)

`origin/main` (commit **9fb14bb**) tabanlı, **yalnızca VM’ye uygun minimal** değişiklikler:

| Dosya | Değişiklik |
|--------|------------|
| `app/utils/security.py` | HSTS: `request.url` kaldırıldı; `X-Forwarded-Proto` / `request.is_secure` ile sınırlı. |
| `app/__init__.py` | `FLASK_ENV=production` veya `TRUST_PROXY` ile **ProxyFix** middleware. |
| `config.py` | `RATELIMIT_STORAGE_URL` varsayılan **`memory://`**; Redis otomatik bağlantı kaldırıldı. `SQLALCHEMY_ENGINE_OPTIONS` (pool + Postgres için `connect_timeout`). |
| `Dockerfile` | `ENV FLASK_ENV=production`, `ENV TRUST_PROXY=1`; Gunicorn **`--timeout 90`**, **`--graceful-timeout 25`**. |

Dal **GitHub**’a push edildi: **`hotfix/vm-cloudflare-524`**.

### 3.2. VM deploy (30 Mart 2026)

1. `/home/kokpitim.com/public_html` altında **`sudo git fetch`**, **`sudo git checkout hotfix/vm-cloudflare-524`**, **`sudo git pull`**.
2. Mevcut konteyner ortamının kaybını önlemek için: **`docker exec sps-web env > /tmp/sps-web.env`**.
3. **`docker stop` / `rm`**, ardından **`docker build -t sps_web_final:latest .`**.
4. **`docker run`** ile:
   - `-p 80:5000`
   - `-v .../instance:/app/instance`
   - **`--env-file /tmp/sps-web.env`** (PostgreSQL URI, `SECRET_KEY`, vb.)
   - **`-e FLASK_ENV=production`**, **`-e TRUST_PROXY=1`**
   - **`--add-host=host.docker.internal:host-gateway`** (Postgres host adı için)

### 3.3. Doğrulama

- VM içi: **`curl http://127.0.0.1/health`** → **HTTP 200**, `database: ok`.

### 3.4. Veri yedekleri (yerel diske çekildi)

- **`kokpitim_db`** için **`pg_dump -Fc`** çıktısı.
- Konteyner **`kokpitim.db`** SQLite dosyası (volume ile aynı; tarih olarak VM’de daha eski görünse de, canlı veri için Postgres dump önceliklidir).

Yerel klasör: `backups/vm_pull/` (tarih damgalı dosya adları ve kısa README).

---

## 4. Bu sorun bir daha çıkabilir mi?

**Evet, koşullar tekrarlarsa benzer semptomlar görülebilir.** Özellikle:

- **`after_request` veya benzeri hook’ta** Host / URL erişimiyle Werkzeug’un **SecurityError** üretmesi.
- **Rate limiter** veya cache için **erişilemeyen Redis** URL’sinin tekrar varsayılan veya zorunlu hale getirilmesi.
- **PostgreSQL** erişilemezliği, kilit, aşırı yavaş sorgu veya havuz tükenmesi.
- **Cloudflare / origin** SSL modu veya yanlış port / firewall değişikliği.
- **Gunicorn** worker’larının tümünün uzun süre meşgul kalması (uzun süren istekler, dış API bekleme süresi sınırı yok).

Hotfix, yukarıdaki **en sık kod ve yapılandırma tuzaklarını** azaltır; garanti tek başına değildir.

---

## 5. Ne yapmalı, ne yapmamalı?

### Yapılması iyi olur

- **Deploy öncesi:** VM’de **PostgreSQL `pg_dump`** (veya kurumsal yedek politikası).
- **Deploy sonrası:** VM içi **`/health`**, ardından tarayıcıdan **giriş ve kritik sayfalar**.
- **Cloudflare arkasında** origin HTTP ise: **`ProxyFix`** ve **`TRUST_PROXY`**/ **`FLASK_ENV=production`** tutarlılığını koru.
- **`docker run`** ile ortamı kaybedilmemesi için: **`--env-file`** veya eşdeğeri dokümante edilmiş komut; `SQLALCHEMY_DATABASE_URI` ve `SECRET_KEY` asla repo içine yazılmaz.
- Rate limiting için Redis kullanılacaksa: **`RATELIMIT_STORAGE_URL`** açıkça ayarlanır ve Redis gerçekten erişilebilir olur; aksi halde **`memory://`** ile tek konteyner davranışı bilinçli seçilir.
- **`git fetch` / `pull`** VM’de dosya sahipliği yüzünden hata verirse: proje dizininde **`sudo`** ile git kullan (bu olayda zaten böyle çözüldü).

### Yapılmaması iyi olur

- **`request.url`** kullanmadan önce **Host doğrulaması** düşünmeden `after_request` içinde kullanmak.
- **`REDIS_URL`** tanımlı diye limiteri **otomatik Redis’e** bağlamak (Redis yoksa üretimi kilitleme riski).
- **`git reset --hard`** ile sunucudaki el ile yapılmış düzeltmeleri kaybetmek (PROJE-MASTER uyarısıyla uyumlu).
- Yedek almadan **veritabanı migration** veya büyük şema değişikliği.
- **`/tmp/sps-web.env`** gibi geçici dosyaları, içinde gizli anahtarlar varken uzun süre dünya okunur dizinde bırakmak (iş bitince silinmesi iyi pratik).

---

## 6. İlgili artefact’lar

- Git dalı: **`hotfix/vm-cloudflare-524`**
- Yerel patch (isteğe bağlı uygulama): **`patches/0001-hotfix-vm-Cloudflare-524-...patch`**, **`patches/VM_HOTFIX_README.txt`**
- Yerel DB yedekleri: **`backups/vm_pull/`**

---

## 7. Kısa özet cümle

Sorun, tek başına “sunucu kapalı” değil; **Cloudflare 524** ve loglarda görülen **Host / güvenlik başlığı**, **Redis’e bağlı rate limit** ve **ters vkil (HTTPS) uyumsuzluğu** riskleri bir araya gelince origin yanıtının gecikmesi veya bozulması ihtimali yüksekti. **Minimal hotfix dalı** ve **ortamı koruyan yeniden oluşturulmuş konteyner** ile VM yeniden ayağa kaldırıldı; **Postgres ve SQLite yedekleri** yerel alındı. Benzer sorunlar **yanlış yapılandırma veya altyapı değişikliği** ile yinelenebilir; yukarıdaki **yap / yapma** listesi ve düzenli yedek bunu yönetmeye yardımcı olur.
