"""
Configurações do Sistema JurisDoc
=================================

Variáveis de ambiente e configurações globais.
"""

from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Ambiente
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # Database (Supabase Postgres)
    DATABASE_URL: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # CORS - Aceita string (separada por vírgula) ou lista
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS de string ou lista."""
        if isinstance(v, str):
            # String separada por vírgula
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # JWT (Supabase Auth)
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Constituição Técnica - Configurações Imutáveis
    # ⚠️ ATENÇÃO: Estas configurações NÃO devem ser alteradas
    CONSTITUTION_VERSION: str = "1.0"
    REQUIRE_SOURCE_FOR_ASSERTION: bool = True  # LEI 2 - Nunca False
    REQUIRE_VERSIONING: bool = True            # LEI 3 - Nunca False
    ALLOW_TEXT_AS_PRIMARY: bool = False        # LEI 4 - Nunca True
    ALLOW_DESTRUCTIVE_EDIT: bool = False       # Nunca True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retorna settings cacheadas."""
    return Settings()


settings = get_settings()


# Validação de Constituição na inicialização
def validate_constitution():
    """
    Valida que as configurações da Constituição estão corretas.
    Lança exceção se alguma regra foi violada.
    """
    errors = []
    
    if not settings.REQUIRE_SOURCE_FOR_ASSERTION:
        errors.append("VIOLAÇÃO LEI 2: REQUIRE_SOURCE_FOR_ASSERTION não pode ser False")
    
    if not settings.REQUIRE_VERSIONING:
        errors.append("VIOLAÇÃO LEI 3: REQUIRE_VERSIONING não pode ser False")
    
    if settings.ALLOW_TEXT_AS_PRIMARY:
        errors.append("VIOLAÇÃO LEI 4: ALLOW_TEXT_AS_PRIMARY não pode ser True")
    
    if settings.ALLOW_DESTRUCTIVE_EDIT:
        errors.append("VIOLAÇÃO: ALLOW_DESTRUCTIVE_EDIT não pode ser True")
    
    if errors:
        raise ValueError(
            "⚠️ VIOLAÇÕES DA CONSTITUIÇÃO TÉCNICA DETECTADAS:\n" + 
            "\n".join(f"  - {e}" for e in errors)
        )
    
    return True


# Executar validação ao importar
validate_constitution()
