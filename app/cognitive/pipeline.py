"""
Pipeline Cognitivo - Sistema Jurídico Inteligente AI-First.

⚠️ LEIS APLICÁVEIS:
- LEI 5: IA não escreve texto final (produz assertions)
- LEI 6: Agente = Função jurídica única
- LEI 2: Nenhuma afirmação sem fonte

Este módulo orquestra a geração de peças jurídicas.
"""
from typing import AsyncGenerator, Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.assertion import LegalSource, SourceType
from app.services.document_service import DocumentService
from app.services.assertion_service import AssertionService
from app.services.source_service import SourceService
from app.services.audit_service import AuditService


class PipelineEventType(str, Enum):
    """Tipos de eventos do pipeline."""
    STARTED = "started"
    VERSION_CREATED = "version_created"
    NORMALIZATION_COMPLETE = "normalization_complete"
    RESEARCH_STARTED = "research_started"
    SOURCE_FOUND = "source_found"
    RESEARCH_COMPLETE = "research_complete"
    GENERATION_STARTED = "generation_started"
    ASSERTION_GENERATED = "assertion_generated"
    ASSERTION_VALIDATED = "assertion_validated"
    VALIDATION_COMPLETE = "validation_complete"
    PERSISTENCE_COMPLETE = "persistence_complete"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class PipelineEvent:
    """Evento do pipeline para streaming SSE."""
    type: PipelineEventType
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_sse(self) -> str:
        """Converte para formato SSE."""
        import json
        return f"event: {self.type.value}\ndata: {json.dumps(self.data)}\n\n"


@dataclass
class GenerationInput:
    """Input estruturado para geração."""
    document_id: UUID
    agent_type: str
    fatos_principais: List[str]
    pedidos: List[str]
    valor_causa: Optional[float] = None
    partes: Optional[Dict[str, str]] = None
    contexto_adicional: Optional[str] = None


@dataclass
class NormalizedInput:
    """Input normalizado para o agente."""
    fatos: List[str]
    pedidos: List[str]
    possiveis_fundamentos: List[str]
    classe_procedimental: str
    partes: Dict[str, str]
    valor_causa: Optional[float]


@dataclass 
class GeneratedAssertion:
    """Assertion gerada pelo agente."""
    text: str
    assertion_type: str
    confidence_level: str
    suggested_sources: List[str]
    position: int


@dataclass
class ValidatedAssertion:
    """Assertion validada com fontes vinculadas."""
    assertion: GeneratedAssertion
    sources: List[LegalSource]
    is_valid: bool
    validation_notes: Optional[str] = None


