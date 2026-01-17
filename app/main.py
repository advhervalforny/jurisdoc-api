"""
Sistema Jurídico Inteligente AI-First

FastAPI Application Entry Point

⚠️ CONSTITUIÇÃO TÉCNICA DO SISTEMA:
- LEI 1: Documento ≠ Texto
- LEI 2: Nenhuma afirmação sem fonte
- LEI 3: Versionamento obrigatório
- LEI 4: Texto final é derivado
- LEI 5: IA não escreve texto final
- LEI 6: Agente = Função jurídica única
- LEI 7: API valida juridicamente
- LEI 8: Frontend não decide nada
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.constitution import ConstitutionViolation, JuridicalValidationError

# Import routers
from app.api.routes.cases import router as cases_router
from app.api.routes.documents import router as documents_router
from app.api.routes.assertions import router as assertions_router
from app.api.routes.sources import router as sources_router
from app.api.routes.rendering import router as rendering_router
from app.api.routes.audit import router as audit_router
from app.api.routes.generation import router as generation_router


# Create FastAPI app
app = FastAPI(
    title="Sistema Jurídico Inteligente",
    description="""
## Sistema Jurídico Inteligente AI-First

Motor cognitivo jurídico para advocacia brasileira.

### Princípios Fundamentais

- **Postura Conservadora**: Na dúvida, não afirma
- **Hierarquia Normativa**: Constituição → Lei → Jurisprudência → Doutrina
- **Human-in-the-Loop**: Nenhuma peça é final sem revisão humana
- **Auditabilidade Total**: Todo texto é rastreável até fontes

### Endpoints Principais

- `/cases` - Gestão de casos/processos
- `/documents` - Gestão de documentos jurídicos
- `/assertions` - Afirmações jurídicas (coração do sistema)
- `/sources` - Fontes jurídicas
- `/rendering` - Renderização de documentos
- `/audit` - Auditoria e rastreabilidade
- `/generate` - Geração com IA (streaming SSE)
- `/agents` - Agentes jurídicos disponíveis
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ✅ CORS CORRIGIDO - Permite Lovable + origens do settings
cors_origins = [
    "https://532e9cb3-d5af-4bd5-807e-4bf4005e726e.lovableproject.com",
    "https://id-preview--532e9cb3-d5af-4bd5-807e-4bf4005e726e.lovable.app",
    "http://localhost:5173",
    "http://localhost:3000",
]
# Adiciona origens do settings se existirem
if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
