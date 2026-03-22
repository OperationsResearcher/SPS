# Micro Proje Modülü — Kilitleşmiş Gereksinimler

> Karar tarihi: 2026-03-19  
> Önceki planlama sorularına verilen yanıtların teknik özeti. Kodlamadan önce referans.

---

## 1. Veri ve kurumsal bağlantı

| Karar | Açıklama |
|--------|-----------|
| **Kurum bağlantısı** | Projeler **kurum** ile bağlı kalır (`kurum_id` / mevcut `Project` modeli çizgisi korunur). |
| **Proje görevi ↔ PG** | **Proje görevleri** (`Task`), bir **performans göstergesine (PG)** bağlanabilir. Kural: **bir proje görevi en fazla bir PG’ye** bağlanabilir (1:0..1). PG, ilgili süreçteki `ProcessKpi` (veya eşdeğeri) kaydına işaret eder. |

**Not (uygulama):** Proje `Task` modeli üzerinde `process_kpi_id` / `pg_id` gibi tekil FK + benzersiz kısıt; API ve UI’da PG seçimi tek seçim olacak şekilde tasarlanır.

---

## 2. Strateji / KPI / portföy

| Karar | Açıklama |
|--------|-----------|
| **Micro kaynağı** | Stratejik proje portföyü, strateji KPI paneli, matrisle ilişkili ekranlar **Micro üzerinden** sunulacak (kök `/strategy/...` sayfaları uzun vadede yönlendirme veya kaldırma ile hizalanır). |

Kapsam önceki planda “hepsi” olarak onaylandı: portföy, operasyonel proje detayı, görevler, uzantılar (takvim, Gantt, RAID, …) Micro planına dahil edilir (fazlara bölünebilir, kapsam iptal edilmez).

---

## 3. URL isimlendirme (İngilizce)

Önümüzdeki uygulama **`/micro`** öneki altında **İngilizce** path segmentleri kullanır.

**Önerilen iskelet** (kesin rotalar implementasyonda netleşir):

| Alan | Örnek path |
|------|------------|
| Modül giriş / liste | `/micro/project` |
| Proje detay (Kanban vb.) | `/micro/project/<int:project_id>` |
| Yeni / düzenle | `/micro/project/new`, `/micro/project/<id>/edit` |
| Stratejik portföy | `/micro/project/portfolio` veya `/micro/strategy/project-portfolio` |
| Stratejik proje analizi | `/micro/project/<id>/strategy` |
| Görev detay | `/micro/project/<project_id>/task/<task_id>` |
| Alt araçlar | `/micro/project/<id>/calendar`, `/gantt`, `/raid`, … (İngilizce) |

Eski kök URL’ler (`/projeler/...`, `/strategy/projects`) istenirse **301 → yeni Micro URL** ile birlikte yaşatılır.

---

## 4. Yetkilendirme (Süreç Yönetimi ile aynı mantık)

| Süreç Yönetimi | Proje Yönetimi (eşlenik) |
|----------------|---------------------------|
| Süreç lideri + sahip (owners) | **Proje lideri** + proje sahipleri (aynı ayrıcalık seviyesi) |
| Süreç üyeleri | **Proje üyeleri** |
| `PRIVILEGED_ROLES` (Admin, tenant_admin, executive_manager) | Aynı — kurum/platform yöneticileri tam erişim |
| `user_can_access_process` | `user_can_access_project` — atanan + ayrıcalıklı |
| `user_is_process_leader` | `user_is_project_leader` — CRUD / yapılandırma eşiği |
| `accessible_processes_filter` | `accessible_projects_filter` — listelerde tenant + atama filtresi |

**Uygulama notu:** Mevcut `Project` modelinde `manager_id`, `project_members`, `project_observers` var. Süreçteki **leaders / members / owners** üçlüsü ile birebir hizalanacak şekilde ya mevcut alanlar genişletilir ya da `process` ile aynı desende ek tablolar (`project_leaders`, `project_owners`) tanımlanır; net DB tasarımı bir sonraki teknik görevde çıkarılır.

Gözlemci (observer) rolü süreç tarafında yoksa, proje tarafında **salt okunur erişim** için mevcut `observers` korunur; ayrıcalıklı + lider + üye kuralları süreç modülüyle aynı kalır.

---

## 5. Mimari hatırlatmalar (değişmeyen teknik gerçekler)

- **REST:** Kök `/api/projeler/...` geniş; Micro UI ilk aşamada burayı tüketebilir; istenirse `/micro/project/api/...` ince sarmalayıcı eklenir.
- **Tenant / kurum:** Oturum kullanıcısı `tenant_id` ile gelir; proje `kurum_id` ile bağlıdır — üretimde ID eşlemesi tutarlı olmalı (mevcut `User.kurum_id` ↔ `tenant_id` uyumu).
- **Proje görevi – PG bağlantısı:** İlişki **proje görevi** (`Task`) ile **app tarafındaki süreç PG modeli** (`ProcessKpi` vb.) arasında FK ile kurulur; legacy `Surec` ile çakışma varsa veri katmanında tek kaynak seçilir.

---

## 6. Sonraki adım (kod öncesi)

1. **ER diyagramı:** Project ↔ Kurum, Task ↔ PG (1:1), Project leaders/members/owners eşlemesi.  
2. **URL manifestosu:** Tüm Micro proje rotalarının İngilizce listesi + `micro_bp` kayıtları.  
3. **İzin matrisi tablosu:** Süreç modülündeki fonksiyonlar ↔ proje modülü fonksiyonları satır satır.  
4. **Sprint sırası:** API tüketimi hazır ekranlar önce; stratejik skor servisi (matris mantığı) ortak modüle çekme.

Bu dosya, ürün kararlarının kaynağıdır; TASKLOG’a işlenen geliştirme görevleri buraya referans verebilir.

---

## 7. Uygulama (TASK-099 — 2026-03-19)

| Rota | Açıklama |
|------|-----------|
| `GET /micro/project` | Proje listesi (tenant + atama filtresi) |
| `GET /micro/project/portfolio` | Stratejik portföy (ayrıcalıklı roller) |
| `GET/POST /micro/project/new` | Yeni proje |
| `GET /micro/project/<id>` | Kanban detay |
| `GET/POST /micro/project/<id>/edit` | Proje düzenle (lider) |
| `GET /micro/project/<id>/strategy` | Stratejik analiz + süreç bağlantı formu |
| `POST .../strategy/processes` | Süreç–proje ilişkisi kaydet |
| `GET/POST .../task/new`, `.../task/<tid>`, `.../task/<tid>/edit` | Görev + isteğe bağlı `process_kpi_id` |
| `POST /micro/project/<id>/delete` | Proje sil (ayrıcalıklı) |
| `GET /micro/proje` | `301` → `/micro/project` (redirect) |

**Veritabanı:** `flask db upgrade` ile `task.process_kpi_id` eklenir (`f8a9b0c1d2e3`).

**Sonraki sprint önerileri:** Takvim/Gantt/RAID sayfaları (kök şablon veya `/api` + SPA), üye/gözlemci yönetimi UI, kök `/projeler` → `/micro/project` yönlendirmesi.
