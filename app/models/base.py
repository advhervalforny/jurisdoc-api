from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class BaseModel(SQLModel):
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
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("NOW()"),
            onupdate=datetime.utcnow,
            nullable=False
        )
    )
