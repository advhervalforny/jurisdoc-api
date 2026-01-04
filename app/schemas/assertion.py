"""
Schemas de Afirmação Jurídica.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class AssertionCreate(BaseModel):
    """Schema para criação de assertion."""
    text: str = Field(
        ...,
        min_length=10,
        description="Texto da afirmação jurídica"
    )
    type: str = Field(
        ...,
        description="Tipo (fato, tese, fundamento, pedido)",
        examples=["fundamento"]
    )
    confidence_level: str = Field(
        "medio",
        description="Nível de confiança (alto, medio, baixo)",
        examples=["alto"]
    )


class AssertionBulkCreate(BaseModel):
    """Schema para criação em lote de assertions."""
    document_version_id: UUID = Field(
        ...,
        description="ID da versão do documento"
    )
    assertions: List[AssertionCreate] = Field(
        ...,
        min_length=1,
        description="Lista de assertions a criar"
    )


class AssertionSourceLink(BaseModel):
    """Schema para vincular fonte a assertion."""
    source_id: UUID = Field(
        ...,
        description="ID da fonte a vincular"
    )


class SourceSummary(BaseModel):
    """Resumo de fonte para listagem."""
    id: UUID
    source_type: str
    reference: str
    
    model_config = {"from_attributes": True}


class AssertionResponse(BaseModel):
    """Schema de resposta para assertion."""
    id: UUID
    document_version_id: UUID
    assertion_text: str
    assertion_type: str
    confidence_level: str
    position: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AssertionWithSourcesResponse(BaseModel):
    """Schema de resposta para assertion com fontes."""
    id: UUID
    document_version_id: UUID
    assertion_text: str
    assertion_type: str
    confidence_level: str
    position: int
    created_at: datetime
    sources: List[SourceSummary] = []
    has_sources: bool = False
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle source_links."""
        if hasattr(obj, 'source_links'):
            sources = [
                SourceSummary.model_validate(link.source)
                for link in obj.source_links
                if link.source
            ]
            has_sources = len(sources) > 0
        else:
            sources = []
            has_sources = False
        
        return cls(
            id=obj.id,
            document_version_id=obj.document_version_id,
            assertion_text=obj.assertion_text,
            assertion_type=obj.assertion_type.value if hasattr(obj.assertion_type, 'value') else obj.assertion_type,
            confidence_level=obj.confidence_level.value if hasattr(obj.confidence_level, 'value') else obj.confidence_level,
            position=obj.position,
            created_at=obj.created_at,
            sources=sources,
            has_sources=has_sources
        )


class AssertionListResponse(BaseModel):
    """Schema para lista de assertions."""
    items: List[AssertionWithSourcesResponse]
    total: int


class AssertionBulkResponse(BaseModel):
    """Schema de resposta para criação em lote."""
    created_count: int
    assertions: List[AssertionResponse]


class AssertionValidationResponse(BaseModel):
    """Schema de resposta para validação de assertion."""
    assertion_id: UUID
    is_valid: bool
    error: Optional[str] = None
