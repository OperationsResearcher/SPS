# D7 — SİNAPS API TASARIM STANDARTLARI v1.0
> REST + OpenAPI 3.1 · versiyonlama · hata formatı · pagination · idempotency · rate limit
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Bağımlılık: D1–D6 (özellikle ADR-04, ADR-09)

---

## 1. Temel İlkeler

1. **REST + OpenAPI 3.1.** GraphQL yok, tRPC yok (ADR-04).
2. **JSON only.** `Content-Type: application/json; charset=utf-8`. Binary upload `multipart/form-data`.
3. **HTTPS zorunlu.** HTTP 308 → HTTPS.
4. **Tenant context implicit.** Path'te tenant_id yok; JWT claim'inden çıkarılır.
5. **Backend snake_case, JSON snake_case** (Python ile uyum). Frontend `api-client` paketinde tip dönüşümü yapılmaz; TS de snake_case kabul eder.
6. **Resource-oriented URL'ler.** Fiil yok; aksiyonlar alt-resource (`/cancel`, `/publish`).
7. **Stateless.** Server-side session yok; JWT taşır.

---

## 2. URL Yapısı

### 2.1 Tabanca
```
https://api.sinaps.app/v1/{resource}
```

### 2.2 Versiyonlama
- URL path'inde major: `/v1/`, `/v2/`. Minor değişiklik (additive) sürüm artırmaz.
- Bir major sürüm en az **18 ay** desteklenir; deprecation header'ı:
  `Sunset: Wed, 01 Jan 2028 00:00:00 GMT`
  `Deprecation: true`

### 2.3 Hiyerarşi
```
GET    /v1/tenants/{tenant_id}/strategy/plans
POST   /v1/tenants/{tenant_id}/strategy/plans
GET    /v1/tenants/{tenant_id}/strategy/plans/{plan_id}
PATCH  /v1/tenants/{tenant_id}/strategy/plans/{plan_id}
DELETE /v1/tenants/{tenant_id}/strategy/plans/{plan_id}

# Alt resource
GET    /v1/tenants/{tenant_id}/strategy/plans/{plan_id}/okrs
POST   /v1/tenants/{tenant_id}/strategy/plans/{plan_id}/okrs

# Aksiyon (idempotent değilse POST)
POST   /v1/tenants/{tenant_id}/strategy/plans/{plan_id}/publish
POST   /v1/tenants/{tenant_id}/execution/initiatives/{id}/stage-gates/{gate}/decide
```

> Not: `tenant_id` URL'de bulunur ama yetki JWT'den gelir. URL ile JWT çatışırsa **403 Forbidden**.

### 2.4 Adlandırma
- Resource = çoğul isim: `plans`, `okrs`, `risks`
- Kebab-case path segment: `stage-gates`, `early-warning-signals`
- Query parametre snake_case: `?page_size=50&include_deleted=false`

---

## 3. HTTP Metod Anlamları

| Metod | Anlam | Idempotent | Body |
|-------|-------|:---:|:---:|
| GET   | Oku | ✅ | ❌ |
| POST  | Oluştur veya aksiyon | ❌ (idempotency-key ile ✅) | ✅ |
| PUT   | Tam yer değiştir | ✅ | ✅ |
| PATCH | Kısmi güncelle (JSON Merge Patch — RFC 7396) | ❌ | ✅ |
| DELETE | Soft delete | ✅ | ❌ |

> **PATCH** = JSON Merge Patch (sade). JSON Patch (RFC 6902) kullanılmaz — istemcide karmaşık.

---

## 4. Status Code Sözleşmesi

| Kod | Anlam | Ne zaman |
|-----|-------|----------|
| 200 | OK | GET, PATCH, PUT başarılı |
| 201 | Created | POST yeni kaynak |
| 202 | Accepted | Async iş kuyruğa alındı; `Location: /v1/jobs/{id}` |
| 204 | No Content | DELETE başarılı |
| 400 | Bad Request | Validation, format hatası |
| 401 | Unauthorized | JWT yok/geçersiz |
| 403 | Forbidden | JWT geçerli, yetki yok (OPA reddetti) |
| 404 | Not Found | Yok veya RLS sebebiyle "yok gibi" |
| 409 | Conflict | Versiyon çakışması (optimistic lock), slug çakışması |
| 410 | Gone | Hard-deleted (GDPR) |
| 412 | Precondition Failed | `If-Match` ETag uyumsuz |
| 422 | Unprocessable Entity | İş kuralı reddi (örn. Stage-Gate sıralaması) |
| 423 | Locked | Plan kilitli (publish edilmiş, edit kısıtlı) |
| 429 | Too Many Requests | Rate limit; `Retry-After` header |
| 500 | Internal Server Error | Beklenmeyen sunucu hatası |
| 502/503/504 | Gateway/Available/Timeout | Bağımlı servis hatası |

