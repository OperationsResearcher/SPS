-- Performans Optimizasyonu: Index Ekleme Script'i
-- Task, Project ve TaskImpact tablolarında en çok aranan/filtreleme yapılan alanlara index ekler

USE [stratejik_planlama];  -- Veritabanı adınızı buraya yazın
GO

-- ============================================
-- TASK TABLOSU İNDEXLERİ
-- ============================================

-- project_id index (zaten varsa hata vermez)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_project_id' AND object_id = OBJECT_ID('task'))
BEGIN
    CREATE INDEX idx_task_project_id ON task(project_id);
    PRINT 'idx_task_project_id index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_project_id index''i zaten mevcut.';
END
GO

-- status index
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_status' AND object_id = OBJECT_ID('task'))
BEGIN
    CREATE INDEX idx_task_status ON task(status);
    PRINT 'idx_task_status index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_status index''i zaten mevcut.';
END
GO

-- assigned_to_id index
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_assigned_to_id' AND object_id = OBJECT_ID('task'))
BEGIN
    CREATE INDEX idx_task_assigned_to_id ON task(assigned_to_id) WHERE assigned_to_id IS NOT NULL;
    PRINT 'idx_task_assigned_to_id index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_assigned_to_id index''i zaten mevcut.';
END
GO

-- due_date index (tarih filtrelemeleri için)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_due_date' AND object_id = OBJECT_ID('task'))
BEGIN
    CREATE INDEX idx_task_due_date ON task(due_date) WHERE due_date IS NOT NULL;
    PRINT 'idx_task_due_date index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_due_date index''i zaten mevcut.';
END
GO

-- Composite index: project_id + status (en çok kullanılan kombinasyon)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_project_status' AND object_id = OBJECT_ID('task'))
BEGIN
    CREATE INDEX idx_task_project_status ON task(project_id, status);
    PRINT 'idx_task_project_status composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_project_status composite index''i zaten mevcut.';
END
GO

-- ============================================
-- PROJECT TABLOSU İNDEXLERİ
-- ============================================

-- kurum_id index (zaten varsa hata vermez)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_kurum_id' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_kurum_id ON project(kurum_id);
    PRINT 'idx_project_kurum_id index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_kurum_id index''i zaten mevcut.';
END
GO

-- manager_id index
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_manager_id' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_manager_id ON project(manager_id);
    PRINT 'idx_project_manager_id index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_manager_id index''i zaten mevcut.';
END
GO

-- start_date index (tarih filtrelemeleri için)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_start_date' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_start_date ON project(start_date) WHERE start_date IS NOT NULL;
    PRINT 'idx_project_start_date index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_start_date index''i zaten mevcut.';
END
GO

-- end_date index
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_end_date' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_end_date ON project(end_date) WHERE end_date IS NOT NULL;
    PRINT 'idx_project_end_date index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_end_date index''i zaten mevcut.';
END
GO

-- priority index
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_priority' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_priority ON project(priority);
    PRINT 'idx_project_priority index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_priority index''i zaten mevcut.';
END
GO

-- ============================================
-- TASK_IMPACT TABLOSU İNDEXLERİ
-- ============================================

-- task_id index (zaten varsa hata vermez)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_impact_task_id' AND object_id = OBJECT_ID('task_impact'))
BEGIN
    CREATE INDEX idx_task_impact_task_id ON task_impact(task_id);
    PRINT 'idx_task_impact_task_id index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_impact_task_id index''i zaten mevcut.';
END
GO

-- related_pg_id index
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_impact_related_pg_id' AND object_id = OBJECT_ID('task_impact'))
BEGIN
    CREATE INDEX idx_task_impact_related_pg_id ON task_impact(related_pg_id) WHERE related_pg_id IS NOT NULL;
    PRINT 'idx_task_impact_related_pg_id index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_impact_related_pg_id index''i zaten mevcut.';
END
GO

-- is_processed index (zaten varsa hata vermez - V1.5.4'te eklendi)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_impact_is_processed' AND object_id = OBJECT_ID('task_impact'))
BEGIN
    CREATE INDEX idx_task_impact_is_processed ON task_impact(is_processed);
    PRINT 'idx_task_impact_is_processed index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_impact_is_processed index''i zaten mevcut.';
END
GO

-- Composite index: task_id + is_processed (en çok kullanılan kombinasyon)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_impact_task_processed' AND object_id = OBJECT_ID('task_impact'))
BEGIN
    CREATE INDEX idx_task_impact_task_processed ON task_impact(task_id, is_processed);
    PRINT 'idx_task_impact_task_processed composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_impact_task_processed composite index''i zaten mevcut.';
