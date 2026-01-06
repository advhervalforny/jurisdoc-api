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
    # Removido sa_column. O SQLModel criará uma coluna nova para cada tabela.
    # O tipo UUID do Python já mapeia corretamente para PG_UUID no Postgres.
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    
    # Use sa_column_kwargs para passar parâmetros extras sem instanciar uma Column fixa
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("NOW()"),
            "nullable": False
        }
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
            "nullable": False
        }
    )
