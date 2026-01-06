from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile
    from app.models.legal_domain import LegalArea
    from app.models.document import LegalDocument
    from app.models.attachment import DocumentAttachment


class Case(BaseModel, TimestampMixin, table=True):
    __tablename__ = "cases"

    user_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"nullable": False, "index": True},
    )
    legal_area_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"nullable": False, "index": True},
        foreign_key="legal_areas.id",
    )
    title: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False},
    )
    description: Optional[str] = Field(
        default=None,
        sa_type=String,
        sa_column_kwargs={"nullable": True},
    )
    process_number: Optional[str] = Field(
        default=None,
        sa_type=String,
        sa_column_kwargs={"nullable": True},
    )

    legal_area: Optional["LegalArea"] = Relationship(back_populates="cases")
    documents: List["LegalDocument"] = Relationship(back_populates="case")
    attachments: List["DocumentAttachment"] = Relationship(back_populates="case")
    user_profile: Optional["UserProfile"] = Relationship(
        back_populates="cases",
        sa_relationship_kwargs={
            "primaryjoin": "Case.user_id == UserProfile.user_id",
            "foreign_keys": "[Case.user_id]",
        },
    )
