-- TaskImpact tablosuna yeni kolonları ekleme script'i
-- is_processed, processed_at kolonlarını ekler

USE [stratejik_planlama];  -- Veritabanı adınızı buraya yazın
GO

-- is_processed kolonu ekle (eğer yoksa)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'task_impact' AND COLUMN_NAME = 'is_processed')
BEGIN
    ALTER TABLE task_impact ADD is_processed BIT DEFAULT 0;
    CREATE INDEX idx_task_impact_is_processed ON task_impact(is_processed);
    PRINT 'is_processed kolonu ve index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'is_processed kolonu zaten mevcut.';
END
GO

-- processed_at kolonu ekle (eğer yoksa)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'task_impact' AND COLUMN_NAME = 'processed_at')
BEGIN
    ALTER TABLE task_impact ADD processed_at DATETIME NULL;
    PRINT 'processed_at kolonu eklendi.';
END
ELSE
BEGIN
    PRINT 'processed_at kolonu zaten mevcut.';
END
GO

PRINT 'Tüm kolonlar başarıyla eklendi!';
GO





















