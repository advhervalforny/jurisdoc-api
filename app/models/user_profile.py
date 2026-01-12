from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.case import Case


class UserProfile(BaseModel, TimestampMixin, table=True):
    __tablename__ = "user_profiles"

    user_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"unique": True, "nullable": False, "index": True},
    )
    full_name: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False},
    )
    oab_number: Optional[str] = Field(
        default=None,
        sa_type=String,
        sa_column_kwargs={"nullable": True},
    )
    oab_state: Optional[str] = Field(
        default=None,
        sa_type=String(2),
        sa_column_kwargs={"nullable": True},
    )
    phone: Optional[str] = Field(
        default=None,
        sa_type=String,
        sa_column_kwargs={"nullable": True},
    )

    # Relacionamento com Case - configurado para usar user_id como join
    cases: List["Case"] = Relationship(
        back_populates="user_profile",
        sa_relationship_kwargs={
            "primaryjoin": "UserProfile.user_id == Case.user_id",
            "foreign_keys": "[Case.user_id]",
        },
    )
