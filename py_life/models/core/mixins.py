"""
SQLAlchemy mixins for common model functionality.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean, String, event
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import Query


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type when available, otherwise uses CHAR(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class UUIDMixin:
    """Mixin to add UUID primary key to models."""
    
    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps."""
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin to add soft delete functionality."""
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False
    )
    
    deleted_at = Column(
        DateTime,
        nullable=True
    )
    
    def soft_delete(self):
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
    
    @classmethod
    def filter_active(cls, query: Query):
        """Filter out soft-deleted records."""
        return query.filter(cls.is_deleted == False)
    
    @classmethod
    def filter_deleted(cls, query: Query):
        """Filter only soft-deleted records."""
        return query.filter(cls.is_deleted == True)


# Event listeners for automatic timestamp updates
@event.listens_for(TimestampMixin, 'before_update', propagate=True)
def update_timestamp(mapper, connection, target):
    """Automatically update the updated_at timestamp before update."""
    target.updated_at = datetime.utcnow()


@event.listens_for(SoftDeleteMixin, 'before_update', propagate=True)
def update_deleted_at(mapper, connection, target):
    """Automatically set deleted_at when is_deleted is set to True."""
    if target.is_deleted and target.deleted_at is None:
        target.deleted_at = datetime.utcnow()
    elif not target.is_deleted:
        target.deleted_at = None
