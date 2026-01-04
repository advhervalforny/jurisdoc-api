"""
Service de Auditoria.

Permite rastrear todas as ações no sistema.
Essencial para:
- Defesa jurídica do sistema
- Compliance
- Debug
- Análise de uso
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func, and_

from app.models.activity_log import ActivityLog, EntityTypes
from app.services.base import BaseService


class AuditService(BaseService[ActivityLog]):
    """
    Service para Auditoria e Rastreabilidade.
    
    Permite consultar o histórico de ações no sistema.
    """
    
    def __init__(self):
        super().__init__(ActivityLog)
    
    async def get_entity_history(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[ActivityLog]:
        """
        Lista histórico de ações para uma entidade específica.
        
        Exemplo: todas as ações em um documento específico.
        """
        statement = (
            select(ActivityLog)
            .where(ActivityLog.entity_type == entity_type)
            .where(ActivityLog.entity_id == entity_id)
            .order_by(ActivityLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def get_user_activity(
        self,
        db: AsyncSession,
        user_id: UUID,
        since: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ActivityLog]:
        """
        Lista atividades de um usuário.
        
        Opcionalmente filtra por período.
        """
        statement = (
            select(ActivityLog)
            .where(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
        )
        
        if since:
            statement = statement.where(ActivityLog.created_at >= since)
        
        statement = statement.offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def get_recent_activity(
        self,
        db: AsyncSession,
        hours: int = 24,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[ActivityLog]:
        """
        Lista atividades recentes.
        
        Útil para monitoramento.
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        statement = (
            select(ActivityLog)
            .where(ActivityLog.created_at >= since)
            .order_by(ActivityLog.created_at.desc())
        )
        
        if entity_type:
            statement = statement.where(ActivityLog.entity_type == entity_type)
        
        if action:
            statement = statement.where(ActivityLog.action == action)
        
        statement = statement.limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def get_document_audit_trail(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> dict:
        """
        Gera trilha de auditoria completa para um documento.
        
        Inclui:
        - Criação do documento
        - Criação de versões
        - Criação de assertions
        - Vinculação de fontes
        - Renderizações
        
        Usado para defesa jurídica: "Este texto foi gerado com base em..."
        """
        # Logs do documento
        doc_logs = await self.get_entity_history(
            db, EntityTypes.DOCUMENT, document_id
        )
        
        # Buscar versões do documento
        version_statement = (
            select(ActivityLog)
            .where(ActivityLog.entity_type == EntityTypes.VERSION)
            .where(ActivityLog.details['document_id'].astext == str(document_id))
            .order_by(ActivityLog.created_at.desc())
        )
        version_result = await db.execute(version_statement)
        version_logs = list(version_result.scalars().all())
        
        return {
            "document_id": str(document_id),
            "document_actions": [
                {
                    "action": log.action,
                    "timestamp": log.created_at.isoformat(),
                    "user_id": str(log.user_id) if log.user_id else None,
                    "details": log.details
                }
                for log in doc_logs
            ],
            "version_actions": [
                {
                    "action": log.action,
                    "timestamp": log.created_at.isoformat(),
                    "user_id": str(log.user_id) if log.user_id else None,
                    "details": log.details
                }
                for log in version_logs
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def count_actions_by_type(
        self,
        db: AsyncSession,
        since: Optional[datetime] = None
    ) -> dict:
        """
        Conta ações agrupadas por tipo.
        
        Útil para métricas e dashboards.
        """
        statement = (
            select(ActivityLog.action, func.count())
            .group_by(ActivityLog.action)
        )
        
        if since:
            statement = statement.where(ActivityLog.created_at >= since)
        
        result = await db.execute(statement)
        return dict(result.all())
    
    async def count_by_entity_type(
        self,
        db: AsyncSession,
        since: Optional[datetime] = None
    ) -> dict:
        """
        Conta ações agrupadas por tipo de entidade.
        """
        statement = (
            select(ActivityLog.entity_type, func.count())
            .group_by(ActivityLog.entity_type)
        )
        
        if since:
            statement = statement.where(ActivityLog.created_at >= since)
        
        result = await db.execute(statement)
        return dict(result.all())
    
    async def get_user_stats(
        self,
        db: AsyncSession,
        user_id: UUID,
        days: int = 30
    ) -> dict:
        """
        Estatísticas de uso de um usuário.
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Total de ações
        total_statement = (
            select(func.count())
            .select_from(ActivityLog)
            .where(ActivityLog.user_id == user_id)
            .where(ActivityLog.created_at >= since)
        )
        total_result = await db.execute(total_statement)
        total_actions = total_result.scalar_one()
        
        # Ações por tipo
        by_type_statement = (
            select(ActivityLog.action, func.count())
            .where(ActivityLog.user_id == user_id)
            .where(ActivityLog.created_at >= since)
            .group_by(ActivityLog.action)
        )
        by_type_result = await db.execute(by_type_statement)
        actions_by_type = dict(by_type_result.all())
        
        return {
            "user_id": str(user_id),
            "period_days": days,
            "total_actions": total_actions,
            "actions_by_type": actions_by_type
        }


# Instância singleton
audit_service = AuditService()
