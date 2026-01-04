"""
Schemas de Caso/Processo.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    """Schema para criação de caso."""
    legal_area_slug: str = Field(
        ...,
        description="Slug da área jurídica (civil, penal)",
        examples=["civil"]
    )
    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Título do caso",
        examples=["Negativação Indevida – João da Silva"]
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descrição do caso"
    )
    process_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Número do processo judicial"
    )


class CaseUpdate(BaseModel):
    """Schema para atualização de caso."""
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255
    )
    description: Optional[str] = Field(
        None,
        max_length=1000
    )
    process_number: Optional[str] = Field(
        None,
        max_length=50
    )


class LegalAreaResponse(BaseModel):
    """Schema de resposta para área jurídica."""
    id: UUID
    slug: str
    name: str
    
    model_config = {"from_attributes": True}


class CaseResponse(BaseModel):
    """Schema de resposta para caso."""
    id: UUID
    user_id: UUID
    legal_area_id: UUID
    title: str
    description: Optional[str]
    process_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class DocumentSummary(BaseModel):
    """Resumo de documento para listagem."""
    id: UUID
    piece_type_id: UUID
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class CaseWithDocumentsResponse(BaseModel):
    """Schema de resposta para caso com documentos."""
    id: UUID
    user_id: UUID
    legal_area_id: UUID
    title: str
    description: Optional[str]
    process_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentSummary] = []
    
    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    """Schema para lista paginada de casos."""
    items: List[CaseResponse]
    total: int
    skip: int
    limit: int
