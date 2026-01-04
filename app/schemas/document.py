"""
Schemas de Documento e Versão.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """Schema para criação de documento."""
    piece_type_slug: str = Field(
        ...,
        description="Slug do tipo de peça (peticao-inicial, contestacao, etc)",
        examples=["peticao-inicial"]
    )


class DocumentStatusUpdate(BaseModel):
    """Schema para atualização de status."""
    status: str = Field(
        ...,
        description="Novo status (draft, generated, revised, finalized)",
        examples=["generated"]
    )


class DocumentVersionCreate(BaseModel):
    """Schema para criação de versão."""
    created_by: str = Field(
        ...,
        description="Quem criou (human ou agent)",
        examples=["agent"]
    )
    agent_name: Optional[str] = Field(
        None,
        description="Nome do agente (se created_by == agent)",
        examples=["Agente Petição Inicial – Art. 319 CPC"]
    )


class PieceTypeResponse(BaseModel):
    """Schema de resposta para tipo de peça."""
    id: UUID
    slug: str
    name: str
    legal_basis: Optional[str]
    
    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    """Schema de resposta para documento."""
    id: UUID
    case_id: UUID
    piece_type_id: UUID
    status: str
    current_version_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class VersionSummary(BaseModel):
    """Resumo de versão para listagem."""
    id: UUID
    version_number: int
    created_by: str
    agent_name: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class DocumentWithVersionsResponse(BaseModel):
    """Schema de resposta para documento com versões."""
    id: UUID
    case_id: UUID
    piece_type_id: UUID
    status: str
    current_version_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    versions: List[VersionSummary] = []
    
    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Schema para lista de documentos."""
    items: List[DocumentResponse]
    total: int


class DocumentVersionResponse(BaseModel):
    """Schema de resposta para versão."""
    id: UUID
    document_id: UUID
    version_number: int
    created_by: str
    agent_name: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class DocumentVersionListResponse(BaseModel):
    """Schema para lista de versões."""
    items: List[DocumentVersionResponse]
    total: int
