"""
Agentes Jurídicos Especializados.

⚠️ LEI 6: Agente = Função Jurídica Única

Agentes disponíveis:
- peticao-inicial-civil: Petição Inicial Cível (Art. 319 CPC)
- contestacao-civil: Contestação Cível (Art. 335 CPC)
- civil-generic: Agente genérico (fallback)
"""
from app.cognitive.agents.base import (
    BaseAgent,
    GeneratedAssertion,
    NormalizedInput,
    get_agent,
    list_agents,
    register_agent
)

# Importar agentes para registro automático
from app.cognitive.agents.civil_peticao_inicial import PeticaoInicialCivilAgent
from app.cognitive.agents.civil_contestacao import ContestacaoCivilAgent
from app.cognitive.agents.civil_generic import CivilGenericAgent


__all__ = [
    "BaseAgent",
    "GeneratedAssertion",
    "NormalizedInput",
    "get_agent",
    "list_agents",
    "register_agent",
    "PeticaoInicialCivilAgent",
    "ContestacaoCivilAgent",
    "CivilGenericAgent",
]
