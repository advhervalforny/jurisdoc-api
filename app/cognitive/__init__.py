"""
Módulo Cognitivo - Sistema Jurídico Inteligente AI-First.

⚠️ LEIS APLICÁVEIS:
- LEI 5: IA não escreve texto final
- LEI 6: Agente = Função jurídica única

Componentes:
- pipeline: Orquestrador do fluxo de geração
- agents: Agentes jurídicos especializados
"""
from app.cognitive.pipeline import (
    CognitivePipeline,
    GenerationInput,
    PipelineEvent,
    PipelineEventType
)

__all__ = [
    "CognitivePipeline",
    "GenerationInput",
    "PipelineEvent",
    "PipelineEventType"
]
