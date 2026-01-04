# 🧠 Pipeline Cognitivo - Sistema Jurídico Inteligente

## Visão Geral

O pipeline cognitivo é o coração do sistema de geração de peças jurídicas.

⚠️ **LEIS APLICÁVEIS**:
- **LEI 5**: IA não escreve texto final (produz assertions)
- **LEI 6**: Agente = Função jurídica única
- **LEI 2**: Nenhuma afirmação sem fonte

## Fluxo do Pipeline

```
Input Humano (Wizard)
        ↓
┌───────────────────┐
│  1. Criar Versão  │ → LEI 3: Versionamento
└───────────────────┘
        ↓
┌───────────────────┐
│  2. Normalização  │ → Estrutura jurídica
└───────────────────┘
        ↓
┌───────────────────┐
│  3. Pesquisa RAG  │ → Busca fontes no banco
└───────────────────┘
        ↓
┌───────────────────┐
│  4. Agente IA     │ → LEI 5, LEI 6
└───────────────────┘
        ↓
┌───────────────────┐
│  5. Validação     │ → LEI 2: Fonte obrigatória
└───────────────────┘
        ↓
┌───────────────────┐
│  6. Persistência  │ → Banco de dados
└───────────────────┘
        ↓
   Streaming SSE
```

## Agentes Disponíveis

| Agent ID | Nome | Base Legal | Área |
|----------|------|------------|------|
| `peticao-inicial-civil` | Petição Inicial Cível | Art. 319 CPC | Civil |
| `contestacao-civil` | Contestação Cível | Art. 335 CPC | Civil |
| `civil-generic` | Agente Genérico | CPC | Civil |

## Endpoint de Geração

### `POST /api/v1/documents/{document_id}/generate`

Inicia o pipeline com streaming SSE.

**Request:**
```json
{
  "document_id": "uuid",
  "agent_type": "peticao-inicial-civil",
  "fatos_principais": [
    "Nome do autor foi negativado indevidamente",
    "Não houve notificação prévia"
  ],
  "pedidos": [
    "Declaração de inexistência do débito",
    "Indenização por danos morais"
  ],
  "valor_causa": 10000.00,
  "partes": {
    "autor": "João da Silva",
    "reu": "Empresa X"
  }
}
```

**Response (SSE):**
```
event: started
data: {"document_id": "uuid", "agent_type": "peticao-inicial-civil"}

event: version_created
data: {"version_id": "uuid", "version_number": 1}

event: normalization_complete
data: {"fatos_count": 2, "pedidos_count": 2, "possiveis_fundamentos": ["CPC, art. 319", ...]}

event: research_started
data: {"fundamentos_buscados": ["CPC, art. 319", ...]}

event: source_found
data: {"reference": "CPC, art. 319", "type": "lei", "excerpt": "A petição inicial..."}

event: research_complete
data: {"sources_found": 5}

event: generation_started
data: {"agent": "peticao-inicial-civil"}

event: assertion_generated
data: {"text": "Nos termos do art. 319...", "type": "fundamento", "confidence": "alto", "position": 1}

event: assertion_validated
data: {"position": 1, "is_valid": true, "sources_count": 1}

event: validation_complete
data: {"total": 10, "valid": 10}

event: persistence_complete
data: {"version_id": "uuid"}

event: completed
data: {"version_id": "uuid", "assertions_created": 10, "valid_assertions": 10}
```

## Estrutura de Assertions

Cada assertion gerada contém:

```json
{
  "text": "Texto da afirmação jurídica",
  "assertion_type": "fato | tese | fundamento | pedido",
  "confidence_level": "alto | medio | baixo",
  "suggested_sources": ["CPC, art. 319"],
  "position": 1
}
```

### Tipos de Assertion

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `fato` | Fato narrado | "O autor foi negativado em 01/01/2024" |
| `tese` | Tese jurídica | "O dano moral é presumido (in re ipsa)" |
| `fundamento` | Fundamento legal | "Conforme art. 319 do CPC..." |
| `pedido` | Pedido do autor | "Requer seja julgado procedente..." |

### Níveis de Confiança

| Nível | Descrição | Requer Fonte? |
|-------|-----------|---------------|
| `alto` | Alta certeza | ✅ Sim |
| `medio` | Certeza moderada | ✅ Sim |
| `baixo` | Baixa certeza | ❌ Não (LEI 2 exceção) |

## Validação Jurídica (LEI 2)

Antes de persistir, cada assertion é validada:

```python
# LEI 2: Nenhuma afirmação sem fonte
if assertion.confidence_level != "baixo" and not linked_sources:
    is_valid = False
    notes = "Assertion sem fonte vinculada"
```

⚠️ **Exceção**: Assertions com `confidence_level = "baixo"` são válidas sem fonte.

## Criando Novos Agentes

```python
from app.cognitive.agents.base import BaseAgent, register_agent

@register_agent
class MeuNovoAgente(BaseAgent):
    agent_id = "meu-agente"
    name = "Meu Agente Especializado"
    legal_basis = "Lei X, art. Y"
    legal_area = "civil"
    piece_type = "Tipo de Peça"
    
    async def generate(self, input_data, sources):
        # ⚠️ LEI 5: Retornar assertions, NÃO texto
        return [
            GeneratedAssertion(
                text="...",
                assertion_type="fundamento",
                confidence_level="alto",
                suggested_sources=["Lei X, art. Y"],
                position=1
            )
        ]
```

## Integração com Frontend (Lovable)

O frontend deve:

1. Conectar ao endpoint SSE
2. Processar eventos em tempo real
3. Mostrar progresso ao usuário
4. NÃO enviar texto direto (LEI 1)
5. NÃO decidir validação (LEI 8)

```javascript
const eventSource = new EventSource(`/api/v1/documents/${docId}/generate`);

eventSource.addEventListener('assertion_generated', (e) => {
  const data = JSON.parse(e.data);
  console.log('Nova assertion:', data.text);
});

eventSource.addEventListener('completed', (e) => {
  const data = JSON.parse(e.data);
  console.log('Pipeline concluído:', data.assertions_created);
  eventSource.close();
});
```

## Referência Rápida

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/documents/{id}/generate` | Inicia geração (SSE) |
| GET | `/api/v1/agents` | Lista agentes |
| GET | `/api/v1/agents/{type}` | Info do agente |

### Eventos SSE

| Evento | Descrição |
|--------|-----------|
| `started` | Pipeline iniciado |
| `version_created` | Nova versão criada |
| `normalization_complete` | Inputs normalizados |
| `research_started` | Pesquisa iniciada |
| `source_found` | Fonte encontrada |
| `research_complete` | Pesquisa concluída |
| `generation_started` | Geração iniciada |
| `assertion_generated` | Assertion gerada |
| `assertion_validated` | Assertion validada |
| `validation_complete` | Validação concluída |
| `persistence_complete` | Dados salvos |
| `completed` | Pipeline concluído |
| `error` | Erro no pipeline |
