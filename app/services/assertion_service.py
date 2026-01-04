"""
Service de Afirmações Jurídicas.

⚠️ ESTE É O CORAÇÃO DO SISTEMA

LEIS CONSTITUCIONAIS IMPLEMENTADAS:
- LEI 2: Nenhuma afirmação sem fonte
- LEI 4: Texto final é derivado das assertions
- LEI 5: IA não escreve texto final, escreve assertions
"""
from typing import Optional, List, Tuple
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.document import LegalDocument, LegalDocumentVersion
from app.models.assertion import (
    LegalAssertion, 
    LegalSource, 
    AssertionSource,
    AssertionType,
    ConfidenceLevel,
    SourceType,
    SOURCE_HIERARCHY
)
from app.models.activity_log import LogActions, EntityTypes
from app.services.base import BaseService, log_activity
from app.schemas.assertion import AssertionCreate, AssertionBulkCreate
from app.core.constitution import (
    ConstitutionViolation,
    JuridicalValidationError,
    require_source_for_assertion,
    validate_normative_hierarchy
)


class AssertionService(BaseService[LegalAssertion]):
    """
    Service para gerenciamento de Afirmações Jurídicas.
    
    ⚠️ CORAÇÃO DO SISTEMA
    
    As assertions são a fonte da verdade do conteúdo jurídico.
    O texto final é DERIVADO das assertions.
    
    LEI 2: Uma assertion só é válida se tiver pelo menos uma fonte.
    LEI 5: IA produz assertions, não texto final.
    """
    
    def __init__(self):
        super().__init__(LegalAssertion)
    
    async def get_assertion_with_sources(
        self,
        db: AsyncSession,
        assertion_id: UUID,
        user_id: UUID
    ) -> Optional[LegalAssertion]:
        """
        Busca assertion com fontes carregadas.
        
        Verifica ownership através da cadeia:
        assertion → version → document → case → user
        """
        statement = (
            select(LegalAssertion)
            .join(LegalDocumentVersion)
            .join(LegalDocument)
            .join(Case)
            .options(selectinload(LegalAssertion.source_links).selectinload(AssertionSource.source))
            .where(LegalAssertion.id == assertion_id)
            .where(Case.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_version_assertions(
        self,
        db: AsyncSession,
        version_id: UUID,
        user_id: UUID
    ) -> List[LegalAssertion]:
        """
        Lista assertions de uma versão ordenadas por posição.
        """
        statement = (
            select(LegalAssertion)
            .join(LegalDocumentVersion)
            .join(LegalDocument)
            .join(Case)
            .options(selectinload(LegalAssertion.source_links).selectinload(AssertionSource.source))
            .where(LegalAssertion.document_version_id == version_id)
            .where(Case.user_id == user_id)
            .order_by(LegalAssertion.position)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def create_assertion(
        self,
        db: AsyncSession,
        user_id: UUID,
        version_id: UUID,
        assertion_in: AssertionCreate,
        position: Optional[int] = None
    ) -> LegalAssertion:
        """
        Cria nova assertion.
        
        ⚠️ LEI 2: Assertion criada sem fonte terá is_juridically_valid=False
        
        A assertion deve ter fontes vinculadas posteriormente
        para ser considerada válida.
        """
        # Validar versão
        version = await self._get_version_for_user(db, version_id, user_id)
        if not version:
            raise ValueError(f"Versão '{version_id}' não encontrada")
        
        # Calcular posição se não informada
        if position is None:
            position = await self._get_next_position(db, version_id)
        
        # Criar assertion
        assertion = LegalAssertion(
            document_version_id=version_id,
            assertion_text=assertion_in.text,
            assertion_type=AssertionType(assertion_in.type),
            confidence_level=ConfidenceLevel(assertion_in.confidence_level),
            position=position
        )
        
        db.add(assertion)
        await db.commit()
        await db.refresh(assertion)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.ASSERTION_CREATE,
            entity_type=EntityTypes.ASSERTION,
            entity_id=assertion.id,
            details={
                "version_id": str(version_id),
                "type": assertion_in.type,
                "confidence": assertion_in.confidence_level,
                "has_sources": False  # Recém criada, sem fontes
            }
        )
        
        return assertion
    
    async def create_assertions_bulk(
        self,
        db: AsyncSession,
        user_id: UUID,
        bulk_in: AssertionBulkCreate
    ) -> List[LegalAssertion]:
        """
        Cria múltiplas assertions de uma vez.
        
        Usado principalmente pelo pipeline de IA.
        
        ⚠️ LEI 5: IA produz assertions, não texto final.
        """
        # Validar versão
        version = await self._get_version_for_user(db, bulk_in.document_version_id, user_id)
        if not version:
            raise ValueError(f"Versão '{bulk_in.document_version_id}' não encontrada")
        
        # Obter posição inicial
        start_position = await self._get_next_position(db, bulk_in.document_version_id)
        
        created_assertions = []
        for idx, assertion_in in enumerate(bulk_in.assertions):
            assertion = LegalAssertion(
                document_version_id=bulk_in.document_version_id,
                assertion_text=assertion_in.text,
                assertion_type=AssertionType(assertion_in.type),
                confidence_level=ConfidenceLevel(assertion_in.confidence_level),
                position=start_position + idx
            )
            db.add(assertion)
            created_assertions.append(assertion)
        
        await db.commit()
        
        # Refresh all
        for assertion in created_assertions:
            await db.refresh(assertion)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.ASSERTION_BULK_CREATE,
            entity_type=EntityTypes.VERSION,
            entity_id=bulk_in.document_version_id,
            details={
                "count": len(created_assertions),
                "types": [a.assertion_type.value for a in created_assertions]
            }
        )
        
        return created_assertions
    
    async def link_source(
        self,
        db: AsyncSession,
        user_id: UUID,
        assertion_id: UUID,
        source_id: UUID
    ) -> AssertionSource:
        """
        Vincula fonte a uma assertion.
        
        ⚠️ LEI 2: Nenhuma afirmação sem fonte
        Este é o método que torna uma assertion juridicamente válida.
        """
        # Validar assertion
        assertion = await self.get_assertion_with_sources(db, assertion_id, user_id)
        if not assertion:
            raise ValueError(f"Assertion '{assertion_id}' não encontrada")
        
        # Validar source
        source = await self._get_source(db, source_id)
        if not source:
            raise ValueError(f"Fonte '{source_id}' não encontrada")
        
        # Verificar se já está vinculada
        existing = await self._get_assertion_source_link(db, assertion_id, source_id)
        if existing:
            return existing
        
        # Criar vínculo
        link = AssertionSource(
            assertion_id=assertion_id,
            source_id=source_id
        )
        
        db.add(link)
        await db.commit()
        await db.refresh(link)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.SOURCE_LINK,
            entity_type=EntityTypes.ASSERTION,
            entity_id=assertion_id,
            details={
                "source_id": str(source_id),
                "source_type": source.source_type.value,
                "source_ref": source.reference
            }
        )
        
        return link
    
    async def unlink_source(
        self,
        db: AsyncSession,
        user_id: UUID,
        assertion_id: UUID,
        source_id: UUID
    ) -> bool:
        """
        Remove vínculo entre assertion e fonte.
        
        ⚠️ Cuidado: Isso pode tornar a assertion juridicamente inválida.
        """
        link = await self._get_assertion_source_link(db, assertion_id, source_id)
        if not link:
            return False
        
        await db.delete(link)
        await db.commit()
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.SOURCE_UNLINK,
            entity_type=EntityTypes.ASSERTION,
            entity_id=assertion_id,
            details={"source_id": str(source_id)}
        )
        
        return True
    
    async def get_assertion_sources(
        self,
        db: AsyncSession,
        assertion_id: UUID
    ) -> List[LegalSource]:
        """
        Lista fontes vinculadas a uma assertion.
        """
        statement = (
            select(LegalSource)
            .join(AssertionSource)
            .where(AssertionSource.assertion_id == assertion_id)
            .order_by(LegalSource.source_type)  # Ordenar por hierarquia
        )
        result = await db.execute(statement)
        sources = list(result.scalars().all())
        
        # Ordenar por hierarquia normativa
        return sorted(sources, key=lambda s: SOURCE_HIERARCHY.get(s.source_type, 99))
    
    async def validate_assertion_juridically(
        self,
        db: AsyncSession,
        assertion_id: UUID
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida se assertion é juridicamente válida.
        
        ⚠️ LEI 2: Nenhuma afirmação sem fonte
        
        Returns:
            Tuple (is_valid, error_message)
        """
        # Buscar assertion com sources
        statement = (
            select(LegalAssertion)
            .options(selectinload(LegalAssertion.source_links))
            .where(LegalAssertion.id == assertion_id)
        )
        result = await db.execute(statement)
        assertion = result.scalar_one_or_none()
        
        if not assertion:
            return False, "Assertion não encontrada"
        
        # ⚠️ LEI 2: Verificar se tem fontes
        if not assertion.source_links:
            # Permitido apenas se confidence == baixo
            if assertion.confidence_level != ConfidenceLevel.BAIXO:
                return False, "Assertion sem fonte deve ter confidence_level='baixo'"
        
        return True, None
    
    async def validate_version_juridically(
        self,
        db: AsyncSession,
        version_id: UUID
    ) -> Tuple[bool, List[str]]:
        """
        Valida se todas as assertions de uma versão são juridicamente válidas.
        
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        # Buscar todas assertions da versão
        statement = (
            select(LegalAssertion)
            .options(selectinload(LegalAssertion.source_links).selectinload(AssertionSource.source))
            .where(LegalAssertion.document_version_id == version_id)
            .order_by(LegalAssertion.position)
        )
        result = await db.execute(statement)
        assertions = list(result.scalars().all())
        
        if not assertions:
            return False, ["Versão não possui assertions"]
        
        errors = []
        for assertion in assertions:
            is_valid, error = await self.validate_assertion_juridically(db, assertion.id)
            if not is_valid:
                errors.append(f"Assertion {assertion.position}: {error}")
        
        return len(errors) == 0, errors
    
    async def _get_version_for_user(
        self,
        db: AsyncSession,
        version_id: UUID,
        user_id: UUID
    ) -> Optional[LegalDocumentVersion]:
        """Busca versão validando ownership."""
        statement = (
            select(LegalDocumentVersion)
            .join(LegalDocument)
            .join(Case)
            .where(LegalDocumentVersion.id == version_id)
            .where(Case.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def _get_source(
        self,
        db: AsyncSession,
        source_id: UUID
    ) -> Optional[LegalSource]:
        """Busca fonte por ID."""
        statement = select(LegalSource).where(LegalSource.id == source_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def _get_assertion_source_link(
        self,
        db: AsyncSession,
        assertion_id: UUID,
        source_id: UUID
    ) -> Optional[AssertionSource]:
        """Busca vínculo assertion-source existente."""
        statement = (
            select(AssertionSource)
            .where(AssertionSource.assertion_id == assertion_id)
            .where(AssertionSource.source_id == source_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def _get_next_position(
        self,
        db: AsyncSession,
        version_id: UUID
    ) -> int:
        """Calcula próxima posição para assertion."""
        statement = (
            select(func.coalesce(func.max(LegalAssertion.position), -1))
            .where(LegalAssertion.document_version_id == version_id)
        )
        result = await db.execute(statement)
        current_max = result.scalar_one()
        return current_max + 1


# Instância singleton
assertion_service = AssertionService()
