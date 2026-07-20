# Geçiş Promptu — Yeni Sohbet İçin

> Bu dosyayı yeni sohbetin başına yapıştır. 2026-07-17 oturumunun devamı.

---

## Nerede kaldık — bir cümle

Kokpitim'in analitik/rapor araçlarını **3 katmanlı mimariye** böldük ve
**UYGULAMASI TAMAMLANDI** (Faz 0-6, `main`'e merge'li). Sıra: açık borçlar + Yayın.

## KATMAN MİMARİSİ — UYGULANDI ✅ (tekrar tartışma AÇMA)

Üç katman URL'de canlı, çalışıyor (ölçüldü):

| Katman | URL öneki | Route | Rol |
|---|---|---|---|
| 1. Girdi | `/k-plan/*` | 216 | Yaz + anlık yönet (TEK SAHİP) |
| 2. Teşhis | `/k-radar/*` | 77 | Gör (SALT-OKU) |
| 3. Rapor | `/k-report/*` | 136 | Konsolide + dağıt (k_rapor+raporlar birleşti) |

- Eski adresler (`/sp`, `/reports`, `/k-rapor`…) **kalıcı 307 redirect** — kırılmadı.
- Endpoint adları hiç değişmedi → ~64 template'e dokunulmadı.
- URL dili İngilizce konu (`/k-plan/strategy/swot`), ekran metni Türkçe.
- **602 passed, sıfır regresyon, 4 smoke paketi 70/70. Yayın'a ÇIKMADI** (yerelde birikiyor).

**Otorite belgeler (OKU):**
- `docs/kontrol/KATMAN-MIMARISI-YOL-HARITASI.md` — 6 faz, ne yapıldı, bulgular
- `docs/kontrol/ENDPOINT-SOZLESMESI.md` — endpoint adı sözleşmesi + faz detayları
- `docs/kontrol/KATMAN-MIMARISI-YEREL-TEST.md` — kullanıcının elle test rehberi

**⚠️ URL yazım tuzağı:** `//k-plan/...` (çift slash) 404 verir — tarayıcı `k-plan`'ı
sunucu adı sanar. Tek slash doğru: `http://127.0.0.1:5001/k-plan/strategy/swot` → 200.
Linkler doğru üretiliyor; sadece adres çubuğuna elle yazarken dikkat.

**Yeni katman öneki eklenirse 6 DOSYA aynı commit'te güncellenir** (yol haritası §Faz 6):
`_GATED_PREFIX_MODULE` · `_ROLE_GATED_PREFIX_MODULE` · `module_registry` ·
`legacy_sunset::_is_platform_canonical` · `app/__init__.py::sections` ·
`hata_kontrol_service::_MODULE_MAP`. Path önekine bakan kapılar SESSİZCE açılır — dikkat.

## AÇIK İŞLER — kullanıcı kararı bekliyor
1. **🔻 Tenant 28'in 10 gerçek riski** — `source_type`'ta kategori değeri taşıyor
   (`Finansal`/`Operasyonel`…), seed'de kolon yanlış anlaşılmış. Migration dokunmadı
   (gerçek müşteri verisi). Karar: kategori ayrı kolona mı, kaynağa mı eşlensin?
2. **🔻 Ölü proje zinciri** — `sp/projeler.html` + `sp_projeler.js` + 6 route. TASK-258.
3. **🔻 Rapor katmanı sidebar'da yok** — K-Radar hub'dan erişiliyor. Ayrı tasarım kararı.
4. **TASK-258** — 29 kırık route + mock model temizliği (harita hazır, izin bekliyor).
5. **Fiyat modeli / MCP** — ticari kararlar (`docs/oneri/`).
6. **Yayın deploy** — tüm katman işi yerelde; kullanıcı "yayına çıkalım" derse.

## Bu oturumda tamamlanıp PUSH edilenler
- **Katman mimarisi Faz 0-6** (TASK-274…277) — 3 katman URL'de canlı.
- **Yayın→Yerel veri çekme** yordamı + ilk gerçek koşu. Yerel artık Yayın kopyası:
  tenant 13, users 451, kpi_data 366.716. **admin@kokpitim.com / MfG_4660 açılıyor.**
- Yönetim Özeti kart açıklamaları (YO01-YO09).
- Analiz forecast "[object Object]" düzeltmesi (AN04).

## KRİTİK UYARILAR (yeni oturum BİLMELİ)
- **Şifre sızıntısı:** `MfG_4660` (Yayın admin) `scripts/docs/take_screenshots.py`
  içinde, PUBLIC repoda, Mayıs'tan beri. Kullanıcı "ben hallederim" dedi —
  ŞİFREYİ KODA/COMMIT MESAJINA/ÇIKTIYA YAZMA.
- **Repo PUBLIC** (OperationsResearcher/SPS) — push'a müşteri adı/şifre/IP karışmasın.
- **CI çalışmıyor** (GitHub Actions hesap kilidi, Haziran'dan). Yeşil tik = koşmadı.
  Geçerli doğrulama: `python -m pytest -q` + `scripts/ci/yerel_kontrol.py --hizli`.
- **pybabel update KULLANMA** — i18n katalogunu bozuyor.
- **Yerel DB = PostgreSQL 18** (sqlite değil). pg_dump/restore `C:\pgdata\bin`.
  `DATABASE_URL` env shell'de sqlite'a takılabilir → create_app'in URL'sini kullan.
- **Yayın DB host'ta** (`sudo -u postgres pg_dump kokpitim_db`), Test/Demo container'da.
- **Branch disiplini:** main'e doğrudan commit YOK. merge/push/deploy sadece kullanıcı
  "merge edelim/push'la/yayına çıkalım" deyince. L paketleri: iş yerelde birikir.
- **Terminoloji:** Yerel/Test/Demo/Yayın de, "VM"/"production" deme.
- **base.html/route değişince** `python pybasla.py` ile yeniden başlat (auto-reload güvenilmez).

## İlk adım (yeni oturumda)
Kullanıcıya sor: açık işlerden hangisi öncelikli — tenant 28 risk kategorisi (karar
gerekli), TASK-258 temizlik, yoksa katman mimarisini Yayın'a çıkarma hazırlığı mı?
Mimari TAMAM olduğu için artık uygulama değil, KARAR + deploy sırası.
