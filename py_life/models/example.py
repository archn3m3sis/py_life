"""
Example model demonstrating usage of the base model and mixins.
"""
from sqlalchemy import Column, String, Text, Integer

from .core import BaseModel, TimestampOnlyModel


class User(BaseModel):
    """
    Example User model using BaseModel.
    
    This model will have:
    - UUID primary key (id)
    - Timestamps (created_at, updated_at)
    - Soft delete (is_deleted, deleted_at)
    - Table name: 'user' (auto-generated from class name)
    """
    
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class UserSession(TimestampOnlyModel):
    """
    Example UserSession model using TimestampOnlyModel.
    
    This model will have:
    - UUID primary key (id)
    - Timestamps (created_at, updated_at)
    - No soft delete (sessions should be permanently deleted)
    - Table name: 'user_session' (auto-generated from class name)
    """
    
    user_id = Column(String(36), nullable=False)  # UUID as string
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(Integer, nullable=False)  # Unix timestamp
    
    def __repr__(self):
        return f"<UserSession(user_id='{self.user_id}', token='{self.session_token[:10]}...')>"
