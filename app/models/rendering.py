from uuid import UUID
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Text, Enum as SAEnum, text
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
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"nullable": False, "index": True},
        foreign_key="legal_document_versions.id",
    )
    rendered_text: str = Field(
        sa_type=Text,
        sa_column_kwargs={"nullable": False},
    )
    render_format: RenderFormat = Field(
        default=RenderFormat.MARKDOWN,
        sa_type=SAEnum(RenderFormat),
        sa_column_kwargs={"nullable": False, "server_default": text("'markdown'")},
    )

    document_version: Optional["LegalDocumentVersion"] = Relationship(back_populates="renderings")
