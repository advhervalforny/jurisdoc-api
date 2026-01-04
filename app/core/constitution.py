"""
CONSTITUIÇÃO TÉCNICA DO SISTEMA
===============================
Versão: 1.0
Status: Obrigatória / Imutável

Este arquivo implementa as LEIS do sistema.
Qualquer código que viole estas leis está, por definição, ERRADO.

LEIS IMPLEMENTADAS:
- LEI 1: Documento Jurídico ≠ Texto
- LEI 2: Nenhuma Afirmação sem Fonte
- LEI 3: Versionamento é Obrigatório
- LEI 4: Texto Final é Derivado, Nunca Primário
- LEI 5: IA não escreve "texto final"
- LEI 6: Agente = Função Jurídica Única
- LEI 7: API Valida Juridicamente
- LEI 8: Frontend não decide nada
"""

from typing import List, Optional, Any
from datetime import datetime


class ConstitutionViolation(Exception):
    """
    Exceção lançada quando qualquer lei da Constituição é violada.
    
    Esta exceção NUNCA deve ser silenciada ou ignorada.
    Se esta exceção ocorre, há um BUG no código.
    """
    
    def __init__(self, law: str, message: str, details: Optional[dict] = None):
        self.law = law
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(f"[{law}] {message}")


class JuridicalValidationError(Exception):
    """
    Erro de validação jurídica (não técnica).
    
    Diferente de ConstitutionViolation, este erro indica
    que o usuário enviou dados juridicamente inválidos,
    não que o código está errado.
    """
    
    def __init__(self, error_type: str, message: str, entity_id: Optional[str] = None):
        self.error_type = error_type
        self.message = message
        self.entity_id = entity_id
        super().__init__(f"JURIDICAL_VALIDATION_ERROR: {message}")


# =============================================================================
# LEI 1: Documento Jurídico ≠ Texto
# =============================================================================

def forbid_text_as_document(payload: dict) -> None:
    """
    LEI 1: É proibido armazenar peças como texto único.
    
    Documento jurídico é composto por:
    - Versões
    - Afirmações jurídicas
    - Fontes explícitas
    
    Raises:
        ConstitutionViolation: Se payload contiver texto como documento
    """
    forbidden_keys = ["text", "content", "body", "documento", "texto", "conteudo"]
    
    for key in forbidden_keys:
        if key in payload and isinstance(payload[key], str) and len(payload[key]) > 100:
            raise ConstitutionViolation(
                law="LEI_1",
                message="Documento jurídico não pode ser armazenado como texto único",
                details={
                    "forbidden_key": key,
                    "payload_keys": list(payload.keys()),
                    "hint": "Use assertions estruturadas com fontes"
                }
            )


# =============================================================================
# LEI 2: Nenhuma Afirmação sem Fonte
# =============================================================================

def require_source_for_assertion(
    assertion_id: str,
    sources: List[Any],
    allow_low_confidence: bool = True
) -> None:
    """
    LEI 2: Uma afirmação jurídica relevante só é válida se possuir
    ao menos uma fonte explícita.
    
    Args:
        assertion_id: ID da afirmação sendo validada
        sources: Lista de fontes vinculadas
        allow_low_confidence: Se True, permite afirmações sem fonte
                             mas marca como confidence=baixo
    
    Raises:
        JuridicalValidationError: Se não houver fontes e low_confidence não permitido
    """
    if not sources:
        if not allow_low_confidence:
            raise JuridicalValidationError(
                error_type="ASSERTION_WITHOUT_SOURCE",
                message="Afirmação jurídica sem fonte vinculada",
                entity_id=assertion_id
            )
        # Se allow_low_confidence, retorna sem erro mas caller deve marcar confidence=baixo
        return
    
    # Validar que as fontes são válidas
    for source in sources:
        if not hasattr(source, 'source_type') or not source.source_type:
            raise JuridicalValidationError(
                error_type="INVALID_SOURCE",
                message="Fonte sem tipo definido",
                entity_id=assertion_id
            )


# =============================================================================
# LEI 3: Versionamento é Obrigatório
# =============================================================================

def require_new_version_for_change(
    document_id: str,
    current_version: int,
    operation: str
) -> int:
    """
    LEI 3: Toda geração/modificação cria nova versão.
    É proibido sobrescrever conteúdo jurídico.
    
    Args:
        document_id: ID do documento
        current_version: Versão atual
        operation: Tipo de operação sendo realizada
    
    Returns:
        int: Número da nova versão
    
    Raises:
        ConstitutionViolation: Se tentativa de edição destrutiva
    """
    forbidden_operations = ["update", "edit", "modify", "patch", "replace"]
    
    for forbidden in forbidden_operations:
        if forbidden in operation.lower():
            raise ConstitutionViolation(
                law="LEI_3",
                message=f"Operação '{operation}' viola versionamento obrigatório",
                details={
                    "document_id": document_id,
                    "current_version": current_version,
                    "hint": "Use 'create_new_version' ao invés de modificar"
                }
            )
    
    return current_version + 1


