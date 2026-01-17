# COPIE E COLE ESTE ARQUIVO INTEIRO no lugar do seu main.py:
"""
Sistema Jurídico Inteligente AI-First
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.constitution import ConstitutionViolation, JuridicalValidationError

from app.api.routes.cases import router as cases_router
from app.api.routes.documents import router as documents_router
from app.api.routes.assertions import router as assertions_router
from app.api.routes.sources import router as sources_router
from app.api.routes.rendering import router as rendering_router
from app.api.routes.audit import router as audit_router
from app.api.routes.generation import router as generation_router

app = FastAPI(
    title="Sistema Jurídico Inteligente",
    description="Motor cognitivo jurídico para advocacia brasileira.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ CORS CORRIGIDO - Lista fixa (sem depender de settings)
cors_origins = [
    "https://532e9cb3-d5af-4bd5-807e-4bf4005e726e.lovableproject.com",
    "https://id-preview--532e9cb3-d5af-4bd5-807e-4bf4005e726e.lovable.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "*",  # Permite qualquer origem (para testes)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(ConstitutionViolation)
async def constitution_violation_handler(request: Request, exc: ConstitutionViolation):
    return JSONResponse(status_code=403, content={"error": "CONSTITUTION_VIOLATION", "message": str(exc)})

@app.exception_handler(JuridicalValidationError)
async def juridical_validation_handler(request: Request, exc: JuridicalValidationError):
    return JSONResponse(status_code=422, content={"error": "JURIDICAL_VALIDATION_ERROR", "message": str(exc)})

app.include_router(cases_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(assertions_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")
app.include_router(rendering_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(generation_router)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "Sistema Jurídico Inteligente", "version": "1.0.0"}

@app.get("/", tags=["root"])
async def root():
    return {"message": "Sistema Jurídico Inteligente AI-First", "docs": "/docs", "health": "/health"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

