"""
Agentes Jurídicos Especializados.

⚠️ LEI 6: Agente = Função Jurídica Única

Cada agente possui:
- Escopo jurídico fechado
- Prompt próprio
- Restrições negativas explícitas

⚠️ LEI 5: IA não escreve texto final
Os agentes produzem assertions estruturadas, não texto.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

from app.models.assertion import LegalSource


@dataclass
class GeneratedAssertion:
    """Assertion gerada pelo agente."""
    text: str
    assertion_type: str  # fato | tese | fundamento | pedido
    confidence_level: str  # alto | medio | baixo
    suggested_sources: List[str]
    position: int


@dataclass
class NormalizedInput:
    """Input normalizado para o agente."""
    fatos: List[str]
    pedidos: List[str]
    possiveis_fundamentos: List[str]
    classe_procedimental: str
    partes: Dict[str, str]
    valor_causa: Optional[float]


class BaseAgent(ABC):
    """
    Agente jurídico base.
    
    ⚠️ LEI 6: Cada agente tem função única.
    Subclasses implementam generate() para sua especialidade.
    """
    
    # Identificador do agente
    agent_id: str = "base"
    
    # Nome legível
    name: str = "Agente Base"
    
    # Base legal principal
    legal_basis: str = ""
    
    # Área do direito
    legal_area: str = "civil"
    
    # Tipo de peça
    piece_type: str = ""
    
    @abstractmethod
    async def generate(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource]
    ) -> List[GeneratedAssertion]:
        """
        Gera assertions para a peça jurídica.
        
        ⚠️ LEI 5: NÃO gera texto final, apenas assertions.
        
        Args:
            input_data: Dados normalizados do caso
            sources: Fontes disponíveis (mapa ref -> source)
        
        Returns:
            Lista de assertions estruturadas
        """
        pass
    
    def _get_system_prompt(self) -> str:
        """
        Retorna system prompt do agente.
        
        ⚠️ Inclui restrições negativas obrigatórias.
        """
        return f"""You are a specialized legal agent for Brazilian law.

IDENTITY:
- Agent: {self.name}
- Legal Basis: {self.legal_basis}
- Area: {self.legal_area}
- Piece Type: {self.piece_type}

CRITICAL RESTRICTIONS (NEVER VIOLATE):
1. DO NOT invent facts not provided in input
2. DO NOT cite sources not available in the provided sources map
3. DO NOT generate final text - generate ONLY structured assertions
4. DO NOT provide legal advice or opinions
5. DO NOT assume facts not explicitly stated
6. ALWAYS respect the normative hierarchy: Constitution > Law > Case Law > Doctrine

OUTPUT FORMAT:
Generate assertions as structured objects with:
- text: The assertion content
- type: One of [fato, tese, fundamento, pedido]
- confidence: One of [alto, medio, baixo]
- sources: List of source references that support this assertion

CONSERVATIVE POSTURE:
When in doubt, DO NOT assert. Silence is preferable to legal error.
Mark uncertain assertions with confidence="baixo".
"""
    
    def _build_generation_prompt(
        self,
        input_data: NormalizedInput,
        available_sources: List[str]
    ) -> str:
        """Constrói prompt de geração."""
        return f"""
CASE DATA:
- Facts: {input_data.fatos}
- Requests: {input_data.pedidos}
- Procedural Class: {input_data.classe_procedimental}
- Parties: {input_data.partes}
- Claim Value: {input_data.valor_causa}

AVAILABLE SOURCES (use ONLY these):
{available_sources}

Generate structured assertions for a {self.piece_type} following the legal basis {self.legal_basis}.
Remember: Output assertions as JSON objects, NOT free text.
"""


# Registry de agentes
_AGENTS: Dict[str, type] = {}


def register_agent(agent_class: type) -> type:
    """Decorator para registrar agente."""
    _AGENTS[agent_class.agent_id] = agent_class
    return agent_class


def get_agent(agent_type: str) -> BaseAgent:
    """Retorna instância do agente."""
    if agent_type not in _AGENTS:
        # Fallback para agente genérico
        from app.cognitive.agents.civil_generic import CivilGenericAgent
        return CivilGenericAgent()
    
    return _AGENTS[agent_type]()


def list_agents() -> List[Dict[str, str]]:
    """Lista agentes disponíveis."""
    return [
        {
            "id": agent_class.agent_id,
            "name": agent_class.name,
            "legal_basis": agent_class.legal_basis,
            "legal_area": agent_class.legal_area
        }
        for agent_class in _AGENTS.values()
    ]