def forbid_version_deletion(version_id: str) -> None:
    """
    LEI 3 (complemento): Histórico é imutável.
    
    Raises:
        ConstitutionViolation: Sempre (deleção de versão é proibida)
    """
    raise ConstitutionViolation(
        law="LEI_3",
        message="Deleção de versão é proibida",
        details={
            "version_id": version_id,
            "hint": "Versões são imutáveis. Crie nova versão se necessário."
        }
    )


# =============================================================================
# LEI 4: Texto Final é Derivado, Nunca Primário
# =============================================================================

def forbid_text_as_primary_input(payload: dict) -> None:
    """
    LEI 4: Texto jurídico não pode ser input primário.
    O texto exibido ao usuário é renderização.
    A verdade do sistema está nas afirmações estruturadas.
    
    Raises:
        ConstitutionViolation: Se texto for enviado como entrada principal
    """
    if "generated_text" in payload or "final_text" in payload or "rendered_text" in payload:
        if "assertions" not in payload:
            raise ConstitutionViolation(
                law="LEI_4",
                message="Texto não pode ser entrada primária sem assertions",
                details={
                    "payload_keys": list(payload.keys()),
                    "hint": "Texto é derivado de assertions, não o contrário"
                }
            )


def validate_rendering_has_sources(assertions: List[Any]) -> None:
    """
    LEI 4 (complemento): Só renderiza se todas assertions tiverem fonte.
    
    Raises:
        JuridicalValidationError: Se alguma assertion não tiver fonte
    """
    for assertion in assertions:
        if not hasattr(assertion, 'sources') or not assertion.sources:
            raise JuridicalValidationError(
                error_type="RENDERING_WITHOUT_SOURCES",
                message="Impossível renderizar: assertion sem fonte",
                entity_id=str(assertion.id) if hasattr(assertion, 'id') else None
            )


# =============================================================================
# LEI 5: IA não escreve "texto final"
# =============================================================================

def validate_ai_output_structure(ai_response: dict) -> None:
    """
    LEI 5: Modelos de linguagem nunca produzem diretamente petições prontas.
    
    Output válido de IA:
    - assertions (afirmações estruturadas)
    - classifications (classificações)
    - suggested_sources (sugestões de fonte)
    - confidence_levels (níveis de confiança)
    
    Raises:
        ConstitutionViolation: Se IA retornar texto final diretamente
    """
    forbidden_keys = [
        "final_text", "peticao", "petition", "document_text",
        "complete_document", "generated_document"
    ]
    
    for key in forbidden_keys:
        if key in ai_response:
            raise ConstitutionViolation(
                law="LEI_5",
                message="IA não pode produzir texto final diretamente",
                details={
                    "forbidden_key": key,
                    "hint": "IA deve retornar assertions + sources + confidence"
                }
            )
    
    # Validar que retornou estrutura esperada
    required_keys = ["assertions"]
    missing = [k for k in required_keys if k not in ai_response]
    
    if missing:
        raise ConstitutionViolation(
            law="LEI_5",
            message=f"Output de IA faltando estrutura obrigatória: {missing}",
            details={
                "response_keys": list(ai_response.keys()),
                "required_keys": required_keys
            }
        )


# =============================================================================
# LEI 6: Agente = Função Jurídica Única
# =============================================================================

VALID_AGENTS = {
    "peticao-inicial-civil": {
        "legal_basis": "Art. 319 CPC",
        "scope": "Petição inicial cível",
        "legal_area": "civil"
    },
    "contestacao-civil": {
        "legal_basis": "Art. 335 CPC",
        "scope": "Contestação cível",
        "legal_area": "civil"
    },
    # Adicionar mais agentes conforme implementados
}


def validate_agent_scope(agent_name: str, requested_piece_type: str) -> None:
    """
    LEI 6: Um agente possui escopo fechado. É proibido agente "genérico".
    
    Raises:
        JuridicalValidationError: Se agente não existir ou for usado fora do escopo
    """
    if agent_name not in VALID_AGENTS:
        raise JuridicalValidationError(
            error_type="INVALID_AGENT",
            message=f"Agente '{agent_name}' não existe ou não é válido",
            entity_id=agent_name
        )
    
    agent_config = VALID_AGENTS[agent_name]
    
    # Validar que o tipo de peça é compatível com o agente
    if requested_piece_type and agent_config["scope"].lower() not in requested_piece_type.lower():
        raise JuridicalValidationError(
            error_type="AGENT_SCOPE_MISMATCH",
            message=f"Agente '{agent_name}' não pode gerar '{requested_piece_type}'",
            entity_id=agent_name
        )


