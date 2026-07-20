# YIL BAZLI SİSTEM — Çalışma Klasörü

> **Durum: HASAR TESPİTİ.** Uygulama başlamadı, başlamayacak — kapsam netleşip
> kullanıcı onayı gelene kadar hiçbir kod değişikliği yapılmaz.
>
> Açılış: 2026-07-20 · Dal: `claude/fix-pg-yil-hedef`

---

## Neden bu klasör var

Hedef ilkesi (kullanıcı, 2026-07-20):

> "Tüm sistem yıl bazlı olmalı. Stratejik Planlamanın her aşaması, stratejiler,
> süreçler, projeler dahil. Süreçlerin ve projelerin içindeki tüm bilgiler, PG'ler,
> bağlar, PG ile ilgili tüm bilgiler — her şey ama her şey yıl bazlı olmalı.
> Kullanıcı hangi yılda çalışmak istediğini seçtiğinde o yıla göre gelmeli her şey,
> tüm K-Radar vs ama her şey."

Denetim sonucu: **sistem bugün bu ilkeye uymuyor.** Yıl altyapısı kısmen var,
kısmen yok, kısmen var ama kullanılmıyor. Kapsam tek commit'e sığmaz — bu bir
program. Bu klasör o programın tek gerçek kaynağıdır.

---

## Dosyalar

| Dosya | İçerik |
|---|---|
| [`HASAR-TESPITI.md`](HASAR-TESPITI.md) | **Ana belge.** Katman katman ne çalışıyor, ne bozuk, kök neden |
| [`OLCUMLER.md`](OLCUMLER.md) | Ham sayısal ölçümler — KMF veri kıyası, hardcoded yıl dağılımı |
| [`SORULAR.md`](SORULAR.md) | Sorular + kararlar — S1-S15, K5-K9, T1-T13 · **tümü kapandı** |
| [`UYGULAMA-PLANI.md`](UYGULAMA-PLANI.md) | **Uygulama planı** — 3 faz, dosya/satır/migration/doğrulama · onay bekliyor |
| [`SONRAKI-ISLER.md`](SONRAKI-ISLER.md) | Kapsam dışı işler — **yıl bazlı iş bitince** yapılacak, birikiyor |

Kıyas script'i: [`scripts/ops/pg_yil_hedef_kiyas.py`](../../scripts/ops/pg_yil_hedef_kiyas.py)
— salt okunur, hiçbir yazma yapmaz.

---

## Tespit edilen üç seviye — özet

| Seviye | Kapsam |
|---|---|
| ✅ **Doğru** | SWOT/TOWS/PESTEL/Porter, Misyon-Vizyon, OKR, BSC, Süreç, KpiData, Faaliyet takibi, Raporlar Faz0/Faz3-vizyon/Faz5, SP Analiz |
| ⚠️ **Kırılgan** | K-Rapor (17 API) — yıl filtreliyor ama frontend `?year` göndermezse takvim yılına düşüyor, session'a bakmıyor |
| ❌ **Bozuk** | K-Radar/Analiz (yıl kavramı yok), Masaüstü, Raporlar Faz4, PG yazma yolu, Proje/Görev, Blue Ocean, VRIO, Süreç-Strateji bağı |

**Kök neden:** Merkezî çözücü [`app/services/date_sovereign.py`](../../app/services/date_sovereign.py)
`get_view_year()` olarak **zaten yazılmış** ama tüm sistemde onu import eden
**tek modül** var. Onun yerine **72 noktada** `date.today().year` hardcoded —
her biri kullanıcının yıl seçimini sessizce yok sayıyor.

Hatanın sessiz olmasının sebebi bu: ekran yanlış veriyi hatasız gösteriyor.

---

## Sonraki adım

**Hasar tespiti kapandı. Kapsam kapandı. Uygulama planı yazıldı.**

Tüm sorular cevaplandı (S1-S15, K5-K9, T1-T13). Mimari kararlar
[`SORULAR.md` §M](SORULAR.md)'de: full-clone tek mekanizma (T9), `PlanProject`
ana model (T10), kapalı yıllar taslağa (T11), `kpi_data` yılın PG kopyasına (T12),
kesintisiz uygulama (T13).

Plan → [`UYGULAMA-PLANI.md`](UYGULAMA-PLANI.md). **Kullanıcı onayı bekliyor** —
onay gelene kadar kod değişikliği yok (K3).
