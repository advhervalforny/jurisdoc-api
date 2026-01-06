from uuid import UUID
from typing import Optional, Dict, Any
from sqlmodel import Field
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INET
from app.models.base import BaseModel

class ActivityLog(BaseModel, table=True):
    __tablename__ = "activity_logs"
    user_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), nullable=True, index=True))
    action: str = Field(sa_column=Column(String, nullable=False, index=True))
    entity_type: str = Field(sa_column=Column(String, nullable=False, index=True))
    entity_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), nullable=False, index=True))
    details: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    ip_address: Optional[str] = Field(default=None, sa_column=Column(INET, nullable=True))
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

class LogActions:
    CASE_CREATE = "case.create"; DOCUMENT_CREATE = "document.create"
    VERSION_CREATE = "version.create"; RENDER_DOCUMENT = "render.document"

class EntityTypes:
    CASE = "case"; DOCUMENT = "document"; VERSION = "version"; USER = "user"
