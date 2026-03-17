"""
Cache Service - Centralized caching for frequently accessed data
"""
from functools import wraps
from flask import current_app
from extensions import cache
import json

# Cache key prefixes
CACHE_PREFIX_DASHBOARD = 'dashboard'
CACHE_PREFIX_USER_PERMS = 'user_perms'
CACHE_PREFIX_STRATEGY_TREE = 'strategy_tree'
CACHE_PREFIX_ORG_STATS = 'org_stats'
CACHE_PREFIX_PROJECT_LIST = 'project_list'

# Cache timeouts (in seconds)
CACHE_TIMEOUT_SHORT = 300      # 5 minutes
CACHE_TIMEOUT_MEDIUM = 900     # 15 minutes
CACHE_TIMEOUT_LONG = 1800      # 30 minutes
CACHE_TIMEOUT_VERY_LONG = 3600 # 1 hour


def cache_key_with_user(prefix, user_id, **kwargs):
    """Generate cache key with user ID and optional parameters"""
    key_parts = [prefix, str(user_id)]
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    return ':'.join(key_parts)


def cache_key_with_org(prefix, kurum_id, **kwargs):
    """Generate cache key with organization ID"""
    key_parts = [prefix, f"org_{kurum_id}"]
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    return ':'.join(key_parts)


def invalidate_user_cache(user_id):
    """Invalidate all cache entries for a specific user"""
    try:
        patterns = [
            f"{CACHE_PREFIX_DASHBOARD}:{user_id}*",
            f"{CACHE_PREFIX_USER_PERMS}:{user_id}*",
        ]
        for pattern in patterns:
            cache.delete_memoized_verhash(pattern)
        current_app.logger.info(f"Cache invalidated for user {user_id}")
    except Exception as e:
        current_app.logger.error(f"Cache invalidation error: {e}")


def invalidate_org_cache(kurum_id):
    """Invalidate all cache entries for a specific organization"""
    try:
        patterns = [
            f"{CACHE_PREFIX_ORG_STATS}:org_{kurum_id}*",
            f"{CACHE_PREFIX_PROJECT_LIST}:org_{kurum_id}*",
        ]
        for pattern in patterns:
            cache.delete_memoized_verhash(pattern)
        current_app.logger.info(f"Cache invalidated for org {kurum_id}")
    except Exception as e:
        current_app.logger.error(f"Cache invalidation error: {e}")


def invalidate_strategy_cache():
    """Invalidate strategy tree cache (affects all users)"""
    try:
        cache.delete_memoized(f"{CACHE_PREFIX_STRATEGY_TREE}:*")
        current_app.logger.info("Strategy cache invalidated")
    except Exception as e:
        current_app.logger.error(f"Cache invalidation error: {e}")


# Decorators for easy caching

def cache_dashboard_data(timeout=CACHE_TIMEOUT_MEDIUM):
    """Decorator to cache dashboard data per user"""
    def decorator(f):
        @wraps(f)
        def wrapped(user_id, *args, **kwargs):
            key = cache_key_with_user(CACHE_PREFIX_DASHBOARD, user_id, **kwargs)
            result = cache.get(key)
            if result is None:
                result = f(user_id, *args, **kwargs)
                cache.set(key, result, timeout=timeout)
            return result
        return wrapped
    return decorator


def cache_user_permissions(timeout=CACHE_TIMEOUT_LONG):
    """Decorator to cache user permissions"""
    def decorator(f):
        @wraps(f)
        def wrapped(user_id, *args, **kwargs):
            key = cache_key_with_user(CACHE_PREFIX_USER_PERMS, user_id)
            result = cache.get(key)
            if result is None:
                result = f(user_id, *args, **kwargs)
                cache.set(key, result, timeout=timeout)
            return result
        return wrapped
    return decorator


def cache_org_stats(timeout=CACHE_TIMEOUT_MEDIUM):
    """Decorator to cache organization statistics"""
    def decorator(f):
        @wraps(f)
        def wrapped(kurum_id, *args, **kwargs):
            key = cache_key_with_org(CACHE_PREFIX_ORG_STATS, kurum_id, **kwargs)
            result = cache.get(key)
            if result is None:
                result = f(kurum_id, *args, **kwargs)
                cache.set(key, result, timeout=timeout)
            return result
        return wrapped
    return decorator


# Manual caching functions

def get_cached_dashboard_stats(user_id):
    """Get cached dashboard statistics for a user"""
    key = cache_key_with_user(CACHE_PREFIX_DASHBOARD, user_id)
    return cache.get(key)


def set_cached_dashboard_stats(user_id, data, timeout=CACHE_TIMEOUT_MEDIUM):
    """Cache dashboard statistics for a user"""
    key = cache_key_with_user(CACHE_PREFIX_DASHBOARD, user_id)
    cache.set(key, data, timeout=timeout)


def get_cached_strategy_tree():
    """Get cached strategy tree"""
    key = f"{CACHE_PREFIX_STRATEGY_TREE}:all"
    return cache.get(key)


def set_cached_strategy_tree(data, timeout=CACHE_TIMEOUT_LONG):
    """Cache strategy tree"""
    key = f"{CACHE_PREFIX_STRATEGY_TREE}:all"
    cache.set(key, data, timeout=timeout)


def clear_all_cache():
    """Clear all application cache (use with caution)"""
    try:
        cache.clear()
        current_app.logger.info("All cache cleared")
        return True
    except Exception as e:
        current_app.logger.error(f"Cache clear error: {e}")
        return False