END
GO

-- ============================================
-- PROJECT_RISK TABLOSU İNDEXLERİ (Performans için)
-- ============================================

-- project_id index
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_risk_project_id' AND object_id = OBJECT_ID('project_risk'))
BEGIN
    CREATE INDEX idx_project_risk_project_id ON project_risk(project_id);
    PRINT 'idx_project_risk_project_id index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_risk_project_id index''i zaten mevcut.';
END
GO

-- status index
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_risk_status' AND object_id = OBJECT_ID('project_risk'))
BEGIN
    CREATE INDEX idx_project_risk_status ON project_risk(status);
    PRINT 'idx_project_risk_status index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_risk_status index''i zaten mevcut.';
END
GO

-- Composite index: project_id + status (aktif riskler için)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_risk_project_status' AND object_id = OBJECT_ID('project_risk'))
BEGIN
    CREATE INDEX idx_project_risk_project_status ON project_risk(project_id, status);
    PRINT 'idx_project_risk_project_status composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_risk_project_status composite index''i zaten mevcut.';
END
GO

-- ============================================
-- V1.9.0: EK COMPOSITE INDEXLER (Performans İyileştirmesi)
-- ============================================

-- Task composite indexes (due_date + project_id)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_project_due_date' AND object_id = OBJECT_ID('task'))
BEGIN
    CREATE INDEX idx_task_project_due_date ON task(project_id, due_date) WHERE due_date IS NOT NULL;
    PRINT 'idx_task_project_due_date composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_project_due_date composite index''i zaten mevcut.';
END
GO

-- Task composite index (project_id + status + is_archived)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_task_project_status_archived' AND object_id = OBJECT_ID('task'))
BEGIN
    CREATE INDEX idx_task_project_status_archived ON task(project_id, status, is_archived) WHERE is_archived = 0;
    PRINT 'idx_task_project_status_archived composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_task_project_status_archived composite index''i zaten mevcut.';
END
GO

-- Project composite index (kurum_id + dates + is_archived)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_kurum_dates' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_kurum_dates ON project(kurum_id, start_date, end_date, is_archived) WHERE is_archived = 0;
    PRINT 'idx_project_kurum_dates composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_kurum_dates composite index''i zaten mevcut.';
END
GO

-- Project composite index (manager_id + dates)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_project_manager_dates' AND object_id = OBJECT_ID('project'))
BEGIN
    CREATE INDEX idx_project_manager_dates ON project(manager_id, start_date, end_date) WHERE is_archived = 0;
    PRINT 'idx_project_manager_dates composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_project_manager_dates composite index''i zaten mevcut.';
END
GO

-- ProjectRisk composite index (project_id + status + risk_score)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_risk_project_status_score' AND object_id = OBJECT_ID('project_risk'))
BEGIN
    CREATE INDEX idx_risk_project_status_score ON project_risk(project_id, status, risk_score) WHERE status = 'Aktif';
    PRINT 'idx_risk_project_status_score composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_risk_project_status_score composite index''i zaten mevcut.';
END
GO

-- Notification composite index (user_id + okundu + created_at)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_notification_user_read' AND object_id = OBJECT_ID('notification'))
BEGIN
    CREATE INDEX idx_notification_user_read ON notification(user_id, okundu, created_at DESC);
    PRINT 'idx_notification_user_read composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_notification_user_read composite index''i zaten mevcut.';
END
GO

-- PerformansGostergeVeri composite indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pg_veri_pg_tarih' AND object_id = OBJECT_ID('performans_gosterge_veri'))
BEGIN
    CREATE INDEX idx_pg_veri_pg_tarih ON performans_gosterge_veri(pg_id, veri_tarihi DESC);
    PRINT 'idx_pg_veri_pg_tarih composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_pg_veri_pg_tarih composite index''i zaten mevcut.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pg_veri_user_tarih' AND object_id = OBJECT_ID('performans_gosterge_veri'))
BEGIN
    CREATE INDEX idx_pg_veri_user_tarih ON performans_gosterge_veri(user_id, veri_tarihi DESC);
    PRINT 'idx_pg_veri_user_tarih composite index''i eklendi.';
END
ELSE
BEGIN
    PRINT 'idx_pg_veri_user_tarih composite index''i zaten mevcut.';
END
GO

PRINT '';
PRINT '========================================';
PRINT 'Tüm index''ler (V1.9.0 dahil) başarıyla eklendi!';
PRINT '========================================';
GO






















