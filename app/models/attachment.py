"""
Model de Anexos/Autos.

PDFs e outros documentos anexados ao caso.
Suporta extração de texto (OCR) e busca vetorial (RAG).
"""
from datetime import datetime
from uuid import UUID
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case


class DocumentAttachment(BaseModel, table=True):
    """
    Anexo de Documento.
    
    PDFs e outros arquivos anexados ao caso.
    Usado para ingestão de autos e documentos de referência.
    
    Suporta:
    - Extração de texto via OCR
    - Busca semântica via embedding (RAG)
    """
    __tablename__ = "document_attachments"
    
    # FK para caso
    case_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="cases.id"
    )
    
    # Informações do arquivo
    file_name: str = Field(
        sa_column=Column(String, nullable=False)
    )
    file_path: str = Field(
        sa_column=Column(String, nullable=False),
        description="Caminho no Supabase Storage"
    )
    file_size: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
        description="Tamanho em bytes"
    )
    mime_type: str = Field(
        sa_column=Column(String, nullable=False),
        description="Tipo MIME (ex: application/pdf)"
    )
    
    # Texto extraído via OCR
    extracted_text: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Texto extraído do documento via OCR"
    )
    
    # Embedding para busca vetorial (RAG)
    # Nota: O campo vector é gerenciado diretamente via SQL/pgvector
    # embedding: Optional[List[float]] = None  # vector(1536)
    
    # Timestamp de upload (diferente de created_at)
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("NOW()"),
            nullable=False
        )
    )
    
    # Relacionamentos
    case: Optional["Case"] = Relationship(back_populates="attachments")
    
    @property
    def has_extracted_text(self) -> bool:
        """Verifica se o texto foi extraído."""
        return self.extracted_text is not None and len(self.extracted_text) > 0
    
    @property
    def file_size_kb(self) -> Optional[float]:
        """Retorna o tamanho do arquivo em KB."""
        if self.file_size:
            return self.file_size / 1024
        return None
    
    def __repr__(self) -> str:
        return f"<DocumentAttachment {self.file_name} ({self.mime_type})>"