# =============================================================================
# LEI 7: API Valida Juridicamente
# =============================================================================

def validate_juridical_payload(payload: dict, operation: str) -> None:
    """
    LEI 7: API valida juridicamente, não só tecnicamente.
    Payload juridicamente inválido → Erro de domínio, não erro técnico.
    
    Esta função deve ser chamada em TODAS as rotas que manipulam
    conteúdo jurídico.
    """
    # Aplicar todas as validações relevantes
    forbid_text_as_document(payload)
    forbid_text_as_primary_input(payload)
    
    # Validações específicas por operação
    if operation == "create_assertion":
        if "type" not in payload:
            raise JuridicalValidationError(
                error_type="MISSING_ASSERTION_TYPE",
                message="Tipo de afirmação é obrigatório"
            )
        
        valid_types = ["fato", "tese", "fundamento", "pedido"]
        if payload.get("type") not in valid_types:
            raise JuridicalValidationError(
                error_type="INVALID_ASSERTION_TYPE",
                message=f"Tipo de afirmação inválido. Válidos: {valid_types}"
            )


# =============================================================================
# LEI 8: Frontend não decide nada
# =============================================================================

def validate_backend_sovereignty(payload: dict) -> None:
    """
    LEI 8: Frontend nunca é fonte de verdade.
    Backend é soberano em regras jurídicas.
    
    Esta função rejeita tentativas do frontend de:
    - Definir status jurídico
    - Marcar como válido/aprovado
    - Ignorar validações
    """
    forbidden_frontend_decisions = [
        "is_valid",
        "is_approved", 
        "skip_validation",
        "force_save",
        "bypass_checks",
        "juridically_valid"
    ]
    
    for key in forbidden_frontend_decisions:
        if key in payload:
            raise ConstitutionViolation(
                law="LEI_8",
                message=f"Frontend não pode definir '{key}'",
                details={
                    "forbidden_key": key,
                    "hint": "Validação jurídica é responsabilidade exclusiva do backend"
                }
            )


# =============================================================================
# VALIDAÇÃO HIERARQUIA NORMATIVA
# =============================================================================

HIERARCHY_ORDER = {
    "constituicao": 1,
    "lei": 2,
    "jurisprudencia": 3,
    "doutrina": 4,
    "argumentacao": 5
}


def validate_normative_hierarchy(sources: List[Any]) -> None:
    """
    Princípio 2.2: Hierarquia Normativa Obrigatória.
    
    Toda argumentação deve respeitar a ordem:
    1. Constituição
    2. Lei
    3. Jurisprudência
    4. Doutrina
    5. Argumentação lógica
    
    É proibido inverter essa hierarquia.
    """
    if len(sources) < 2:
        return  # Não há hierarquia a validar com menos de 2 fontes
    
    for i in range(len(sources) - 1):
        current_type = sources[i].source_type.lower()
        next_type = sources[i + 1].source_type.lower()
        
        current_order = HIERARCHY_ORDER.get(current_type, 99)
        next_order = HIERARCHY_ORDER.get(next_type, 99)
        
        # Se a próxima fonte tem ordem MENOR (mais importante), está invertido
        if next_order < current_order:
            raise JuridicalValidationError(
                error_type="HIERARCHY_VIOLATION",
                message=f"Hierarquia normativa invertida: {next_type} não pode vir depois de {current_type}",
                entity_id=None
            )


# =============================================================================
# CHECKLIST DE CONFORMIDADE
# =============================================================================

def full_constitution_check(
    payload: dict,
    operation: str,
    assertions: List[Any] = None,
    sources: List[Any] = None,
    ai_response: dict = None
) -> bool:
    """
    Executa checklist completo de conformidade com a Constituição.
    
    Uma feature só pode ser considerada pronta se:
    - Respeita versionamento
    - Respeita hierarquia normativa
    - É auditável
    - Não depende de boa vontade humana para ser segura
    
    Returns:
        bool: True se todas as validações passaram
    
    Raises:
        ConstitutionViolation ou JuridicalValidationError se algo falhar
    """
    # LEI 1, 4, 8
    validate_juridical_payload(payload, operation)
    validate_backend_sovereignty(payload)
    
    # LEI 2
    if assertions and sources is not None:
        for assertion in assertions:
            assertion_sources = [s for s in (sources or []) 
                               if hasattr(s, 'assertion_id') and s.assertion_id == assertion.id]
            require_source_for_assertion(str(assertion.id), assertion_sources)
    
    # LEI 5
    if ai_response:
        validate_ai_output_structure(ai_response)
    
    # Hierarquia normativa
    if sources:
        validate_normative_hierarchy(sources)
    
    return True
