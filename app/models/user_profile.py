"""
Model de perfil de usuário.
Complementa auth.users do Supabase com dados profissionais.
"""
from datetime import datetime
from uuid import UUID
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case


class UserProfile(BaseModel, TimestampMixin, table=True):
    """
    Perfil profissional do usuário.
    
    Relacionado com auth.users do Supabase via user_id.
    Contém informações como OAB, nome completo, etc.
    """
    __tablename__ = "user_profiles"
    
    # FK para auth.users (gerenciado pelo Supabase)
    user_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            unique=True,
            nullable=False,
            index=True
        )
    )
    
    # Dados profissionais
    full_name: str = Field(
        sa_column=Column(String, nullable=False)
    )
    oab_number: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True)
    )
    oab_state: Optional[str] = Field(
        default=None,
        sa_column=Column(String(2), nullable=True)  # UF
    )
    phone: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True)
    )
    
    # Relacionamentos
    cases: list["Case"] = Relationship(back_populates="user_profile")
    
    def __repr__(self) -> str:
        return f"<UserProfile {self.full_name} (OAB: {self.oab_state}/{self.oab_number})>"
