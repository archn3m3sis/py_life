"""
Core database models and mixins.

This module provides the foundational database components:
- Base: SQLAlchemy declarative base
- BaseModel: Full-featured base model with UUID, timestamps, and soft delete
- TimestampOnlyModel: Base model with UUID and timestamps only
- Individual mixins: UUIDMixin, TimestampMixin, SoftDeleteMixin
- Database utilities: engine, SessionLocal, get_db
"""

from .base import Base, engine, SessionLocal, get_db
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin, GUID
from .models import BaseModel, TimestampOnlyModel

__all__ = [
    # Base components
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    
    # Mixins
    'UUIDMixin',
    'TimestampMixin',
    'SoftDeleteMixin',
    'GUID',
    
    # Base models
    'BaseModel',
    'TimestampOnlyModel',
]
