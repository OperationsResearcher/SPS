# -*- coding: utf-8 -*-
"""Raporlar modülü — 93 route, 6 dosya.
=============================================================================

NEDEN "faz" İSİMLERİ? (2026-07-15 notu)
Dosyalar geliştirme sırasına göre adlandırıldı (faz0…faz5), alanına göre
değil. İlk yorum "yeni rapor önerileri için staging bölüm — kullanıcı
sonradan uygun modüle taşıyacak" diyordu; taşıma olmadı ve bu yapı fiilen
KALICI. Artık öyle davranıyoruz: yeniden adlandırma ayrı bir iş (bkz. §Not),
ama hangi raporun nerede olduğu aşağıda yazılı — kod okurken buradan bak.

ÖNEMLİ: Dosya adları kronolojik ama URL'ler ve endpoint adları alan-bazlı
(`/reports/cfo-dashboard` → `app_bp.raporlar_cfo_dashboard`). Dosya taşımak
URL'leri KIRMAZ (72 template `url_for` çağrısı fonksiyon adına bağlı,
dosya yoluna değil). Yani yeniden adlandırma yapılabilir; yapılmadı çünkü
kazanç (isim netliği) ~5000 satırlık diff'i şu an haklı çıkarmıyor.

-----------------------------------------------------------------------------
HANGİ RAPOR NEREDE
-----------------------------------------------------------------------------
routes.py        landing — /reports

routes_faz0.py   21 route · Veri kalitesi + strateji analizi + AI özet
                 data-quality · k-vector-skewness · alignment-sankey
                 target-revision · department-performance · executive-leadership
                 initiative-bubble · morning-summary · evolution-film
                 ai-presentation

routes_faz1.py   28 route · "Hızlı kazanç" karışık küme (EN BÜYÜK, en karışık)
                 sunburst · vrio-portfoy · okr-cascade · initiative-roadmap
                 muda-analysis · cmmi-heatmap · operation-statistics
                 individual-alignment · risk-heatmap · two-fa · carbon-trend
                 ai-advisor · ai-coach · early-warning

routes_faz2.py   10 route · Persona dashboard'ları (tutarlı küme)
                 cfo-dashboard · coo-dashboard · chro-dashboard
                 quarterly-review · strategy-story

routes_faz3.py   13 route · Premium dosya ürünleri (tutarlı küme)
                 strategic-annual · investor-presentation · esg-report
                 audit-package · individual-scorecard-batch

routes_faz4.py   10 route · Sektörel paketler + AI NLP
                 sectoral · sectoral/<code> · nlp-query · sektor-benchmark

routes_faz5.py   11 route · Büyük altyapı MVP
                 mobile · bi-connector · ml-anomaly · approval-chain
                 pi-project-impact

routes_esg.py     7 route · ESG metrik + değer girişi (L3 Dal 4)
                 esg-management

-----------------------------------------------------------------------------
NOT — yeniden adlandırma adayı
-----------------------------------------------------------------------------
faz2 (persona) ve faz3 (premium dosya) zaten tutarlı kümeler; faz0/faz1 ise
karışık. Yeniden adlandırılırsa öneri:
    faz2 → personas.py · faz3 → premium_dosyalar.py · faz4 → sektorel.py
    faz5 → altyapi_mvp.py · faz0/faz1 → alanlarına bölünür
Yapılırken: fonksiyon adları DEĞİŞMEMELİ (url_for'lar kırılır).
"""
from . import routes  # landing — defines /reports
from . import routes_faz0  # noqa: F401
from . import routes_faz1  # noqa: F401
from . import routes_faz2  # noqa: F401
from . import routes_faz3  # noqa: F401
from . import routes_faz4  # noqa: F401
from . import routes_faz5  # noqa: F401
from . import routes_esg  # noqa: F401  # L3 Dal 4 — ESG metrik + değer girişi
