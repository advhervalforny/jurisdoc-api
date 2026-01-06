"""
Models de Afirmação Jurídica e Fontes.
"""
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import text, Column, Text, Integer, String
# Importamos o BaseModel corrigido
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

# Hierarquia normativa definida no topo para evitar ImportError
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
    
    # SQLModel mapeia Enums automaticamente
    source_type: SourceType = Field(index=True, nullable=False)
    reference: str = Field(index=True, nullable=False)
    
    # Correção: sa_column evita o conflito de tipos posicionais/keywords
    excerpt: str = Field(sa_column=Column(Text, nullable=False))
    source_url: Optional[str] = Field(default=None, nullable=True)
    
    assertion_links: List["AssertionSource"] = Relationship(back_populates="source")
    
    @property
    def hierarchy_order(self) -> int:
        return SOURCE_HIERARCHY.get(self.source_type, 99)

class LegalAssertion(BaseModel, table=True):
    """ Afirmação Jurídica. """
    __tablename__ = "legal_assertions"
    
    document_version_id: UUID = Field(
        foreign_key="legal_document_versions.id",
        index=True,
        nullable=False
    )
    
    # Correção: sa_column para evitar conflito ArgumentError
    assertion_text: str = Field(sa_column=Column(Text, nullable=False))
    assertion_type: AssertionType = Field(index=True, nullable=False)
    
    # Para Enums e inteiros com default, usamos sa_column_kwargs sem o "type_"
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
    
    # Definimos como primary_key para garantir que o vínculo seja único
    assertion_id: UUID = Field(foreign_key="legal_assertions.id", primary_key=True)
    source_id: UUID = Field(foreign_key="legal_sources.id", primary_key=True)
    
    assertion: Optional[LegalAssertion] = Relationship(back_populates="source_links")
    source: Optional[LegalSource] = Relationship(back_populates="assertion_links")
