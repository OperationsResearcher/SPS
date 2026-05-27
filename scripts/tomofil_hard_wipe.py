"""Tomofil (tenant_id=27) HARD DELETE.

Kapsam: SP ağacı + ölçüm + plan year + analizler + initiative + OKR/BSC/ESG +
SP projeleri + portföy projeleri + bildirimler. Tenant, users, roles, tickets,
audit_logs, e-posta/LLM konfigleri ve kullanım logları KORUNUR.

Tek transaction. DRY_RUN=True iken sadece sayar; False yapıp tekrar çalıştırırsan
gerçekten siler.
"""
import os, sys, psycopg2

DRY_RUN = os.environ.get("WIPE_COMMIT", "0") != "1"
TENANT_ID = 27

conn = psycopg2.connect(
    host="localhost", user="kokpitim_user",
    password="kokpitim_dev_123", dbname="kokpitim_db",
)
conn.autocommit = False
cur = conn.cursor()

# Mevcut tabloları al
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
EXISTING = {r[0] for r in cur.fetchall()}

def _table_of(sql):
    s = sql.upper()
    if " FROM " in s:
        return s.split(" FROM ", 1)[1].split()[0].lower()
    if "UPDATE " in s:
        return s.split("UPDATE ", 1)[1].split()[0].lower()
    return ""

def q(sql, params=None):
    cur.execute(sql, params or ())

def delete(label, sql, params=None):
    t = _table_of(sql)
    if t and t not in EXISTING:
        print(f"  {label:48s}   SKIP (tablo yok)")
        return
    cur.execute("SAVEPOINT sp")
    try:
        q(sql, params)
        print(f"  {label:48s} {cur.rowcount:>8d}")
        cur.execute("RELEASE SAVEPOINT sp")
    except Exception as e:
        cur.execute("ROLLBACK TO SAVEPOINT sp")
        print(f"  {label:48s}   ERR: {str(e).splitlines()[0][:60]}")

def ids(sql, params=None):
    t = _table_of(sql)
    if t and t not in EXISTING:
        return (0,)
    try:
        q(sql, params)
        rows = [r[0] for r in cur.fetchall()]
        return tuple(rows) if rows else (0,)
    except Exception:
        conn.rollback()
        return (0,)

print(f"== TOMOFIL WIPE (tenant_id={TENANT_ID}) — DRY_RUN={DRY_RUN} ==\n")

# Snapshot IDs (single source for all child deletes)
user_ids   = ids("SELECT id FROM users WHERE tenant_id=%s", (TENANT_ID,))
proc_ids   = ids("SELECT id FROM processes WHERE tenant_id=%s", (TENANT_ID,))
kpi_ids    = ids("SELECT pk.id FROM process_kpis pk JOIN processes p ON pk.process_id=p.id WHERE p.tenant_id=%s", (TENANT_ID,))
act_ids    = ids("SELECT pa.id FROM process_activities pa JOIN processes p ON pa.process_id=p.id WHERE p.tenant_id=%s", (TENANT_ID,))
strat_ids  = ids("SELECT id FROM strategies WHERE tenant_id=%s", (TENANT_ID,))
sub_ids    = ids("SELECT ss.id FROM sub_strategies ss JOIN strategies s ON ss.strategy_id=s.id WHERE s.tenant_id=%s", (TENANT_ID,))
py_ids     = ids("SELECT id FROM plan_years WHERE tenant_id=%s", (TENANT_ID,))
init_ids   = ids("SELECT id FROM initiatives WHERE tenant_id=%s", (TENANT_ID,))
okr_ids    = ids("SELECT id FROM okr_objectives WHERE tenant_id=%s", (TENANT_ID,))
esg_ids    = ids("SELECT id FROM esg_metrics WHERE tenant_id=%s", (TENANT_ID,))
boc_ids    = ids("SELECT id FROM blue_ocean_canvases WHERE tenant_id=%s", (TENANT_ID,))
proj_ids   = ids("SELECT id FROM project WHERE tenant_id=%s", (TENANT_ID,))
task_ids   = ids("SELECT id FROM task WHERE project_id IN %s", (proj_ids,))
sprint_ids = ids("SELECT id FROM sprint WHERE project_id IN %s", (proj_ids,))
ind_pg_ids = ids("SELECT id FROM individual_performance_indicators WHERE user_id IN %s", (user_ids,))
ind_act_ids= ids("SELECT id FROM individual_activities WHERE user_id IN %s", (user_ids,))
ind_kpi_data_ids = ids("SELECT id FROM individual_kpi_data WHERE individual_pg_id IN %s", (ind_pg_ids,))
kpi_data_ids = ids("SELECT id FROM kpi_data WHERE process_kpi_id IN %s", (kpi_ids,))
rep_trig_ids = ids("SELECT id FROM replan_triggers WHERE tenant_id=%s", (TENANT_ID,))