class CognitivePipeline:
    """
    Pipeline de geração cognitiva.
    
    Fluxo:
    1. Criar versão do documento
    2. Normalizar inputs
    3. Pesquisar fontes (RAG)
    4. Gerar assertions (agente)
    5. Validar juridicamente
    6. Persistir
    
    ⚠️ LEI 5: IA produz assertions, não texto final.
    """
    
    def __init__(
        self,
        db: AsyncSession,
        document_service: DocumentService,
        assertion_service: AssertionService,
        source_service: SourceService,
        audit_service: AuditService
    ):
        self.db = db
        self.document_service = document_service
        self.assertion_service = assertion_service
        self.source_service = source_service
        self.audit_service = audit_service
    
    async def run(
        self,
        input_data: GenerationInput,
        user_id: UUID
    ) -> AsyncGenerator[PipelineEvent, None]:
        """
        Executa o pipeline completo com streaming.
        
        Yields eventos SSE para o frontend.
        """
        try:
            # 1. Evento inicial
            yield PipelineEvent(
                type=PipelineEventType.STARTED,
                data={
                    "document_id": str(input_data.document_id),
                    "agent_type": input_data.agent_type
                }
            )
            
            # 2. Criar versão
            version = await self.document_service.create_version(
                self.db,
                document_id=input_data.document_id,
                created_by="agent",
                agent_name=input_data.agent_type,
                user_id=user_id
            )
            
            yield PipelineEvent(
                type=PipelineEventType.VERSION_CREATED,
                data={
                    "version_id": str(version.id),
                    "version_number": version.version_number
                }
            )
            
            # 3. Normalizar inputs
            normalized = await self._normalize_inputs(input_data)
            
            yield PipelineEvent(
                type=PipelineEventType.NORMALIZATION_COMPLETE,
                data={
                    "fatos_count": len(normalized.fatos),
                    "pedidos_count": len(normalized.pedidos),
                    "possiveis_fundamentos": normalized.possiveis_fundamentos
                }
            )
            
            # 4. Pesquisar fontes
            yield PipelineEvent(
                type=PipelineEventType.RESEARCH_STARTED,
                data={"fundamentos_buscados": normalized.possiveis_fundamentos}
            )
            
            sources_map = await self._research_sources(normalized)
            
            for ref, source in sources_map.items():
                yield PipelineEvent(
                    type=PipelineEventType.SOURCE_FOUND,
                    data={
                        "reference": ref,
                        "type": source.source_type.value if hasattr(source.source_type, 'value') else str(source.source_type),
                        "excerpt": source.excerpt[:100] + "..." if len(source.excerpt) > 100 else source.excerpt
                    }
                )
            
            yield PipelineEvent(
                type=PipelineEventType.RESEARCH_COMPLETE,
                data={"sources_found": len(sources_map)}
            )
            
            # 5. Gerar assertions
            yield PipelineEvent(
                type=PipelineEventType.GENERATION_STARTED,
                data={"agent": input_data.agent_type}
            )
            
            # Importar agente dinamicamente
            agent = await self._get_agent(input_data.agent_type)
            generated_assertions = await agent.generate(normalized, sources_map)
            
            for assertion in generated_assertions:
                yield PipelineEvent(
                    type=PipelineEventType.ASSERTION_GENERATED,
                    data={
                        "text": assertion.text[:100] + "..." if len(assertion.text) > 100 else assertion.text,
                        "type": assertion.assertion_type,
                        "confidence": assertion.confidence_level,
                        "position": assertion.position
                    }
                )
            
            # 6. Validar assertions
            validated_assertions = await self._validate_assertions(
                generated_assertions,
                sources_map
            )
            
            for va in validated_assertions:
                yield PipelineEvent(
                    type=PipelineEventType.ASSERTION_VALIDATED,
                    data={
                        "position": va.assertion.position,
                        "is_valid": va.is_valid,
                        "sources_count": len(va.sources),
                        "notes": va.validation_notes
                    }
                )
            
            yield PipelineEvent(
                type=PipelineEventType.VALIDATION_COMPLETE,
                data={
                    "total": len(validated_assertions),
                    "valid": sum(1 for va in validated_assertions if va.is_valid)
                }
            )
            
            # 7. Persistir
            await self._persist_assertions(
                version.id,
                validated_assertions,
                user_id
            )
            
            yield PipelineEvent(
                type=PipelineEventType.PERSISTENCE_COMPLETE,
                data={"version_id": str(version.id)}
            )
            
            # 8. Concluir
            yield PipelineEvent(
                type=PipelineEventType.COMPLETED,
                data={
                    "version_id": str(version.id),
                    "assertions_created": len(validated_assertions),
                    "valid_assertions": sum(1 for va in validated_assertions if va.is_valid)
                }
            )
            
        except Exception as e:
            yield PipelineEvent(
                type=PipelineEventType.ERROR,
                data={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise
    
    async def _normalize_inputs(
        self,
        input_data: GenerationInput
    ) -> NormalizedInput:
        """
        Normaliza inputs do usuário para estrutura jurídica.
        
        Não gera conteúdo, apenas estrutura.
        """
        # Determinar possíveis fundamentos com base no tipo de ação
        possiveis_fundamentos = self._infer_fundamentos(
            input_data.agent_type,
            input_data.fatos_principais
        )
        
        # Determinar classe procedimental
        classe = self._infer_classe_procedimental(input_data.agent_type)
        
        return NormalizedInput(
            fatos=input_data.fatos_principais,
            pedidos=input_data.pedidos,
            possiveis_fundamentos=possiveis_fundamentos,
            classe_procedimental=classe,
            partes=input_data.partes or {},
            valor_causa=input_data.valor_causa
        )
    
    def _infer_fundamentos(
        self,
        agent_type: str,
        fatos: List[str]
    ) -> List[str]:
        """Infere possíveis fundamentos jurídicos."""
        # Mapeamento básico por tipo de agente
        fundamentos_map = {
            "peticao-inicial-civil": [
                "CPC, art. 319",
                "CPC, art. 320",
                "CF, art. 5º, XXXV"
            ],
            "peticao-inicial-indenizacao": [
                "CPC, art. 319",
                "CC, art. 186",
                "CC, art. 927",
                "CDC, art. 6º",
                "CDC, art. 14"
            ],
            "peticao-inicial-cobranca": [
                "CPC, art. 319",
                "CC, art. 389",
                "CC, art. 395"
            ],
            "contestacao-civil": [
                "CPC, art. 335",
                "CPC, art. 336",
                "CPC, art. 337"
            ],
            "denuncia-penal": [
                "CPP, art. 41",
                "CPP, art. 43"
            ]
        }
        
        base = fundamentos_map.get(agent_type, ["CPC, art. 319"])
        
        # Analisar fatos para adicionar fundamentos específicos
        fatos_lower = " ".join(fatos).lower()
        
        if "negativação" in fatos_lower or "serasa" in fatos_lower or "spc" in fatos_lower:
            base.extend(["CDC, art. 43", "Súmula 385 STJ"])
        
        if "consumidor" in fatos_lower or "produto" in fatos_lower:
            base.extend(["CDC, art. 12", "CDC, art. 14"])
        
        if "dano moral" in fatos_lower:
            base.append("CC, art. 186")
        
        if "contrato" in fatos_lower:
            base.extend(["CC, art. 421", "CC, art. 422"])
        
        return list(set(base))  # Remove duplicatas
    
    def _infer_classe_procedimental(self, agent_type: str) -> str:
        """Infere classe procedimental."""
        if "inicial" in agent_type:
            return "procedimento_comum"
        elif "contestacao" in agent_type:
            return "procedimento_comum"
        elif "denuncia" in agent_type:
            return "acao_penal"
        else:
            return "procedimento_comum"
    
    async def _research_sources(
        self,
        normalized: NormalizedInput
    ) -> Dict[str, LegalSource]:
        """
        Pesquisa fontes jurídicas via RAG.
        
        ⚠️ Aqui mora o maior risco de alucinação.
        Só usamos fontes do banco de dados.
        """
        sources_map = {}
        
        for ref in normalized.possiveis_fundamentos:
            # Buscar fonte existente
            source = await self.source_service.find_by_reference(self.db, ref)
            
            if source:
                sources_map[ref] = source
            else:
                # Tentar buscar por texto similar
                similar = await self.source_service.search(
                    self.db,
                    query=ref,
                    limit=1
                )
                if similar:
                    sources_map[ref] = similar[0]
        
        return sources_map
    
    async def _get_agent(self, agent_type: str):
        """Carrega agente especializado."""
        from app.cognitive.agents import get_agent
        return get_agent(agent_type)
    
    async def _validate_assertions(
        self,
        assertions: List[GeneratedAssertion],
        sources_map: Dict[str, LegalSource]
    ) -> List[ValidatedAssertion]:
        """
        Valida assertions juridicamente.
        
        ⚠️ LEI 2: Nenhuma afirmação sem fonte.
        """
        validated = []
        
        for assertion in assertions:
            # Encontrar fontes sugeridas
            linked_sources = []
            for ref in assertion.suggested_sources:
                if ref in sources_map:
                    linked_sources.append(sources_map[ref])
            
            # Determinar validade
            is_valid = True
            notes = None
            
            # LEI 2: Precisa de fonte (exceto baixa confiança)
            if assertion.confidence_level != "baixo" and not linked_sources:
                is_valid = False
                notes = "Assertion sem fonte vinculada (LEI 2)"
            
            validated.append(ValidatedAssertion(
                assertion=assertion,
                sources=linked_sources,
                is_valid=is_valid,
                validation_notes=notes
            ))
        
        return validated
    
    async def _persist_assertions(
        self,
        version_id: UUID,
        validated_assertions: List[ValidatedAssertion],
        user_id: UUID
    ) -> None:
        """Persiste assertions validadas no banco."""
        for va in validated_assertions:
            # Criar assertion
            assertion = await self.assertion_service.create(
                self.db,
                version_id=version_id,
                text=va.assertion.text,
                assertion_type=va.assertion.assertion_type,
                confidence_level=va.assertion.confidence_level,
                position=va.assertion.position,
                user_id=user_id
            )
            
            # Vincular fontes
            for source in va.sources:
                await self.assertion_service.link_source(
                    self.db,
                    assertion_id=assertion.id,
                    source_id=source.id,
                    user_id=user_id
                )
        
        await self.db.commit()
