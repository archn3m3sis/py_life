from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..core.models import BaseModel

class FamilyMember(BaseModel):
    __tablename__ = 'family_members'

    family_id = Column(String, ForeignKey('families.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    role = Column(String, nullable=False)  # e.g., "parent", "child", "admin", etc.

    # Relationships
    family = relationship("Family", back_populates="members")
    user = relationship("User", back_populates="family_memberships")

    # Ensure unique combination of family_id and user_id
    __table_args__ = (
        UniqueConstraint('family_id', 'user_id', name='unique_family_user'),
    )

    def __repr__(self):
        return f"<FamilyMember(family_id={self.family_id}, user_id={self.user_id}, role={self.role})>"