print(f"Snapshot: users={len(user_ids) if user_ids!=(0,) else 0}, processes={len(proc_ids) if proc_ids!=(0,) else 0}, "
      f"kpis={len(kpi_ids) if kpi_ids!=(0,) else 0}, kpi_data={len(kpi_data_ids) if kpi_data_ids!=(0,) else 0}, "
      f"strategies={len(strat_ids) if strat_ids!=(0,) else 0}, plan_years={len(py_ids) if py_ids!=(0,) else 0}, "
      f"projects={len(proj_ids) if proj_ids!=(0,) else 0}, tasks={len(task_ids) if task_ids!=(0,) else 0}\n")

print("-- DELETING (silinen satır sayısı) --\n")

# ─── AUDIT / DERIVED (en alttan başla) ──────────────────────────────────
delete("kpi_data_audits",                   "DELETE FROM kpi_data_audits WHERE kpi_data_id IN %s", (kpi_data_ids,))
delete("individual_kpi_data_audits",        "DELETE FROM individual_kpi_data_audits WHERE individual_kpi_data_id IN %s", (ind_kpi_data_ids,))
delete("k_vektor_config_snapshots",         "DELETE FROM k_vektor_config_snapshots WHERE tenant_id=%s", (TENANT_ID,))

# ─── ACTIVITY TRACKING / DETAIL ─────────────────────────────────────────
delete("activity_tracks",                   "DELETE FROM activity_tracks WHERE activity_id IN %s", (act_ids,))
delete("process_activity_reminders",        "DELETE FROM process_activity_reminders WHERE activity_id IN %s", (act_ids,))
delete("process_activity_assignees",        "DELETE FROM process_activity_assignees WHERE activity_id IN %s", (act_ids,))
delete("individual_activity_tracks",        "DELETE FROM individual_activity_tracks WHERE individual_activity_id IN %s", (ind_act_ids,))
delete("favorite_kpis (by user)",           "DELETE FROM favorite_kpis WHERE user_id IN %s OR process_kpi_id IN %s", (user_ids, kpi_ids))

# kpi_data önce auto_pgv referansını kopar
delete("process_activities.auto_pgv unset", "UPDATE process_activities SET auto_pgv_kpi_data_id=NULL WHERE auto_pgv_kpi_data_id IN %s", (kpi_data_ids,))
delete("kpi_data",                          "DELETE FROM kpi_data WHERE id IN %s", (kpi_data_ids,))
delete("individual_kpi_data",               "DELETE FROM individual_kpi_data WHERE id IN %s", (ind_kpi_data_ids,))

# ─── MID-LEVEL ──────────────────────────────────────────────────────────
delete("process_activities",                "DELETE FROM process_activities WHERE process_id IN %s", (proc_ids,))
delete("individual_activities",             "DELETE FROM individual_activities WHERE user_id IN %s", (user_ids,))
delete("bottleneck_log (by process)",       "DELETE FROM bottleneck_log WHERE process_id IN %s OR kpi_id IN %s OR tenant_id=%s", (proc_ids, kpi_ids, TENANT_ID))
delete("process_maturity (by process)",     "DELETE FROM process_maturity WHERE process_id IN %s OR tenant_id=%s", (proc_ids, TENANT_ID))
delete("value_chain_items (by process)",    "DELETE FROM value_chain_items WHERE linked_process_id IN %s OR tenant_id=%s", (proc_ids, TENANT_ID))
delete("bsc_kpi_perspectives",              "DELETE FROM bsc_kpi_perspectives WHERE tenant_id=%s", (TENANT_ID,))
delete("esg_metric_values",                 "DELETE FROM esg_metric_values WHERE metric_id IN %s", (esg_ids,))
delete("esg_metrics",                       "DELETE FROM esg_metrics WHERE tenant_id=%s", (TENANT_ID,))
delete("okr_key_results",                   "DELETE FROM okr_key_results WHERE objective_id IN %s", (okr_ids,))
delete("okr_objectives",                    "DELETE FROM okr_objectives WHERE tenant_id=%s", (TENANT_ID,))
delete("initiative_milestones",             "DELETE FROM initiative_milestones WHERE initiative_id IN %s", (init_ids,))
delete("initiatives",                       "DELETE FROM initiatives WHERE tenant_id=%s", (TENANT_ID,))
delete("k_radar_recommendation_actions",    "DELETE FROM k_radar_recommendation_actions WHERE tenant_id=%s", (TENANT_ID,))
delete("process_sub_strategy_links",        "DELETE FROM process_sub_strategy_links WHERE process_id IN %s OR sub_strategy_id IN %s", (proc_ids, sub_ids))
delete("k_vektor_strategy_weights",         "DELETE FROM k_vektor_strategy_weights WHERE tenant_id=%s", (TENANT_ID,))
delete("k_vektor_sub_strategy_weights",     "DELETE FROM k_vektor_sub_strategy_weights WHERE tenant_id=%s", (TENANT_ID,))
delete("process_kpis",                      "DELETE FROM process_kpis WHERE process_id IN %s", (proc_ids,))
delete("individual_performance_indicators", "DELETE FROM individual_performance_indicators WHERE user_id IN %s", (user_ids,))

