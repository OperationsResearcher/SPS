"""
Marshmallow Schemas
Sprint 5-6: Güvenlik ve Stabilite
Input validation ve serialization
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import datetime

__all__ = [
    'KpiDataSchema',
    'ProcessSchema',
    'ProcessKpiSchema',
    'UserSchema',
    'StrategySchema',
    'ActivitySchema'
]
