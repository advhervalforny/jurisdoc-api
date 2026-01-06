from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import String, Boolean, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.document import LegalDocument


class LegalArea(BaseModel, table=True):
    __tablename__ = "legal_areas"

    slug: str = Field(
        sa_type=String,
        sa_column_kwargs={"unique": True, "nullable": False, "index": True},
    )
    name: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False},
    )
    description: Optional[str] = Field(
        default=None,
        sa_type=String,
        sa_column_kwargs={"nullable": True},
    )
    is_active: bool = Field(
        default=True,
        sa_type=Boolean,
        sa_column_kwargs={"nullable": False, "server_default": text("true")},
    )

    piece_types: List["LegalPieceType"] = Relationship(back_populates="legal_area")
    cases: List["Case"] = Relationship(back_populates="legal_area")


class LegalPieceType(BaseModel, table=True):
    __tablename__ = "legal_piece_types"

    legal_area_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={
            "nullable": False,
            "index": True,
        },
        foreign_key="legal_areas.id",
    )
    slug: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False},
    )
    name: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False},
    )
    description: Optional[str] = Field(
        default=None,
        sa_type=String,
        sa_column_kwargs={"nullable": True},
    )
    legal_basis: Optional[str] = Field(
        default=None,
        sa_type=String,
        sa_column_kwargs={"nullable": True},
    )
    is_active: bool = Field(
        default=True,
        sa_type=Boolean,
        sa_column_kwargs={"nullable": False, "server_default": text("true")},
    )

    legal_area: Optional[LegalArea] = Relationship(back_populates="piece_types")
    documents: List["LegalDocument"] = Relationship(back_populates="piece_type")
