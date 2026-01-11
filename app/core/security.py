"""
Security - Autenticação e Autorização
=====================================
Integração com Supabase Auth.
Validação de JWT tokens com suporte a ES256 (JWKS).
"""
from typing import Optional
from datetime import datetime
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
from jose.exceptions import JWTError, JWKError
from pydantic import BaseModel
from functools import lru_cache
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class TokenPayload(BaseModel):
    """Payload do token JWT do Supabase."""
    sub: str  # user_id
    email: Optional[str] = None
    exp: int
    iat: int
    role: Optional[str] = "authenticated"
    aud: Optional[str] = None


class CurrentUser(BaseModel):
    """Usuário atual extraído do token."""
    id: str
    email: Optional[str] = None
    role: str = "user"


# Cache das chaves JWKS (atualiza a cada 1 hora)
_jwks_cache: dict = {}
_jwks_cache_time: float = 0
JWKS_CACHE_TTL = 3600  # 1 hora


async def get_jwks() -> dict:
    """
    Busca as chaves JWKS do Supabase.
    Usa cache para evitar requests a cada validação.
    """
    global _jwks_cache, _jwks_cache_time
    
    current_time = datetime.utcnow().timestamp()
    
    # Retorna cache se ainda válido
    if _jwks_cache and (current_time - _jwks_cache_time) < JWKS_CACHE_TTL:
        return _jwks_cache
    
    # Busca novas chaves
    jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=10.0)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = current_time
            logger.info(f"JWKS atualizado de {jwks_url}")
            return _jwks_cache
    except Exception as e:
        logger.error(f"Erro ao buscar JWKS: {e}")
        # Se tiver cache antigo, usa ele
        if _jwks_cache:
            logger.warning("Usando JWKS em cache (expirado)")
            return _jwks_cache
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível validar autenticação"
        )


def get_signing_key(token: str, jwks: dict) -> str:
    """
    Extrai a chave de assinatura correta do JWKS baseado no kid do token.
    """
    try:
        # Decodifica header sem verificar (apenas para pegar o kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        alg = unverified_header.get("alg")
        
        logger.debug(f"Token header - kid: {kid}, alg: {alg}")
        
        # Busca a chave correspondente
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        
        # Se não encontrou pelo kid, tenta a primeira chave compatível
        for key in jwks.get("keys", []):
            if key.get("alg") == alg or key.get("kty") == "EC":
                logger.warning(f"Usando chave por fallback (alg match)")
                return key
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de assinatura não encontrada"
        )
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token mal formado: {str(e)}"
        )


async def verify_token(token: str) -> TokenPayload:
    """
    Verifica e decodifica um token JWT do Supabase.
    Suporta tanto HS256 (legacy) quanto ES256 (novo).
    
    Args:
        token: Token JWT
        
    Returns:
        TokenPayload com dados do usuário
        
    Raises:
        HTTPException: Se token inválido ou expirado
    """
    try:
        # Primeiro, verifica qual algoritmo o token usa
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "HS256")
        
        logger.debug(f"Verificando token com algoritmo: {alg}")
        
        if alg == "HS256":
            # Token legacy - usa JWT_SECRET
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
        elif alg == "ES256":
            # Token novo - usa JWKS
            jwks = await get_jwks()
            signing_key = get_signing_key(token, jwks)
            
            # Converte JWK para formato PEM para jose
            from jose.backends import ECKey
            key = jwk.construct(signing_key)
            
            payload = jwt.decode(
                token,
                key,
                algorithms=["ES256"],
                options={"verify_aud": False}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Algoritmo não suportado: {alg}"
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
        logger.error(f"Erro JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro inesperado na validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro na validação do token: {str(e)}"
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
    payload = await verify_token(token)
    
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