**Önemli kural:** RLS sızıntısı yapma — yetkisiz tenant erişiminde **404 (Not Found)**, asla 403 (varlığını ifşa etmek olur). Tek istisna: kullanıcı kaynağın varlığını başka şekilde biliyorsa (URL paylaşımı) → 403 + minimal mesaj.

---

## 5. Hata Formatı (RFC 7807 + uzantı)

```json
{
  "type": "https://docs.sinaps.app/errors/validation",
  "title": "Validation failed",
  "status": 400,
  "code": "validation_error",
  "detail": "OKR objective is required.",
  "instance": "/v1/tenants/.../okrs",
  "trace_id": "01H...ULID",
  "errors": [
    { "field": "objective.tr", "code": "required", "message": "Bu alan zorunlu." },
    { "field": "key_results", "code": "min_length", "message": "En az 1 KR olmalı." }
  ]
}
```

- `code`: stabil string ID (frontend i18n için). Asla string değişmez.
- `trace_id`: OpenTelemetry trace_id (W3C traceparent). Loglara bağ.
- `errors[]`: 400/422 için field-level detay.
- **Hassas bilgi yok**: stack trace, DB query, internal path → sadece loga, response'a değil.

---

## 6. Pagination

### 6.1 Cursor-based (varsayılan — tüm liste endpoint'leri)
```
GET /v1/tenants/{t}/strategy/okrs?page_size=50&cursor=eyJpZCI6...

Response:
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6...",   // null ise son sayfa
    "page_size": 50,
    "has_more": true
  }
}
```
- `page_size`: 1–200, default 50
- Cursor opaque base64; içeride `(sort_key, id)` taşır
- Offset-pagination **yok** (büyük ofsetlerde Postgres yavaşlar)

### 6.2 Sıralama
```
?sort=-updated_at,name
```
- `-` prefix = desc. Beyaz listede olmayan alan → 400.

