"""
Models package for py_life application.

This package contains all database models including:
- User and authentication models
- Core base models and mixins
- Association tables for RBAC
"""

from .core.models import (
    BaseModel,
    TimestampOnlyModel,
    User,
    MagicLink,
    Role,
    Permission,
    UserRole,
    RolePermission,
)
from .core.base import Base, engine, SessionLocal, get_db
from .core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from .associations import Family, FamilyMember, FamilyInvitation

__all__ = [
    # Base models
    'BaseModel',
    'TimestampOnlyModel',
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    
    # Mixins
    'UUIDMixin',
    'TimestampMixin',
    'SoftDeleteMixin',
    
    # User and Auth models
    'User',
    'MagicLink',
    'Role',
    'Permission',
    'UserRole',
    'RolePermission',
    
    # Family models
    'Family',
    'FamilyMember',
    'FamilyInvitation',
]
