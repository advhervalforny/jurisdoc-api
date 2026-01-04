"""
Models de Afirmação Jurídica e Fontes.

⚠️ ESTE É O CORAÇÃO DO SISTEMA

LEIS CONSTITUCIONAIS IMPLEMENTADAS:
- LEI 2: Nenhuma afirmação sem fonte
- LEI 4: Texto final é derivado das assertions
- LEI 5: IA não escreve texto final, escreve assertions
"""
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, Text, DateTime, Enum as SAEnum, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.document import LegalDocumentVersion


class AssertionType(str, Enum):
    """
    Tipo de afirmação jurídica.
    
    Classifica o papel da afirmação na peça.
    """
    FATO = "fato"             # Descrição factual
    TESE = "tese"             # Argumento/tese jurídica
    FUNDAMENTO = "fundamento" # Fundamentação legal
    PEDIDO = "pedido"         # Pedido ao juízo


class ConfidenceLevel(str, Enum):
    """
    Nível de confiança da afirmação.
    
    Usado para indicar certeza jurídica.
    """
    ALTO = "alto"     # Alta confiança (fonte clara, jurisprudência consolidada)
    MEDIO = "medio"   # Média confiança (interpretação razoável)
    BAIXO = "baixo"   # Baixa confiança (argumentação, sem fonte forte)


class SourceType(str, Enum):
    """
    Tipo de fonte jurídica.
    
    ⚠️ Respeita HIERARQUIA NORMATIVA:
    1. Constituição
    2. Lei
    3. Jurisprudência
    4. Doutrina
    5. Argumentação
    """
    CONSTITUICAO = "constituicao"     # Constituição Federal
    LEI = "lei"                       # Leis (CPC, CC, CDC, etc)
    JURISPRUDENCIA = "jurisprudencia" # Jurisprudência (STF, STJ, etc)
    DOUTRINA = "doutrina"             # Doutrina jurídica
    ARGUMENTACAO = "argumentacao"     # Argumentação lógica


# Hierarquia normativa (menor número = maior hierarquia)
SOURCE_HIERARCHY = {
    SourceType.CONSTITUICAO: 1,
    SourceType.LEI: 2,
    SourceType.JURISPRUDENCIA: 3,
    SourceType.DOUTRINA: 4,
    SourceType.ARGUMENTACAO: 5,
}


class LegalSource(BaseModel, table=True):
    """
    Fonte Jurídica.
    
    Entidade de primeira classe no sistema.
    Toda afirmação jurídica deve ter pelo menos uma fonte.
    
    Inclui suporte para busca vetorial (RAG) via embedding.
    """
    __tablename__ = "legal_sources"
    
    # Tipo da fonte (respeita hierarquia normativa)
    source_type: SourceType = Field(
        sa_column=Column(
            SAEnum(SourceType, name="source_type", create_type=False),
            nullable=False,
            index=True
        )
    )
    
    # Referência (ex: "CPC, art. 319")
    reference: str = Field(
        sa_column=Column(String, nullable=False, index=True)
    )
    
    # Trecho relevante da fonte
    excerpt: str = Field(
        sa_column=Column(Text, nullable=False)
    )
    
    # URL da fonte (opcional)
    source_url: Optional[str] = Field(
        default=None,
        sa_column=Column(String, nullable=True)
    )
    
    # Embedding para busca vetorial (RAG)
    # Nota: O campo vector é gerenciado diretamente via SQL/pgvector
    # embedding: Optional[List[float]] = None  # vector(1536)
    
    # Relacionamentos
    assertion_links: List["AssertionSource"] = Relationship(back_populates="source")
    
    @property
    def hierarchy_order(self) -> int:
        """Retorna a ordem na hierarquia normativa (1 = mais alto)."""
        return SOURCE_HIERARCHY.get(self.source_type, 99)
    
    def __repr__(self) -> str:
        return f"<LegalSource {self.source_type.value}: {self.reference}>"


class LegalAssertion(BaseModel, table=True):
    """
    Afirmação Jurídica.
    
    ⚠️ CORAÇÃO DO SISTEMA
    
    Cada afirmação representa uma unidade semântica da peça jurídica.
    O texto final é DERIVADO das assertions, nunca primário.
    
    LEI 2: Uma assertion só é válida se tiver pelo menos uma fonte vinculada.
    """
    __tablename__ = "legal_assertions"
    
    # FK para versão do documento
    document_version_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="legal_document_versions.id"
    )
    
    # Texto da afirmação
    assertion_text: str = Field(
        sa_column=Column(Text, nullable=False)
    )
    
    # Tipo da afirmação
    assertion_type: AssertionType = Field(
        sa_column=Column(
            SAEnum(AssertionType, name="assertion_type", create_type=False),
            nullable=False,
            index=True
        )
    )
    
    # Nível de confiança
    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIO,
        sa_column=Column(
            SAEnum(ConfidenceLevel, name="confidence_level", create_type=False),
            nullable=False,
            server_default=text("'medio'")
        )
    )
    
    # Posição na peça (ordem)
    position: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default=text("0"))
    )
    
    # Relacionamentos
    document_version: Optional["LegalDocumentVersion"] = Relationship(back_populates="assertions")
    source_links: List["AssertionSource"] = Relationship(back_populates="assertion")
    
    @property
    def sources(self) -> List[LegalSource]:
        """Retorna as fontes vinculadas a esta assertion."""
        return [link.source for link in self.source_links if link.source]
    
    @property
    def has_sources(self) -> bool:
        """
        Verifica se a assertion tem pelo menos uma fonte.
        
        ⚠️ LEI 2: Nenhuma afirmação sem fonte.
        """
        return len(self.source_links) > 0
    
    @property
    def is_juridically_valid(self) -> bool:
        """
        Verifica se a assertion é juridicamente válida.
        
        Uma assertion é válida se:
        1. Tem pelo menos uma fonte, OU
        2. Tem confidence_level == 'baixo' (indica sem fonte forte)
        """
        if self.has_sources:
            return True
        # Se não tem fonte, só é "válido" se marcado como baixa confiança
        return self.confidence_level == ConfidenceLevel.BAIXO
    
    @property
    def sources_count(self) -> int:
        """Retorna a quantidade de fontes vinculadas."""
        return len(self.source_links)
    
    def __repr__(self) -> str:
        return f"<LegalAssertion {self.assertion_type.value} (sources: {self.sources_count}, valid: {self.is_juridically_valid})>"


class AssertionSource(BaseModel, table=True):
    """
    Vínculo entre Assertion e Source.
    
    ⚠️ LEI 2: Uma assertion só é válida se existir pelo menos
    um registro nesta tabela vinculando-a a uma fonte.
    
    Esta tabela implementa a rastreabilidade:
    texto → assertion → fonte
    """
    __tablename__ = "assertion_sources"
    
    # FK para assertion
    assertion_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="legal_assertions.id"
    )
    
    # FK para source
    source_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            nullable=False,
            index=True
        ),
        foreign_key="legal_sources.id"
    )
    
    # Relacionamentos
    assertion: Optional[LegalAssertion] = Relationship(back_populates="source_links")
    source: Optional[LegalSource] = Relationship(back_populates="assertion_links")
    
    def __repr__(self) -> str:
        return f"<AssertionSource assertion={self.assertion_id} -> source={self.source_id}>"
