"""
Schemas de Renderização.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    """Schema para requisição de renderização."""
    format: str = Field(
        "markdown",
        description="Formato de saída (markdown, html, docx, pdf)",
        examples=["markdown"]
    )


class RenderingResponse(BaseModel):
    """Schema de resposta para renderização."""
    id: UUID
    document_version_id: UUID
    rendered_text: str
    render_format: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle enums."""
        return cls(
            id=obj.id,
            document_version_id=obj.document_version_id,
            rendered_text=obj.rendered_text,
            render_format=obj.render_format.value if hasattr(obj.render_format, 'value') else obj.render_format,
            created_at=obj.created_at
        )


class RenderingListResponse(BaseModel):
    """Schema para lista de renderizações."""
    items: List[RenderingResponse]
    total: int
