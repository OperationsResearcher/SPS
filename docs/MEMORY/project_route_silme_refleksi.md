---
name: project_route_silme_refleksi
description: "Legacy route silerken ZORUNLU refleks: hem Python hem template url_for referanslarını tara (BuildError 500 tuzağı)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

**Strangler temizliğinde (legacy route silme) sert ders (2026-06-17):** Bir `main_bp` route'unu silmek, o
endpoint'e kalan `url_for('main.X')` çağrılarını **iki ayrı yüzeyde** kırık bırakır → çağıran sayfa
render/redirect anında **BuildError → 500**:
1. **Python tarafı:** başka route fonksiyonlarındaki `redirect(url_for('main.X'))` (yetki-reddi/hata akışları).
2. **Template tarafı:** CANLI render edilen template'lerdeki `{{ url_for('main.X') }}`.

İlk turlarda sadece route gövdesini sildim, referansları kovalamadım → 2 tur sonra **çift hasar** patladı
(35 Python ref + ~45 template ref, canlı sayfalar sessizce 500 veriyordu: help_center 8 kırık ref, doküman
merkezi, executive dashboard, admin feedback, proje detay…).

**ZORUNLU REFLEKS — her route silme commit'inde, AYNI commit içinde:**
1. Sil.
2. `grep -rn "url_for(['\"]main.X['\"]" app/ micro/ main/ ui/ bsc/ templates/ --include=*.py --include=*.html` (safe_url_for hariç).
3. CANLI olanları (route 302/200; template'i render eden route canlı mı runtime test_client ile) modern endpoint'e çevir.
   Eşleme runtime redirect hedefinden: dashboard→app_bp.masaustu, kurum_paneli→app_bp.kurum, surec*→app_bp.surec,
   admin_panel→app_bp.yonetim_paneli, projeler→app_bp.project_list, gorevlerim/performans_kartim/redmine→app_bp.bireysel_karne,
   stratejik*→app_bp.sp.
4. `safe_urls.py` `_LEGACY_ENDPOINT_FALLBACK`'e de ekle (geriye-uyum ağı; düz url_for bunu KULLANMAZ ama eski bookmark'lar için).
5. Hedef endpoint'lerin varlığını + `url_for` çözümlemesini runtime'da doğrula (BuildError yok).

Eski `templates/` (render edilmeyen ölü) içindeki ref'ler sorun değil — ama template RENDER ediliyorsa (canlı route'tan)
mutlaka düzelt. [[project_teknik_borc_haritasi]] [[project_strangler_karari]]
