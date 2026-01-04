from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class BaseModel(SQLModel):
    # CORREÇÃO AQUI: Removemos o primary_key=True de fora e deixamos apenas dentro do sa_column
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            primary_key=True, 
            nullable=False, 
            server_default=text("gen_random_uuid()")
        )
    )

class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()")
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
            onupdate=text("now()")
        )
    )
