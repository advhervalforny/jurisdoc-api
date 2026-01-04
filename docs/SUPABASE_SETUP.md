# 🚀 Guia de Configuração do Supabase

## Passo 1: Criar Projeto

1. Acesse [supabase.com](https://supabase.com)
2. Faça login ou crie uma conta
3. Clique em **"New Project"**
4. Configure:
   - **Name**: `jurisdoc-prod` (ou `jurisdoc-dev` para desenvolvimento)
   - **Database Password**: Gere uma senha forte e **GUARDE**
   - **Region**: Escolha a mais próxima (ex: `South America (São Paulo)`)
5. Clique em **"Create new project"**
6. Aguarde ~2 minutos para provisionamento

---

## Passo 2: Obter Credenciais

Após o projeto ser criado, vá em **Settings > API**:

### Copie estas informações:

| Variável | Onde encontrar |
|----------|----------------|
| `SUPABASE_URL` | Project URL (ex: `https://xxxxx.supabase.co`) |
| `SUPABASE_ANON_KEY` | `anon` `public` key |
| `SUPABASE_SERVICE_KEY` | `service_role` key (⚠️ NUNCA exponha no frontend) |
| `JWT_SECRET` | Settings > API > JWT Settings > JWT Secret |

### Database URL:

Vá em **Settings > Database**:
- **Connection string** > **URI**
- Formato: `postgresql://postgres:[SUA-SENHA]@db.[REF].supabase.co:5432/postgres`

---

## Passo 3: Configurar .env

```bash
cd jurisdoc-backend
cp .env.example .env
```

Edite o `.env`:

```env
# Ambiente
ENVIRONMENT=development
DEBUG=true

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database
DATABASE_URL=postgresql://postgres:sua-senha@db.xxx.supabase.co:5432/postgres

# JWT
JWT_SECRET=seu-jwt-secret-do-supabase

# OpenAI
OPENAI_API_KEY=sk-...
```

---

## Passo 4: Executar Migrations

### Opção A: Via Supabase Dashboard (Recomendado)

1. Vá em **SQL Editor** no dashboard do Supabase
2. Cole o conteúdo de `migrations/001_initial_schema.sql`
3. Clique em **"Run"**

### Opção B: Via CLI

```bash
# Instalar Supabase CLI
npm install -g supabase

# Login
supabase login

# Linkar projeto
supabase link --project-ref seu-project-ref

# Executar migration
supabase db push
```

---

## Passo 5: Configurar Auth

### 5.1 Habilitar Email Auth

1. Vá em **Authentication > Providers**
2. **Email** deve estar habilitado por padrão
3. Configure:
   - ✅ Enable Email Signup
   - ✅ Confirm Email (recomendado para produção)

### 5.2 Configurar Redirect URLs (para Lovable)

1. Vá em **Authentication > URL Configuration**
2. Adicione em **Redirect URLs**:
   ```
   http://localhost:3000/**
   http://localhost:5173/**
   https://*.lovable.app/**
   https://seu-dominio.com/**
   ```

### 5.3 (Opcional) Habilitar OAuth

Se quiser login com Google:
1. **Authentication > Providers > Google**
2. Siga as instruções para obter Client ID/Secret do Google Cloud Console

---

## Passo 6: Configurar Storage (para PDFs)

1. Vá em **Storage**
2. Clique em **"New bucket"**
3. Crie o bucket:
   - **Name**: `documents`
   - **Public**: ❌ Não (arquivos privados)
4. Configure políticas de acesso (RLS):

```sql
-- Usuário pode ver apenas seus próprios arquivos
CREATE POLICY "Users can view own files"
ON storage.objects FOR SELECT
USING (auth.uid()::text = (storage.foldername(name))[1]);

-- Usuário pode fazer upload em sua pasta
CREATE POLICY "Users can upload own files"
ON storage.objects FOR INSERT
WITH CHECK (auth.uid()::text = (storage.foldername(name))[1]);
```

---

## Passo 7: Habilitar pgvector (para RAG)

1. Vá em **Database > Extensions**
2. Procure por **"vector"**
3. Clique em **"Enable"**

Ou execute via SQL:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Passo 8: Verificar Conexão

```bash
# Testar conexão
cd jurisdoc-backend
python -c "
from app.core.config import settings
print(f'Supabase URL: {settings.SUPABASE_URL}')
print(f'Database: {settings.DATABASE_URL[:50]}...')
print('✅ Configuração carregada!')
"
```

---

## Passo 9: Executar Backend

```bash
# Desenvolvimento
uvicorn app.main:app --reload --port 8000

# Ou com Docker
docker-compose up --build
```

Acesse:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 🔒 Checklist de Segurança

- [ ] `SUPABASE_SERVICE_KEY` nunca no frontend
- [ ] `DATABASE_URL` nunca exposta
- [ ] RLS habilitado em todas as tabelas
- [ ] Policies configuradas corretamente
- [ ] `.env` no `.gitignore`

---

## ⚠️ Troubleshooting

### Erro: "Invalid JWT"
- Verifique se `JWT_SECRET` está correto
- Verifique se o token não expirou

### Erro: "Connection refused"
- Verifique `DATABASE_URL`
- Verifique se o IP está liberado (Settings > Database > Connection Pooling)

### Erro: "Permission denied"
- Verifique as policies RLS
- Use `service_role` key para operações admin

---

## 📚 Links Úteis

- [Supabase Docs](https://supabase.com/docs)
- [Supabase Auth](https://supabase.com/docs/guides/auth)
- [Supabase Storage](https://supabase.com/docs/guides/storage)
- [pgvector](https://supabase.com/docs/guides/ai/vector-columns)
