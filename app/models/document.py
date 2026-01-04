from uuid import UUID
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

class LegalDocument(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_documents"
    
    filename: str = Field(max_length=255)
    file_path: str = Field(max_length=512)
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    doc_type: Optional[str] = Field(default=None, max_length=50)
    
    # CORREÇÃO: Movido foreign_key para dentro do sa_column
    case_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    
    # Relacionamentos
    # case: "Case" = Relationship(back_populates="documents")