### 6.3 Filtreleme
```
?status=active&owner_id=uuid&period=2026-Q1
?created_after=2026-01-01&created_before=2026-04-01
```
- Karmaşık filtre = ayrı `POST /search` endpoint (body'de filtre DSL).

### 6.4 Field selection
```
?fields=id,title,owner_id
```
- Bandwidth tasarrufu; mobile için önemli.

### 6.5 Expand (include)
```
?include=owner,key_results,plan
```
- Beyaz liste; N+1 patlamasını önlemek için maksimum 3 seviye.

---

## 7. Idempotency

### 7.1 POST için Idempotency-Key

```
POST /v1/tenants/{t}/strategy/plans
Idempotency-Key: 01H...ULID
```
- Aynı key + aynı body → aynı sonuç (24 saat cache)
- Aynı key + farklı body → 409
- Stage-Gate karar verme, ödeme tetikleme, batch import için **zorunlu**

### 7.2 Optimistic Locking (PATCH/PUT/DELETE)

```
GET /v1/.../plans/{id}
→ ETag: W/"42"

PATCH /v1/.../plans/{id}
If-Match: W/"42"
→ 200 (yeni ETag) veya 412 Precondition Failed (versiyon değişti)
```
- ETag = `version` kolonundan
- Eksik `If-Match` → izin verilir ama uyarı log (kademeli sıkılaştırma)

---

## 8. Authentication & Authorization

### 8.1 Auth
- Bearer JWT, RS256 (Keycloak)
- `Authorization: Bearer <token>`
- Token süresi: access 15dk, refresh 12 saat
- Service-to-service: Keycloak client_credentials grant

### 8.2 JWT Claim'leri (gerekli)
```json
{
  "sub": "<keycloak_sub>",
  "user_id": "<uuid>",
  "tenant_path": "tomofil.eu.berlin",
  "tenant_paths": ["tomofil.eu.berlin"],   // çok-tenant durumda array
  "roles": ["strategy_editor","okr_owner"],
  "package": "enterprise",
  "exp": 1747459200
}
```

### 8.3 Yetki Kontrolü (OPA — ADR-09)
- FastAPI middleware her request'te OPA'ya:
  ```
  input: { user, action, resource, tenant_path, package }
  ```
- OPA yanıtı: `{allow: true|false, reason: "..."}`
- Reddedilirse 403 (RLS kuralı saklı — bkz §4)

### 8.4 API Key (3rd party)
- Tenant başına oluşturulur (admin UI)
- `Authorization: Bearer sk_live_...`
- Scope'lu (read-only, write-strategy vs.)
- Per-key rate limit + audit

---

## 9. Rate Limiting

### 9.1 Politika
| Tier | Genel | Auth endpoint | AI endpoint |
|------|-------|---------------|-------------|
| Starter | 60/dk/user | 10/dk | 5/dk |
| Pro | 300/dk/user | 20/dk | 30/dk |
| Enterprise | 1000/dk/user | 60/dk | 200/dk |
| Enterprise+ | Özel | Özel | Özel |

### 9.2 Header'lar (RFC 9239 draft uyumlu)
```
RateLimit-Limit: 1000
RateLimit-Remaining: 947
RateLimit-Reset: 42
Retry-After: 42   (yalnız 429'da)
```
- Algoritma: Token bucket (Redis)
- Tenant başına ek limit (paket bazlı)

---

## 10. Bulk / Batch Endpoint'leri

```
POST /v1/tenants/{t}/strategy/okrs/batch
{
  "operations": [
    {"op":"create", "data":{...}},
    {"op":"update", "id":"...", "data":{...}, "if_version": 3},
    {"op":"delete", "id":"..."}
  ]
}

Response 207 Multi-Status:
{
  "results": [
    {"status":201, "id":"...", "data":{...}},
    {"status":412, "error":{...}},
    {"status":204}
  ]
}
```
- Maksimum 100 operasyon/istek
- Tek transaction (`atomic: true` flag) veya bağımsız (`atomic: false`)
- Idempotency-Key burada da geçerli

---

## 11. Long-Running İş (Async)

```
POST /v1/tenants/{t}/imports/excel
→ 202 Accepted
  Location: /v1/jobs/{job_id}
  {"job_id":"...", "status":"queued"}

GET /v1/jobs/{job_id}
→ 200
  {"id":"...", "status":"running|succeeded|failed",
   "progress": 0.42, "result_url": null, "error": null}
```
- SSE alternatifi: `GET /v1/jobs/{job_id}/stream` (text/event-stream)
- Webhook opsiyonu: oluştururken `?notify_webhook_id=...`

---

## 12. Webhook'lar (Outbound)

### 12.1 Konfigürasyon
```
POST /v1/tenants/{t}/webhooks
{
  "url": "https://customer.example/sinaps-hook",
  "events": ["okr.updated","stagegate.decision_made"],
  "secret": "..."  // HMAC
}
```

### 12.2 Delivery
```
POST customer URL
Headers:
  X-Sinaps-Event: okr.updated
  X-Sinaps-Delivery-Id: 01H...
  X-Sinaps-Signature: sha256=...   (HMAC-SHA256(secret, body))
  X-Sinaps-Timestamp: 1747459200
Body: domain event (D3 §8 katalog şeması)
```
- Retry: exponential backoff, 24 saat
- 2xx başarı; 4xx kalıcı hata (durdurulur), 5xx geçici (retry)
- İmza doğrulama zorunlu; 5dk timestamp toleransı

---

## 13. Versiyonlama Davranış Sözleşmesi

**Breaking değişiklik = yeni major:**
- Alan kaldırma
- Alan tipini değiştirme
- Zorunluluk ekleme
- Enum değer kaldırma
- Default değişimi (semantik)
- Hata `code` string değişimi

**Non-breaking (minor):**
- Yeni opsiyonel alan
- Yeni endpoint
- Yeni enum değer (istemci unknown handle etmeli)
- Performans iyileştirme

---

## 14. OpenAPI Üretimi

- FastAPI native `app.openapi()` → `contracts/openapi/v1.yaml`
- CI her main merge'de regenerate → repo'ya commit
- TS SDK: `packages/api-client` → `openapi-typescript` ile otomatik
- Mobile aynı SDK'yı tüketir
- Public docs: Scalar veya Redocly statik build → `docs.sinaps.app`

---

## 15. Standart Header'lar

### Request
| Header | Zorunlu | Açıklama |
|--------|:---:|----------|
| Authorization | ✅ | Bearer JWT/API key |
| Accept-Language | — | `tr-TR`, `en-US` (yoksa user.locale) |
| Idempotency-Key | POST için önerilen | ULID/UUID |
| If-Match | PATCH/PUT için önerilen | ETag |
| traceparent | — | W3C trace propagation |

### Response
| Header | Açıklama |
|--------|----------|
| ETag | Resource versiyonu |
| Last-Modified | RFC 7231 tarih |
| Cache-Control | Genel: `no-store`; statik için `max-age=...` |
| RateLimit-* | §9.2 |
| X-Trace-Id | Trace ID (debug için) |
| Deprecation, Sunset | §2.2 |

---

## 16. CORS

- Allow-Origin: tenant config'inden (allowlist; `*` yok)
- Allow-Methods: GET, POST, PATCH, PUT, DELETE, OPTIONS
- Allow-Headers: Authorization, Content-Type, Idempotency-Key, If-Match, traceparent
- Allow-Credentials: true (cookie-tabanlı admin UI için)
- Max-Age: 86400

---

## 17. i18n Davranışı

- İstemci `Accept-Language: tr-TR,en;q=0.8`
- Sunucu: `translatable` alanları **tüm dilleri** döner (JSONB), istemci kendi seçer
- Hata mesajları: server-side i18n yok; `code` döner, frontend çevirir
- Tarih/sayı formatlama: tamamen frontend

---

## 18. Caching

- GET kaynak: `ETag` + `Cache-Control: private, must-revalidate`
- Liste: cache yok (varsayılan), tenant izolasyonu sebebiyle
- Statik (paket tanımı, SDG listesi): `public, max-age=3600`
- CDN: sadece public marketing site

---

## 19. Güvenlik Header'ları (Response)

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'  (API için)
Permissions-Policy: geolocation=(), camera=(), microphone=()
```

---

## 20. Örnek Endpoint — OKR Oluştur

```http
POST /v1/tenants/01HA.../strategy/plans/01HB.../okrs HTTP/1.1
Host: api.sinaps.app
Authorization: Bearer eyJ...
Content-Type: application/json
Idempotency-Key: 01HZX...
Accept-Language: tr-TR

{
  "level": "bu",
  "owner_type": "workspace",
  "owner_id": "01HC...",
  "objective": { "tr": "AB pazarında EV payını %15'e çıkar", "en": "..." },
  "period": "2026",
  "key_results": [
    {
      "title": { "tr": "Berlin tesisi üretim hacmi" },
      "metric_id": "01HK...",
      "baseline": 12000, "target": 30000, "unit": "adet",
      "confidence": 70
    }
  ]
}
```

```http
HTTP/1.1 201 Created
Location: /v1/tenants/.../okrs/01HD...
ETag: W/"1"
X-Trace-Id: 4bf92f3577b34da6a3ce929d0e0e4736

{
  "id": "01HD...",
  "level": "bu",
  ...
  "version": 1,
  "created_at": "2026-05-16T10:24:00Z"
}
```

---

## 21. Anti-Patterns (Yapma)

- `/getOkrs`, `/createOkr` — fiil URL
- 200 + `{"error":"..."}` — hata gizleme
- Liste endpoint'i offset pagination
- DELETE'in hard delete olması
- Hata mesajını UI'a doğrudan yansıtmak (i18n bozulur — `code` kullan)
- SQL hatasını response'da göstermek
- Tenant ID query parametresi (path'te olmalı)
- `id` alanı integer (UUID/ULID kullan)

---

## 22. Onay

Onaylanırsa **D8 — Marka Mimarisi Önerisi** (Kokpit Group umbrella + Kokpitim + Sinaps konumlandırma) yazılır.

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi
