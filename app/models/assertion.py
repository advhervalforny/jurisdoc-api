"""
Models de Afirmação Jurídica e Fontes.
"""
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import text, Column, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import LegalDocumentVersion

class AssertionType(str, Enum):
    FATO = "fato"
    TESE = "tese"
    FUNDAMENTO = "fundamento"
    PEDIDO = "pedido"

class ConfidenceLevel(str, Enum):
    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"

class SourceType(str, Enum):
    CONSTITUICAO = "constituicao"
    LEI = "lei"
    JURISPRUDENCIA = "jurisprudencia"
    DOUTRINA = "doutrina"
    ARGUMENTACAO = "argumentacao"

# Hierarquia normativa (DEFINIDA NO TOPO PARA EVITAR IMPORT ERRORS)
SOURCE_HIERARCHY = {
    SourceType.CONSTITUICAO: 1,
    SourceType.LEI: 2,
    SourceType.JURISPRUDENCIA: 3,
    SourceType.DOUTRINA: 4,
    SourceType.ARGUMENTACAO: 5,
}

class LegalSource(BaseModel, table=True):
    """ Fonte Jurídica. """
    __tablename__ = "legal_sources"
    
    # SQLModel lida com Enums automaticamente
    source_type: SourceType = Field(index=True, nullable=False)
    reference: str = Field(index=True, nullable=False)
    
    # Para campos de texto longo, usamos sa_column_kwargs
    excerpt: str = Field(sa_column_kwargs={"type_": Text, "nullable": False})
    source_url: Optional[str] = Field(default=None, nullable=True)
    
    assertion_links: List["AssertionSource"] = Relationship(back_populates="source")
    
    @property
    def hierarchy_order(self) -> int:
        return SOURCE_HIERARCHY.get(self.source_type, 99)

class LegalAssertion(BaseModel, table=True):
    """ Afirmação Jurídica (Coração do Sistema). """
    __tablename__ = "legal_assertions"
    
    document_version_id: UUID = Field(
        foreign_key="legal_document_versions.id",
        index=True,
        nullable=False
    )
    
    assertion_text: str = Field(sa_column_kwargs={"type_": Text, "nullable": False})
    assertion_type: AssertionType = Field(index=True, nullable=False)
    
    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIO,
        sa_column_kwargs={"server_default": text("'medio'")}
    )
    
    position: int = Field(
        default=0,
        sa_column_kwargs={"server_default": text("0")}
    )
    
    source_links: List["AssertionSource"] = Relationship(back_populates="assertion")

class AssertionSource(BaseModel, table=True):
    """ Vínculo entre Assertion e Source. """
    __tablename__ = "assertion_sources"
    
    assertion_id: UUID = Field(foreign_key="legal_assertions.id", primary_key=True)
    source_id: UUID = Field(foreign_key="legal_sources.id", primary_key=True)
    
    assertion: Optional[LegalAssertion] = Relationship(back_populates="source_links")
    source: Optional[LegalSource] = Relationship(back_populates="assertion_links")
