"""
Schemas de Fonte Jurídica.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    """Schema para criação de fonte."""
    source_type: str = Field(
        ...,
        description="Tipo (constituicao, lei, jurisprudencia, doutrina, argumentacao)",
        examples=["lei"]
    )
    reference: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Referência da fonte",
        examples=["CPC, art. 319"]
    )
    excerpt: str = Field(
        ...,
        min_length=10,
        description="Trecho relevante da fonte"
    )
    source_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL da fonte"
    )


class SourceResponse(BaseModel):
    """Schema de resposta para fonte."""
    id: UUID
    source_type: str
    reference: str
    excerpt: str
    source_url: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle enums."""
        return cls(
            id=obj.id,
            source_type=obj.source_type.value if hasattr(obj.source_type, 'value') else obj.source_type,
            reference=obj.reference,
            excerpt=obj.excerpt,
            source_url=obj.source_url,
            created_at=obj.created_at
        )


class SourceListResponse(BaseModel):
    """Schema para lista de fontes."""
    items: List[SourceResponse]
    total: int


class SourceTypeInfo(BaseModel):
    """Informações sobre tipo de fonte."""
    type: str
    hierarchy_order: int
    name: str
