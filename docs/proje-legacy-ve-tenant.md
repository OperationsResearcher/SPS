# Proje modülü: Legacy `kurum` / `surec` ve Micro `tenant` / `users`

## Özet

- **Proje, görev, RAID** modelleri eski şemada: `project.kurum_id` → `kurum`, `manager_id` / üyeler → FK `user.id` (legacy tablo `user`).
- **Micro oturum** `app.models.core.User` → tablo `users`, **`tenant_id`**.
- Üye/lider atamaları Micro’da **`users.id`** ile yapılır; ilişki tablolarına doğrudan yazım kullanılır (ORM `LegacyUser` append yerine).

## Portföy skoru

1. **Klasik matris** (`ana_strateji` / `alt_strateji` + `strategy_process_matrix` + `surec`) kurumda kayıt varsa bu yol kullanılır.
2. Aksi halde **App tenant** yolu: `strategies` / `sub_strategies` + `processes` + `process_sub_strategy_links`; projedeki bağlı **Surec** kayıtları **kod veya ad** ile App `Process` ile eşleştirilerek skor alınır.

## FK notu

Veritabanında `project_members.user_id` → `user.id` FK’sı varsa ve yalnızca `users` doluysa migration veya FK gevşetme gerekebilir; üretimde SQLite FK kapalı olabilir.
