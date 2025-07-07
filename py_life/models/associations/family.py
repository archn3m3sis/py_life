from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship
from ..core.models import BaseModel

class Family(BaseModel):
    __tablename__ = 'families'

    name = Column(String, nullable=False)
    settings = Column(JSON, nullable=True)  # Settings stored as JSON

    members = relationship("FamilyMember", back_populates="family")

