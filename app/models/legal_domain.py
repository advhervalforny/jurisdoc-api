"""
Models de domínio jurídico estrutural.
- LegalArea: Áreas do direito (civil, penal)
- LegalPieceType: Tipos de peças jurídicas
"""
from datetime import datetime
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.document import LegalDocument


class LegalArea(BaseModel, table=True):
    """
    Área do Direito.
    
    Exemplos: civil, penal, trabalhista, etc.
    Define o domínio jurídico dos casos e peças.
    """
    __tablename__ = "legal_areas"
    
    slug: str = Field(
        sa_column=Column(String, unique=True, nullable=False, index=True)
    )
    name: str = Field(
        sa_column=Column(String, nullable=False)
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True)
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true"))
    )
    
    # Relacionamentos
    piece_types: List["LegalPieceType"] = Relationship(back_populates="legal_area")
    cases: List["Case"] = Relationship(back_populates="legal_area")
    
    def __repr__(self) -> str:
        return f"<LegalArea {self.slug}: {self.name}>"


class LegalPieceType(BaseModel, table=True):
    """
    Tipo de peça jurídica.
    
    Exemplos: petição inicial, contestação, réplica, apelação.
    Cada tipo pertence a uma área do direito.
    """
    __tablename__ = "legal_piece_types"
    
    # FK para área do direito
    legal_area_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="legal_areas.id"
    )
    
    slug: str = Field(
        sa_column=Column(String, nullable=False)
    )
    name: str = Field(
        sa_column=Column(String, nullable=False)
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True)
    )
    legal_basis: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
        description="Base legal, ex: 'Art. 319 CPC'"
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true"))
    )
    
    # Relacionamentos
    legal_area: Optional[LegalArea] = Relationship(back_populates="piece_types")
    documents: List["LegalDocument"] = Relationship(back_populates="piece_type")
    
    def __repr__(self) -> str:
        return f"<LegalPieceType {self.slug}: {self.name} ({self.legal_basis})>"
