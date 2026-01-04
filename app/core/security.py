"""
Security - Autenticação e Autorização
=====================================

Integração com Supabase Auth.
Validação de JWT tokens.
"""

from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings


# Security scheme
security = HTTPBearer()


class TokenPayload(BaseModel):
    """Payload do token JWT do Supabase."""
    sub: str  # user_id
    email: Optional[str] = None
    exp: int
    iat: int
    role: Optional[str] = "authenticated"


class CurrentUser(BaseModel):
    """Usuário atual extraído do token."""
    id: str
    email: Optional[str] = None
    role: str = "user"


def verify_token(token: str) -> TokenPayload:
    """
    Verifica e decodifica um token JWT do Supabase.
    
    Args:
        token: Token JWT
        
    Returns:
        TokenPayload com dados do usuário
        
    Raises:
        HTTPException: Se token inválido ou expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False}
        )
        
        # Verificar expiração
        exp = payload.get("exp", 0)
        if datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        
        return TokenPayload(**payload)
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Dependency para obter usuário atual do token JWT.
    
    Usage:
        @router.get("/me")
        async def get_me(user: CurrentUser = Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    return CurrentUser(
        id=payload.sub,
        email=payload.email,
        role=payload.role or "user"
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[CurrentUser]:
    """
    Dependency para obter usuário atual (opcional).
    Retorna None se não autenticado ao invés de erro.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    """
    Dependency factory para exigir role específica.
    
    Usage:
        @router.delete("/admin/users/{id}")
        async def delete_user(
            id: str,
            user: CurrentUser = Depends(require_role("admin"))
        ):
            ...
    """
    async def role_checker(
        user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Role necessária: {required_role}"
            )
        return user
    
    return role_checker
