# Veri Çekme — Yayın → Yerel

> Kural: `docs/KURALLAR-MASTER.md` §8.6 · Script: `scripts/ops/yayin_yerele_cek.py`
> Bu belge **yordam ve tuzaklar**. Kuralın kendisi MASTER'da.
> Son ölçüm: 2026-07-15

---

## Ne zaman

Kullanıcı **"yayındaki verileri yerele çek"** dediğinde. Otomatik değil, planlı değil.

Amaç: gerçek veriyle yerel test + Yayın'ın yedeğini almak.

---

## Yön kuralı — tek cümle

**Yapı yukarı, veri aşağı.**

```
Şema (yapı) :  Yerel ──► Yayın     alembic, kod deploy
Veri        :  Yayın ──► Yerel     bu yordam
```

Bu iki ok asla ters çevrilmez. Veriyi yukarı itmek müşteri verisini ezer; şemayı aşağı çekmek migration geçmişini bozar.

---

## Komut

```bash
python scripts/ops/yayin_yerele_cek.py              # KONTROL — hiçbir şey yazmaz
python scripts/ops/yayin_yerele_cek.py --calistir   # çek
```

Yalnız kıyas isterseniz:
```bash
python scripts/ops/yayin_yerel_kiyas.py --out docs/kontrol/kiyas.md
```

---

## Neden tablo listesi yok

**Bilerek yok.** Elle tutulan liste bakılmadığı gün yalan söyler: yeni tablo eklenir, listeye yazılmaz, senkronizasyon onu sessizce atlar. Kimse fark etmez — veri kaybolana kadar.

Bu teorik değil. Kod tabanında canlı örneği var: `scripts/ops/compare_db_counts.py` **6 tablo** listeliyor, oysa DB'de **169 tablo** var. Bayatlamış.

Onun yerine:
- `pg_dump` → **her şeyi** alır
- kıyas aracı → tabloları **`pg_tables`'tan okur**

Yeni tablo eklendiğinde ikisi de otomatik kapsar. **Bu tasarımı "iyileştirip" liste eklemeyin.**

### Otomatik sınıflandırma da çalışmaz

`tenant_id` var mı diye bakıp "müşteri verisi" ayırmayı denedim — **yanlış cevap verdi**. `kpi_data` (366.716 satır, en değerli veri) `tenant_id` taşımıyor; bağı `process_kpi_id → process_id → processes.tenant_id` üzerinden dolaylı. Şemaya bakan her sınıflandırma bunu kaçırır.

---

## Akış — script yapar

| # | Adım | Neden |
|---|------|-------|
| 1 | **Kıyas** | "Yerelde Yayın'da olmayan ne var?" — ezilecekleri gösterir |
| 2 | **Yerel yedek** | Geri dönüş noktası (`backups/yayin/yerel_ONCESI_*.dump`) |
| 3 | **Yayın dump** | `pg_dump`, salt okunur — **aynı zamanda Yayın yedeği** |
| 4 | **Restore** | Yerele tam yazım |
| 5 | **`alembic upgrade head`** | Şemayı geri getirir (yapı yerelde ileri) |
| 6 | **Kıyas** | Kayıp doğrula |

**1 ve 6 listeyi gereksiz kılar.** Atlanan tablo diye bir şey olamaz — hiçbir tablo adı yazılı değil.

---

## Güvenlik kilidi

Adım 1'de "yerelde fazla" bulunursa script **durur**. O satırlar restore'da silinecek.

Bilinçli eziyorsanız: `--yine-de`. **Kilidi kaldırmayın.**

2026-07-15 ölçümünde 24 tabloda yerel öndeydi — en büyükleri `bsc_kpi_perspectives` (-420), `system_cards` (-216), `system_components` (-176), `system_pages` (-165).

---

## Yayın'a asla yazılmaz

Yayın'daki tek işlem `pg_dump` (salt okunur). Container silinir, iz bırakılmaz.

**Kimlik bilgisi dışarı çıkarılmaz:** dump container'ın *kendi içinde* `$DATABASE_URL` ile üretilir, sonra dosya olarak çekilir. `DATABASE_URL` geliştirme makinesine hiç inmez.

---

## Yedek — bedava gelir

Adım 3'ün çıktısı `backups/yayin/yayin_<tarih>.dump` **Yayın'ın gerçek yedeğidir**. Silmeyin.

