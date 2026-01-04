"""
Database Configuration - Supabase/PostgreSQL
=============================================
Configuração de conexão com banco de dados.
Usa SQLModel para ORM com suporte async.
"""

from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Criar engine async
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True
)

# Session factory - O NOME FOI CORRIGIDO AQUI
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db() -> None:
    """Inicializa o banco de dados e cria tabelas."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para injetar sessão do banco nas rotas."""
    # O USO TAMBÉM FOI CORRIGIDO AQUI
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def close_db() -> None:
    """Fecha conexões com o banco."""
    await engine.dispose()
