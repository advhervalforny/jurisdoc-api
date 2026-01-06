"""
Model de renderização de documentos.
"""
from uuid import UUID
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
# Importamos ForeignKey do sqlalchemy
from sqlalchemy import Column, Text, ForeignKey 
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import LegalDocumentVersion

class DocumentRendering(BaseModel, table=True):
    __tablename__ = "document_renderings"
    
    # CORREÇÃO: Removido 'foreign_key' do Field e adicionado 'ForeignKey' no Column
    document_version_id: UUID = Field(
        sa_column=Column(
            # O tipo é inferido, mas a FK deve estar aqui dentro
            ForeignKey("legal_document_versions.id"), 
            nullable=False,
            index=True
        )
    )
    
    # Se houver campos de texto longo (como o conteúdo renderizado), aplique o mesmo:
    rendered_content: str = Field(sa_column=Column(Text, nullable=False))
    
    # Relacionamentos
    document_version: Optional["LegalDocumentVersion"] = Relationship(back_populates="renderings")
