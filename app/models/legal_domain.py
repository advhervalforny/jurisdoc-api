"""
Models de domínio jurídico estrutural.
"""
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import text
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.document import LegalDocument

class LegalArea(BaseModel, table=True):
    """
    Área do Direito.
    """
    __tablename__ = "legal_areas"
    
    slug: str = Field(unique=True, nullable=False, index=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(
        default=True,
        sa_column_kwargs={"server_default": text("true")}
    )
    
    # Relacionamentos
    piece_types: List["LegalPieceType"] = Relationship(back_populates="legal_area")
    cases: List["Case"] = Relationship(back_populates="legal_area")
    
    def __repr__(self) -> str:
        return f"<LegalArea {self.slug}: {self.name}>"

class LegalPieceType(BaseModel, table=True):
    """
    Tipo de peça jurídica.
    """
    __tablename__ = "legal_piece_types"
    
    # FK corrigida: usamos foreign_key diretamente no Field do SQLModel
    legal_area_id: UUID = Field(
        foreign_key="legal_areas.id",
        nullable=False,
        index=True
    )
    
    slug: str = Field(nullable=False)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    legal_basis: Optional[str] = Field(
        default=None,
        description="Base legal, ex: 'Art. 319 CPC'"
    )
    is_active: bool = Field(
        default=True,
        sa_column_kwargs={"server_default": text("true")}
    )
    
    # Relacionamentos
    legal_area: Optional[LegalArea] = Relationship(back_populates="piece_types")
    documents: List["LegalDocument"] = Relationship(back_populates="piece_type")
    
    def __repr__(self) -> str:
        return f"<LegalPieceType {self.slug}: {self.name}>"
