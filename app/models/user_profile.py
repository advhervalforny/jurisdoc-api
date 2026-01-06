"""
Model de perfil de usuário.
Complementa auth.users do Supabase com dados profissionais.
"""
from uuid import UUID
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case

class UserProfile(BaseModel, TimestampMixin, table=True):
    """
    Perfil profissional do usuário.
    """
    __tablename__ = "user_profiles"
    
    # ID do usuário vindo do Supabase Auth
    user_id: UUID = Field(
        unique=True,
        nullable=False,
        index=True
    )
    
    full_name: str = Field(nullable=False)
    oab_number: Optional[str] = Field(default=None, nullable=True)
    oab_state: Optional[str] = Field(default=None, max_length=2, nullable=True)
    phone: Optional[str] = Field(default=None, nullable=True)
    
    # Relacionamentos
    cases: list["Case"] = Relationship(back_populates="user_profile")
    
    def __repr__(self) -> str:
        return f"<UserProfile {self.full_name} (OAB: {self.oab_state}/{self.oab_number})>"
