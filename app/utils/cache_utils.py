# -*- coding: utf-8 -*-
"""
Cache utilities and decorators
"""
from functools import wraps
from flask import request
from flask_login import current_user
from app.extensions import cache


def make_cache_key(*args, **kwargs):
    """
    Generate cache key from request path and args
    Includes tenant_id for multi-tenancy
    """
    path = request.path
    args_str = str(sorted(request.args.items()))
    
    # Include tenant_id if user is authenticated
    tenant_id = ""
    if current_user and current_user.is_authenticated:
        tenant_id = f"_tenant_{current_user.tenant_id}"
    
    return f"{path}{args_str}{tenant_id}"


def cache_with_tenant(timeout=300, key_prefix='view'):
    """
    Cache decorator that includes tenant_id in cache key
    
    Usage:
        @cache_with_tenant(timeout=600)
        def get_processes():
            return Process.query.all()
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            tenant_id = current_user.tenant_id if current_user.is_authenticated else 'anonymous'
            cache_key = f"{key_prefix}_{f.__name__}_{tenant_id}_{args}_{kwargs}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        
        return decorated_function
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching pattern
    
    Usage:
        invalidate_cache_pattern('process_*')
    """
    try:
        # This works with Redis backend
        if hasattr(cache.cache, '_client'):
            redis_client = cache.cache._client
            keys = redis_client.keys(f"{cache.config['CACHE_KEY_PREFIX']}{pattern}")
            if keys:
                redis_client.delete(*keys)
                return len(keys)
        return 0
    except Exception as e:
        # Fallback: clear all cache
        cache.clear()
        return -1


def invalidate_tenant_cache(tenant_id):
    """
    Invalidate all cache for a specific tenant
    
    Usage:
        invalidate_tenant_cache(current_user.tenant_id)
    """
    return invalidate_cache_pattern(f'*_tenant_{tenant_id}_*')


def cache_key_for_model(model_name, model_id, tenant_id=None):
    """
    Generate consistent cache key for model instances
    
    Usage:
        key = cache_key_for_model('Process', 123, tenant_id=1)
    """
    if tenant_id:
        return f"model_{model_name}_{model_id}_tenant_{tenant_id}"
    return f"model_{model_name}_{model_id}"


# Predefined cache keys
CACHE_KEYS = {
    'vision_score': lambda tenant_id, year: f'vision_score_{tenant_id}_{year}',
    'process_list': lambda tenant_id: f'process_list_{tenant_id}',
    'process_detail': lambda process_id, tenant_id: f'process_{process_id}_{tenant_id}',
    'kpi_list': lambda process_id: f'kpi_list_{process_id}',
    'strategy_list': lambda tenant_id: f'strategy_list_{tenant_id}',
    'user_list': lambda tenant_id: f'user_list_{tenant_id}',
}


def get_cached_or_compute(cache_key, compute_func, timeout=300):
    """
    Get from cache or compute and cache
    
    Usage:
        result = get_cached_or_compute(
            cache_key='my_key',
            compute_func=lambda: expensive_computation(),
            timeout=600
        )
    """
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    result = compute_func()
    cache.set(cache_key, result, timeout=timeout)
    return result


# Cache warming functions
def warm_cache_for_tenant(tenant_id):
    """
    Pre-populate cache with frequently accessed data
    Call this after data updates or on application start
    """
    from app.models.process import Process
    from app.models.core import Strategy, User
    
    try:
        # Cache process list
        processes = Process.query.filter_by(
            tenant_id=tenant_id,
            is_active=True
        ).all()
        cache.set(
            CACHE_KEYS['process_list'](tenant_id),
            processes,
            timeout=600
        )
        
        # Cache strategy list
        strategies = Strategy.query.filter_by(
            tenant_id=tenant_id,
            is_active=True
        ).all()
        cache.set(
            CACHE_KEYS['strategy_list'](tenant_id),
            strategies,
            timeout=600
        )
        
        # Cache user list
        users = User.query.filter_by(
            tenant_id=tenant_id,
            is_active=True
        ).all()
        cache.set(
            CACHE_KEYS['user_list'](tenant_id),
            users,
            timeout=600
        )
        
        return True
    except Exception as e:
        import logging
        logging.error(f"Cache warming failed for tenant {tenant_id}: {e}")
        return False
