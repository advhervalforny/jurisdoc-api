from uuid import UUID
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case

class UserProfile(BaseModel, TimestampMixin, table=True):
    __tablename__ = "user_profiles"
    user_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), unique=True, nullable=False, index=True))
    full_name: str = Field(sa_column=Column(String, nullable=False))
    oab_number: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    oab_state: Optional[str] = Field(default=None, sa_column=Column(String(2), nullable=True))
    phone: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    
    # Sincronizado com o back_populates do case.py
    cases: List["Case"] = Relationship(back_populates="user_profile")
