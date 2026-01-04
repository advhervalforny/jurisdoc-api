"""
Service de Casos/Processos.

Gerencia a criação e manipulação de casos jurídicos.
Um caso é o contexto onde todas as peças jurídicas existem.
"""
from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.legal_domain import LegalArea
from app.models.document import LegalDocument
from app.models.activity_log import LogActions, EntityTypes
from app.services.base import BaseService, log_activity
from app.schemas.case import CaseCreate, CaseUpdate


class CaseService(BaseService[Case]):
    """
    Service para gerenciamento de Casos.
    
    Responsabilidades:
    - Criar casos
    - Listar casos do usuário
    - Buscar caso por ID
    - Atualizar caso
    - Validar área jurídica
    """
    
    def __init__(self):
        super().__init__(Case)
    
    async def get_by_id_with_documents(
        self,
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID
    ) -> Optional[Case]:
        """
        Busca caso por ID com documentos carregados.
        
        Verifica ownership pelo user_id.
        """
        statement = (
            select(Case)
            .options(selectinload(Case.documents))
            .options(selectinload(Case.legal_area))
            .where(Case.id == case_id)
            .where(Case.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_user_cases(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        legal_area_slug: Optional[str] = None
    ) -> List[Case]:
        """
        Lista casos do usuário com paginação.
        
        Opcionalmente filtra por área jurídica.
        """
        statement = (
            select(Case)
            .options(selectinload(Case.legal_area))
            .where(Case.user_id == user_id)
            .order_by(Case.created_at.desc())
        )
        
        # Filtro por área jurídica
        if legal_area_slug:
            statement = statement.join(LegalArea).where(LegalArea.slug == legal_area_slug)
        
        statement = statement.offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def count_user_cases(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> int:
        """Conta total de casos do usuário."""
        statement = (
            select(func.count())
            .select_from(Case)
            .where(Case.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one()
    
    async def create_case(
        self,
        db: AsyncSession,
        user_id: UUID,
        case_in: CaseCreate
    ) -> Case:
        """
        Cria novo caso.
        
        Valida:
        - Área jurídica existe e está ativa
        """
        # Validar área jurídica
        legal_area = await self._get_legal_area_by_slug(db, case_in.legal_area_slug)
        if not legal_area:
            raise ValueError(f"Área jurídica '{case_in.legal_area_slug}' não encontrada")
        
        if not legal_area.is_active:
            raise ValueError(f"Área jurídica '{case_in.legal_area_slug}' não está ativa")
        
        # Criar caso
        case = Case(
            user_id=user_id,
            legal_area_id=legal_area.id,
            title=case_in.title,
            description=case_in.description,
            process_number=case_in.process_number
        )
        
        db.add(case)
        await db.commit()
        await db.refresh(case)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.CASE_CREATE,
            entity_type=EntityTypes.CASE,
            entity_id=case.id,
            details={
                "title": case.title,
                "legal_area": case_in.legal_area_slug
            }
        )
        
        return case
    
    async def update_case(
        self,
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        case_in: CaseUpdate
    ) -> Optional[Case]:
        """
        Atualiza caso existente.
        
        Apenas título, descrição e número do processo podem ser atualizados.
        Área jurídica NÃO pode ser alterada após criação.
        """
        case = await self.get_by_id_with_documents(db, case_id, user_id)
        if not case:
            return None
        
        # Atualizar campos permitidos
        if case_in.title is not None:
            case.title = case_in.title
        if case_in.description is not None:
            case.description = case_in.description
        if case_in.process_number is not None:
            case.process_number = case_in.process_number
        
        await db.commit()
        await db.refresh(case)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.CASE_UPDATE,
            entity_type=EntityTypes.CASE,
            entity_id=case.id,
            details=case_in.model_dump(exclude_unset=True)
        )
        
        return case
    
    async def delete_case(
        self,
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Deleta caso (soft delete recomendado em produção).
        
        ⚠️ Isso também deleta todos os documentos do caso (CASCADE).
        """
        case = await self.get_by_id_with_documents(db, case_id, user_id)
        if not case:
            return False
        
        await db.delete(case)
        await db.commit()
        
        return True
    
    async def get_case_documents_count(
        self,
        db: AsyncSession,
        case_id: UUID
    ) -> int:
        """Conta documentos de um caso."""
        statement = (
            select(func.count())
            .select_from(LegalDocument)
            .where(LegalDocument.case_id == case_id)
        )
        result = await db.execute(statement)
        return result.scalar_one()
    
    async def _get_legal_area_by_slug(
        self,
        db: AsyncSession,
        slug: str
    ) -> Optional[LegalArea]:
        """Busca área jurídica por slug."""
        statement = select(LegalArea).where(LegalArea.slug == slug)
        result = await db.execute(statement)
        return result.scalar_one_or_none()


# Instância singleton
case_service = CaseService()
