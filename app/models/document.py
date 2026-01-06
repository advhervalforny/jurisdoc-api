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

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    REVISED = "revised"
    FINALIZED = "finalized"

class VersionCreator(str, Enum):
    HUMAN = "human"
    AGENT = "agent"

class LegalDocument(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_documents"
    
    case_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True))
    piece_type_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_piece_types.id"), nullable=False, index=True))
    status: DocumentStatus = Field(
        default=DocumentStatus.DRAFT,
        sa_column=Column(SAEnum(DocumentStatus), nullable=False, server_default=text("'draft'"))
    )
    current_version_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), nullable=True))
    
    case: Optional["Case"] = Relationship(back_populates="documents")
    piece_type: Optional["LegalPieceType"] = Relationship(back_populates="documents")
    versions: List["LegalDocumentVersion"] = Relationship(back_populates="document")

class LegalDocumentVersion(BaseModel, table=True):
    __tablename__ = "legal_document_versions"
    
    document_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_documents.id"), nullable=False, index=True))
    version_number: int = Field(sa_column=Column(Integer, nullable=False))
    created_by: VersionCreator = Field(sa_column=Column(SAEnum(VersionCreator), nullable=False))
    agent_name: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    
    document: Optional[LegalDocument] = Relationship(back_populates="versions")
    assertions: List["LegalAssertion"] = Relationship(back_populates="document_version")
    renderings: List["DocumentRendering"] = Relationship(back_populates="document_version")
