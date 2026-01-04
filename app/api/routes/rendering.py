"""
Rotas de Renderização.

⚠️ LEI 4: Texto final é DERIVADO, nunca primário.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db, get_current_user_id
from app.schemas.rendering import (
    RenderRequest,
    RenderingResponse,
    RenderingListResponse
)
from app.models.rendering import RenderFormat
from app.services.rendering_service import rendering_service
from app.core.constitution import ConstitutionViolation


router = APIRouter(tags=["rendering"])


@router.post(
    "/document-versions/{version_id}/render",
    response_model=RenderingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Renderizar versão do documento",
    description="Gera texto a partir das assertions da versão."
)
async def render_version(
    version_id: UUID,
    render_request: RenderRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> RenderingResponse:
    """
    Renderiza versão do documento.
    
    ⚠️ LEI 4: Texto final é derivado das assertions.
    
    ⚠️ Requisito: Todas as assertions devem ter fontes vinculadas (LEI 2).
    
    - **format**: Formato de saída (markdown, html, docx, pdf)
    """
    try:
        rendering = await rendering_service.render_version(
            db=db,
            user_id=user_id,
            version_id=version_id,
            render_format=RenderFormat(render_request.format)
        )
        return RenderingResponse.model_validate(rendering)
    
    except ConstitutionViolation as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "JURIDICAL_VALIDATION_ERROR",
                "message": str(e),
                "hint": "Todas as assertions devem ter fontes vinculadas antes de renderizar"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/document-versions/{version_id}/renderings",
    response_model=RenderingListResponse,
    summary="Listar renderizações da versão",
    description="Lista todas as renderizações de uma versão."
)
async def list_version_renderings(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> RenderingListResponse:
    """
    Lista renderizações de uma versão.
    """
    renderings = await rendering_service.get_version_renderings(db, version_id)
    
    return RenderingListResponse(
        items=[RenderingResponse.model_validate(r) for r in renderings],
        total=len(renderings)
    )


@router.get(
    "/document-versions/{version_id}/render/{format}",
    response_model=RenderingResponse,
    summary="Buscar renderização específica",
    description="Busca renderização de uma versão em formato específico."
)
async def get_rendering(
    version_id: UUID,
    format: str,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> RenderingResponse:
    """
    Busca renderização existente.
    
    Retorna 404 se não existir (precisa chamar POST para criar).
    """
    try:
        render_format = RenderFormat(format)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato inválido: {format}. "
                   f"Válidos: {[f.value for f in RenderFormat]}"
        )
    
    rendering = await rendering_service.get_rendering(
        db=db,
        version_id=version_id,
        render_format=render_format
    )
    
    if not rendering:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Renderização não encontrada para versão {version_id} no formato {format}. "
                   f"Use POST /document-versions/{version_id}/render para criar."
        )
    
    return RenderingResponse.model_validate(rendering)


@router.post(
    "/renderings/{rendering_id}/regenerate",
    response_model=RenderingResponse,
    summary="Regenerar renderização",
    description="Regenera uma renderização existente."
)
async def regenerate_rendering(
    rendering_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> RenderingResponse:
    """
    Regenera renderização existente.
    
    Útil quando assertions foram modificadas.
    """
    try:
        rendering = await rendering_service.regenerate_rendering(
            db=db,
            user_id=user_id,
            rendering_id=rendering_id
        )
        return RenderingResponse.model_validate(rendering)
    
    except ConstitutionViolation as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "JURIDICAL_VALIDATION_ERROR",
                "message": str(e)
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/renderings/{rendering_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar renderização",
    description="Remove uma renderização (pode ser regenerada)."
)
async def delete_rendering(
    rendering_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> None:
    """
    Deleta renderização.
    
    ⚠️ LEI 4: Isso é permitido pois texto é derivado.
    A renderização pode ser regenerada a qualquer momento.
    """
    deleted = await rendering_service.delete_rendering(db, rendering_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Renderização {rendering_id} não encontrada"
        )