# ─── PLAN YEAR CONFIGS & ANALYSES (CASCADE'lı tablolar — yine de explicit) ─
delete("kpi_year_configs",                  "DELETE FROM kpi_year_configs WHERE plan_year_id IN %s", (py_ids,))
delete("strategy_year_configs",             "DELETE FROM strategy_year_configs WHERE plan_year_id IN %s", (py_ids,))
delete("sub_strategy_year_configs",         "DELETE FROM sub_strategy_year_configs WHERE plan_year_id IN %s", (py_ids,))
delete("process_year_configs",              "DELETE FROM process_year_configs WHERE plan_year_id IN %s", (py_ids,))
delete("individual_kpi_year_configs",       "DELETE FROM individual_kpi_year_configs WHERE plan_year_id IN %s", (py_ids,))
delete("tenant_year_identities",            "DELETE FROM tenant_year_identities WHERE tenant_id=%s", (TENANT_ID,))
delete("plan_project_activities",           "DELETE FROM plan_project_activities WHERE plan_year_id IN %s", (py_ids,))
delete("plan_project_tasks",                "DELETE FROM plan_project_tasks WHERE plan_year_id IN %s", (py_ids,))
delete("plan_projects",                     "DELETE FROM plan_projects WHERE tenant_id=%s", (TENANT_ID,))
delete("swot_analyses",                     "DELETE FROM swot_analyses WHERE tenant_id=%s", (TENANT_ID,))
delete("tows_analyses",                     "DELETE FROM tows_analyses WHERE tenant_id=%s", (TENANT_ID,))
delete("pestel_analyses",                   "DELETE FROM pestel_analyses WHERE tenant_id=%s", (TENANT_ID,))
delete("porter_analyses",                   "DELETE FROM porter_analyses WHERE tenant_id=%s", (TENANT_ID,))
delete("risk_heatmap_items",                "DELETE FROM risk_heatmap_items WHERE tenant_id=%s", (TENANT_ID,))
delete("stakeholder_maps",                  "DELETE FROM stakeholder_maps WHERE tenant_id=%s", (TENANT_ID,))
delete("stakeholder_surveys",               "DELETE FROM stakeholder_surveys WHERE tenant_id=%s", (TENANT_ID,))
delete("a3_reports",                        "DELETE FROM a3_reports WHERE tenant_id=%s", (TENANT_ID,))
delete("competitor_analyses",               "DELETE FROM competitor_analyses WHERE tenant_id=%s", (TENANT_ID,))
delete("blue_ocean_factors",                "DELETE FROM blue_ocean_factors WHERE canvas_id IN %s", (boc_ids,))
delete("blue_ocean_errc_items",             "DELETE FROM blue_ocean_errc_items WHERE canvas_id IN %s", (boc_ids,))
delete("blue_ocean_canvases",               "DELETE FROM blue_ocean_canvases WHERE tenant_id=%s", (TENANT_ID,))
delete("vrio_resources",                    "DELETE FROM vrio_resources WHERE tenant_id=%s", (TENANT_ID,))
delete("plan_years",                        "DELETE FROM plan_years WHERE tenant_id=%s", (TENANT_ID,))

# ─── STRATEGY TREE ─────────────────────────────────────────────────────
delete("sub_strategies",                    "DELETE FROM sub_strategies WHERE strategy_id IN %s", (strat_ids,))
delete("strategies",                        "DELETE FROM strategies WHERE tenant_id=%s", (TENANT_ID,))

# ─── PROCESSES (en son) ────────────────────────────────────────────────
delete("process_members",                   "DELETE FROM process_members WHERE process_id IN %s", (proc_ids,))
delete("process_leaders",                   "DELETE FROM process_leaders WHERE process_id IN %s", (proc_ids,))
delete("process_owners_table",              "DELETE FROM process_owners_table WHERE process_id IN %s", (proc_ids,))
# Cross-tenant FK referansları null'la (başka tenant'ların kaydı bu süreçlere işaret ediyorsa)
delete("ind_act source_process_id null",    "UPDATE individual_activities SET source_process_id=NULL WHERE source_process_id IN %s", (proc_ids,))
delete("ind_pg source_process_id null",     "UPDATE individual_performance_indicators SET source_process_id=NULL WHERE source_process_id IN %s", (proc_ids,))
delete("processes parent_id null",          "UPDATE processes SET parent_id=NULL WHERE tenant_id=%s", (TENANT_ID,))
delete("processes source_process_id null",  "UPDATE processes SET source_process_id=NULL WHERE source_process_id IN %s", (proc_ids,))
delete("processes",                         "DELETE FROM processes WHERE tenant_id=%s", (TENANT_ID,))

