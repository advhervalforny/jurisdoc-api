"""
Fixtures para testes de integração.

Configuração do ambiente de teste:
- Cliente HTTP assíncrono
- Banco de dados de teste
- Usuário autenticado mockado
- Dados de seed para testes
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4, UUID
from datetime import datetime

from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.api.deps import get_db, get_current_user_id
from app.core.config import settings


# ==================== DATABASE SETUP ====================

# Usar SQLite em memória para testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


# ==================== FIXTURES ====================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Cria sessão de banco de dados para cada teste.
    
    Cria as tabelas no início e limpa no final.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture(scope="function")
def test_user_id() -> UUID:
    """ID do usuário de teste."""
    return uuid4()


@pytest.fixture(scope="function")
async def client(
    db_session: AsyncSession,
    test_user_id: UUID
) -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP para testes.
    
    Sobrescreve dependências:
    - get_db: usa sessão de teste
    - get_current_user_id: usa usuário de teste
    """
    
    async def override_get_db():
        yield db_session
    
    async def override_get_current_user_id():
        return test_user_id
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ==================== SEED DATA FIXTURES ====================

@pytest.fixture(scope="function")
async def seeded_db(db_session: AsyncSession) -> AsyncSession:
    """
    Banco de dados com dados iniciais.
    
    Cria:
    - Áreas jurídicas (civil, penal)
    - Tipos de peça
    - Fontes jurídicas básicas
    """
    from app.models.legal_domain import LegalArea, LegalPieceType
    from app.models.assertion import LegalSource, SourceType
    
    # Áreas jurídicas
    civil = LegalArea(
        id=uuid4(),
        slug="civil",
        name="Direito Civil",
        is_active=True
    )
    penal = LegalArea(
        id=uuid4(),
        slug="penal",
        name="Direito Penal",
        is_active=True
    )
    
    db_session.add(civil)
    db_session.add(penal)
    await db_session.flush()
    
    # Tipos de peça - Civil
    peticao_inicial = LegalPieceType(
        id=uuid4(),
        legal_area_id=civil.id,
        slug="peticao-inicial",
        name="Petição Inicial",
        legal_basis="Art. 319 CPC"
    )
    contestacao = LegalPieceType(
        id=uuid4(),
        legal_area_id=civil.id,
        slug="contestacao",
        name="Contestação",
        legal_basis="Art. 335 CPC"
    )
    
    db_session.add(peticao_inicial)
    db_session.add(contestacao)
    
    # Tipos de peça - Penal
    denuncia = LegalPieceType(
        id=uuid4(),
        legal_area_id=penal.id,
        slug="denuncia",
        name="Denúncia",
        legal_basis="Art. 41 CPP"
    )
    
    db_session.add(denuncia)
    
    # Fontes jurídicas básicas
    fonte_cpc_319 = LegalSource(
        id=uuid4(),
        source_type=SourceType.LEI,
        reference="CPC, art. 319",
        excerpt="A petição inicial indicará: I - o juízo a que é dirigida...",
        hierarchy_order=2
    )
    fonte_cf_5 = LegalSource(
        id=uuid4(),
        source_type=SourceType.CONSTITUICAO,
        reference="CF, art. 5º, XXXV",
        excerpt="A lei não excluirá da apreciação do Poder Judiciário lesão ou ameaça a direito",
        hierarchy_order=1
    )
    fonte_stj = LegalSource(
        id=uuid4(),
        source_type=SourceType.JURISPRUDENCIA,
        reference="STJ, REsp 1.234.567/SP",
        excerpt="O dano moral decorrente de negativação indevida é presumido (in re ipsa).",
        hierarchy_order=3
    )
    
    db_session.add(fonte_cpc_319)
    db_session.add(fonte_cf_5)
    db_session.add(fonte_stj)
    
    await db_session.commit()
    
    return db_session


@pytest.fixture(scope="function")
async def seeded_client(
    seeded_db: AsyncSession,
    test_user_id: UUID
) -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP com banco de dados seedado.
    """
    
    async def override_get_db():
        yield seeded_db
    
    async def override_get_current_user_id():
        return test_user_id
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ==================== HELPER FIXTURES ====================

@pytest.fixture
def case_payload() -> dict:
    """Payload para criação de caso."""
    return {
        "legal_area_slug": "civil",
        "title": "Negativação Indevida – João da Silva",
        "description": "Nome negativado sem prévia notificação"
    }


@pytest.fixture
def document_payload() -> dict:
    """Payload para criação de documento."""
    return {
        "piece_type_slug": "peticao-inicial"
    }


@pytest.fixture
def version_payload() -> dict:
    """Payload para criação de versão."""
    return {
        "created_by": "agent",
        "agent_name": "Agente Petição Inicial – Art. 319 CPC"
    }


@pytest.fixture
def assertion_payload() -> dict:
    """Payload para criação de assertion."""
    return {
        "text": "Nos termos do art. 319 do CPC, a petição inicial deve conter a exposição dos fatos e fundamentos jurídicos do pedido.",
        "type": "fundamento",
        "confidence_level": "alto"
    }


@pytest.fixture
def source_payload() -> dict:
    """Payload para criação de fonte."""
    return {
        "source_type": "lei",
        "reference": "CPC, art. 320",
        "excerpt": "A petição inicial será instruída com os documentos indispensáveis à propositura da ação."
    }
