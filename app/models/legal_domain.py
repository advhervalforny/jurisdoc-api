from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Boolean, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.document import LegalDocument

class LegalArea(BaseModel, table=True):
    __tablename__ = "legal_areas"
    slug: str = Field(sa_column=Column(String, unique=True, nullable=False, index=True))
    name: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    
    piece_types: List["LegalPieceType"] = Relationship(back_populates="legal_area")
    cases: List["Case"] = Relationship(back_populates="legal_area")

class LegalPieceType(BaseModel, table=True):
    __tablename__ = "legal_piece_types"
    # CORREÇÃO: ForeignKey movida para dentro do sa_column
    legal_area_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("legal_areas.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    slug: str = Field(sa_column=Column(String, nullable=False))
    name: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    legal_basis: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    
    legal_area: Optional[LegalArea] = Relationship(back_populates="piece_types")
    documents: List["LegalDocument"] = Relationship(back_populates="piece_type")
