"""
Base model e configurações comuns para todos os models.
"""
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import text

class BaseModel(SQLModel):
    """
    Model base com campos comuns a todas as entidades.
    """
    # Usamos primary_key e index no Field. O SQLModel cuidará de criar
    # uma nova coluna UUID para cada tabela filha.
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="ID único gerado automaticamente (UUID v4)"
    )
    
    # sa_column_kwargs permite passar parâmetros ao SQLAlchemy sem instanciar
    # o objeto Column diretamente aqui, evitando conflitos entre tabelas.
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
