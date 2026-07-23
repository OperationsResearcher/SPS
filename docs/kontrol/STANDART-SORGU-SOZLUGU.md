# Standart Sorgu Sözlüğü — Kart / Modal

> Kullanıcı kısa ID veya “standart değil” dediğinde **tahmin etme**.
> Kısa ID → `system_cards.short_id`. Kabuk ile iç etkileşimi ayır.

---

## 1. Dil → ne kontrol edilir?

| Kullanıcı cümlesi (örnek) | Anlam | Kontrol seti |
|---------------------------|--------|--------------|
| “KR28 standartlarımızda değil” | **Kart kabuğu** görsel standarda uymuyor | §2 Kart görsel |
| “SPDN03 kartı standartta mı?” | Aynı — kabuk checklist | §2 |
| “SPDN03’te mühüre basınca gelen modal standartta değil” | Kart **içindeki** etkileşim → **modal** standardı | §3 Modal |
| “(i) modalı bozuk / standart değil” | Kart bilgi modalı (`#kk-card-info-modal`) | §2 madde (i) + §3 yapı |
| “Bu sayfa kart standardında değil” | Sayfadaki kartların çoğuna §2 uygula | `KART-STANDART-ILERLEME.md` |

**Kural:** Kısa ID + “modal/mühür/buton/dialog” geçiyorsa önce §3; yalnız kısa ID + “kart/standart” ise §2.

---

## 2. Kart görsel standardı (checklist)

Otorite: `docs/KURALLAR-MASTER.md` §5.1 · `docs/paketler/KART-KATMANI-TASARIM.md` · `docs/MEMORY/project_kart_gorsel_standardi.md`

Kısa ID verildiğinde (örn. KR28):

1. DB: `system_cards` satırı — `short_id`, `code`, `description`, `is_active`
2. Template/JS: `data-card-code="<code>"` var mı?
3. Başlık: `mc-card-title` veya `mc-stat-label` + mini FontAwesome ikon
4. **(i)** herkese görünür; `description` dolu; modal `renderInfoBody` / `#kk-card-info-modal`
5. Sağ üst **short_id** yalnız Admin; tıklanamaz / kopyalama yok
6. base.html değiştiyse `python pybasla.py` restart (stale JS tuzağı)

Önek hatırlatma: MA masaüstü · SP/SPDN sp · PR süreç · KR k-rapor · KD k-radar · RP raporlar · PJ proje …

---

## 3. Modal standardı (checklist)

Otorite: `docs/KURALLAR-MASTER.md` §5

Uygun:

```html
<div class="mc-modal-overlay" id="…">
  <div class="mc-modal-lg">  <!-- veya mc-modal / mc-modal-sm -->
    <div class="mc-modal-header">… <button class="mc-modal-close">✕</button></div>
    <div class="mc-modal-body">…</div>
    <div class="mc-modal-footer">
      <button class="mc-btn mc-btn-secondary">…</button>
      <button class="mc-btn mc-btn-primary">…</button>
    </div>
  </div>
</div>
```

SweetAlert2 **yalnız:** onay (`confirm`) · başarı/hata toast · kısa bilgi.

**Sapma sayılır:** Alpine/özel popup · Swal’ı form/modal olarak kullanmak · inline rastgele overlay · Bootstrap modal (platform kart/SP akışında)

SPDN03 örneği: kart = `sp_donemler.tum_donemler` (dönem tablosu). Mühür butonu → açılan UI §3’e tabi; kart kabuğu ayrıca §2.

---

## 4. Yanıt formatı (zorunlu)

Kullanıcıya tek seferde:

1. **Kart:** `short_id` → `code` → dosya yolu (template/JS)
2. **Kapsam:** kabuk (§2) mi, iç etkileşim (§3) mi, ikisi mi?
3. **Sonuç:** UYUYOR / SAPMA — madde madde (kanıt: dosya:satır veya DOM sınıfı)
4. Düzeltme istenmediyse kod yazma; istendiyse onay sonrası uygula

---

## 5. Hızlı ID çözümü

```text
Yerel DB veya kod:
  short_id = 'SPDN03'  →  code ≈ sp_donemler.tum_donemler  →  ui/templates/platform/sp/donemler.html
  short_id = 'KR28'    →  code ≈ k_rapor_paydas.paydas_anket_ozeti  →  k_rapor şablon/JS
```

Belirsizse tek soru: “Kabuk (ikon/(i)/ID) mi, yoksa tıklanınca açılan modal mı?”
