"""
Service de Documentos Jurídicos.

⚠️ LEIS CONSTITUCIONAIS IMPLEMENTADAS:
- LEI 1: Documento ≠ Texto (documento é container)
- LEI 3: Versionamento é obrigatório

Este service gerencia documentos e suas versões.
"""
from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.document import LegalDocument, LegalDocumentVersion, DocumentStatus, VersionCreator
from app.models.legal_domain import LegalPieceType, LegalArea
from app.models.activity_log import LogActions, EntityTypes
from app.services.base import BaseService, log_activity
from app.schemas.document import DocumentCreate, DocumentVersionCreate
from app.core.constitution import (
    ConstitutionViolation,
    require_new_version_for_change,
    forbid_version_deletion
)


class DocumentService(BaseService[LegalDocument]):
    """
    Service para gerenciamento de Documentos Jurídicos.
    
    ⚠️ LEI 1: Documento ≠ Texto
    Documentos são containers, o texto está nas assertions das versões.
    
    ⚠️ LEI 3: Versionamento é Obrigatório
    Toda alteração cria nova versão, nunca sobrescreve.
    """
    
    def __init__(self):
        super().__init__(LegalDocument)
    
    async def get_document_with_versions(
        self,
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID
    ) -> Optional[LegalDocument]:
        """
        Busca documento com todas as versões carregadas.
        
        Verifica ownership através do case.
        """
        statement = (
            select(LegalDocument)
            .join(Case)
            .options(selectinload(LegalDocument.versions))
            .options(selectinload(LegalDocument.piece_type))
            .options(selectinload(LegalDocument.case))
            .where(LegalDocument.id == document_id)
            .where(Case.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_case_documents(
        self,
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID,
        status: Optional[DocumentStatus] = None
    ) -> List[LegalDocument]:
        """
        Lista documentos de um caso.
        
        Opcionalmente filtra por status.
        """
        statement = (
            select(LegalDocument)
            .join(Case)
            .options(selectinload(LegalDocument.piece_type))
            .where(LegalDocument.case_id == case_id)
            .where(Case.user_id == user_id)
            .order_by(LegalDocument.created_at.desc())
        )
        
        if status:
            statement = statement.where(LegalDocument.status == status)
        
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def create_document(
        self,
        db: AsyncSession,
        user_id: UUID,
        case_id: UUID,
        document_in: DocumentCreate
    ) -> LegalDocument:
        """
        Cria novo documento.
        
        ⚠️ LEI 1: Documento ≠ Texto
        O documento é criado VAZIO, sem texto.
        Texto será adicionado via assertions em versões.
        
        Valida:
        - Caso existe e pertence ao usuário
        - Tipo de peça existe e pertence à área do caso
        """
        # Validar caso
        case = await self._get_case_for_user(db, case_id, user_id)
        if not case:
            raise ValueError(f"Caso '{case_id}' não encontrado")
        
        # Validar tipo de peça
        piece_type = await self._get_piece_type_for_area(
            db, 
            document_in.piece_type_slug,
            case.legal_area_id
        )
        if not piece_type:
            raise ValueError(
                f"Tipo de peça '{document_in.piece_type_slug}' não encontrado "
                f"para a área jurídica do caso"
            )
        
        # ⚠️ LEI 1: Criar documento VAZIO (sem texto)
        document = LegalDocument(
            case_id=case_id,
            piece_type_id=piece_type.id,
            status=DocumentStatus.DRAFT,
            current_version_id=None  # Sem versão inicial
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.DOCUMENT_CREATE,
            entity_type=EntityTypes.DOCUMENT,
            entity_id=document.id,
            details={
                "case_id": str(case_id),
                "piece_type": document_in.piece_type_slug
            }
        )
        
        return document
    
    async def create_version(
        self,
        db: AsyncSession,
        user_id: UUID,
        document_id: UUID,
        version_in: DocumentVersionCreate
    ) -> LegalDocumentVersion:
        """
        Cria nova versão do documento.
        
        ⚠️ LEI 3: Versionamento é Obrigatório
        - Sempre cria NOVA versão
        - Nunca sobrescreve versão existente
        - Versões são IMUTÁVEIS
        
        Args:
            document_id: ID do documento
            version_in: Dados da versão (created_by, agent_name)
        
        Returns:
            Nova versão criada
        """
        # Validar documento
        document = await self.get_document_with_versions(db, document_id, user_id)
        if not document:
            raise ValueError(f"Documento '{document_id}' não encontrado")
        
        # Calcular próximo número de versão
        next_version = await self._get_next_version_number(db, document_id)
        
        # ⚠️ LEI 3: Criar NOVA versão (nunca sobrescrever)
        version = LegalDocumentVersion(
            document_id=document_id,
            version_number=next_version,
            created_by=VersionCreator(version_in.created_by),
            agent_name=version_in.agent_name
        )
        
        db.add(version)
        
        # Atualizar current_version_id do documento
        document.current_version_id = version.id
        
        await db.commit()
        await db.refresh(version)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.VERSION_CREATE,
            entity_type=EntityTypes.VERSION,
            entity_id=version.id,
            details={
                "document_id": str(document_id),
                "version_number": next_version,
                "created_by": version_in.created_by,
                "agent_name": version_in.agent_name
            }
        )
        
        return version
    
    async def get_version(
        self,
        db: AsyncSession,
        version_id: UUID,
        user_id: UUID
    ) -> Optional[LegalDocumentVersion]:
        """
        Busca versão por ID com assertions carregadas.
        """
        statement = (
            select(LegalDocumentVersion)
            .join(LegalDocument)
            .join(Case)
            .options(selectinload(LegalDocumentVersion.assertions))
            .options(selectinload(LegalDocumentVersion.renderings))
            .where(LegalDocumentVersion.id == version_id)
            .where(Case.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_document_versions(
        self,
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID
    ) -> List[LegalDocumentVersion]:
        """
        Lista todas as versões de um documento.
        
        Ordenadas por version_number decrescente (mais recente primeiro).
        """
        statement = (
            select(LegalDocumentVersion)
            .join(LegalDocument)
            .join(Case)
            .where(LegalDocumentVersion.document_id == document_id)
            .where(Case.user_id == user_id)
            .order_by(LegalDocumentVersion.version_number.desc())
        )
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def update_document_status(
        self,
        db: AsyncSession,
        user_id: UUID,
        document_id: UUID,
        new_status: DocumentStatus
    ) -> Optional[LegalDocument]:
        """
        Atualiza status do documento.
        
        Status válidos: draft → generated → revised → finalized
        """
        document = await self.get_document_with_versions(db, document_id, user_id)
        if not document:
            return None
        
        old_status = document.status
        document.status = new_status
        
        await db.commit()
        await db.refresh(document)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.DOCUMENT_STATUS_CHANGE,
            entity_type=EntityTypes.DOCUMENT,
            entity_id=document.id,
            details={
                "old_status": old_status.value,
                "new_status": new_status.value
            }
        )
        
        return document
    
    async def delete_version(
        self,
        db: AsyncSession,
        version_id: UUID,
        user_id: UUID
    ) -> None:
        """
        ⚠️ LEI 3: Versões são IMUTÁVEIS
        
        Este método SEMPRE lança exceção.
        Versões NÃO podem ser deletadas.
        """
        # ⚠️ LEI 3: Proibido deletar versões
        forbid_version_deletion()
    
    async def _get_case_for_user(
        self,
        db: AsyncSession,
        case_id: UUID,
        user_id: UUID
    ) -> Optional[Case]:
        """Busca caso validando ownership."""
        statement = (
            select(Case)
            .where(Case.id == case_id)
            .where(Case.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def _get_piece_type_for_area(
        self,
        db: AsyncSession,
        piece_type_slug: str,
        legal_area_id: UUID
    ) -> Optional[LegalPieceType]:
        """Busca tipo de peça validando área jurídica."""
        statement = (
            select(LegalPieceType)
            .where(LegalPieceType.slug == piece_type_slug)
            .where(LegalPieceType.legal_area_id == legal_area_id)
            .where(LegalPieceType.is_active == True)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def _get_next_version_number(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> int:
        """Calcula próximo número de versão."""
        statement = (
            select(func.coalesce(func.max(LegalDocumentVersion.version_number), 0))
            .where(LegalDocumentVersion.document_id == document_id)
        )
        result = await db.execute(statement)
        current_max = result.scalar_one()
        return current_max + 1


# Instância singleton
document_service = DocumentService()
