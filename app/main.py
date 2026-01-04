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


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Adiciona header com tempo de processamento."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(ConstitutionViolation)
async def constitution_violation_handler(request: Request, exc: ConstitutionViolation):
    """
    Handler para violações da Constituição Técnica.
    
    Retorna 403 Forbidden para violações constitucionais.
    """
    return JSONResponse(
        status_code=403,
        content={
            "error": "CONSTITUTION_VIOLATION",
            "message": str(exc),
            "hint": "Esta operação viola as leis fundamentais do sistema"
        }
    )


@app.exception_handler(JuridicalValidationError)
async def juridical_validation_handler(request: Request, exc: JuridicalValidationError):
    """
    Handler para erros de validação jurídica.
    
    Retorna 422 Unprocessable Entity para erros de validação.
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": "JURIDICAL_VALIDATION_ERROR",
            "message": str(exc),
            "hint": "O conteúdo não passou na validação jurídica"
        }
    )


# Include routers
app.include_router(cases_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(assertions_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")
app.include_router(rendering_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(generation_router)  # Já tem prefix /api/v1


# Health check
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Retorna status do sistema.
    """
    return {
        "status": "healthy",
        "service": "Sistema Jurídico Inteligente",
        "version": "1.0.0",
        "constitution": {
            "lei_1": "Documento ≠ Texto",
            "lei_2": "Nenhuma afirmação sem fonte",
            "lei_3": "Versionamento obrigatório",
            "lei_4": "Texto final é derivado",
            "lei_5": "IA não escreve texto final",
            "lei_6": "Agente = Função jurídica única",
            "lei_7": "API valida juridicamente",
            "lei_8": "Frontend não decide nada"
        }
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint.
    
    Retorna informações básicas da API.
    """
    return {
        "message": "Sistema Jurídico Inteligente AI-First",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
