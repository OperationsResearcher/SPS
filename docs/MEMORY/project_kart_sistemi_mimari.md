---
name: project_kart_sistemi_mimari
description: "Kart/sayfa/paket hiyerarşisi, DB tabloları, mekanizma — tam mimari belgeye işaretçi"
metadata: 
  node_type: memory
  type: project
  originSessionId: 91906003-7dd8-45ad-a61f-27ad19461258
---

KART SİSTEMİ tamamlandı (2026-06-23). Otorite belge:
**docs/paketler/KART-SISTEMI-MIMARI.md** — her kart/sayfa/paket işinde ÖNCE bunu oku.

HİYERARŞİ: Paket(4) → Modül(13) → Bileşen(35) → Kart(343) → Veri(card_data_sources).
Ayrıca Sayfa kataloğu (system_pages, 68). Hepsi `app/models/saas.py`.

DB tabloları (PostgreSQL): subscription_packages, system_modules, system_components,
module_component_slugs, package_modules, system_cards (short_id+description+code=<sayfa>.<kart>),
card_data_sources, system_pages (short_id modül-kısa: MA/RP-CD/KR-K).

short_id önekleri: MA=masaustu SP=sp PR=process PK=karne PJ=project KD=k-radar
KR=k-rapor(81) RP=raporlar(179). Toplam 343 kart.

MEKANİZMA: ui/templates/platform/base.html merkezî — (i) butonu herkese, kart short_id
rozeti + sayfa ID rozeti yalnız Admin (role.name=='Admin'). API'ler
micro/modules/admin/routes.py: card-info, cards-meta(GET), page-meta(Admin 403), discover.
Keşif: app/services/card_discovery_service.py (template tarar, JS taramaz).
Migration zinciri: c3d4e5f6a7b8 → d4e5f6a7b8c9 → e5f6a7b8c9d0.

**Why:** Devasa çok-oturumlu iş; gelecekte tutarlı davranmak için tek referans gerekti.

**How to apply:** Yeni/değişen kart → KART GÖRSEL STANDARDI (sol ikon+başlık+(i), sağ ID).
JS-üretilen kartlar keşifle bulunmaz, elle DB'ye yazılır + helper'a code param.
Template/route/base değişince `python pybasla.py` RESTART (auto-reload güvenilmez).
Toplu-meta endpoint GET olmalı (POST CSRF'e takılır). DB'ye güven, ajana değil.
[[project_kart_gorsel_standardi]] [[project_yerel_stale_surec_5001]] [[project_yedekleme_ve_db]]
