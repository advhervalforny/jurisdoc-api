from uuid import UUID
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Column, Text, Enum as SAEnum, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import LegalDocumentVersion

class RenderFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    DOCX = "docx"
    PDF = "pdf"

class DocumentRendering(BaseModel, table=True):
    __tablename__ = "document_renderings"
    document_version_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("legal_document_versions.id"), nullable=False, index=True)
    )
    rendered_text: str = Field(sa_column=Column(Text, nullable=False))
    render_format: RenderFormat = Field(
        default=RenderFormat.MARKDOWN,
        sa_column=Column(SAEnum(RenderFormat), nullable=False, server_default=text("'markdown'"))
    )
    document_version: Optional["LegalDocumentVersion"] = Relationship(back_populates="renderings")
