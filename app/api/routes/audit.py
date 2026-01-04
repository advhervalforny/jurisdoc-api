"""
Rotas de Auditoria.

Endpoints para consulta de histórico e rastreabilidade.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db, get_current_user_id, PaginationParams
from app.services.audit_service import audit_service
from app.models.activity_log import EntityTypes


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get(
    "/documents/{document_id}",
    summary="Trilha de auditoria do documento",
    description="Retorna histórico completo de ações em um documento."
)
async def get_document_audit_trail(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Trilha de auditoria completa para um documento.
    
    Inclui:
    - Criação do documento
    - Criação de versões
    - Criação de assertions
    - Vinculação de fontes
    - Renderizações
    
    Usado para defesa jurídica: "Este texto foi gerado com base em..."
    """
    audit_trail = await audit_service.get_document_audit_trail(db, document_id)
    return audit_trail


@router.get(
    "/entity/{entity_type}/{entity_id}",
    summary="Histórico de entidade",
    description="Lista histórico de ações para uma entidade específica."
)
async def get_entity_history(
    entity_type: str,
    entity_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Histórico de ações para uma entidade.
    
    entity_type: case, document, version, assertion, source, rendering
    """
    # Validar entity_type
    valid_types = [
        EntityTypes.CASE,
        EntityTypes.DOCUMENT,
        EntityTypes.VERSION,
        EntityTypes.ASSERTION,
        EntityTypes.SOURCE,
        EntityTypes.RENDERING
    ]
    
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de entidade inválido: {entity_type}. "
                   f"Válidos: {valid_types}"
        )
    
    logs = await audit_service.get_entity_history(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    return {
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "history": [
            {
                "id": str(log.id),
                "action": log.action,
                "user_id": str(log.user_id) if log.user_id else None,
                "timestamp": log.created_at.isoformat(),
                "details": log.details
            }
            for log in logs
        ],
        "total": len(logs)
    }


@router.get(
    "/me",
    summary="Minha atividade",
    description="Lista atividades do usuário autenticado."
)
async def get_my_activity(
    days: int = Query(7, ge=1, le=90, description="Período em dias"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Lista atividades do usuário.
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    logs = await audit_service.get_user_activity(
        db=db,
        user_id=user_id,
        since=since,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    return {
        "user_id": str(user_id),
        "period_days": days,
        "activity": [
            {
                "id": str(log.id),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": str(log.entity_id),
                "timestamp": log.created_at.isoformat(),
                "details": log.details
            }
            for log in logs
        ],
        "total": len(logs)
    }


@router.get(
    "/me/stats",
    summary="Minhas estatísticas",
    description="Estatísticas de uso do usuário."
)
async def get_my_stats(
    days: int = Query(30, ge=1, le=365, description="Período em dias"),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Estatísticas de uso do usuário.
    """
    stats = await audit_service.get_user_stats(
        db=db,
        user_id=user_id,
        days=days
    )
    return stats


@router.get(
    "/recent",
    summary="Atividade recente",
    description="Lista atividades recentes no sistema."
)
async def get_recent_activity(
    hours: int = Query(24, ge=1, le=168, description="Período em horas"),
    entity_type: Optional[str] = Query(None, description="Filtrar por tipo de entidade"),
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    limit: int = Query(50, ge=1, le=200, description="Limite de resultados"),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Lista atividades recentes.
    
    Útil para monitoramento.
    """
    logs = await audit_service.get_recent_activity(
        db=db,
        hours=hours,
        entity_type=entity_type,
        action=action,
        limit=limit
    )
    
    return {
        "period_hours": hours,
        "filters": {
            "entity_type": entity_type,
            "action": action
        },
        "activity": [
            {
                "id": str(log.id),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": str(log.entity_id),
                "user_id": str(log.user_id) if log.user_id else None,
                "timestamp": log.created_at.isoformat(),
                "details": log.details
            }
            for log in logs
        ],
        "total": len(logs)
    }


@router.get(
    "/stats",
    summary="Estatísticas gerais",
    description="Estatísticas gerais de atividade."
)
async def get_activity_stats(
    days: int = Query(7, ge=1, le=90, description="Período em dias"),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Estatísticas gerais de atividade.
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    by_action = await audit_service.count_actions_by_type(db, since)
    by_entity = await audit_service.count_by_entity_type(db, since)
    
    return {
        "period_days": days,
        "by_action": by_action,
        "by_entity_type": by_entity,
        "total": sum(by_action.values())
    }
