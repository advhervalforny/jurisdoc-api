"""
Services do Sistema Jurídico Inteligente.

Camada de lógica de negócio que implementa as regras da Constituição Técnica.

⚠️ LEIS CONSTITUCIONAIS IMPLEMENTADAS:
- LEI 1: Documento ≠ Texto (DocumentService)
- LEI 2: Nenhuma afirmação sem fonte (AssertionService)
- LEI 3: Versionamento obrigatório (DocumentService)
- LEI 4: Texto derivado (RenderingService)
- LEI 5: IA não escreve texto final (AssertionService)

Todos os services usam o AuditService para rastreabilidade.
"""

from app.services.base import BaseService, log_activity
from app.services.case_service import CaseService, case_service
from app.services.document_service import DocumentService, document_service
from app.services.assertion_service import AssertionService, assertion_service
from app.services.source_service import SourceService, source_service
from app.services.rendering_service import RenderingService, rendering_service
from app.services.audit_service import AuditService, audit_service

__all__ = [
    # Base
    "BaseService",
    "log_activity",
    
    # Services
    "CaseService",
    "DocumentService",
    "AssertionService",
    "SourceService",
    "RenderingService",
    "AuditService",
    
    # Singletons
    "case_service",
    "document_service",
    "assertion_service",
    "source_service",
    "rendering_service",
    "audit_service",
]
