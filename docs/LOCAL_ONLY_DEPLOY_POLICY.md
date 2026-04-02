# Local-Only Change Policy

Bu çalışma seti yalnızca yerel ortam için hazırlanmıştır.

- GitHub push yapılmaz.
- VM deploy yapılmaz.
- Uzak ortama (GitHub/VM) geçiş için iki aşamalı kullanıcı onayı zorunludur.
- Migration çalıştırmadan önce full backup alınır.
- Hard-migration sonrası smoke test tamamlanmadan hiçbir dış ortama çıkılmaz.
