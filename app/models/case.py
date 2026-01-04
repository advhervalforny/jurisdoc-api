"""
Model de Caso/Processo.

Contexto jurídico onde todas as peças existem.
Regra constitucional: Nenhuma peça existe sem um caso.
"""
from datetime import datetime
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile
    from app.models.legal_domain import LegalArea
    from app.models.document import LegalDocument
    from app.models.attachment import DocumentAttachment


class Case(BaseModel, TimestampMixin, table=True):
    """
    Caso/Processo jurídico.
    
    Representa o contexto onde todas as peças jurídicas existem.
    Um caso pertence a um usuário e a uma área do direito.
    
    ⚠️ REGRA CONSTITUCIONAL:
    Nenhum documento jurídico pode existir sem estar vinculado a um caso.
    """
    __tablename__ = "cases"
    
    # FK para usuário (auth.users do Supabase)
    user_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        )
    )
    
    # FK para área do direito
    legal_area_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="legal_areas.id"
    )
    
    # Dados do caso
    title: str = Field(
        sa_column=Column(String, nullable=False),
        description="Título do caso, ex: 'Negativação Indevida – João da Silva'"
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
        description="Descrição breve do caso"
    )
    process_number: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
        description="Número do processo judicial, se houver"
    )
    
    # Relacionamentos
    legal_area: Optional["LegalArea"] = Relationship(back_populates="cases")
    documents: List["LegalDocument"] = Relationship(back_populates="case")
    attachments: List["DocumentAttachment"] = Relationship(back_populates="case")
    
    # Relacionamento com UserProfile via user_id
    # Nota: Este relacionamento é indireto pois user_id referencia auth.users
    
    @property
    def documents_count(self) -> int:
        """Retorna a quantidade de documentos no caso."""
        return len(self.documents) if self.documents else 0
    
    def __repr__(self) -> str:
        return f"<Case {self.title} (user: {self.user_id})>"
