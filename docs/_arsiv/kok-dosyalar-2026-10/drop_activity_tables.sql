-- SQL Server'da Activity ve ActivityStatus tablolarını silmek için script
-- DİKKAT: Bu script geri dönülmez şekilde tabloları siler!

USE [StratejikPlanlama]  -- Veritabanı adınızı buraya yazın
GO

-- Foreign key constraint'leri önce sil
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_assigned_to')
    ALTER TABLE [activity] DROP CONSTRAINT FK_activity_assigned_to;
GO

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_created_by')
    ALTER TABLE [activity] DROP CONSTRAINT FK_activity_created_by;
GO

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_surec_pg')
    ALTER TABLE [activity] DROP CONSTRAINT FK_activity_surec_pg;
GO

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_activity_status')
    ALTER TABLE [activity] DROP CONSTRAINT FK_activity_status;
GO

-- Tabloları sil
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[activity]') AND type in (N'U'))
    DROP TABLE [activity];
GO

IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[activity_status]') AND type in (N'U'))
    DROP TABLE [activity_status];
GO

PRINT 'Activity ve ActivityStatus tabloları başarıyla silindi.';
GO






































