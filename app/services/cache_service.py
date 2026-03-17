# -*- coding: utf-8 -*-
"""
Cache Service - Centralized caching logic for business operations
"""
from app.extensions import cache
from app.utils.cache_utils import CACHE_KEYS, get_cached_or_compute, invalidate_tenant_cache


class CacheService:
    """Centralized cache management service"""
    
    @staticmethod
    def get_vision_score(tenant_id, year):
        """Get cached vision score or compute"""
        from app.services.score_engine_service import compute_vision_score
        
        cache_key = CACHE_KEYS['vision_score'](tenant_id, year)
        
        return get_cached_or_compute(
            cache_key=cache_key,
            compute_func=lambda: compute_vision_score(tenant_id, year, persist_pg_scores=False),
            timeout=3600  # 1 hour
        )
    
    @staticmethod
    def invalidate_vision_score(tenant_id, year=None):
        """Invalidate vision score cache"""
        if year:
            cache.delete(CACHE_KEYS['vision_score'](tenant_id, year))
        else:
            # Invalidate all years
            from datetime import datetime
            current_year = datetime.now().year
            for y in range(current_year - 2, current_year + 2):
                cache.delete(CACHE_KEYS['vision_score'](tenant_id, y))
    
    @staticmethod
    def get_process_list(tenant_id, include_inactive=False):
        """Get cached process list"""
        from app.models.process import Process, ProcessSubStrategyLink
        from sqlalchemy.orm import joinedload, selectinload
        
        if include_inactive:
            # Don't cache inactive processes
            return Process.query.filter_by(tenant_id=tenant_id).all()
        
        cache_key = CACHE_KEYS['process_list'](tenant_id)
        
        def compute():
            return Process.query.options(
                joinedload(Process.leaders),
                joinedload(Process.members),
                joinedload(Process.owners),
                selectinload(Process.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.sub_strategy)
            ).filter_by(
                tenant_id=tenant_id,
                is_active=True
            ).order_by(Process.code).all()
        
        return get_cached_or_compute(
            cache_key=cache_key,
            compute_func=compute,
            timeout=600  # 10 minutes
        )
    
    @staticmethod
    def invalidate_process_cache(tenant_id, process_id=None):
        """Invalidate process cache"""
        cache.delete(CACHE_KEYS['process_list'](tenant_id))
        
        if process_id:
            cache.delete(CACHE_KEYS['process_detail'](process_id, tenant_id))
            cache.delete(CACHE_KEYS['kpi_list'](process_id))
    
    @staticmethod
    def get_process_kpis(process_id):
        """Get cached KPI list for process"""
        from app.models.process import ProcessKpi
        
        cache_key = CACHE_KEYS['kpi_list'](process_id)
        
        def compute():
            return ProcessKpi.query.filter_by(
                process_id=process_id,
                is_active=True
            ).order_by(ProcessKpi.code).all()
        
        return get_cached_or_compute(
            cache_key=cache_key,
            compute_func=compute,
            timeout=600  # 10 minutes
        )
    
    @staticmethod
    def invalidate_kpi_cache(process_id):
        """Invalidate KPI cache"""
        cache.delete(CACHE_KEYS['kpi_list'](process_id))
    
    @staticmethod
    def get_strategy_list(tenant_id):
        """Get cached strategy list"""
        from app.models.core import Strategy
        from sqlalchemy.orm import joinedload, selectinload
        
        cache_key = CACHE_KEYS['strategy_list'](tenant_id)
        
        def compute():
            return Strategy.query.options(
                selectinload(Strategy.sub_strategies)
            ).filter_by(
                tenant_id=tenant_id,
                is_active=True
            ).order_by(Strategy.code).all()
        
        return get_cached_or_compute(
            cache_key=cache_key,
            compute_func=compute,
            timeout=600  # 10 minutes
        )
    
    @staticmethod
    def invalidate_strategy_cache(tenant_id):
        """Invalidate strategy cache"""
        cache.delete(CACHE_KEYS['strategy_list'](tenant_id))
    
    @staticmethod
    def clear_tenant_cache(tenant_id):
        """Clear all cache for tenant"""
        return invalidate_tenant_cache(tenant_id)
    
    @staticmethod
    def warm_cache(tenant_id):
        """Warm cache with frequently accessed data"""
        from app.utils.cache_utils import warm_cache_for_tenant
        return warm_cache_for_tenant(tenant_id)
