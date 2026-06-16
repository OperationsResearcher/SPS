# kokpitim.com (apex) erişim düzeltmesi

## Durum (2026-05-22)

| Adres | Durum |
|-------|--------|
| `https://www.kokpitim.com` | Çalışıyor |
| `https://kokpitim.com` (apex) | Cloudflare üzerinden zaman aşımı (522) |
| Oracle VM (`129.159.30.175`) | Çalışıyor — container `kokpitim-web`, `/health` OK |

**Kök neden:** Origin SSL sertifikasında yalnızca `www.kokpitim.com` var; `kokpitim.com` yok. Cloudflare **Full (strict)** modunda apex için origin’e bağlanırken sertifika uyuşmazlığı → zaman aşımı.

## Hızlı çözüm A — Cloudflare yönlendirme (önerilen, 2 dk)

Cloudflare → **kokpitim.com** → **Rules** → **Redirect Rules** → Create rule:

- **If:** Hostname equals `kokpitim.com`
- **Then:** Static redirect → `https://www.kokpitim.com${uri.path}` — **301**

Kullanıcılar `kokpitim.com` yazsa da `www`’ye gider; origin apex SSL sorunu bypass edilir.

## Hızlı çözüm B — SSL modu (geçici)

Cloudflare → **SSL/TLS** → Overview → **Full** (strict değil).

Ardından VM’de:

```bash
sudo certbot certonly --nginx -d www.kokpitim.com -d kokpitim.com --expand --non-interactive
sudo nginx -t && sudo systemctl reload nginx
```

Sonra Cloudflare’i tekrar **Full (strict)** yapın.

## Kalıcı çözüm — DNS TXT (Let’s Encrypt)

VM’de betik çalışıyorsa talimat dosyası:

`/opt/kokpitim/backups/acme_dns_kokpitim.com.txt`

Cloudflare → DNS → **TXT** kaydı:

| Alan | Değer |
|------|--------|
| Name | `_acme-challenge` |
| Content | *(dosyadaki değer)* |
| Proxy | DNS only (gri bulut) |

Yayılım sonrası (1–15 dk):

```bash
sudo bash /opt/kokpitim/app/scripts/ops/oracle/fix_kokpitim_apex_ssl.sh
```

Doğrulama:

```bash
curl -fsS https://kokpitim.com/health
openssl x509 -in /etc/letsencrypt/live/www.kokpitim.com/fullchain.pem -noout -text | grep -A1 "Subject Alternative"
```

Beklenen SAN: `DNS:kokpitim.com` ve `DNS:www.kokpitim.com`.

## Alternatif — @ kaydını geçici DNS only

1. Cloudflare’de `@` A kaydını **Proxied → DNS only** (gri bulut) yapın.
2. VM’de: `sudo certbot certonly --nginx -d www.kokpitim.com -d kokpitim.com --expand`
3. `@` kaydını tekrar **Proxied** (turuncu) yapın.

## İlgili betikler

- `scripts/ops/oracle/fix_kokpitim_apex_ssl.sh`
- `scripts/ops/oracle/acme_dns_auth_hook.sh`
