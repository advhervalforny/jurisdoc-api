"""
Rotas da API.

Endpoints organizados por domínio:
- cases: Casos/processos
- documents: Documentos jurídicos e versões
- assertions: Afirmações jurídicas
- sources: Fontes jurídicas
- rendering: Renderização de documentos
- audit: Auditoria e rastreabilidade
- generation: Geração com IA (pipeline cognitivo)
"""

from app.api.routes.cases import router as cases_router
from app.api.routes.documents import router as documents_router
from app.api.routes.assertions import router as assertions_router
from app.api.routes.sources import router as sources_router
from app.api.routes.rendering import router as rendering_router
from app.api.routes.audit import router as audit_router
from app.api.routes.generation import router as generation_router

__all__ = [
    "cases_router",
    "documents_router",
    "assertions_router",
    "sources_router",
    "rendering_router",
    "audit_router",
    "generation_router",
]
