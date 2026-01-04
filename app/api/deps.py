"""
Dependências de API.

Injeção de dependências para rotas:
- Sessão de banco de dados
- Usuário autenticado
- Validações comuns
"""
from typing import AsyncGenerator, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import async_session_maker
from app.core.security import verify_token


# Security scheme
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência que fornece sessão de banco de dados.
    
    Uso:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Dependência que extrai e valida o usuário do token JWT.
    
    Retorna o user_id (UUID) do usuário autenticado.
    
    Uso:
        @router.get("/me")
        async def get_me(user_id: UUID = Depends(get_current_user_id)):
            ...
    """
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        user_id_str = payload.get("sub")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: user_id não encontrado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return UUID(user_id_str)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user_id(
    request: Request
) -> Optional[UUID]:
    """
    Dependência que tenta extrair user_id, mas não falha se não houver token.
    
    Útil para endpoints que funcionam com ou sem autenticação.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        payload = verify_token(token)
        user_id_str = payload.get("sub")
        return UUID(user_id_str) if user_id_str else None
    except:
        return None


def get_client_info(request: Request) -> dict:
    """
    Extrai informações do cliente da requisição.
    
    Útil para logging de auditoria.
    """
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("User-Agent")
    }


class PaginationParams:
    """
    Parâmetros de paginação padrão.
    
    Uso:
        @router.get("/items")
        async def list_items(pagination: PaginationParams = Depends()):
            ...
    """
    def __init__(
        self,
        skip: int = 0,
        limit: int = 50
    ):
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="skip deve ser >= 0"
            )
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="limit deve estar entre 1 e 100"
            )
        
        self.skip = skip
        self.limit = limit
