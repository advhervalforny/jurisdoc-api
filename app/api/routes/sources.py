"""
Rotas de Fontes Jurídicas.

Gerencia fontes (leis, jurisprudência, doutrina) usadas nas assertions.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db, get_current_user_id, get_optional_user_id, PaginationParams
from app.schemas.source import (
    SourceCreate,
    SourceResponse,
    SourceListResponse,
    SourceTypeInfo
)
from app.models.assertion import SourceType
from app.services.source_service import source_service


router = APIRouter(prefix="/sources", tags=["sources"])


@router.post(
    "",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar fonte jurídica",
    description="Cria uma nova fonte jurídica no sistema."
)
async def create_source(
    source_in: SourceCreate,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[UUID] = Depends(get_optional_user_id)
) -> SourceResponse:
    """
    Cria nova fonte jurídica.
    
    Se a fonte já existir (mesma type, reference, excerpt), retorna a existente.
    
    - **source_type**: Tipo (constituicao, lei, jurisprudencia, doutrina, argumentacao)
    - **reference**: Referência (ex: "CPC, art. 319")
    - **excerpt**: Trecho relevante
    - **source_url**: URL da fonte (opcional)
    """
    source = await source_service.create_source(
        db=db,
        source_in=source_in,
        user_id=user_id
    )
    return SourceResponse.model_validate(source)


@router.post(
    "/bulk",
    response_model=SourceListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar fontes em lote",
    description="Cria múltiplas fontes de uma vez."
)
async def create_sources_bulk(
    sources_in: List[SourceCreate],
    db: AsyncSession = Depends(get_db),
    user_id: Optional[UUID] = Depends(get_optional_user_id)
) -> SourceListResponse:
    """
    Cria múltiplas fontes de uma vez.
    
    Ignora duplicatas silenciosamente.
    """
    sources = await source_service.create_sources_bulk(
        db=db,
        sources_in=sources_in,
        user_id=user_id
    )
    
    return SourceListResponse(
        items=[SourceResponse.model_validate(s) for s in sources],
        total=len(sources)
    )


@router.get(
    "",
    response_model=SourceListResponse,
    summary="Buscar fontes",
    description="Busca fontes com filtros opcionais."
)
async def search_sources(
    query: Optional[str] = Query(
        None,
        description="Texto para buscar em reference e excerpt"
    ),
    source_type: Optional[str] = Query(
        None,
        description="Filtrar por tipo (constituicao, lei, jurisprudencia, doutrina, argumentacao)"
    ),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
) -> SourceListResponse:
    """
    Busca fontes com filtros.
    
    Resultados ordenados por hierarquia normativa.
    """
    # Validar source_type se fornecido
    st = None
    if source_type:
        try:
            st = SourceType(source_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de fonte inválido: {source_type}. "
                       f"Válidos: {[t.value for t in SourceType]}"
            )
    
    sources = await source_service.search_sources(
        db=db,
        query=query,
        source_type=st,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    return SourceListResponse(
        items=[SourceResponse.model_validate(s) for s in sources],
        total=len(sources)
    )


@router.get(
    "/types",
    response_model=List[SourceTypeInfo],
    summary="Listar tipos de fonte",
    description="Retorna informações sobre os tipos de fonte disponíveis."
)
async def list_source_types() -> List[SourceTypeInfo]:
    """
    Lista tipos de fonte disponíveis.
    
    Inclui hierarquia normativa.
    """
    types_info = source_service.get_source_types_info()
    return [SourceTypeInfo(**info) for info in types_info]


@router.get(
    "/stats",
    summary="Estatísticas de fontes",
    description="Retorna contagem de fontes por tipo."
)
async def get_sources_stats(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Estatísticas de fontes no sistema.
    """
    counts = await source_service.count_by_type(db)
    total = sum(counts.values())
    
    return {
        "by_type": counts,
        "total": total
    }


@router.get(
    "/{source_id}",
    response_model=SourceResponse,
    summary="Buscar fonte por ID",
    description="Retorna detalhes de uma fonte específica."
)
async def get_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> SourceResponse:
    """
    Busca fonte por ID.
    """
    source = await source_service.get_source_by_id(db, source_id)
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fonte {source_id} não encontrada"
        )
    
    return SourceResponse.model_validate(source)


@router.get(
    "/by-reference/{source_type}/{reference:path}",
    response_model=SourceResponse,
    summary="Buscar fonte por referência",
    description="Busca fonte por tipo e referência."
)
async def get_source_by_reference(
    source_type: str,
    reference: str,
    db: AsyncSession = Depends(get_db)
) -> SourceResponse:
    """
    Busca fonte por tipo e referência.
    
    Útil para verificar se uma fonte já existe.
    """
    try:
        st = SourceType(source_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de fonte inválido: {source_type}"
        )
    
    source = await source_service.get_source_by_reference(db, st, reference)
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fonte não encontrada: {source_type}/{reference}"
        )
    
    return SourceResponse.model_validate(source)
