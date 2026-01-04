"""
Models de Documento Jurídico e Versões.

⚠️ LEIS CONSTITUCIONAIS IMPLEMENTADAS AQUI:
- LEI 1: Documento ≠ Texto (documento é container, não texto)
- LEI 3: Versionamento é obrigatório (versões são imutáveis)
- LEI 4: Texto final é derivado (via renderings)
"""
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, DateTime, Enum as SAEnum, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.legal_domain import LegalPieceType
    from app.models.assertion import LegalAssertion
    from app.models.rendering import DocumentRendering


class DocumentStatus(str, Enum):
    """
    Status do documento jurídico.
    
    Fluxo normal: draft → generated → revised → finalized
    """
    DRAFT = "draft"           # Criado, sem geração
    GENERATED = "generated"   # Gerado pela IA
    REVISED = "revised"       # Revisado pelo humano
    FINALIZED = "finalized"   # Finalizado, pronto para uso


class VersionCreator(str, Enum):
    """
    Quem criou a versão.
    
    Usado para auditoria e rastreabilidade.
    """
    HUMAN = "human"   # Criada manualmente pelo usuário
    AGENT = "agent"   # Criada por agente de IA


class LegalDocument(BaseModel, TimestampMixin, table=True):
    """
    Documento Jurídico (Container).
    
    ⚠️ LEI 1: Documento ≠ Texto
    Este model é apenas um CONTAINER lógico.
    NÃO contém texto diretamente.
    O texto está nas assertions das versões.
    
    Um documento pertence a um caso e tem um tipo de peça.
    """
    __tablename__ = "legal_documents"
    
    # FK para caso
    case_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="cases.id"
    )
    
    # FK para tipo de peça
    piece_type_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="legal_piece_types.id"
    )
    
    # Status do documento
    status: DocumentStatus = Field(
        default=DocumentStatus.DRAFT,
        sa_column=Column(
            SAEnum(DocumentStatus, name="document_status", create_type=False),
            nullable=False,
            server_default=text("'draft'")
        )
    )
    
    # FK para versão atual (preenchida após primeira versão)
    current_version_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=True
        )
    )
    
    # Relacionamentos
    case: Optional["Case"] = Relationship(back_populates="documents")
    piece_type: Optional["LegalPieceType"] = Relationship(back_populates="documents")
    versions: List["LegalDocumentVersion"] = Relationship(back_populates="document")
    
    @property
    def versions_count(self) -> int:
        """Retorna a quantidade de versões do documento."""
        return len(self.versions) if self.versions else 0
    
    @property
    def latest_version_number(self) -> int:
        """Retorna o número da última versão."""
        if not self.versions:
            return 0
        return max(v.version_number for v in self.versions)
    
    def __repr__(self) -> str:
        return f"<LegalDocument {self.id} (status: {self.status}, versions: {self.versions_count})>"


class LegalDocumentVersion(BaseModel, table=True):
    """
    Versão de Documento Jurídico.
    
    ⚠️ LEI 3: Versionamento é Obrigatório
    - Toda geração cria uma nova versão
    - É PROIBIDO sobrescrever versões existentes
    - Versões são IMUTÁVEIS após criação
    
    Cada versão contém as assertions que formam o conteúdo.
    """
    __tablename__ = "legal_document_versions"
    
    # FK para documento
    document_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="legal_documents.id"
    )
    
    # Número da versão (auto-incrementado por documento)
    version_number: int = Field(
        sa_column=Column(Integer, nullable=False)
    )
    
    # Quem criou esta versão
    created_by: VersionCreator = Field(
        sa_column=Column(
            SAEnum(VersionCreator, name="version_creator", create_type=False),
            nullable=False
        )
    )
    
    # Nome do agente (se created_by == 'agent')
    agent_name: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True),
        description="Nome do agente de IA que criou esta versão"
    )
    
    # Relacionamentos
    document: Optional[LegalDocument] = Relationship(back_populates="versions")
    assertions: List["LegalAssertion"] = Relationship(back_populates="document_version")
    renderings: List["DocumentRendering"] = Relationship(back_populates="document_version")
    
    @property
    def assertions_count(self) -> int:
        """Retorna a quantidade de assertions na versão."""
        return len(self.assertions) if self.assertions else 0
    
    @property
    def is_valid(self) -> bool:
        """
        Verifica se a versão é juridicamente válida.
        
        ⚠️ LEI 2: Toda assertion deve ter pelo menos uma fonte.
        Uma versão só é válida se TODAS as suas assertions tiverem fontes.
        """
        if not self.assertions:
            return False
        return all(a.has_sources for a in self.assertions)
    
    def __repr__(self) -> str:
        return f"<LegalDocumentVersion v{self.version_number} (by: {self.created_by}, assertions: {self.assertions_count})>"
    
    class Config:
        """
        Configuração do model.
        """
        # ⚠️ LEI 3: Versões são imutáveis
        # Não permitir update após criação (enforced na API)
        pass
