from enum import Enum
from uuid import UUID
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, ForeignKey, Text, Integer, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

# 1. Restaurando o DocumentStatus que estava faltando
class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class LegalDocument(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_documents"
    
    filename: str = Field(max_length=255)
    file_path: str = Field(max_length=512)
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Usando o Enum restaurado
    status: DocumentStatus = Field(
        default=DocumentStatus.PENDING,
        sa_column=Column(SAEnum(DocumentStatus), nullable=False, server_default="pending")
    )
    
    doc_type: Optional[str] = Field(default=None, max_length=50)
    
    # Conexão corrigida com o processo
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
    
    # Conexão corrigida com o documento principal
    document_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            ForeignKey("legal_documents.id", ondelete="CASCADE"),
            nullable=False
        )
    )
