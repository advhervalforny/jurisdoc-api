# 🚀 Guia de Deploy - JurisDoc Backend

## Pré-requisitos

Antes do deploy, você precisa ter:

1. ✅ **Supabase configurado** (ver `docs/SUPABASE_SETUP.md`)
2. ✅ **Schema SQL executado** (migrations/001_initial_schema.sql)
3. ✅ **Seed data inserido** (migrations/002_seed_data.sql)

## Opção 1: Render (Recomendado)

### Passo 1: Criar conta no Render

1. Acesse [render.com](https://render.com)
2. Crie conta com GitHub

### Passo 2: Criar Web Service

1. Dashboard → **New** → **Web Service**
2. Conecte seu repositório GitHub
3. Configure:

| Campo | Valor |
|-------|-------|
| Name | `jurisdoc-api` |
| Region | `Oregon (US West)` |
| Branch | `main` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | `Starter ($7/mês)` ou `Free` |

### Passo 3: Configurar Variáveis de Ambiente

No dashboard do Render, vá em **Environment** e adicione:

```env
# Supabase (OBRIGATÓRIO)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database (OBRIGATÓRIO)
DATABASE_URL=postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres

# JWT (OBRIGATÓRIO)
JWT_SECRET=sua-chave-secreta-muito-longa-aqui-123456
JWT_ALGORITHM=HS256

# CORS (OBRIGATÓRIO)
CORS_ORIGINS=https://seu-app.lovable.app,http://localhost:5173

# OpenAI (OPCIONAL - para agente genérico)
OPENAI_API_KEY=sk-...

# Environment
ENVIRONMENT=production
```

### Passo 4: Deploy

1. Clique **Create Web Service**
2. Aguarde o build (~3-5 minutos)
3. Acesse a URL fornecida (ex: `https://jurisdoc-api.onrender.com`)

### Passo 5: Verificar

```bash
# Health check
curl https://jurisdoc-api.onrender.com/health

# Docs
open https://jurisdoc-api.onrender.com/docs
```

---

## Opção 2: Railway

### Passo 1: Criar conta no Railway

1. Acesse [railway.app](https://railway.app)
2. Crie conta com GitHub

### Passo 2: Criar Projeto

1. Dashboard → **New Project**
2. **Deploy from GitHub repo**
3. Selecione o repositório

### Passo 3: Configurar Variáveis

No dashboard, clique no serviço → **Variables**:

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres
JWT_SECRET=sua-chave-secreta
JWT_ALGORITHM=HS256
CORS_ORIGINS=https://seu-app.lovable.app
OPENAI_API_KEY=sk-... (opcional)
ENVIRONMENT=production
```

### Passo 4: Gerar Domínio

1. Clique no serviço → **Settings** → **Domains**
2. Clique **Generate Domain**
3. URL será algo como `jurisdoc-api-production.up.railway.app`

---

## Opção 3: Docker (Self-hosted)

### Build

```bash
docker build -t jurisdoc-api .
```

### Run

```bash
docker run -d \
  -p 8000:8000 \
  -e SUPABASE_URL=https://xxx.supabase.co \
  -e SUPABASE_ANON_KEY=eyJ... \
  -e DATABASE_URL=postgresql://... \
  -e JWT_SECRET=secret \
  -e CORS_ORIGINS=http://localhost:5173 \
  jurisdoc-api
```

### Docker Compose

```bash
docker-compose up -d
```

---

## Verificação Pós-Deploy

### 1. Health Check

```bash
curl https://sua-api.onrender.com/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "Sistema Jurídico Inteligente",
  "version": "1.0.0",
  "constitution": {...}
}
```

### 2. Documentação

Acesse: `https://sua-api.onrender.com/docs`

### 3. Teste de Endpoint

```bash
# Listar áreas jurídicas (via sources)
curl https://sua-api.onrender.com/api/v1/sources/types
```

### 4. Teste de Autenticação

```bash
# Criar caso (requer auth)
curl -X POST https://sua-api.onrender.com/api/v1/cases \
  -H "Authorization: Bearer SEU_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"legal_area_slug": "civil", "title": "Teste", "description": "Teste"}'
```

---

## Integração com Lovable

### 1. Configurar CORS

No Render/Railway, adicione a URL do Lovable:

```env
CORS_ORIGINS=https://seu-projeto.lovable.app,http://localhost:5173
```

### 2. Configurar URL da API no Lovable

No código do Lovable, configure a URL base:

```typescript
// src/lib/api.ts
const API_URL = import.meta.env.VITE_API_URL || 'https://jurisdoc-api.onrender.com';
```

### 3. Configurar Variável no Lovable

No Lovable, adicione variável de ambiente:

```env
VITE_API_URL=https://jurisdoc-api.onrender.com
```

---

## Troubleshooting

### Erro: "Connection refused"

- Verifique se o serviço está rodando
- Verifique health check: `/health`
- Verifique logs no dashboard

### Erro: "CORS blocked"

- Adicione a URL do frontend em `CORS_ORIGINS`
- Inclua tanto `https://` quanto `http://localhost`

### Erro: "Database connection failed"

- Verifique `DATABASE_URL`
- Confirme que o IP do Render/Railway está liberado no Supabase
- No Supabase: Settings → Database → Connection Pooling

### Erro: "JWT invalid"

- Verifique `JWT_SECRET` e `JWT_ALGORITHM`
- Confirme que o token está sendo enviado corretamente

### Erro: "Module not found"

- Verifique `requirements.txt`
- Rebuild o serviço

---

## Custos Estimados

| Serviço | Plano | Custo |
|---------|-------|-------|
| Render | Free | $0/mês |
| Render | Starter | $7/mês |
| Railway | Hobby | $5/mês |
| Supabase | Free | $0/mês |
| Supabase | Pro | $25/mês |

**Recomendação para MVP**: Render Free + Supabase Free = **$0/mês**

---

## Checklist de Deploy

- [ ] Supabase configurado
- [ ] Schema SQL executado
- [ ] Seed data inserido
- [ ] Conta no Render/Railway criada
- [ ] Repositório conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado
- [ ] Health check OK
- [ ] Docs acessíveis
- [ ] CORS configurado para Lovable
- [ ] Teste de autenticação OK

---

## URLs de Referência

- **Render Dashboard**: https://dashboard.render.com
- **Railway Dashboard**: https://railway.app/dashboard
- **Supabase Dashboard**: https://app.supabase.com
- **API Docs**: https://sua-api.onrender.com/docs
