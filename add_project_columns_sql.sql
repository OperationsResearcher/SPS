-- Project tablosuna yeni kolonları ekleme script'i
-- start_date, end_date, priority kolonlarını ekler

USE [stratejik_planlama];  -- Veritabanı adınızı buraya yazın
GO

-- start_date kolonu ekle (eğer yoksa)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'project' AND COLUMN_NAME = 'start_date')
BEGIN
    ALTER TABLE project ADD start_date DATE NULL;
    PRINT 'start_date kolonu eklendi.';
END
ELSE
BEGIN
    PRINT 'start_date kolonu zaten mevcut.';
END
GO

-- end_date kolonu ekle (eğer yoksa)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'project' AND COLUMN_NAME = 'end_date')
BEGIN
    ALTER TABLE project ADD end_date DATE NULL;
    PRINT 'end_date kolonu eklendi.';
END
ELSE
BEGIN
    PRINT 'end_date kolonu zaten mevcut.';
END
GO

-- priority kolonu ekle (eğer yoksa)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'project' AND COLUMN_NAME = 'priority')
BEGIN
    ALTER TABLE project ADD priority NVARCHAR(50) DEFAULT 'Orta';
    PRINT 'priority kolonu eklendi.';
END
ELSE
BEGIN
    PRINT 'priority kolonu zaten mevcut.';
END
GO

-- Index'ler ekle (performans için)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_start_date' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_start_date ON project(start_date);
    PRINT 'start_date index''i eklendi.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_end_date' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_end_date ON project(end_date);
    PRINT 'end_date index''i eklendi.';
END
GO

PRINT 'Tüm kolonlar başarıyla eklendi!';
GO





















