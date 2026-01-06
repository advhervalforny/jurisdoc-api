from uuid import UUID
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Column, Text, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import LegalDocumentVersion

# ... (Enums e SOURCE_HIERARCHY)

class LegalAssertion(BaseModel, table=True):
    __tablename__ = "legal_assertions"
    document_version_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("legal_document_versions.id"),
            nullable=False,
            index=True
        )
    )
    assertion_text: str = Field(sa_column=Column(Text, nullable=False))
    # ... (demais campos e relacionamentos)

class AssertionSource(BaseModel, table=True):
    __tablename__ = "assertion_sources"
    assertion_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_assertions.id"), primary_key=True))
    source_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_sources.id"), primary_key=True))
    assertion: Optional[LegalAssertion] = Relationship(back_populates="source_links")
    source: Optional["LegalSource"] = Relationship(back_populates="assertion_links")
