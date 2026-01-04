"""
Models do Sistema Jurídico Inteligente.

⚠️ LEIS CONSTITUCIONAIS IMPLEMENTADAS NOS MODELS:
- LEI 1: Documento ≠ Texto (LegalDocument é container)
- LEI 2: Nenhuma afirmação sem fonte (AssertionSource)
- LEI 3: Versionamento obrigatório (LegalDocumentVersion)
- LEI 4: Texto final é derivado (DocumentRendering)
- LEI 5: IA não escreve texto final (assertions only)

Hierarquia de relacionamentos:
    UserProfile
        └── Case
            ├── LegalDocument
            │   └── LegalDocumentVersion
            │       ├── LegalAssertion
            │       │   └── AssertionSource ──► LegalSource
            │       └── DocumentRendering
            └── DocumentAttachment
"""

# Base
from app.models.base import BaseModel, TimestampMixin

# User
from app.models.user_profile import UserProfile

# Domínio Jurídico
from app.models.legal_domain import (
    LegalArea,
    LegalPieceType,
)

# Case
from app.models.case import Case

# Document & Version
from app.models.document import (
    LegalDocument,
    LegalDocumentVersion,
    DocumentStatus,
    VersionCreator,
)

# Assertions & Sources (CORAÇÃO DO SISTEMA)
from app.models.assertion import (
    LegalAssertion,
    LegalSource,
    AssertionSource,
    AssertionType,
    ConfidenceLevel,
    SourceType,
    SOURCE_HIERARCHY,
)

# Rendering
from app.models.rendering import (
    DocumentRendering,
    RenderFormat,
)

# Attachments
from app.models.attachment import DocumentAttachment

# Activity Logs
from app.models.activity_log import (
    ActivityLog,
    LogActions,
    EntityTypes,
)

# Export all models for easy importing
__all__ = [
    # Base
    "BaseModel",
    "TimestampMixin",
    
    # User
    "UserProfile",
    
    # Legal Domain
    "LegalArea",
    "LegalPieceType",
    
    # Case
    "Case",
    
    # Document
    "LegalDocument",
    "LegalDocumentVersion",
    "DocumentStatus",
    "VersionCreator",
    
    # Assertions & Sources
    "LegalAssertion",
    "LegalSource",
    "AssertionSource",
    "AssertionType",
    "ConfidenceLevel",
    "SourceType",
    "SOURCE_HIERARCHY",
    
    # Rendering
    "DocumentRendering",
    "RenderFormat",
    
    # Attachments
    "DocumentAttachment",
    
    # Logs
    "ActivityLog",
    "LogActions",
    "EntityTypes",
]
