# JurisDoc Backend

## Sistema Jurídico Inteligente AI-First

Backend FastAPI para geração de peças jurídicas com IA, respeitando princípios de auditabilidade, hierarquia normativa e controle humano.

---

## ⚖️ Constituição Técnica

Este sistema segue uma **Constituição Técnica Imutável**:

| Lei | Princípio |
|-----|-----------|
| **LEI 1** | Documento Jurídico ≠ Texto |
| **LEI 2** | Nenhuma Afirmação sem Fonte |
| **LEI 3** | Versionamento é Obrigatório |
| **LEI 4** | Texto Final é Derivado, Nunca Primário |
| **LEI 5** | IA não escreve "texto final" |
| **LEI 6** | Agente = Função Jurídica Única |
| **LEI 7** | API Valida Juridicamente |
| **LEI 8** | Frontend não decide nada |

⚠️ **Qualquer código que viole estas leis está ERRADO.**

---

## 🚀 Quick Start

### 1. Pré-requisitos

- Python 3.11+
- Docker (opcional)
- Conta no Supabase
- API Key da OpenAI

### 2. Configuração

```bash
# Clonar repositório
git clone <repo-url>
cd jurisdoc-backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais
```

### 3. Executar

```bash
# Desenvolvimento
uvicorn app.main:app --reload --port 8000

# Com Docker
docker-compose up --build
```

### 4. Acessar

- **API**: http://localhost:8000
- **Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📁 Estrutura do Projeto

```
jurisdoc-backend/
├── app/
│   ├── main.py              # Entrada FastAPI
│   ├── core/
│   │   ├── config.py        # Configurações
│   │   ├── constitution.py  # LEIS DO SISTEMA ⚖️
│   │   ├── database.py      # Conexão DB
│   │   └── security.py      # Auth/JWT
│   ├── models/              # SQLModel (ORM)
│   ├── schemas/             # Pydantic DTOs
│   ├── api/routes/          # Endpoints
│   ├── services/            # Lógica de negócio
│   ├── cognitive/           # Pipeline de IA
│   │   ├── pipeline.py      # Orquestrador
│   │   ├── agents/          # Agentes especializados
│   │   └── validators.py    # Validação jurídica
│   └── streaming/           # SSE
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🔌 API Endpoints

### Casos
- `POST /cases` - Criar caso
- `GET /cases` - Listar casos
- `GET /cases/{id}` - Obter caso
- `GET /cases/{id}/documents` - Documentos do caso
- `POST /cases/{id}/documents` - Criar documento

### Documentos
- `GET /documents/{id}` - Obter documento
- `GET /documents/{id}/versions` - Listar versões
- `POST /documents/{id}/versions` - Criar versão
- `GET /documents/{id}/audit` - Auditoria completa

### Geração
- `POST /generation/documents/{id}/generate` - Gerar com IA (SSE)
- `POST /generation/document-versions/{id}/render` - Renderizar texto
- `GET /generation/agents` - Listar agentes

### Assertions
- `POST /assertions` - Criar afirmações
- `GET /assertions/{id}` - Obter afirmação
- `POST /assertions/{id}/sources` - Vincular fonte

### Fontes
- `POST /sources` - Criar fonte
- `GET /sources` - Listar fontes
- `GET /sources/types` - Tipos de fonte

### ❌ Endpoints Proibidos (405)
- `PUT /documents/{id}` - Edição destrutiva
- `PATCH /documents/{id}` - Modificação parcial

---

## 🧠 Fluxo de Geração

```
Input Humano
    ↓
Normalização Jurídica
    ↓
Ingestão Documental (PDFs)
    ↓
Pesquisa Jurídica (RAG)
    ↓
Geração de Assertions (Agente)
    ↓
Validação Jurídica
    ↓
Persistência (Nova Versão)
    ↓
Renderização (Texto Derivado)
```

---

## 🧪 Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=app

# Testes específicos de Constituição
pytest tests/test_constitution.py
```

---

## 📝 Licença

Proprietário - Todos os direitos reservados.

---

## ⚠️ Importante

Este sistema **NÃO É**:
- Um chat jurídico
- Um gerador de texto livre
- Um substituto para advogados

Este sistema **É**:
- Um motor cognitivo jurídico
- Um orquestrador de agentes especializados
- Um sistema auditável e defensável
- Human-in-the-loop obrigatório
