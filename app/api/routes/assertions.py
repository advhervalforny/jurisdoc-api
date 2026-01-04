"""
Rotas de Afirmações Jurídicas.

⚠️ CORAÇÃO DO SISTEMA

LEIS CONSTITUCIONAIS:
- LEI 2: Nenhuma afirmação sem fonte
- LEI 5: IA não escreve texto final, escreve assertions
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.schemas.assertion import (
    AssertionCreate,
    AssertionResponse,
    AssertionWithSourcesResponse,
    AssertionListResponse,
    AssertionBulkCreate,
    AssertionBulkResponse,
    AssertionSourceLink,
    AssertionValidationResponse
)
from app.services.assertion_service import assertion_service
from app.core.constitution import ConstitutionViolation, JuridicalValidationError


router = APIRouter(tags=["assertions"])


# ==================== ASSERTIONS ====================

@router.post(
    "/document-versions/{version_id}/assertions",
    response_model=AssertionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar assertion",
    description="Cria uma nova afirmação jurídica em uma versão."
)
async def create_assertion(
    version_id: UUID,
    assertion_in: AssertionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> AssertionResponse:
    """
    Cria nova afirmação jurídica.
    
    ⚠️ LEI 2: A assertion criada não é válida até ter fontes vinculadas.
    
    - **text**: Texto da afirmação
    - **type**: Tipo (fato, tese, fundamento, pedido)
    - **confidence_level**: Nível de confiança (alto, medio, baixo)
    """
    try:
        assertion = await assertion_service.create_assertion(
            db=db,
            user_id=user_id,
            version_id=version_id,
            assertion_in=assertion_in
        )
        return AssertionResponse.model_validate(assertion)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/document-versions/{version_id}/assertions/bulk",
    response_model=AssertionBulkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar assertions em lote",
    description="Cria múltiplas afirmações de uma vez. Usado pelo pipeline de IA."
)
async def create_assertions_bulk(
    version_id: UUID,
    bulk_in: AssertionBulkCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> AssertionBulkResponse:
    """
    Cria múltiplas assertions de uma vez.
    
    ⚠️ LEI 5: IA produz assertions, não texto final.
    
    Este endpoint é usado principalmente pelo pipeline cognitivo.
    """
    # Garantir que version_id do path é usado
    bulk_in.document_version_id = version_id
    
    try:
        assertions = await assertion_service.create_assertions_bulk(
            db=db,
            user_id=user_id,
            bulk_in=bulk_in
        )
        return AssertionBulkResponse(
            created_count=len(assertions),
            assertions=[AssertionResponse.model_validate(a) for a in assertions]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/document-versions/{version_id}/assertions",
    response_model=AssertionListResponse,
    summary="Listar assertions da versão",
    description="Lista todas as afirmações de uma versão do documento."
)
async def list_version_assertions(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> AssertionListResponse:
    """
    Lista assertions de uma versão.
    
    Ordenadas por posição.
    Inclui fontes vinculadas.
    """
    assertions = await assertion_service.get_version_assertions(
        db=db,
        version_id=version_id,
        user_id=user_id
    )
    
    return AssertionListResponse(
        items=[AssertionWithSourcesResponse.model_validate(a) for a in assertions],
        total=len(assertions)
    )


@router.get(
    "/assertions/{assertion_id}",
    response_model=AssertionWithSourcesResponse,
    summary="Buscar assertion por ID",
    description="Retorna detalhes de uma afirmação com suas fontes."
)
async def get_assertion(
    assertion_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> AssertionWithSourcesResponse:
    """
    Busca assertion por ID.
    
    Inclui fontes vinculadas.
    """
    assertion = await assertion_service.get_assertion_with_sources(
        db=db,
        assertion_id=assertion_id,
        user_id=user_id
    )
    
    if not assertion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assertion {assertion_id} não encontrada"
        )
    
    return AssertionWithSourcesResponse.model_validate(assertion)


# ==================== VÍNCULOS COM FONTES ====================

@router.post(
    "/assertions/{assertion_id}/sources",
    status_code=status.HTTP_201_CREATED,
    summary="Vincular fonte à assertion",
    description="Vincula uma fonte jurídica a uma afirmação."
)
async def link_source_to_assertion(
    assertion_id: UUID,
    link_in: AssertionSourceLink,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Vincula fonte a uma assertion.
    
    ⚠️ LEI 2: Nenhuma afirmação sem fonte
    Este é o método que torna uma assertion juridicamente válida.
    
    - **source_id**: ID da fonte a vincular
    """
    try:
        link = await assertion_service.link_source(
            db=db,
            user_id=user_id,
            assertion_id=assertion_id,
            source_id=link_in.source_id
        )
        return {
            "message": "Fonte vinculada com sucesso",
            "assertion_id": str(assertion_id),
            "source_id": str(link_in.source_id)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/assertions/{assertion_id}/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desvincular fonte da assertion",
    description="Remove vínculo entre fonte e afirmação."
)
async def unlink_source_from_assertion(
    assertion_id: UUID,
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> None:
    """
    Remove vínculo entre assertion e fonte.
    
    ⚠️ Cuidado: Isso pode tornar a assertion juridicamente inválida.
    """
    unlinked = await assertion_service.unlink_source(
        db=db,
        user_id=user_id,
        assertion_id=assertion_id,
        source_id=source_id
    )
    
    if not unlinked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vínculo não encontrado"
        )


