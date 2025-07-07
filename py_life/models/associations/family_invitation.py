from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from ..core.models import BaseModel

class FamilyInvitation(BaseModel):
    __tablename__ = 'family_invitations'

    family_id = Column(String, ForeignKey('families.id'), nullable=False)
    invited_by_user_id = Column(String, ForeignKey('users.id'), nullable=False)
    invited_email = Column(String, nullable=False)
    invited_user_id = Column(String, ForeignKey('users.id'), nullable=True)  # Set when user accepts
    role = Column(String, nullable=False)  # Role to be assigned when accepted
    invitation_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    declined_at = Column(DateTime, nullable=True)
    is_accepted = Column(Boolean, default=False, nullable=False)

    # Relationships
    family = relationship("Family")
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])
    invited_user = relationship("User", foreign_keys=[invited_user_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default expiration to 7 days from now
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=7)

    def is_expired(self):
        """Check if the invitation has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if the invitation is valid (not expired, not accepted, not declined)."""
        return (not self.is_expired() and 
                not self.is_accepted and 
                self.declined_at is None)

    def accept(self, user_id):
        """Accept the invitation."""
        self.invited_user_id = user_id
        self.accepted_at = datetime.utcnow()
        self.is_accepted = True

    def decline(self):
        """Decline the invitation."""
        self.declined_at = datetime.utcnow()

    def __repr__(self):
        return f"<FamilyInvitation(family_id={self.family_id}, invited_email={self.invited_email}, role={self.role})>"
