from uuid import UUID
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

class Case(BaseModel, TimestampMixin, table=True):
    __tablename__ = "cases"
    
    title: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    case_number: Optional[str] = Field(default=None, max_length=100, index=True)
    
    # CORREÇÃO: Removido foreign_key do Field e movido para o sa_column
    legal_area_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            ForeignKey("legal_areas.id", ondelete="RESTRICT"),
            nullable=False
        )
    )
    
    # CORREÇÃO: Removido foreign_key do Field e movido para o sa_column
    piece_type_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            ForeignKey("legal_piece_types.id", ondelete="RESTRICT"),
            nullable=False
        )
    )

    # Relacionamentos
    # legal_area e piece_type devem estar definidos nos respectivos models