@router.get(
    "/assertions/{assertion_id}/sources",
    summary="Listar fontes da assertion",
    description="Lista todas as fontes vinculadas a uma afirmação."
)
async def list_assertion_sources(
    assertion_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Lista fontes vinculadas a uma assertion.
    
    Ordenadas por hierarquia normativa.
    """
    # Validar que assertion existe
    assertion = await assertion_service.get_assertion_with_sources(
        db, assertion_id, user_id
    )
    if not assertion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assertion {assertion_id} não encontrada"
        )
    
    sources = await assertion_service.get_assertion_sources(db, assertion_id)
    
    return {
        "assertion_id": str(assertion_id),
        "sources": [
            {
                "id": str(s.id),
                "source_type": s.source_type.value,
                "reference": s.reference,
                "excerpt": s.excerpt[:200] + "..." if len(s.excerpt) > 200 else s.excerpt,
                "hierarchy_order": s.hierarchy_order
            }
            for s in sources
        ],
        "total": len(sources)
    }


# ==================== VALIDAÇÃO ====================

@router.get(
    "/assertions/{assertion_id}/validate",
    response_model=AssertionValidationResponse,
    summary="Validar assertion juridicamente",
    description="Verifica se a afirmação é juridicamente válida."
)
async def validate_assertion(
    assertion_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> AssertionValidationResponse:
    """
    Valida se assertion é juridicamente válida.
    
    ⚠️ LEI 2: Nenhuma afirmação sem fonte
    
    Uma assertion é válida se:
    - Tem pelo menos uma fonte vinculada, OU
    - Tem confidence_level == 'baixo'
    """
    is_valid, error = await assertion_service.validate_assertion_juridically(
        db=db,
        assertion_id=assertion_id
    )
    
    return AssertionValidationResponse(
        assertion_id=assertion_id,
        is_valid=is_valid,
        error=error
    )


@router.get(
    "/document-versions/{version_id}/validate",
    summary="Validar versão juridicamente",
    description="Verifica se todas as assertions da versão são válidas."
)
async def validate_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    Valida se todas as assertions de uma versão são juridicamente válidas.
    
    Retorna lista de erros se houver assertions inválidas.
    """
    is_valid, errors = await assertion_service.validate_version_juridically(
        db=db,
        version_id=version_id
    )
    
    return {
        "version_id": str(version_id),
        "is_valid": is_valid,
        "errors": errors,
        "can_render": is_valid  # Só pode renderizar se válido
    }
