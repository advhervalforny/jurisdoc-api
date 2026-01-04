"""
Rotas de Geração com IA.

⚠️ LEIS APLICÁVEIS:
- LEI 5: IA produz assertions, não texto final
- LEI 6: Agente = Função jurídica única

Endpoints:
- POST /generate: Inicia geração com streaming SSE
- GET /agents: Lista agentes disponíveis
"""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.services.document_service import DocumentService
from app.services.assertion_service import AssertionService
from app.services.source_service import SourceService
from app.services.audit_service import AuditService
from app.cognitive.pipeline import CognitivePipeline, GenerationInput
from app.cognitive.agents import list_agents


router = APIRouter(prefix="/api/v1", tags=["Generation"])


# ==================== SCHEMAS ====================

class GenerationRequest(BaseModel):
    """Request para geração."""
    document_id: UUID
    agent_type: str = Field(..., description="Tipo do agente (ex: peticao-inicial-civil)")
    fatos_principais: List[str] = Field(..., min_length=1, description="Lista de fatos")
    pedidos: List[str] = Field(..., min_length=1, description="Lista de pedidos")
    valor_causa: Optional[float] = Field(None, ge=0, description="Valor da causa em reais")
    partes: Optional[dict] = Field(None, description="Dados das partes (autor, reu)")
    contexto_adicional: Optional[str] = Field(None, description="Contexto adicional")


class AgentInfo(BaseModel):
    """Informações do agente."""
    id: str
    name: str
    legal_basis: str
    legal_area: str


# ==================== ROUTES ====================

@router.post(
    "/documents/{document_id}/generate",
    summary="Gera peça jurídica com IA",
    description="""
    Inicia o pipeline de geração cognitiva.
    
    ⚠️ LEI 5: A IA produz assertions estruturadas, NÃO texto final.
    
    Retorna streaming SSE com eventos do pipeline:
    - started: Pipeline iniciado
    - version_created: Nova versão criada
    - normalization_complete: Inputs normalizados
    - research_started: Pesquisa de fontes iniciada
    - source_found: Fonte encontrada
    - research_complete: Pesquisa concluída
    - generation_started: Geração iniciada
    - assertion_generated: Assertion gerada
    - assertion_validated: Assertion validada
    - validation_complete: Validação concluída
    - persistence_complete: Dados salvos
    - completed: Pipeline concluído
    - error: Erro no pipeline
    """
)
async def generate_document(
    document_id: UUID,
    request: GenerationRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    Gera peça jurídica via streaming SSE.
    """
    # Validar que document_id coincide
    if request.document_id != document_id:
        raise HTTPException(
            status_code=400,
            detail="document_id no path deve coincidir com body"
        )
    
    # Verificar se documento existe e pertence ao usuário
    document_service = DocumentService()
    document = await document_service.get_by_id(db, document_id, user_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    # Criar input estruturado
    generation_input = GenerationInput(
        document_id=document_id,
        agent_type=request.agent_type,
        fatos_principais=request.fatos_principais,
        pedidos=request.pedidos,
        valor_causa=request.valor_causa,
        partes=request.partes,
        contexto_adicional=request.contexto_adicional
    )
    
    # Criar pipeline
    pipeline = CognitivePipeline(
        db=db,
        document_service=DocumentService(),
        assertion_service=AssertionService(),
        source_service=SourceService(),
        audit_service=AuditService()
    )
    
    # Função geradora para streaming
    async def event_generator():
        try:
            async for event in pipeline.run(generation_input, user_id):
                yield event.to_sse()
        except Exception as e:
            import json
            error_event = f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            yield error_event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Nginx
        }
    )


@router.get(
    "/agents",
    response_model=List[AgentInfo],
    summary="Lista agentes disponíveis",
    description="Retorna lista de agentes jurídicos especializados."
)
async def get_agents():
    """Lista agentes disponíveis."""
    agents = list_agents()
    return [AgentInfo(**agent) for agent in agents]


@router.get(
    "/agents/{agent_type}",
    response_model=AgentInfo,
    summary="Busca agente por tipo",
    description="Retorna informações de um agente específico."
)
async def get_agent_info(agent_type: str):
    """Busca informações de um agente."""
    agents = list_agents()
    
    for agent in agents:
        if agent["id"] == agent_type:
            return AgentInfo(**agent)
    
    raise HTTPException(status_code=404, detail="Agente não encontrado")
