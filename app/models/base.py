"""
Base model e configurações comuns para todos os models.
"""
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class BaseModel(SQLModel):
    """
    Model base com campos comuns a todas as entidades.
    """
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("NOW()"),
            nullable=False
        )
    )


class TimestampMixin(SQLModel):
    """
    Mixin para entidades que precisam de updated_at.
    """
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("NOW()"),
            onupdate=datetime.utcnow,
            nullable=False
        )
    )
