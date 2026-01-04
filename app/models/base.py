from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import text

class BaseModel(SQLModel):
    # Usamos primary_key=True direto no Field para evitar o erro de compartilhamento
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
        }
    )

class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("now()"),
        }
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": text("now()"),
            "onupdate": text("now()"),
        }
    )
