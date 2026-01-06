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

from app.models.base import BaseModel, TimestampMixin
from app.models.user_profile import UserProfile
from app.models.legal_domain import LegalArea, LegalPieceType
from app.models.case import Case
from app.models.document import LegalDocument, LegalDocumentVersion, DocumentStatus, VersionCreator
from app.models.assertion import LegalAssertion, LegalSource, AssertionSource, AssertionType, ConfidenceLevel, SourceType, SOURCE_HIERARCHY
from app.models.rendering import DocumentRendering, RenderFormat
from app.models.attachment import DocumentAttachment
from app.models.activity_log import ActivityLog, LogActions, EntityTypes

__all__ = [
    "BaseModel", "TimestampMixin", "UserProfile", "LegalArea", "LegalPieceType",
    "Case", "LegalDocument", "LegalDocumentVersion", "DocumentStatus", "VersionCreator",
    "LegalAssertion", "LegalSource", "AssertionSource", "AssertionType", "ConfidenceLevel",
    "SourceType", "SOURCE_HIERARCHY", "DocumentRendering", "RenderFormat",
    "DocumentAttachment", "ActivityLog", "LogActions", "EntityTypes"
]
