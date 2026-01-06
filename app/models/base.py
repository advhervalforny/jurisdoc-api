from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


def get_uuid_column():
    """Factory function to create a new UUID column for each model."""
    return Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)


def get_created_at_column():
    """Factory function to create a new created_at column for each model."""
    return Column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )


def get_updated_at_column():
    """Factory function to create a new updated_at column for each model."""
    return Column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=datetime.utcnow,
        nullable=False
    )


class BaseModel(SQLModel):
    """
    Model base com campos comuns a todas as entidades.
    Usa sa_column_kwargs para evitar compartilhamento de objetos Column.
    """
    id: UUID = Field(
        default_factory=uuid4,
        sa_column_kwargs={
            "primary_key": True,
        },
        sa_type=PG_UUID(as_uuid=True),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("NOW()"),
            "nullable": False,
        },
        sa_type=DateTime(timezone=True),
    )


class TimestampMixin(SQLModel):
    """
    Mixin para entidades que precisam de updated_at.
    """
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("NOW()"),
            "onupdate": datetime.utcnow,
            "nullable": False,
        },
        sa_type=DateTime(timezone=True),
    )
