# -*- coding: utf-8 -*-
"""
Query Optimizer - N+1 problem solutions and eager loading helpers
"""
from sqlalchemy.orm import joinedload, selectinload, subqueryload
from app.models.process import Process, ProcessKpi, ProcessActivity, KpiData, ProcessSubStrategyLink
from app.models.core import Strategy, SubStrategy, User


def get_processes_optimized(tenant_id, include_inactive=False):
    """
    Get processes with optimized eager loading to prevent N+1 queries
    
    Args:
        tenant_id: Tenant ID
        include_inactive: Include inactive processes
    
    Returns:
        List of Process objects with preloaded relationships
    """
    query = Process.query.options(
        # Use joinedload for one-to-many with small datasets
        joinedload(Process.leaders),
        joinedload(Process.members),
        joinedload(Process.owners),
        
        # Use selectinload for many-to-many (via association object)
        selectinload(Process.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.sub_strategy),
        
        # Preload parent if exists
        joinedload(Process.parent)
    ).filter_by(tenant_id=tenant_id)
    
    if not include_inactive:
        query = query.filter_by(is_active=True)
    
    return query.order_by(Process.code).all()


def get_process_with_kpis(process_id, tenant_id):
    """
    Get single process with all KPIs and their latest data
    Optimized for process karne page
    
    Args:
        process_id: Process ID
        tenant_id: Tenant ID
    
    Returns:
        Process object with preloaded KPIs and data
    """
    return Process.query.options(
        joinedload(Process.leaders),
        joinedload(Process.members),
        joinedload(Process.owners),
        selectinload(Process.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.sub_strategy),
        
        # Preload KPIs with their data
        selectinload(Process.kpis).joinedload(ProcessKpi.kpi_data),
        
        # Preload activities
        selectinload(Process.activities)
    ).filter_by(
        id=process_id,
        tenant_id=tenant_id,
        is_active=True
    ).first()


def get_kpis_with_data(process_id, year=None):
    """
    Get KPIs with their data for a specific year
    Optimized for karne calculations
    
    Args:
        process_id: Process ID
        year: Year filter (optional)
    
    Returns:
        List of ProcessKpi objects with preloaded data
    """
    query = ProcessKpi.query.options(
        # Preload KPI data
        selectinload(ProcessKpi.kpi_data)
    ).filter_by(
        process_id=process_id,
        is_active=True
    )
    
    kpis = query.all()
    
    # Filter data by year if specified
    if year and kpis:
        for kpi in kpis:
            kpi.kpi_data = [
                data for data in kpi.kpi_data 
                if data.data_date and data.data_date.year == year and data.is_active
            ]
    
    return kpis


def get_strategies_optimized(tenant_id):
    """
    Get strategies with sub-strategies preloaded
    
    Args:
        tenant_id: Tenant ID
    
    Returns:
        List of Strategy objects with preloaded sub-strategies
    """
    return Strategy.query.options(
        selectinload(Strategy.sub_strategies)
    ).filter_by(
        tenant_id=tenant_id,
        is_active=True
    ).order_by(Strategy.code).all()


def get_users_optimized(tenant_id):
    """
    Get users with role preloaded
    
    Args:
        tenant_id: Tenant ID
    
    Returns:
        List of User objects with preloaded roles
    """
    return User.query.options(
        joinedload(User.role),
        joinedload(User.tenant)
    ).filter_by(
        tenant_id=tenant_id,
        is_active=True
    ).order_by(User.first_name, User.last_name).all()


def get_kpi_data_with_audit(kpi_data_id):
    """
    Get KPI data with audit trail
    
    Args:
        kpi_data_id: KpiData ID
    
    Returns:
        KpiData object with preloaded audit records
    """
    from app.models.process import KpiDataAudit
    
    return KpiData.query.options(
        selectinload(KpiData.audit_logs),
        joinedload(KpiData.process_kpi),
        joinedload(KpiData.created_by_user)
    ).filter_by(id=kpi_data_id).first()


def bulk_load_kpi_data(kpi_ids, year=None):
    """
    Bulk load KPI data for multiple KPIs
    Prevents N+1 when loading data for multiple KPIs
    
    Args:
        kpi_ids: List of KPI IDs
        year: Year filter (optional)
    
    Returns:
        Dict mapping kpi_id to list of KpiData objects
    """
    query = KpiData.query.filter(
        KpiData.process_kpi_id.in_(kpi_ids),
        KpiData.is_active == True
    )
    
    if year:
        from sqlalchemy import extract
        query = query.filter(extract('year', KpiData.data_date) == year)
    
    all_data = query.all()
    
    # Group by KPI ID
    result = {}
    for data in all_data:
        if data.process_kpi_id not in result:
            result[data.process_kpi_id] = []
        result[data.process_kpi_id].append(data)
    
    return result


# Query performance monitoring decorator
def log_query_count(func):
    """
    Decorator to log number of queries executed
    Useful for detecting N+1 problems in development
    
    Usage:
        @log_query_count
        def my_view():
            return render_template('page.html')
    """
    from functools import wraps
    import logging
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask_sqlalchemy import get_debug_queries
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Log query count
        queries = get_debug_queries()
        if queries:
            total_duration = sum(q.duration for q in queries)
            logging.info(
                f"{func.__name__}: {len(queries)} queries, "
                f"{total_duration:.2f}s total"
            )
            
            # Warn if too many queries
            if len(queries) > 50:
                logging.warning(
                    f"⚠️ {func.__name__}: {len(queries)} queries detected! "
                    f"Possible N+1 problem"
                )
        
        return result
    
    return wrapper


# Batch operations
def batch_update_processes(process_updates):
    """
    Batch update multiple processes
    More efficient than individual updates
    
    Args:
        process_updates: List of dicts with 'id' and update fields
    
    Example:
        batch_update_processes([
            {'id': 1, 'progress': 50},
            {'id': 2, 'progress': 75}
        ])
    """
    from app.models import db
    
    for update in process_updates:
        process_id = update.pop('id')
        db.session.query(Process).filter_by(id=process_id).update(update)
    
    db.session.commit()


def batch_create_kpi_data(kpi_data_list):
    """
    Batch create KPI data entries
    More efficient than individual inserts
    
    Args:
        kpi_data_list: List of dicts with KpiData fields
    
    Example:
        batch_create_kpi_data([
            {'process_kpi_id': 1, 'actual_value': 85, ...},
            {'process_kpi_id': 2, 'actual_value': 92, ...}
        ])
    """
    from app.models import db
    
    db.session.bulk_insert_mappings(KpiData, kpi_data_list)
    db.session.commit()
