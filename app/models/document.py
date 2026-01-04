from enum import Enum
from uuid import UUID
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, ForeignKey, Text, Integer, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

# 1. Restaurando o status do documento
class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# 2. Restaurando o VersionCreator (Quem criou a versão)
class VersionCreator(str, Enum):
    USER = "user"
    SYSTEM = "system"
    AI = "ai"

class LegalDocument(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_documents"
    
    filename: str = Field(max_length=255)
    file_path: str = Field(max_length=512)
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    status: DocumentStatus = Field(
        default=DocumentStatus.PENDING,
        sa_column=Column(SAEnum(DocumentStatus), nullable=False, server_default="pending")
    )
    
    doc_type: Optional[str] = Field(default=None, max_length=50)
    
    case_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False
        )
    )

class LegalDocumentVersion(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_document_versions"
    
    version_number: int = Field(sa_column=Column(Integer, nullable=False))
    file_path: str = Field(max_length=512)
    change_description: Optional[str] = Field(default=None, max_length=255)
    
    # Usando o VersionCreator restaurado
    created_by: VersionCreator = Field(
        default=VersionCreator.USER,
        sa_column=Column(SAEnum(VersionCreator), nullable=False, server_default="user")
    )
    
    document_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            ForeignKey("legal_documents.id", ondelete="CASCADE"),
            nullable=False
        )
    )
