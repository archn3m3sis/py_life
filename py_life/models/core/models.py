"""
Base models combining mixins for common functionality.
"""
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from datetime import datetime

from .base import Base
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin


class BaseModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Base model class that includes UUID primary key, timestamps, and soft delete.
    
    This abstract base class provides:
    - UUID primary key (id)
    - Automatic timestamps (created_at, updated_at)
    - Soft delete functionality (is_deleted, deleted_at)
    - Common query methods
    """
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        # Convert CamelCase to snake_case for table names
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self, exclude_deleted=True):
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert UUID to string for JSON serialization
            if hasattr(value, 'hex'):
                value = str(value)
            result[column.name] = value
        
        if exclude_deleted and self.is_deleted:
            return None
        
        return result
    
    @classmethod
    def get_active_query(cls, session):
        """Get query for active (non-deleted) records."""
        return cls.filter_active(session.query(cls))
    
    @classmethod
    def get_all_query(cls, session):
        """Get query for all records including deleted ones."""
        return session.query(cls)


class TimestampOnlyModel(Base, UUIDMixin, TimestampMixin):
    """
    Base model with UUID and timestamps only (no soft delete).
    
    Use this for models that should be permanently deleted rather than soft-deleted.
    """
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert UUID to string for JSON serialization
            if hasattr(value, 'hex'):
                value = str(value)
            result[column.name] = value
        return result


# User and Authentication Models

class User(BaseModel):
    """User model with email, name, avatar, and family association."""
    __tablename__ = 'users'

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String)

    # Relationships
    magic_links = relationship("MagicLink", back_populates="user")
    roles = relationship('Role', secondary="user_roles", back_populates="users")
    family_memberships = relationship("FamilyMember", back_populates="user")

    # reflex-magic-link-auth integration helper methods
    def create_magic_link(self, token, expires_at):
        """Create a new magic link for this user."""
        return MagicLink(user_id=self.id, token=token, expires_at=expires_at)
    
    def get_active_magic_links(self, session):
        """Get all active (unused, non-expired) magic links for this user."""
        from sqlalchemy import and_
        return session.query(MagicLink).filter(
            and_(
                MagicLink.user_id == self.id,
                MagicLink.used_at.is_(None),
                MagicLink.expires_at > datetime.utcnow()
            )
        ).all()
    
    def has_permission(self, permission_name):
        """Check if user has a specific permission through their roles."""
        for role in self.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        return False
    
    def get_families(self):
        """Get all families this user belongs to."""
        return [membership.family for membership in self.family_memberships]
    
    def get_family_role(self, family_id):
        """Get user's role in a specific family."""
        for membership in self.family_memberships:
            if str(membership.family_id) == str(family_id):
                return membership.role
        return None
    
    def is_family_member(self, family_id):
        """Check if user is a member of a specific family."""
        return self.get_family_role(family_id) is not None


class MagicLink(BaseModel):
    """Magic link model for passwordless authentication."""
    __tablename__ = 'magic_links'

    token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)

    # Relationships
    user = relationship("User", back_populates="magic_links")

    def is_expired(self):
        """Check if the magic link has expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_used(self):
        """Check if the magic link has been used."""
        return self.used_at is not None
    
    def is_valid(self):
        """Check if the magic link is valid (not expired and not used)."""
        return not self.is_expired() and not self.is_used()
    
    def mark_as_used(self):
        """Mark the magic link as used."""
        self.used_at = datetime.utcnow()


class Role(BaseModel):
    """Role model for RBAC."""
    __tablename__ = 'roles'

    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)

    # Relationships
    users = relationship('User', secondary='user_roles', back_populates='roles')
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')


class Permission(BaseModel):
    """Permission model for RBAC."""
    __tablename__ = 'permissions'

    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)

    # Relationships
    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')


# Association Tables

class UserRole(Base):
    """Association table for User-Role many-to-many relationship."""
    __tablename__ = 'user_roles'

    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    role_id = Column(String, ForeignKey('roles.id'), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = Column(String)  # ID of user who assigned this role


class RolePermission(Base):
    """Association table for Role-Permission many-to-many relationship."""
    __tablename__ = 'role_permissions'

    role_id = Column(String, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(String, ForeignKey('permissions.id'), primary_key=True)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    granted_by = Column(String)  # ID of user who granted this permission
