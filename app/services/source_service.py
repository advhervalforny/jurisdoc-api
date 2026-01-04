"""
Service de Fontes Jurídicas.

Gerencia fontes (leis, jurisprudência, doutrina) usadas nas assertions.
Suporta busca vetorial para RAG.
"""
from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func, or_

from app.models.assertion import (
    LegalSource,
    SourceType,
    SOURCE_HIERARCHY
)
from app.models.activity_log import LogActions, EntityTypes
from app.services.base import BaseService, log_activity
from app.schemas.source import SourceCreate


class SourceService(BaseService[LegalSource]):
    """
    Service para gerenciamento de Fontes Jurídicas.
    
    Fontes são entidades de primeira classe no sistema.
    Respeitam a hierarquia normativa:
    1. Constituição
    2. Lei
    3. Jurisprudência
    4. Doutrina
    5. Argumentação
    """
    
    def __init__(self):
        super().__init__(LegalSource)
    
    async def get_source_by_id(
        self,
        db: AsyncSession,
        source_id: UUID
    ) -> Optional[LegalSource]:
        """Busca fonte por ID."""
        statement = select(LegalSource).where(LegalSource.id == source_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def search_sources(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        source_type: Optional[SourceType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[LegalSource]:
        """
        Busca fontes com filtros.
        
        Args:
            query: Texto para buscar em reference e excerpt
            source_type: Filtrar por tipo de fonte
            skip: Offset para paginação
            limit: Limite de resultados
        
        Returns:
            Lista de fontes ordenadas por hierarquia normativa
        """
        statement = select(LegalSource)
        
        # Filtro por tipo
        if source_type:
            statement = statement.where(LegalSource.source_type == source_type)
        
        # Busca textual
        if query:
            search_pattern = f"%{query}%"
            statement = statement.where(
                or_(
                    LegalSource.reference.ilike(search_pattern),
                    LegalSource.excerpt.ilike(search_pattern)
                )
            )
        
        # Ordenar por tipo (hierarquia) e referência
        statement = (
            statement
            .order_by(LegalSource.source_type, LegalSource.reference)
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(statement)
        sources = list(result.scalars().all())
        
        # Ordenar por hierarquia normativa
        return sorted(sources, key=lambda s: SOURCE_HIERARCHY.get(s.source_type, 99))
    
    async def get_sources_by_type(
        self,
        db: AsyncSession,
        source_type: SourceType,
        skip: int = 0,
        limit: int = 100
    ) -> List[LegalSource]:
        """Lista fontes de um tipo específico."""
        statement = (
            select(LegalSource)
            .where(LegalSource.source_type == source_type)
            .order_by(LegalSource.reference)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def get_source_by_reference(
        self,
        db: AsyncSession,
        source_type: SourceType,
        reference: str
    ) -> Optional[LegalSource]:
        """
        Busca fonte por tipo e referência.
        
        Útil para evitar duplicatas.
        """
        statement = (
            select(LegalSource)
            .where(LegalSource.source_type == source_type)
            .where(LegalSource.reference == reference)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def create_source(
        self,
        db: AsyncSession,
        source_in: SourceCreate,
        user_id: Optional[UUID] = None
    ) -> LegalSource:
        """
        Cria nova fonte jurídica.
        
        Verifica duplicatas antes de criar.
        """
        # Verificar duplicata
        existing = await self._check_duplicate(
            db,
            SourceType(source_in.source_type),
            source_in.reference,
            source_in.excerpt
        )
        if existing:
            return existing  # Retorna existente ao invés de criar duplicata
        
        # Criar fonte
        source = LegalSource(
            source_type=SourceType(source_in.source_type),
            reference=source_in.reference,
            excerpt=source_in.excerpt,
            source_url=source_in.source_url
        )
        
        db.add(source)
        await db.commit()
        await db.refresh(source)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.SOURCE_CREATE,
            entity_type=EntityTypes.SOURCE,
            entity_id=source.id,
            details={
                "type": source_in.source_type,
                "reference": source_in.reference
            }
        )
        
        return source
    
    async def create_sources_bulk(
        self,
        db: AsyncSession,
        sources_in: List[SourceCreate],
        user_id: Optional[UUID] = None
    ) -> List[LegalSource]:
        """
        Cria múltiplas fontes de uma vez.
        
        Ignora duplicatas silenciosamente.
        """
        created_sources = []
        
        for source_in in sources_in:
            # Verificar duplicata
            existing = await self._check_duplicate(
                db,
                SourceType(source_in.source_type),
                source_in.reference,
                source_in.excerpt
            )
            
            if existing:
                created_sources.append(existing)
            else:
                source = LegalSource(
                    source_type=SourceType(source_in.source_type),
                    reference=source_in.reference,
                    excerpt=source_in.excerpt,
                    source_url=source_in.source_url
                )
                db.add(source)
                created_sources.append(source)
        
        await db.commit()
        
        # Refresh all
        for source in created_sources:
            await db.refresh(source)
        
        return created_sources
    
    async def count_by_type(
        self,
        db: AsyncSession
    ) -> dict:
        """
        Conta fontes agrupadas por tipo.
        
        Returns:
            Dict com contagem por tipo de fonte
        """
        statement = (
            select(LegalSource.source_type, func.count())
            .group_by(LegalSource.source_type)
        )
        result = await db.execute(statement)
        
        counts = {st.value: 0 for st in SourceType}
        for source_type, count in result.all():
            counts[source_type.value] = count
        
        return counts
    
    def get_hierarchy_order(self, source_type: SourceType) -> int:
        """
        Retorna ordem na hierarquia normativa.
        
        1 = mais alto (Constituição)
        5 = mais baixo (Argumentação)
        """
        return SOURCE_HIERARCHY.get(source_type, 99)
    
    def get_source_types_info(self) -> List[dict]:
        """
        Retorna informações sobre tipos de fonte.
        
        Útil para frontend exibir opções.
        """
        return [
            {
                "type": st.value,
                "hierarchy_order": SOURCE_HIERARCHY.get(st, 99),
                "name": self._get_type_display_name(st)
            }
            for st in SourceType
        ]
    
    async def _check_duplicate(
        self,
        db: AsyncSession,
        source_type: SourceType,
        reference: str,
        excerpt: str
    ) -> Optional[LegalSource]:
        """Verifica se fonte já existe (mesma type, reference, excerpt)."""
        statement = (
            select(LegalSource)
            .where(LegalSource.source_type == source_type)
            .where(LegalSource.reference == reference)
            .where(LegalSource.excerpt == excerpt)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    def _get_type_display_name(self, source_type: SourceType) -> str:
        """Retorna nome de exibição do tipo de fonte."""
        names = {
            SourceType.CONSTITUICAO: "Constituição Federal",
            SourceType.LEI: "Lei",
            SourceType.JURISPRUDENCIA: "Jurisprudência",
            SourceType.DOUTRINA: "Doutrina",
            SourceType.ARGUMENTACAO: "Argumentação"
        }
        return names.get(source_type, source_type.value)


# Instância singleton
source_service = SourceService()
