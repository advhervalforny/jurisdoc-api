from uuid import UUID
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import BaseModel, TimestampMixin

class LegalAssertion(BaseModel, TimestampMixin, table=True):
    __tablename__ = "legal_assertions"
    
    content: str = Field(sa_column=Column(Text, nullable=False))
    is_fact: bool = Field(default=True, sa_column=Column(Boolean, server_default="true"))
    page_number: Optional[int] = Field(default=None)
    
    # CORREÇÃO: Movido foreign_key do Field para dentro do sa_column
    document_version_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), 
            ForeignKey("legal_document_versions.id", ondelete="CASCADE"),
            nullable=False
        )
    )

    # Caso seu modelo tenha também uma ligação direta com o processo (Case), 
    # aplique a mesma lógica se houver erro:
    # case_id: UUID = Field(
    #     sa_column=Column(
    #         PG_UUID(as_uuid=True), 
    #         ForeignKey("cases.id", ondelete="CASCADE"),
    #         nullable=False
    #     )
    # )
