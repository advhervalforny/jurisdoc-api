# 🧪 Testes do Sistema Jurídico Inteligente

## Visão Geral

Este diretório contém os testes automatizados do backend JurisDoc.

## Estrutura

```
tests/
├── conftest.py           # Fixtures compartilhadas
├── integration/          # Testes de integração (API)
│   ├── test_cases.py     # Rotas de casos
│   ├── test_documents.py # Rotas de documentos
│   ├── test_assertions.py# Rotas de assertions
│   ├── test_sources.py   # Rotas de fontes
│   ├── test_rendering.py # Rotas de renderização
│   └── test_constitution.py # ⚠️ TESTES CRÍTICOS DAS LEIS
└── unit/                 # Testes unitários (futuro)
```

## Executar Testes

### Todos os testes
```bash
pytest
```

### Com cobertura
```bash
pytest --cov=app --cov-report=html
```

### Apenas testes críticos (leis constitucionais)
```bash
pytest tests/integration/test_constitution.py -v
```

### Por arquivo
```bash
pytest tests/integration/test_cases.py -v
```

## ⚠️ Testes Críticos

O arquivo `test_constitution.py` contém testes das **8 LEIS IMUTÁVEIS**:

| Lei | Descrição | Teste |
|-----|-----------|-------|
| **LEI 1** | Documento ≠ Texto | `TestLei1_DocumentoNaoETexto` |
| **LEI 2** | Nenhuma afirmação sem fonte | `TestLei2_NenhumaAfirmacaoSemFonte` |
| **LEI 3** | Versionamento obrigatório | `TestLei3_VersionamentoObrigatorio` |
| **LEI 4** | Texto final é derivado | `TestLei4_TextoFinalDerivado` |
| **LEI 7** | API valida juridicamente | `TestLei7_APIValidaJuridicamente` |

**Se QUALQUER teste de lei falhar, o sistema está comprometido juridicamente.**

## Fixtures Principais

### `seeded_client`
Cliente HTTP com banco de dados populado (áreas jurídicas, tipos de peça, fontes).

### `test_user_id`
UUID do usuário de teste (autenticação mockada).

### Payloads
- `case_payload`: Dados para criar caso
- `document_payload`: Dados para criar documento
- `assertion_payload`: Dados para criar assertion
- `source_payload`: Dados para criar fonte

## Cobertura Esperada

| Componente | Cobertura Mínima |
|------------|------------------|
| Rotas | 90% |
| Services | 80% |
| Models | 70% |
| Constitution | 100% |

## CI/CD

Os testes são executados automaticamente no pipeline CI/CD.

Critérios de falha:
- Qualquer teste de `test_constitution.py` falhar
- Cobertura < 70%
- Tempo de execução > 5 minutos
