from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import text

class BaseModel(SQLModel):
    # Definimos de forma simples para evitar conflito entre tabelas
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": text("now()")}
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("now()"),
            "onupdate": text("now()")
        }
    )
