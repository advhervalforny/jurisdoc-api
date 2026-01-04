from uuid import UUID
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

class LegalArea(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_areas"
    
    name: str = Field(index=True, unique=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    
    # Relacionamentos
    piece_types: List["LegalPieceType"] = Relationship(back_populates="legal_area")

class LegalPieceType(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_piece_types"
    
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    
    # CORREÇÃO AQUI: Removemos o foreign_key do Field e colocamos no Column
    legal_area_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            ForeignKey("legal_areas.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    
    # Relacionamentos
    legal_area: LegalArea = Relationship(back_populates="piece_types")
