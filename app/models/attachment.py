from datetime import datetime
from uuid import UUID
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import String, Integer, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case


class DocumentAttachment(BaseModel, table=True):
    __tablename__ = "document_attachments"

    case_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"nullable": False, "index": True},
        foreign_key="cases.id",
    )
    file_name: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False},
    )
    file_path: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False},
    )
    file_size: Optional[int] = Field(
        default=None,
        sa_type=Integer,
        sa_column_kwargs={"nullable": True},
    )
    mime_type: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False},
    )
    extracted_text: Optional[str] = Field(
        default=None,
        sa_type=Text,
        sa_column_kwargs={"nullable": True},
    )
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": text("NOW()"), "nullable": False},
    )

    case: Optional["Case"] = Relationship(back_populates="attachments")