⚠️ **Yerele kopya tek başına yedek DEĞİLDİR.** Yerel makine bozulursa ikisi de gider. Gerçek yedek = bu dump dosyası, ayrı diskte.

---

## Çekim sonrası — yapı geri getirme

Restore Yayın'ın yapı tablolarını da getirir, yani **yereldeki yapı işi geride kalır**:

```bash
# seed'ler
python scripts/seed_kart_component_eslestirme.py
python scripts/seed_ornek_kart.py
python scripts/seed_sp_kart_aciklamalari.py
python scripts/seed_l2_paketler.py
python scripts/seed_l3_ileri_moduller.py
python scripts/seed_component_module_gating.py
python scripts/seed_l2_module_gating.py

# kart keşfi: Admin > Kart Yönetimi > Keşfet
```

⚠️ **Seed'den doğmayanlar** (ölçüldü 2026-07-15) — bunlar geri gelmez:

| Tablo | Yerel | Nereden doğar |
|---|---:|---|
| `system_pages` | 165 | Admin > Kart Yönetimi keşif düğmesi (route) |
| `bsc_kpi_perspectives` | 1.260 | Kullanıcı ekranı (`micro/modules/sp/routes_analysis.py`) |

`bsc_kpi_perspectives`: 3 kurum × 420 satır, hepsi 2026-05-29'da toplu üretilmiş (tenant 27/58/85 — test kurumları). Yayın'da 840 = 2 kurum. Fark, ID kaymış test kurumundan; **gerçek müşteri verisi değil**.

---

## Bilinen tuzaklar

### ID kayması
Aynı kurum iki tarafta farklı ID'de — Temmuz taşımasının (`project_tenant_1_27_28_migration_2026-07-07`) izi:

| Kurum | Yayın | Yerel |
|---|---:|---:|
| YeniTomofil | 57 | 76 |
| Yeniçağ | 56 | 77 |
| tom1/2/3 | 59-61 | 83-85 |

Tam restore bunu **çözer** (Yayın ID'leri gelir). Ama yereldeki eski ID'lere bağlı hiçbir şeye güvenmeyin — bookmark, elle yazılmış script, not.

**Ders:** satır sayısı kıyası ID kaymasını "eksik kurum" sanır. 2026-07-15'te tam bunu yaşadım: rapor "3 kurum eksik" dedi, **adlarla** eşleştirince gerçek eksiğin bambaşka 3 kurum olduğu çıktı. Kurum farkı incelerken **isimle eşleştir**, ID'yle değil.

### Sequence drift
Restore sonrası `setval` yapılmazsa ilk yeni kayıtta PK çakışması. `pg_restore` sequence'leri dump'tan getirir; yine de çekim sonrası ilk kayıt denemesi patlarsa buraya bakın.

### Yutulan hata transaction'ı abort eder
PostgreSQL dersi (`project_tenant_clone_transaction_dersi`): `try/except` ile yutulan hata transaction'ı abort eder, sonraki `COMMIT` sessizce rollback olur. Restore script'lerinde hata yutmayın.

---

## 2026-07-15 ölçümü — referans

İlk tam kıyas. 169 tablo, 68 kıyaslanan, **39'u birebir aynı**.

**Asıl iş verisi zaten senkrondu:**

| Tablo | Yayın | Yerel |
|---|---:|---:|
| `kpi_data` (PGV) | 366.716 | 366.716 ✅ |
| `processes` | 380 | 380 ✅ |
| `individual_kpi_data` | 19.159 | 19.159 ✅ |
| `individual_performance_indicators` | 1.668 | 1.668 ✅ |

**Yayın'da fazla olanlar:** `notifications` (+10.986 — ortam izi, çekilecek içerik değil), `tenants` (+3), `users` (+3), `demo_requests` (+1), `system_modules` (+1).

**Gerçekten yerelde olmayan 3 kurum** — ama içleri boş:
```
Kara Brothers        kullanıcı=1  süreç=0  PG=0  PGV=0  strateji=0
VolTure Tech (pasif) kullanıcı=1  süreç=0  PG=0  PGV=0  strateji=0
VolTure Tech         kullanıcı=2  süreç=0  PG=0  PGV=0  strateji=0
```
Kayıt olmuş, hiç kullanmamış. Çekmenin kazancı yok.
