from uuid import UUID
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Column, Text, Enum as SAEnum, ForeignKey, String
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

SOURCE_HIERARCHY = {
    SourceType.CONSTITUICAO: 1,
    SourceType.LEI: 2,
    SourceType.JURISPRUDENCIA: 3,
    SourceType.DOUTRINA: 4,
    SourceType.ARGUMENTACAO: 5,
}

class LegalSource(BaseModel, table=True):
    __tablename__ = "legal_sources"
    source_type: SourceType = Field(sa_column=Column(SAEnum(SourceType), nullable=False, index=True))
    reference: str = Field(sa_column=Column(String, nullable=False, index=True))
    excerpt: str = Field(sa_column=Column(Text, nullable=False))
    source_url: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    assertion_links: List["AssertionSource"] = Relationship(back_populates="source")

class LegalAssertion(BaseModel, table=True):
    __tablename__ = "legal_assertions"
    document_version_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_document_versions.id"), nullable=False, index=True)
    )
    assertion_text: str = Field(sa_column=Column(Text, nullable=False))
    assertion_type: AssertionType = Field(sa_column=Column(SAEnum(AssertionType), nullable=False, index=True))
    confidence_level: ConfidenceLevel = Field(sa_column=Column(SAEnum(ConfidenceLevel), nullable=False))
    position: int = Field(default=0)
    source_links: List["AssertionSource"] = Relationship(back_populates="assertion")
    document_version: Optional["LegalDocumentVersion"] = Relationship(back_populates="assertions")

class AssertionSource(BaseModel, table=True):
    __tablename__ = "assertion_sources"
    assertion_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_assertions.id"), primary_key=True))
    source_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_sources.id"), primary_key=True))
    assertion: Optional[LegalAssertion] = Relationship(back_populates="source_links")
    source: Optional[LegalSource] = Relationship(back_populates="assertion_links")
