-- Süreç (surec) tablosuna parent_id sütunu ekler.
-- Mevcut süreçlerin parent_id değeri NULL (bağımsız) kalır.
-- SQLite: ALTER TABLE ADD COLUMN; FK için ayrıca PRAGMA foreign_keys gerekebilir.

-- 1) Sütun ekle (SQLite 3.35+ tek ADD COLUMN destekler)
ALTER TABLE surec ADD COLUMN parent_id INTEGER REFERENCES surec(id);

-- 2) İndeks (performans)
CREATE INDEX IF NOT EXISTS ix_surec_parent_id ON surec(parent_id);

-- Not: SQLite'da ALTER TABLE ile eklenen REFERENCES, ON DELETE davranışı
-- varsayılan olarak uygulanmayabilir. Uygulama katmanında (Flask) parent
-- silindiğinde alt süreçlerin parent_id'sini NULL yapmak güvenlidir.