# ─── REPLAN ────────────────────────────────────────────────────────────
delete("replan_trigger_events",             "DELETE FROM replan_trigger_events WHERE trigger_id IN %s", (rep_trig_ids,))
delete("replan_triggers",                   "DELETE FROM replan_triggers WHERE tenant_id=%s", (TENANT_ID,))

# ─── EVM (FK → project) ────────────────────────────────────────────────
delete("evm_snapshots",                     "DELETE FROM evm_snapshots WHERE tenant_id=%s OR project_id IN %s", (TENANT_ID, proj_ids))

# ─── PORTFÖY PROJELERİ ─────────────────────────────────────────────────
# Task children
delete("task_predecessors",                 "DELETE FROM task_predecessors WHERE task_id IN %s OR predecessor_id IN %s", (task_ids, task_ids))
delete("task_dependency",                   "DELETE FROM task_dependency WHERE project_id IN %s", (proj_ids,))
delete("task_baseline",                     "DELETE FROM task_baseline WHERE task_id IN %s", (task_ids,))
delete("task_subtask",                      "DELETE FROM task_subtask WHERE task_id IN %s", (task_ids,))
delete("task_activity",                     "DELETE FROM task_activity WHERE task_id IN %s", (task_ids,))
delete("task_mention",                      "DELETE FROM task_mention WHERE task_id IN %s", (task_ids,))
delete("task_comment",                      "DELETE FROM task_comment WHERE task_id IN %s", (task_ids,))
delete("task_impact",                       "DELETE FROM task_impact WHERE task_id IN %s", (task_ids,))
delete("task_sprint",                       "DELETE FROM task_sprint WHERE task_id IN %s OR sprint_id IN %s", (task_ids, sprint_ids))
delete("time_entry",                        "DELETE FROM time_entry WHERE task_id IN %s", (task_ids,))
delete("recurring_task",                    "DELETE FROM recurring_task WHERE project_id IN %s", (proj_ids,))
delete("task",                              "DELETE FROM task WHERE project_id IN %s", (proj_ids,))
# Project children
delete("project_file",                      "DELETE FROM project_file WHERE project_id IN %s", (proj_ids,))
delete("project_risk",                      "DELETE FROM project_risk WHERE project_id IN %s", (proj_ids,))
delete("raid_item",                         "DELETE FROM raid_item WHERE project_id IN %s", (proj_ids,))
delete("integration_hook",                  "DELETE FROM integration_hook WHERE project_id IN %s", (proj_ids,))
delete("rule_definition",                   "DELETE FROM rule_definition WHERE project_id IN %s", (proj_ids,))
delete("sla",                               "DELETE FROM sla WHERE project_id IN %s", (proj_ids,))
delete("working_day",                       "DELETE FROM working_day WHERE project_id IN %s", (proj_ids,))
delete("capacity_plan",                     "DELETE FROM capacity_plan WHERE project_id IN %s", (proj_ids,))
delete("sprint",                            "DELETE FROM sprint WHERE project_id IN %s", (proj_ids,))
delete("project_members",                   "DELETE FROM project_members WHERE project_id IN %s", (proj_ids,))
delete("project_leaders",                   "DELETE FROM project_leaders WHERE project_id IN %s", (proj_ids,))
delete("project_observers",                 "DELETE FROM project_observers WHERE project_id IN %s", (proj_ids,))
delete("project_related_processes",         "DELETE FROM project_related_processes WHERE project_id IN %s", (proj_ids,))
delete("project",                           "DELETE FROM project WHERE tenant_id=%s", (TENANT_ID,))

# ─── BİLDİRİMLER ───────────────────────────────────────────────────────
delete("notifications (sistem)",            "DELETE FROM notifications WHERE tenant_id=%s OR user_id IN %s", (TENANT_ID, user_ids))
delete("notifications_ext",                 "DELETE FROM notifications_ext WHERE user_id IN %s", (user_ids,))
delete("push_subscriptions",                "DELETE FROM push_subscriptions WHERE user_id IN %s", (user_ids,))
# notification_preferences kullanıcıya bağlı tercih — silmiyoruz, kullanıcı kalıyor

print()
if DRY_RUN:
    print("DRY_RUN — ROLLBACK ediliyor (hiçbir şey silinmedi)")
    conn.rollback()
else:
    print("COMMIT ediliyor...")
    conn.commit()
    print("Tamamlandı.")
cur.close(); conn.close()
