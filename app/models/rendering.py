"""
Model de Renderização de Documento.

⚠️ LEI 4: Texto final é DERIVADO, nunca primário.

O texto renderizado é sempre reconstruível a partir das assertions.
Este model armazena apenas uma "cache" do texto gerado para performance.
"""
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import LegalDocumentVersion


class RenderFormat(str, Enum):
    """
    Formato de renderização do documento.
    """
    MARKDOWN = "markdown"  # Markdown (padrão)
    HTML = "html"          # HTML
    DOCX = "docx"          # Word
    PDF = "pdf"            # PDF


class DocumentRendering(BaseModel, table=True):
    """
    Renderização de Documento.
    
    ⚠️ LEI 4: Texto final é DERIVADO
    
    Este model armazena o texto renderizado a partir das assertions.
    O texto NÃO é editado diretamente - é sempre regenerado.
    
    Funciona como uma "cache" do texto final:
    - Pode ser deletado e regenerado a qualquer momento
    - A fonte da verdade são as assertions
    """
    __tablename__ = "document_renderings"
    
    # FK para versão do documento
    document_version_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="legal_document_versions.id"
    )
    
    # Texto renderizado
    rendered_text: str = Field(
        sa_column=Column(Text, nullable=False)
    )
    
    # Formato da renderização
    render_format: RenderFormat = Field(
        default=RenderFormat.MARKDOWN,
        sa_column=Column(
            SAEnum(RenderFormat, name="render_format", create_type=False),
            nullable=False,
            server_default=text("'markdown'")
        )
    )
    
    # Relacionamentos
    document_version: Optional["LegalDocumentVersion"] = Relationship(back_populates="renderings")
    
    def __repr__(self) -> str:
        preview = self.rendered_text[:50] + "..." if len(self.rendered_text) > 50 else self.rendered_text
        return f"<DocumentRendering {self.render_format.value}: '{preview}'>"
