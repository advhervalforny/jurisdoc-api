from uuid import UUID
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Column, String, Integer, Enum as SAEnum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.legal_domain import LegalPieceType
    from app.models.assertion import LegalAssertion
    from app.models.rendering import DocumentRendering

# ... (Enums permanecem iguais)

class LegalDocument(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_documents"
    case_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True))
    piece_type_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_piece_types.id"), nullable=False, index=True))
    # ... (status e current_version_id permanecem iguais)
    case: Optional["Case"] = Relationship(back_populates="documents")
    piece_type: Optional["LegalPieceType"] = Relationship(back_populates="documents")
    versions: List["LegalDocumentVersion"] = Relationship(back_populates="document")

class LegalDocumentVersion(BaseModel, table=True):
    __tablename__ = "legal_document_versions"
    document_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_documents.id"), nullable=False, index=True))
    version_number: int = Field(sa_column=Column(Integer, nullable=False))
    # ... (demais campos e relacionamentos)
