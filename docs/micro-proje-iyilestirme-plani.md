# Micro Proje Yönetimi — İyileştirme Planı

> Kod incelemesi: `micro/modules/proje/*`, `micro/templates/micro/project/*`, `main/routes.py` (redirect), `models/project.py`  
> Amaç: modülün “dağınık / yarım / tutarsız” hissedilmesini gidermek; süreç modülü ve Micro tasarım diliyle hizalamak.

---

## 1. Mevcut durum — kısa teşhis

| Alan | Gözlem |
|------|--------|
| **Dil / marka** | Liste sayfası başlığı İngilizce (`Projects`), alt metin Türkçe; sekmeler ve URL’ler karışık (`/micro/project` vs `/proje` redirect). |
| **Veri modeli** | `Project` ve `Task` eski şema (`user`, `kurum`, `surec`); yetki ve form tarafı **`CoreUser` (`users`, `tenant_id`)** ile hizalandı. `manager` / `members` ilişkileri hâlâ `LegacyUser` → detayda isimler boş veya yanlış görünebilir. |
| **Portföy** | `portfolio_service` **`models.Process` + `kurum_id`** kullanıyor; Micro süreçler **`AppProcess` + `tenant_id`**. Stratejik skorlar tenant’ta yanlış/eksik süreç setiyle hesaplanabilir. |
| **UX tekrarı** | Detay sayfasında 4 sütunlu mini Kanban + ayrıca “Klasik Kanban” görünümü; kullanıcıda “iki Kanban” algısı. |
| **Görünümler** | Takvim/Gantt büyük ölçüde CDN + sayfa içi JS; RAID’de Bootstrap + Tailwind bir arada; hata/başarı geri bildirimi sayfaya göre farklı (`showToast` / Swal). |
| **routes.py** | Tek dosyada liste, CRUD, portföy, strateji, 4 görünüm, görev CRUD — bakım maliyeti yüksek. |
| **Silme** | Proje silme yalnızca `show_strategy` (üst yetki) ile gösteriliyor; detay layout’ta `</div>` kapanışı ile silme bloğu hizası zayıf. |

---

## 2. İyileştirme planı (öncelik sırasıyla)

### Faz A — Hızlı kazanımlar (1–3 gün)

1. **Tutarlı Türkçe UI**  
   - `list.html`: `title` / `page_title` → “Projeler” veya “Proje listesi”.  
   - Boş durum / buton metinleri tek dilde.

2. **Ekip / yönetici gösterimi**  
   - Detay ve liste: `project.manager` ve `project.members` yerine (veya yanında) **`CoreUser` ile çözümlü isim** (id eşleştirmesi veya küçük bir `display_user(user_id)` yardımcısı).  
   - Şablonlarda `u.username` yerine `u.email` fallback (CoreUser’da `username` yok).

3. **Detay sayfası bilgi mimarisi**  
   - Üst barda çok buton → **`_project_views_nav.html` benzeri tek “Görünümler” menüsü** veya sekme; özet Kanban’ı kısalt veya “Özet” olarak etiketle, tam panoyu ayrı sayfaya bırak.

4. **Silme ve tehlikeli aksiyonlar**  
   - Silme butonunu yetkiye göre sabit konuma al; onay modalı (mc-modal) ile `confirm()` yerine tutarlı UX.

### Faz B — Mimari ve doğruluk (1–2 hafta)

5. **Portföy servisini tenant ile hizala**  
   - `build_portfolio_context`: mümkünse **`AppProcess` / `tenant_id`** ve strateji matrisinin Micro’da kullanılan kaynaklarıyla aynı sorgular.  
   - `Surec` / `Process` ikilisini tek stratejide netleştir (dokümante et).

6. **FK ve ID tutarlılığı**  
   - `project_members`, `manager_id`, `Task.assignee_id` → DB’de FK hâlâ `user.id` (legacy) ise:  
     - ya **migration** ile `users.id` ile uyum,  
     - ya FK gevşetme / görünüm katmanında net “legacy vs core” ayrımı.  
   - Hedef: tek kaynak gerçek: **Micro oturum = `users.id`**.

7. **routes bölünmesi**  
   - Örnek: `project_list_routes.py`, `project_task_routes.py`, `project_views_routes.py`, `project_portfolio_routes.py` veya Flask Blueprint alt modülleri.

### Faz C — Deneyim ve kalite (2–4 hafta)

8. **Ortak bildirim katmanı**  
   - Micro `app.js` veya küçük `micro-notify.js`: toast API tek tip; Takvim/Gantt/Kanban/RAID aynı çağrıyı kullansın.

9. **RAID ve formlar**  
   - Bootstrap bağımlılığını kaldırıp **saf Tailwind / mc-* bileşenleri** (veya tek CSS çerçevesi) ile RAID’i sadeleştir.

10. **Takvim / Gantt**  
    - Mümkünse **Micro API prefix** (`/micro/api/...`) ile görev tarihleri; kök `/api/projeler` bağımlılığını azalt.  
    - Yükleme/hata durumunda iskelet + boş durum mesajı.

11. **Arama, filtre, sıralama**  
    - Liste: durum, öncelik, yönetici, metin araması; sayfalama korunur.

12. **Test**  
    - En az: yetki matrisi (`user_can_access_project`, `user_can_edit_tasks`, lider), form POST (lider/üye/gözlemci), portföy erişim 403.

---

## 3. Başarı ölçütleri

- Kullanıcı tek ekranda “ne yapacağını” anlıyor (özet vs pano ayrımı net).  
- Detayda ekip ve yönetici isimleri **doğru ve eksiksiz**.  
- Portföy skoru, tenant’taki gerçek süreç/strateji verisiyle **uyumlu**.  
- Kod: proje modülü dosyaları okunabilir boyutta; yeni geliştirici onboarding süresi kısalıyor.

---

## 4. Önerilen sıra (özet)

`A1 dil` → `A2 ekip gösterimi` → `A3/A4 detay + silme` → `B5 portföy` → `B6 FK` → `B7 split` → `C8–C12`.

---

*Bu doküman ihtiyaç netleştikçe güncellenmeli; TASKLOG’a işlemek için ayrı TASK kaydı açılabilir.*
