-- ============================================================
-- Activity ve ActivityStatus Tablolarını Oluşturma Script'i
-- SQL Server için
-- ============================================================

USE [stratejik_planlama];  -- Veritabanı adınızı buraya yazın
GO

-- ============================================================
-- 1. activity_status Tablosu
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[activity_status]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[activity_status] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [ad] NVARCHAR(50) NOT NULL UNIQUE,
        [renk] NVARCHAR(20) DEFAULT 'secondary',
        [sira] INT DEFAULT 0,
        [is_closed] BIT DEFAULT 0,
        [created_at] DATETIME DEFAULT GETDATE()
    );
    PRINT 'activity_status tablosu oluşturuldu.';
END
ELSE
BEGIN
    PRINT 'activity_status tablosu zaten mevcut.';
END
GO

-- ============================================================
-- 2. activity Tablosu (FK'ler olmadan)
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[activity]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[activity] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [title] NVARCHAR(200) NOT NULL,
        [description] NTEXT NULL,
        [assigned_to_id] INT NULL,
        [surec_pg_id] INT NULL,
        [status_id] INT NOT NULL DEFAULT 1,
        [created_by_id] INT NOT NULL,
        [due_date] DATE NULL,
        [estimated_hours] FLOAT NULL,
        [actual_hours] FLOAT NULL,
        [priority] INT DEFAULT 3,
        [progress] INT DEFAULT 0,
        [is_measurable] BIT DEFAULT 0,
        [output_value] NVARCHAR(100) NULL,
        [created_at] DATETIME DEFAULT GETDATE(),
        [updated_at] DATETIME DEFAULT GETDATE(),
        [completed_at] DATETIME NULL
    );
    PRINT 'activity tablosu oluşturuldu.';
END
ELSE
BEGIN
    PRINT 'activity tablosu zaten mevcut.';
END
GO

-- ============================================================
-- 3. Foreign Key Constraints
-- ============================================================

-- FK: assigned_to_id -> user(id)
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_assigned_to')
BEGIN
    ALTER TABLE [activity] 
    ADD CONSTRAINT [FK_activity_assigned_to] 
    FOREIGN KEY ([assigned_to_id]) REFERENCES [user]([id]);
    PRINT 'FK_activity_assigned_to eklendi.';
END
GO

-- FK: created_by_id -> user(id)
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_created_by')
BEGIN
    ALTER TABLE [activity] 
    ADD CONSTRAINT [FK_activity_created_by] 
    FOREIGN KEY ([created_by_id]) REFERENCES [user]([id]);
    PRINT 'FK_activity_created_by eklendi.';
END
GO

-- FK: surec_pg_id -> surec_performans_gostergesi(id)
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_surec_pg')
BEGIN
    ALTER TABLE [activity] 
    ADD CONSTRAINT [FK_activity_surec_pg] 
    FOREIGN KEY ([surec_pg_id]) REFERENCES [surec_performans_gostergesi]([id]);
    PRINT 'FK_activity_surec_pg eklendi.';
END
GO

-- FK: status_id -> activity_status(id)
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_status')
BEGIN
    ALTER TABLE [activity] 
    ADD CONSTRAINT [FK_activity_status] 
    FOREIGN KEY ([status_id]) REFERENCES [activity_status]([id]);
    PRINT 'FK_activity_status eklendi.';
END
GO

-- ============================================================
-- 4. Indexes
-- ============================================================

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_activity_assigned_to_id')
BEGIN
    CREATE INDEX [IX_activity_assigned_to_id] ON [activity]([assigned_to_id]);
    PRINT 'IX_activity_assigned_to_id eklendi.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_activity_surec_pg_id')
BEGIN
    CREATE INDEX [IX_activity_surec_pg_id] ON [activity]([surec_pg_id]);
    PRINT 'IX_activity_surec_pg_id eklendi.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_activity_status_id')
BEGIN
    CREATE INDEX [IX_activity_status_id] ON [activity]([status_id]);
    PRINT 'IX_activity_status_id eklendi.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_activity_created_by_id')
BEGIN
    CREATE INDEX [IX_activity_created_by_id] ON [activity]([created_by_id]);
    PRINT 'IX_activity_created_by_id eklendi.';
END
GO

-- ============================================================
-- 5. Varsayılan Durumlar (ActivityStatus)
-- ============================================================

IF NOT EXISTS (SELECT * FROM [activity_status] WHERE [ad] = 'Yeni')
BEGIN
    INSERT INTO [activity_status] ([ad], [renk], [sira], [is_closed]) 
    VALUES ('Yeni', 'secondary', 1, 0);
    PRINT 'Yeni durumu eklendi.';
END
GO

IF NOT EXISTS (SELECT * FROM [activity_status] WHERE [ad] = 'Devam Ediyor')
BEGIN
    INSERT INTO [activity_status] ([ad], [renk], [sira], [is_closed]) 
    VALUES ('Devam Ediyor', 'primary', 2, 0);
    PRINT 'Devam Ediyor durumu eklendi.';
END
GO

IF NOT EXISTS (SELECT * FROM [activity_status] WHERE [ad] = 'Beklemede')
BEGIN
    INSERT INTO [activity_status] ([ad], [renk], [sira], [is_closed]) 
    VALUES ('Beklemede', 'warning', 3, 0);
    PRINT 'Beklemede durumu eklendi.';
END
GO

IF NOT EXISTS (SELECT * FROM [activity_status] WHERE [ad] = 'Tamamlandı')
BEGIN
    INSERT INTO [activity_status] ([ad], [renk], [sira], [is_closed]) 
    VALUES ('Tamamlandı', 'success', 4, 1);
    PRINT 'Tamamlandı durumu eklendi.';
END
GO

IF NOT EXISTS (SELECT * FROM [activity_status] WHERE [ad] = 'İptal')
BEGIN
    INSERT INTO [activity_status] ([ad], [renk], [sira], [is_closed]) 
    VALUES ('İptal', 'danger', 5, 1);
    PRINT 'İptal durumu eklendi.';
END
GO

-- ============================================================
-- Tamamlandı
-- ============================================================
PRINT '';
PRINT '============================================================';
PRINT '✅ Tüm işlemler tamamlandı!';
PRINT '============================================================';
GO
