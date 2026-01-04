"""
Agente: Civil Genérico

Agente de fallback para peças cíveis não especializadas.
Usa LLM para geração com postura conservadora.
"""
from typing import List, Dict, Optional
import json

from app.cognitive.agents.base import (
    BaseAgent,
    GeneratedAssertion,
    NormalizedInput,
    register_agent
)
from app.models.assertion import LegalSource
from app.core.config import settings


@register_agent
class CivilGenericAgent(BaseAgent):
    """
    Agente genérico para peças cíveis.
    
    Usado quando não há agente especializado.
    Usa LLM com postura ULTRA conservadora.
    """
    
    agent_id = "civil-generic"
    name = "Agente Civil Genérico"
    legal_basis = "CPC"
    legal_area = "civil"
    piece_type = "Peça Cível"
    
    async def generate(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource]
    ) -> List[GeneratedAssertion]:
        """
        Gera assertions usando LLM ou template.
        
        ⚠️ Postura ULTRA conservadora.
        ⚠️ Só usa fontes disponíveis.
        """
        # Se não há chave de API configurada, usa geração por template
        if not settings.OPENAI_API_KEY:
            return self._generate_by_template(input_data, sources)
        
        # Tenta geração com LLM
        try:
            return await self._generate_with_llm(input_data, sources)
        except Exception:
            # Fallback para template
            return self._generate_by_template(input_data, sources)
    
    def _generate_by_template(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource]
    ) -> List[GeneratedAssertion]:
        """
        Geração por template (sem LLM).
        
        Método conservador: só afirma o que é seguro.
        """
        assertions = []
        position = 0
        
        # Fatos (confiança ALTA - vêm do usuário)
        for fato in input_data.fatos:
            position += 1
            assertions.append(GeneratedAssertion(
                text=fato,
                assertion_type="fato",
                confidence_level="alto",
                suggested_sources=[],
                position=position
            ))
        
        # Fundamentos básicos (se disponíveis)
        source_refs = list(sources.keys())
        
        for ref in source_refs:
            source = sources[ref]
            if source.excerpt:
                position += 1
                assertions.append(GeneratedAssertion(
                    text=f"Conforme {ref}: \"{source.excerpt}\"",
                    assertion_type="fundamento",
                    confidence_level="alto",
                    suggested_sources=[ref],
                    position=position
                ))
        
        # Pedidos (confiança ALTA - vêm do usuário)
        for pedido in input_data.pedidos:
            position += 1
            assertions.append(GeneratedAssertion(
                text=f"Requer seja {pedido}",
                assertion_type="pedido",
                confidence_level="alto",
                suggested_sources=[],
                position=position
            ))
        
        return assertions
    
    async def _generate_with_llm(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource]
    ) -> List[GeneratedAssertion]:
        """
        Geração com LLM.
        
        ⚠️ ULTRA conservador.
        ⚠️ Só usa fontes do banco.
        """
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Preparar lista de fontes disponíveis
        available_sources = []
        for ref, source in sources.items():
            available_sources.append({
                "reference": ref,
                "type": source.source_type.value if hasattr(source.source_type, 'value') else str(source.source_type),
                "excerpt": source.excerpt
            })
        
        system_prompt = self._get_system_prompt()
        
        user_prompt = f"""
Generate assertions for a legal petition in Brazilian law.

CASE DATA:
- Facts provided by client: {json.dumps(input_data.fatos, ensure_ascii=False)}
- Requests: {json.dumps(input_data.pedidos, ensure_ascii=False)}
- Procedural class: {input_data.classe_procedimental}

AVAILABLE SOURCES (you may ONLY reference these):
{json.dumps(available_sources, ensure_ascii=False, indent=2)}

CRITICAL RULES:
1. Generate JSON array of assertion objects
2. Each assertion must have: text, type, confidence, sources
3. type must be one of: fato, tese, fundamento, pedido
4. confidence must be one of: alto, medio, baixo
5. sources must ONLY contain references from AVAILABLE SOURCES
6. If you cannot find appropriate source, use confidence="baixo" and empty sources
7. DO NOT invent or hallucinate sources

Output ONLY the JSON array, no explanations.
"""
        
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Baixa temperatura = mais conservador
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON
        try:
            # Limpar possíveis markers de código
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            assertions_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback para template se LLM retornar formato inválido
            return self._generate_by_template(input_data, sources)
        
        # Converter para GeneratedAssertion
        assertions = []
        for i, data in enumerate(assertions_data):
            # Validar que sources referenciadas existem
            valid_sources = [
                s for s in data.get("sources", [])
                if s in sources
            ]
            
            # Se tinha sources mas nenhuma é válida, baixar confiança
            confidence = data.get("confidence", "medio")
            if data.get("sources") and not valid_sources:
                confidence = "baixo"
            
            assertions.append(GeneratedAssertion(
                text=data.get("text", ""),
                assertion_type=data.get("type", "tese"),
                confidence_level=confidence,
                suggested_sources=valid_sources,
                position=i + 1
            ))
        
        return assertions
