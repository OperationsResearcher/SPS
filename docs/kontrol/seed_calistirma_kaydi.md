# Seed script çalıştırma kaydı — ortam bazında

> Amaç: "yerel ≠ Test/Demo/Yayın" (eksik paket/modül/kart) sorununu önlemek.
> Kod deploy'u (`git pull` / tarball) **DB seed çalıştırmaz** — her seed script'i ortam başına ayrı elle tetiklenmeli.
> Kural: `docs/SUNUCU-GUNCELLEME-REHBERI.md` §8 madde 4.
>
> Her yeni seed script yazıldığında buraya satır ekle. Bir ortamda çalıştırıldığında ilgili hücreyi
> tarihle işaretle. Durum bilinmiyorsa **"?"** yaz — sessizce "yapıldı" varsayma, `--dry-run` ile kontrol et.

| Script | Yerel | Test | Demo | Yayın | Not |
|---|---|---|---|---|---|
| `seed_l2_module_gating.py` | ✅ (tarih bilinmiyor) | ✅ 2026-07-05 | ✅ 2026-07-05 | ? | Eksik 5 system_modules kodu + Master Package bağı. Test+Demo'da sequence drift vardı → `sync_pg_sequence_if_needed('system_modules','id')` sonra çalıştı. |
| `seed_l2_paketler.py` | ✅ (tarih bilinmiyor) | ✅ 2026-07-05 | ✅ 2026-07-05 | ? | Başlangıç/Yönetim/Strateji paketleri. `seed_l2_module_gating.py`'ye bağımlı (önce o çalışmalı). |
| `seed_yonetim_ozeti_kartlari.py` | ✅ (2026-07 öncesi) | ✅ 2026-07-21 (DB yerel kopyası) | ? | ✅ 2026-07-21 | YO01-09 meta. Öncesinde kart keşfi şart. |
| `seed_sp_kart_aciklamalari.py` | ✅ (tarih bilinmiyor) | ✅ 2026-07-21 (DB yerel kopyası) | ? | ✅ 2026-07-21 (içerik md5 doğrulandı) | system_cards içeriği Yayın=Yerel birebir (501 kart, toplu md5 eşit). |
| `seed_card_descriptions.py` | ✅ 2026-07-24 (501/501) | ✅ 2026-07-24 (sıfırdan dump) | ? | ✅ 2026-07-24 (501 güncellendi, ort. 464) | Zengin açıklama (9× `card_descriptions_*.py`). Önkoşul: Text migration `391945351814`. |
| `seed_l3_ileri_moduller.py` | ? | ? | ? | ? | |
| `seed_raporlar_modulu_strateji.py` | ? | ? | ? | ? | |
| `seed_component_module_gating.py` | ? | ? | ? | ? | |
| `seed_kart_component_eslestirme.py` | ? | ? | ? | ? | |
| `seed_ornek_kart.py` | ? | ? | ? | ? | Muhtemelen yalnız yerel/demo örnek verisi — Yayın'da istenmeyebilir, çalıştırmadan önce kullanıcıya sor. |
| `seed_generic_tenant.py` | ? | ? | ? | ? | Tenant oluşturur — Yayın'da dikkat (kullanıcı verisi kırmızı çizgi). |
| `seed_bogazici_strategies.py` | ? | ? | ? | ? | Örnek/demo veri olabilir. |
| `seed_boun_sample_project.py` | ? | ? | ? | ? | Örnek/demo veri olabilir. |
| `seed_kmf_full.py` | ? | ? | ? | ? | |
| `seed_tomofil_full.py` | ? | ? | ? | ? | Demo ortamının Tomofil baseline'ı ile ilişkili olabilir — bkz. `docs/DEMO-ORTAMI-PLAN.md`. |

## Kullanım

1. Yeni bir seed script yazdığında: tabloya bir satır ekle, Yerel'de çalıştırdığında o hücreyi işaretle.
2. Test/Demo/Yayın'a deploy ederken (§8 madde 4): bu tabloda ilgili ortam hücresi boş/`?` olan script'leri
   `--dry-run` ile o ortamda kontrol et. Rapor "eksik" derse kullanıcıya danış → çalıştır → tabloyu güncelle.
3. `?` = durum hiç doğrulanmadı, **"yapılmadı" ile aynı muamele et** (varsayım yapma).
