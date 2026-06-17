# Ölü Static Arşivi

## pwa/ (2026-06-17)
Terk edilmiş PWA/Service Worker zinciri — runtime teyitli ölü:
service-worker.js, pwa-manager.js, push-manager.js (static/js/modules/), sw.js (static/).

Kanıt: hiçbir template (modern ui/templates VEYA eski templates/ + base.html zinciri)
bu dosyaları yüklemiyor/register etmiyor (grep=0). Modern platform (ui/static, /m yolu)
kendi PWA'sını kullanmıyor. pwa-manager register('/static/js/service-worker.js')
yapıyordu ama pwa-manager'ı hiçbir canlı sayfa yüklemiyor → zincir hiç başlamıyor.

## NOT — static/ temizliği neden burada durdu
Eski static/js, static/css içinde daha çok ölü aday VAR (~45) ama RİSKLİ:
templates/base.html (CANLI — 18 template extend ediyor, canlı route'lardan render)
bir sürü CSS/JS'i url_for('static', filename=...) ile yüklüyor (custom.css, layout.css,
responsive.css, loading-states.css, kpi-cards-modern.css, inline-edit.js, layout.js,
loading-manager.js, kule.js...). Bunlar CANLI. Otomatik ölü-analiz base.html paylaşımlı
zincirini güvenilir çözemedi. Bu yüzden sadece kesin-ölü PWA alındı; gerisi her dosyayı
elle base.html+extends zincirine karşı doğrulamayı gerektirir (düşük getiri, yüksek risk).
