"""
Model de Logs de Auditoria.

Permite responder: Quem fez o quê, quando, e com base em quê?

Essencial para:
- Rastreabilidade
- Compliance
- Debug
- Defesa jurídica do sistema
"""
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INET

from app.models.base import BaseModel


class ActivityLog(BaseModel, table=True):
    """
    Log de Atividade.
    
    Registra todas as ações relevantes no sistema.
    Permite auditoria completa e rastreabilidade.
    
    Responde:
    - Quem? (user_id)
    - O quê? (action)
    - Em quê? (entity_type, entity_id)
    - Quando? (created_at)
    - Como? (details)
    """
    __tablename__ = "activity_logs"
    
    # Quem fez a ação (pode ser null para ações do sistema)
    user_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=True,
            index=True
        )
    )
    
    # Ação realizada
    action: str = Field(
        sa_column=Column(String, nullable=False, index=True),
        description="Ex: 'create', 'generate', 'render', 'link_source'"
    )
    
    # Tipo da entidade afetada
    entity_type: str = Field(
        sa_column=Column(String, nullable=False, index=True),
        description="Ex: 'case', 'document', 'version', 'assertion'"
    )
    
    # ID da entidade afetada
    entity_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        )
    )
    
    # Detalhes adicionais (JSON)
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Detalhes adicionais da ação em JSON"
    )
    
    # Informações de contexto
    ip_address: Optional[str] = Field(
        default=None,
        sa_column=Column(INET, nullable=True)
    )
    user_agent: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    
    def __repr__(self) -> str:
        return f"<ActivityLog {self.action} on {self.entity_type}:{self.entity_id} by {self.user_id}>"


# Constantes de ações comuns
class LogActions:
    """Ações padrão para logging."""
    
    # Casos
    CASE_CREATE = "case.create"
    CASE_UPDATE = "case.update"
    
    # Documentos
    DOCUMENT_CREATE = "document.create"
    DOCUMENT_STATUS_CHANGE = "document.status_change"
    
    # Versões
    VERSION_CREATE = "version.create"
    VERSION_GENERATE = "version.generate"
    
    # Assertions
    ASSERTION_CREATE = "assertion.create"
    ASSERTION_BULK_CREATE = "assertion.bulk_create"
    
    # Sources
    SOURCE_CREATE = "source.create"
    SOURCE_LINK = "source.link"
    SOURCE_UNLINK = "source.unlink"
    
    # Rendering
    RENDER_DOCUMENT = "render.document"
    RENDER_EXPORT = "render.export"
    
    # Attachments
    ATTACHMENT_UPLOAD = "attachment.upload"
    ATTACHMENT_EXTRACT = "attachment.extract_text"
    
    # Auth
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"


class EntityTypes:
    """Tipos de entidades para logging."""
    
    CASE = "case"
    DOCUMENT = "document"
    VERSION = "version"
    ASSERTION = "assertion"
    SOURCE = "source"
    RENDERING = "rendering"
    ATTACHMENT = "attachment"
    USER = "user"
