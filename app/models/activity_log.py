from uuid import UUID
from typing import Optional, Dict, Any
from sqlmodel import Field
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INET
from app.models.base import BaseModel


class ActivityLog(BaseModel, table=True):
    __tablename__ = "activity_logs"

    user_id: Optional[UUID] = Field(
        default=None,
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"nullable": True, "index": True},
    )
    action: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False, "index": True},
    )
    entity_type: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False, "index": True},
    )
    entity_id: UUID = Field(
        sa_type=PG_UUID(as_uuid=True),
        sa_column_kwargs={"nullable": False, "index": True},
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSONB,
        sa_column_kwargs={"nullable": True},
    )
    ip_address: Optional[str] = Field(
        default=None,
        sa_type=INET,
        sa_column_kwargs={"nullable": True},
    )
    user_agent: Optional[str] = Field(
        default=None,
        sa_type=Text,
        sa_column_kwargs={"nullable": True},
    )


class LogActions:
    CASE_CREATE = "case.create"
    DOCUMENT_CREATE = "document.create"
    VERSION_CREATE = "version.create"
    RENDER_DOCUMENT = "render.document"


class EntityTypes:
    CASE = "case"
    DOCUMENT = "document"
    VERSION = "version"
    USER = "user"
