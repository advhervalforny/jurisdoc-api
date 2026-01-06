from uuid import UUID
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Text, Enum as SAEnum, String
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

    source_type: SourceType = Field(
        sa_type=SAEnum(SourceType),
        sa_column_kwargs={"nullable": False, "index": True},
    )
    reference: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False, "index": True},
    )
    excerpt: str = Field(
        sa_type=Text,
        sa_column_kwargs={"nullable": False},
    )
    source_url: Optional[str] = Field(
        default=None,
        sa_type=String,
        sa_column_kwargs={"nullable": True},
    )

    assertion_links: List["AssertionSource"] = Relationship(back_populates="source")


class LegalAssertion(BaseModel, table=True):
    __tablename__ = "legal_assertions"

    document_version_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"nullable": False, "index": True},
        foreign_key="legal_document_versions.id",
    )
    assertion_text: str = Field(
        sa_type=Text,
        sa_column_kwargs={"nullable": False},
    )
    assertion_type: AssertionType = Field(
        sa_type=SAEnum(AssertionType),
        sa_column_kwargs={"nullable": False, "index": True},
    )
    confidence_level: ConfidenceLevel = Field(
        sa_type=SAEnum(ConfidenceLevel),
        sa_column_kwargs={"nullable": False},
    )
    position: int = Field(default=0)

    source_links: List["AssertionSource"] = Relationship(back_populates="assertion")
    document_version: Optional["LegalDocumentVersion"] = Relationship(back_populates="assertions")


class AssertionSource(BaseModel, table=True):
    __tablename__ = "assertion_sources"

    assertion_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"primary_key": True},
        foreign_key="legal_assertions.id",
    )
    source_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"primary_key": True},
        foreign_key="legal_sources.id",
    )

    # Override id from BaseModel since this table uses composite primary key
    id: Optional[UUID] = Field(default=None, primary_key=False, exclude=True)

    assertion: Optional[LegalAssertion] = Relationship(back_populates="source_links")
    source: Optional[LegalSource] = Relationship(back_populates="assertion_links")
