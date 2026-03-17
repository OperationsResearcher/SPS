-- Performance Optimization: SQLite Index Creation Script
-- Adds indexes to most frequently queried/filtered fields

-- ============================================
-- TASK TABLE INDEXES
-- ============================================

-- project_id index
CREATE INDEX IF NOT EXISTS idx_task_project_id ON task(project_id);

-- status index
CREATE INDEX IF NOT EXISTS idx_task_status ON task(status);

-- assigned_to_id index (for user task queries)
CREATE INDEX IF NOT EXISTS idx_task_assigned_to_id ON task(assigned_to_id);

-- due_date index (for deadline filtering)
CREATE INDEX IF NOT EXISTS idx_task_due_date ON task(due_date);

-- Composite index (project_id, status) - most common query combination
CREATE INDEX IF NOT EXISTS idx_task_project_status ON task(project_id, status);

-- Composite index (due_date, status) - for overdue task queries
CREATE INDEX IF NOT EXISTS idx_task_due_status ON task(due_date, status);

-- created_at index (for sorting and date range queries)
CREATE INDEX IF NOT EXISTS idx_task_created_at ON task(created_at);

-- parent_id index (for subtask queries)
CREATE INDEX IF NOT EXISTS idx_task_parent_id ON task(parent_id);

-- ============================================
-- PROJECT TABLE INDEXES
-- ============================================

-- kurum_id index
CREATE INDEX IF NOT EXISTS idx_project_kurum_id ON project(kurum_id);

-- manager_id index
CREATE INDEX IF NOT EXISTS idx_project_manager_id ON project(manager_id);

-- start_date index
CREATE INDEX IF NOT EXISTS idx_project_start_date ON project(start_date);

-- end_date index
CREATE INDEX IF NOT EXISTS idx_project_end_date ON project(end_date);

-- status index
CREATE INDEX IF NOT EXISTS idx_project_status ON project(status);

-- Composite index (kurum_id, manager_id)
CREATE INDEX IF NOT EXISTS idx_project_kurum_manager ON project(kurum_id, manager_id);

-- Composite index (start_date, end_date)
CREATE INDEX IF NOT EXISTS idx_project_dates ON project(start_date, end_date);

-- ============================================
-- TASK_IMPACT TABLE INDEXES
-- ============================================

-- task_id index
CREATE INDEX IF NOT EXISTS idx_task_impact_task_id ON task_impact(task_id);

-- related_pg_id index
CREATE INDEX IF NOT EXISTS idx_task_impact_related_pg_id ON task_impact(related_pg_id);

-- related_faaliyet_id index
CREATE INDEX IF NOT EXISTS idx_task_impact_related_faaliyet_id ON task_impact(related_faaliyet_id);

-- ============================================
-- NOTIFICATION TABLE INDEXES
-- ============================================

-- user_id index
CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);

-- Composite index (user_id, okundu, created_at)
CREATE INDEX IF NOT EXISTS idx_notification_user_read ON notification(user_id, okundu, created_at DESC);

-- ============================================
-- USER_ACTIVITY_LOG TABLE INDEXES
-- ============================================

-- user_id index
CREATE INDEX IF NOT EXISTS idx_activity_user_id ON user_activity_log(user_id);

-- Composite index (user_id, timestamp)
CREATE INDEX IF NOT EXISTS idx_activity_user_timestamp ON user_activity_log(user_id, timestamp DESC);

-- action index
CREATE INDEX IF NOT EXISTS idx_activity_action ON user_activity_log(action);

-- ============================================
-- SUREC_PERFORMANS_GOSTERGESI TABLE INDEXES
-- ============================================

-- surec_id index
CREATE INDEX IF NOT EXISTS idx_pg_surec_id ON surec_performans_gostergesi(surec_id);

-- sorumlu_user_id index
CREATE INDEX IF NOT EXISTS idx_pg_sorumlu_user_id ON surec_performans_gostergesi(sorumlu_user_id);

-- ============================================
-- TASK_COMMENT TABLE INDEXES
-- ============================================

-- task_id index
CREATE INDEX IF NOT EXISTS idx_task_comment_task_id ON task_comment(task_id);

-- user_id index
CREATE INDEX IF NOT EXISTS idx_task_comment_user_id ON task_comment(user_id);

-- Composite index (task_id, created_at)
CREATE INDEX IF NOT EXISTS idx_task_comment_task_created ON task_comment(task_id, created_at DESC);

-- ============================================
-- PROJECT_RISK TABLE INDEXES
-- ============================================

-- project_id index
CREATE INDEX IF NOT EXISTS idx_risk_project_id ON project_risk(project_id);

-- risk_level index
CREATE INDEX IF NOT EXISTS idx_risk_level ON project_risk(risk_level);

-- Composite index (project_id, risk_level)
CREATE INDEX IF NOT EXISTS idx_risk_project_level ON project_risk(project_id, risk_level);

-- ============================================
-- STRATEGY_PROCESS_MATRIX TABLE INDEXES
-- ============================================

-- alt_strateji_id index
CREATE INDEX IF NOT EXISTS idx_matrix_alt_strateji_id ON strategy_process_matrix(alt_strateji_id);

-- surec_id index
CREATE INDEX IF NOT EXISTS idx_matrix_surec_id ON strategy_process_matrix(surec_id);

-- Composite index (alt_strateji_id, surec_id)
CREATE INDEX IF NOT EXISTS idx_matrix_strategy_process ON strategy_process_matrix(alt_strateji_id, surec_id);

-- ============================================
-- TASK_ACTIVITY TABLE INDEXES
-- ============================================

-- task_id index
CREATE INDEX IF NOT EXISTS idx_task_activity_task_id ON task_activity(task_id);

-- user_id index
CREATE INDEX IF NOT EXISTS idx_task_activity_user_id ON task_activity(user_id);

-- Composite index (task_id, created_at)
CREATE INDEX IF NOT EXISTS idx_task_activity_task_created ON task_activity(task_id, created_at DESC);

-- ============================================
-- TIME_ENTRY TABLE INDEXES
-- ============================================

-- task_id index
CREATE INDEX IF NOT EXISTS idx_time_entry_task_id ON time_entry(task_id);

-- user_id index
CREATE INDEX IF NOT EXISTS idx_time_entry_user_id ON time_entry(user_id);

-- Composite index (user_id, start_time)
CREATE INDEX IF NOT EXISTS idx_time_entry_user_start ON time_entry(user_id, start_time DESC);
