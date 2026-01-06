from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.legal_domain import LegalArea
    from app.models.document import LegalDocument
    from app.models.attachment import DocumentAttachment

class Case(BaseModel, TimestampMixin, table=True):
    __tablename__ = "cases"
    user_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), nullable=False, index=True))
    # FK corrigida
    legal_area_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("legal_areas.id"),
            nullable=False,
            index=True
        )
    )
    title: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    process_number: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    
    legal_area: Optional["LegalArea"] = Relationship(back_populates="cases")
    documents: List["LegalDocument"] = Relationship(back_populates="case")
    attachments: List["DocumentAttachment"] = Relationship(back_populates="case")
