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

# ✅ CORS CORRIGIDO - SEM wildcard "*" (incompatível com credentials)
cors_origins = [
    "https://532e9cb3-d5af-4bd5-807e-4bf4005e726e.lovableproject.com",
    "https://id-preview--532e9cb3-d5af-4bd5-807e-4bf4005e726e.lovable.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, ca
