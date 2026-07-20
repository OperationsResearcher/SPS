# BÜYÜK KEŞİF — 2026-07-21

> 132.000 satırlık Kokpitim kod tabanının 6 uzman şapkasıyla taranması.
> **Hiçbir kod değiştirilmedi** — bu klasör yalnızca bulgu ve öneri içerir.

## Nereden başlamalı

👉 **[00-YONETICI-OZETI.md](00-YONETICI-OZETI.md)** — en kritik 8 bulgu, ortak kök neden, öncelik sırası

## Kapsam

| | |
|---|---|
| Python | 328 dosya · 75.944 satır |
| JavaScript | 88 dosya · 22.559 satır |
| Şablon | 167 dosya · 25.051 satır |
| CSS | 9.009 satır |
| Route | 858 (556 GET'i gezildi) |
| DB tablosu | 170 · 259 FK kısıtı |

## Ham raporlar

| Dosya | Uzman | Bulgu |
|---|---|---|
| [01-frontend.md](ham/01-frontend.md) | Kıdemli frontend | 15 + 5 UX önerisi |
| [02-guvenlik.md](ham/02-guvenlik.md) | Sistem yöneticisi / güvenlik | 10 + olumlu doğrulamalar |
| [03-backend-hesap.md](ham/03-backend-hesap.md) | Backend / hesaplama | 14 + 4 şüpheli |
| [04-metodoloji.md](ham/04-metodoloji.md) | Stratejik planlama gurusu | 12 + 5 stratejik öneri |
| [05-i18n-veri.md](ham/05-i18n-veri.md) | i18n / veri akışı | 14 |
| [06-kullanici-yolculugu.md](ham/06-kullanici-yolculugu.md) | Ürün kalite | 15 + 2 özet tablo |

## Yöntem

1. **Paralel tarama** — 6 uzman ajan, her biri kendi bölgesini satır satır
2. **Bağımsız doğrulama** — her kritik bulgu ana oturumda DB'den veya kod çalıştırılarak teyit edildi
3. **Yanlış alarm ayıklama** — 3 uzman iddiası ölçümle çürütüldü ve raporda düzeltildi

Doğrulanmamış hiçbir iddia rapora girmedi. Emin olunamayanlar "ŞÜPHELİ" olarak ayrı işaretlendi.

## Bulgu kodları

| Önek | Alan |
|---|---|
| `B` | Backend / hesaplama motoru |
| `F` | Frontend / JS / şablon |
| `S` | Güvenlik / sistem |
| `M` | Metodoloji (SP literatürü) |
| `I` | i18n / çeviri |
| `D` | Veri / model tutarlılığı |
| `K` | Kullanıcı yolculuğu (uçtan uca test) |
