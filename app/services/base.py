"""
Service base com utilitários comuns para todos os services.
"""
from typing import TypeVar, Generic, Type, Optional, List, Any
from uuid import UUID
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func

from app.models.base import BaseModel
from app.models.activity_log import ActivityLog, LogActions, EntityTypes

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseService(Generic[ModelType]):
    """
    Service base com operações CRUD genéricas.
    
    Todos os services específicos herdam desta classe.
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get_by_id(
        self, 
        db: AsyncSession, 
        id: UUID
    ) -> Optional[ModelType]:
        """Busca entidade por ID."""
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Lista todas as entidades com paginação."""
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def create(
        self,
        db: AsyncSession,
        obj_in: SQLModel
    ) -> ModelType:
        """Cria nova entidade."""
        db_obj = self.model.model_validate(obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(
        self,
        db: AsyncSession,
        id: UUID
    ) -> bool:
        """Deleta entidade por ID."""
        obj = await self.get_by_id(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False
    
    async def count(self, db: AsyncSession) -> int:
        """Conta total de entidades."""
        statement = select(func.count()).select_from(self.model)
        result = await db.execute(statement)
        return result.scalar_one()


async def log_activity(
    db: AsyncSession,
    user_id: Optional[UUID],
    action: str,
    entity_type: str,
    entity_id: UUID,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> ActivityLog:
    """
    Registra atividade no log de auditoria.
    
    Usado por todos os services para rastreabilidade.
    """
    log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log
