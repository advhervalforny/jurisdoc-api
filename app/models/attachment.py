from datetime import datetime
from uuid import UUID
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Column, String, Integer, Text, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case

class DocumentAttachment(BaseModel, table=True):
    __tablename__ = "document_attachments"
    case_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    )
    file_name: str = Field(sa_column=Column(String, nullable=False))
    file_path: str = Field(sa_column=Column(String, nullable=False))
    file_size: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    mime_type: str = Field(sa_column=Column(String, nullable=False))
    extracted_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    )
    case: Optional["Case"] = Relationship(back_populates="attachments")
