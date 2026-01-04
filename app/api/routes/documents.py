"""
Rotas de Documentos Jurídicos.

⚠️ LEIS CONSTITUCIONAIS:
- LEI 1: Documento ≠ Texto (documento é container)
- LEI 3: Versionamento é obrigatório
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db, get_current_user_id, PaginationParams
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentListResponse,
    DocumentWithVersionsResponse,
    DocumentVersionCreate,
    DocumentVersionResponse,
    DocumentVersionListResponse,
    DocumentStatusUpdate
)
from app.models.document import DocumentStatus
from app.services.document_service import document_service
from app.core.constitution import ConstitutionViolation


router = APIRouter(tags=["documents"])


# ==================== DOCUMENTOS ====================

@router.post(
    "/cases/{case_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo documento",
    description="Cria um novo documento jurídico dentro de um caso."
)
async def create_document(
    case_id: UUID,
    document_in: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> DocumentResponse:
    """
    Cria novo documento jurídico.
    
    ⚠️ LEI 1: Documento ≠ Texto
    O documento é criado VAZIO, sem texto.
    Texto será adicionado via assertions em versões.
    
    - **piece_type_slug**: Tipo de peça (peticao-inicial, contestacao, etc)
    """
    try:
        document = await document_service.create_document(
            db=db,
            user_id=user_id,
            case_id=case_id,
            document_in=document_in
        )
        return DocumentResponse.model_validate(document)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/cases/{case_id}/documents",
    response_model=DocumentListResponse,
    summary="Listar documentos do caso",
    description="Lista todos os documentos de um caso."
)
async def list_case_documents(
    case_id: UUID,
    status_filter: Optional[DocumentStatus] = Query(
        None,
        alias="status",
        description="Filtrar por status (draft, generated, revised, finalized)"
    ),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> DocumentListResponse:
    """
    Lista documentos de um caso.
    
    Opcionalmente filtra por status.
    """
    documents = await document_service.get_case_documents(
        db=db,
        case_id=case_id,
        user_id=user_id,
        status=status_filter
    )
    
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=len(documents)
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentWithVersionsResponse,
    summary="Buscar documento por ID",
    description="Retorna detalhes de um documento com suas versões."
)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> DocumentWithVersionsResponse:
    """
    Busca documento por ID.
    
    Inclui lista de versões.
    """
    document = await document_service.get_document_with_versions(
        db=db,
        document_id=document_id,
        user_id=user_id
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento {document_id} não encontrado"
        )
    
    return DocumentWithVersionsResponse.model_validate(document)


@router.patch(
    "/documents/{document_id}/status",
    response_model=DocumentResponse,
    summary="Atualizar status do documento",
    description="Altera o status de um documento."
)
async def update_document_status(
    document_id: UUID,
    status_update: DocumentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> DocumentResponse:
    """
    Atualiza status do documento.
    
    Status válidos: draft → generated → revised → finalized
    """
    document = await document_service.update_document_status(
        db=db,
        user_id=user_id,
        document_id=document_id,
        new_status=DocumentStatus(status_update.status)
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento {document_id} não encontrado"
        )
    
    return DocumentResponse.model_validate(document)


# ==================== VERSÕES ====================

@router.post(
    "/documents/{document_id}/versions",
    response_model=DocumentVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova versão",
    description="Cria uma nova versão do documento."
)
async def create_version(
    document_id: UUID,
    version_in: DocumentVersionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> DocumentVersionResponse:
    """
    Cria nova versão do documento.
    
    ⚠️ LEI 3: Versionamento é Obrigatório
    - Sempre cria NOVA versão
    - Nunca sobrescreve versão existente
    - Versões são IMUTÁVEIS
    
    - **created_by**: Quem criou (human ou agent)
    - **agent_name**: Nome do agente (se created_by == agent)
    """
    try:
        version = await document_service.create_version(
            db=db,
            user_id=user_id,
            document_id=document_id,
            version_in=version_in
        )
        return DocumentVersionResponse.model_validate(version)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/documents/{document_id}/versions",
    response_model=DocumentVersionListResponse,
    summary="Listar versões do documento",
    description="Lista todas as versões de um documento."
)
async def list_document_versions(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> DocumentVersionListResponse:
    """
    Lista versões de um documento.
    
    Ordenadas por version_number decrescente (mais recente primeiro).
    """
    versions = await document_service.get_document_versions(
        db=db,
        document_id=document_id,
        user_id=user_id
    )
    
    return DocumentVersionListResponse(
        items=[DocumentVersionResponse.model_validate(v) for v in versions],
        total=len(versions)
    )


@router.get(
    "/document-versions/{version_id}",
    response_model=DocumentVersionResponse,
    summary="Buscar versão por ID",
    description="Retorna detalhes de uma versão específica."
)
async def get_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> DocumentVersionResponse:
    """
    Busca versão por ID.
    
    Inclui assertions da versão.
    """
    version = await document_service.get_version(
        db=db,
        version_id=version_id,
        user_id=user_id
    )
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Versão {version_id} não encontrada"
        )
    
    return DocumentVersionResponse.model_validate(version)


@router.delete(
    "/document-versions/{version_id}",
    status_code=status.HTTP_403_FORBIDDEN,
    summary="[PROIBIDO] Deletar versão",
    description="⚠️ LEI 3: Versões são IMUTÁVEIS e não podem ser deletadas."
)
async def delete_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
) -> dict:
    """
    ⚠️ LEI 3: Versões são IMUTÁVEIS
    
    Este endpoint SEMPRE retorna erro 403.
    Versões NÃO podem ser deletadas.
    """
    try:
        await document_service.delete_version(db, version_id, user_id)
    except ConstitutionViolation as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    # Nunca chega aqui
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="LEI 3: Versões são imutáveis e não podem ser deletadas"
    )
