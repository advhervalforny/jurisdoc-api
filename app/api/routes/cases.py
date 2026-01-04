"""
Rotas de Casos/Processos.

Endpoints para gerenciamento de casos jurídicos.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db, get_current_user_id, PaginationParams
from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseListResponse,
    CaseWithDocumentsResponse
)
from app.services.case_service import case_service


router = APIRouter(prefix="/cases", tags=["cases"])


@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo caso",
    description="Cria um novo caso/processo jurídico para o usuário."
)
async def create_case(
    case_in: CaseCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> CaseResponse:
    """
    Cria novo caso jurídico.
    
    - **legal_area_slug**: Área do direito (civil, penal)
    - **title**: Título do caso
    - **description**: Descrição opcional
    - **process_number**: Número do processo (se já existir)
    """
    try:
        case = await case_service.create_case(db, user_id, case_in)
        return CaseResponse.model_validate(case)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=CaseListResponse,
    summary="Listar casos do usuário",
    description="Lista todos os casos do usuário autenticado."
)
async def list_cases(
    legal_area_slug: Optional[str] = Query(
        None,
        description="Filtrar por área jurídica (civil, penal)"
    ),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> CaseListResponse:
    """
    Lista casos do usuário com paginação.
    
    Opcionalmente filtra por área jurídica.
    """
    cases = await case_service.get_user_cases(
        db=db,
        user_id=user_id,
        skip=pagination.skip,
        limit=pagination.limit,
        legal_area_slug=legal_area_slug
    )
    
    total = await case_service.count_user_cases(db, user_id)
    
    return CaseListResponse(
        items=[CaseResponse.model_validate(c) for c in cases],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )


@router.get(
    "/{case_id}",
    response_model=CaseWithDocumentsResponse,
    summary="Buscar caso por ID",
    description="Retorna detalhes de um caso específico com seus documentos."
)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> CaseWithDocumentsResponse:
    """
    Busca caso por ID.
    
    Inclui lista de documentos do caso.
    """
    case = await case_service.get_by_id_with_documents(db, case_id, user_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caso {case_id} não encontrado"
        )
    
    return CaseWithDocumentsResponse.model_validate(case)


@router.patch(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Atualizar caso",
    description="Atualiza dados de um caso existente."
)
async def update_case(
    case_id: UUID,
    case_in: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> CaseResponse:
    """
    Atualiza caso existente.
    
    Apenas título, descrição e número do processo podem ser alterados.
    A área jurídica NÃO pode ser modificada.
    """
    case = await case_service.update_case(db, case_id, user_id, case_in)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caso {case_id} não encontrado"
        )
    
    return CaseResponse.model_validate(case)


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar caso",
    description="Remove um caso e todos os seus documentos."
)
async def delete_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> None:
    """
    Deleta caso.
    
    ⚠️ ATENÇÃO: Isso também remove todos os documentos do caso.
    """
    deleted = await case_service.delete_case(db, case_id, user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caso {case_id} não encontrado"
        )


@router.get(
    "/{case_id}/documents-count",
    summary="Contar documentos do caso",
    description="Retorna a quantidade de documentos em um caso."
)
async def get_case_documents_count(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Conta documentos de um caso.
    """
    # Verificar se caso existe e pertence ao usuário
    case = await case_service.get_by_id_with_documents(db, case_id, user_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caso {case_id} não encontrado"
        )
    
    count = await case_service.get_case_documents_count(db, case_id)
    
    return {"case_id": str(case_id), "documents_count": count}
