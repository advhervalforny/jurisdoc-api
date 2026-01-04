-- ============================================================================
-- JURISDOC - SCHEMA INICIAL
-- Sistema Jurídico Inteligente AI-First
-- ============================================================================
-- Versão: 1.0
-- Data: 2026-01-03
-- 
-- ⚠️ ATENÇÃO: Este schema implementa a Constituição Técnica do Sistema.
-- Modificações devem respeitar as 8 LEIS.
-- ============================================================================

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- 1. PERFIS DE USUÁRIO
-- ============================================================================
-- Complementa auth.users do Supabase com dados profissionais

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    oab_number TEXT,
    oab_state TEXT,
    phone TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT user_profiles_user_id_unique UNIQUE (user_id)
);

-- Índice para busca por user_id
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- ============================================================================
-- 2. ÁREAS DO DIREITO
-- ============================================================================
-- Domínio jurídico estrutural

CREATE TABLE IF NOT EXISTS legal_areas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Dados iniciais
INSERT INTO legal_areas (slug, name, description) VALUES
    ('civil', 'Direito Civil', 'Área do direito que regula as relações entre particulares'),
    ('penal', 'Direito Penal', 'Área do direito que define crimes e penas')
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- 3. TIPOS DE PEÇAS JURÍDICAS
-- ============================================================================
-- Cada tipo de peça pertence a uma área

CREATE TABLE IF NOT EXISTS legal_piece_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    legal_area_id UUID NOT NULL REFERENCES legal_areas(id) ON DELETE RESTRICT,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    legal_basis TEXT, -- Ex: "Art. 319 CPC"
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT legal_piece_types_slug_area_unique UNIQUE (slug, legal_area_id)
);

-- Índice para busca por área
CREATE INDEX idx_legal_piece_types_area ON legal_piece_types(legal_area_id);

-- Dados iniciais - Direito Civil
INSERT INTO legal_piece_types (legal_area_id, slug, name, legal_basis) 
SELECT 
    id,
    'peticao-inicial',
    'Petição Inicial',
    'Art. 319 CPC'
FROM legal_areas WHERE slug = 'civil'
ON CONFLICT DO NOTHING;

INSERT INTO legal_piece_types (legal_area_id, slug, name, legal_basis) 
SELECT 
    id,
    'contestacao',
    'Contestação',
    'Art. 335 CPC'
FROM legal_areas WHERE slug = 'civil'
ON CONFLICT DO NOTHING;

INSERT INTO legal_piece_types (legal_area_id, slug, name, legal_basis) 
SELECT 
    id,
    'replica',
    'Réplica',
    'Art. 351 CPC'
FROM legal_areas WHERE slug = 'civil'
ON CONFLICT DO NOTHING;

INSERT INTO legal_piece_types (legal_area_id, slug, name, legal_basis) 
SELECT 
    id,
    'recurso-apelacao',
    'Recurso de Apelação',
    'Art. 1.009 CPC'
FROM legal_areas WHERE slug = 'civil'
ON CONFLICT DO NOTHING;

-- Dados iniciais - Direito Penal
INSERT INTO legal_piece_types (legal_area_id, slug, name, legal_basis) 
SELECT 
    id,
    'denuncia',
    'Denúncia',
    'Art. 41 CPP'
FROM legal_areas WHERE slug = 'penal'
ON CONFLICT DO NOTHING;

INSERT INTO legal_piece_types (legal_area_id, slug, name, legal_basis) 
SELECT 
    id,
    'resposta-acusacao',
    'Resposta à Acusação',
    'Art. 396-A CPP'
FROM legal_areas WHERE slug = 'penal'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 4. CASOS / PROCESSOS
-- ============================================================================
-- Contexto jurídico onde todas as peças existem
-- Regra: Nenhuma peça existe sem um caso

CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    legal_area_id UUID NOT NULL REFERENCES legal_areas(id) ON DELETE RESTRICT,
    title TEXT NOT NULL,
    description TEXT,
    process_number TEXT, -- Número do processo (se houver)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_cases_user_id ON cases(user_id);
CREATE INDEX idx_cases_legal_area ON cases(legal_area_id);
CREATE INDEX idx_cases_created_at ON cases(created_at DESC);

-- ============================================================================
-- 5. DOCUMENTOS JURÍDICOS (CONTAINER)
-- ============================================================================
-- ⚠️ LEI 1: Documento ≠ Texto
-- Documento é apenas um container lógico, NÃO contém texto diretamente

CREATE TYPE document_status AS ENUM ('draft', 'generated', 'revised', 'finalized');

CREATE TABLE IF NOT EXISTS legal_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    piece_type_id UUID NOT NULL REFERENCES legal_piece_types(id) ON DELETE RESTRICT,
    status document_status NOT NULL DEFAULT 'draft',
    current_version_id UUID, -- Referência à versão atual (preenchida depois)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_legal_documents_case ON legal_documents(case_id);
CREATE INDEX idx_legal_documents_status ON legal_documents(status);

-- ============================================================================
-- 6. VERSÕES DE DOCUMENTO
-- ============================================================================
-- ⚠️ LEI 3: Versionamento é Obrigatório
-- Toda geração cria nova versão. É PROIBIDO sobrescrever.

CREATE TYPE version_creator AS ENUM ('human', 'agent');

CREATE TABLE IF NOT EXISTS legal_document_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    created_by version_creator NOT NULL,
    agent_name TEXT, -- Nome do agente se created_by = 'agent'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- ⚠️ Constraint crítica: versão é imutável e única por documento
    CONSTRAINT legal_document_versions_unique UNIQUE (document_id, version_number)
);

-- Índices
CREATE INDEX idx_legal_document_versions_document ON legal_document_versions(document_id);
CREATE INDEX idx_legal_document_versions_number ON legal_document_versions(document_id, version_number DESC);

-- Adicionar FK de current_version_id após criar a tabela de versões
ALTER TABLE legal_documents 
    ADD CONSTRAINT fk_current_version 
    FOREIGN KEY (current_version_id) 
    REFERENCES legal_document_versions(id) 
    ON DELETE SET NULL;

-- ============================================================================
-- 7. AFIRMAÇÕES JURÍDICAS
-- ============================================================================
-- ⚠️ ESTE É O CORAÇÃO DO SISTEMA
-- LEI 2: Nenhuma afirmação sem fonte (validado na aplicação)
-- LEI 4: Texto final é derivado destas assertions

CREATE TYPE assertion_type AS ENUM ('fato', 'tese', 'fundamento', 'pedido');
CREATE TYPE confidence_level AS ENUM ('alto', 'medio', 'baixo');

CREATE TABLE IF NOT EXISTS legal_assertions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_version_id UUID NOT NULL REFERENCES legal_document_versions(id) ON DELETE CASCADE,
    assertion_text TEXT NOT NULL,
    assertion_type assertion_type NOT NULL,
    confidence_level confidence_level NOT NULL DEFAULT 'medio',
    position INTEGER NOT NULL DEFAULT 0, -- Ordem na peça
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_legal_assertions_version ON legal_assertions(document_version_id);
CREATE INDEX idx_legal_assertions_type ON legal_assertions(assertion_type);
CREATE INDEX idx_legal_assertions_position ON legal_assertions(document_version_id, position);

-- ============================================================================
-- 8. FONTES JURÍDICAS
-- ============================================================================
-- Entidade de primeira classe no sistema
-- Respeita hierarquia normativa

CREATE TYPE source_type AS ENUM ('constituicao', 'lei', 'jurisprudencia', 'doutrina', 'argumentacao');

CREATE TABLE IF NOT EXISTS legal_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type source_type NOT NULL,
    reference TEXT NOT NULL, -- Ex: "CPC, art. 319"
    excerpt TEXT NOT NULL, -- Trecho relevante
    source_url TEXT, -- URL opcional
    -- Para RAG/busca vetorial
    embedding vector(1536), -- OpenAI ada-002 dimension
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Evitar duplicatas exatas
    CONSTRAINT legal_sources_unique UNIQUE (source_type, reference, excerpt)
);

-- Índices
CREATE INDEX idx_legal_sources_type ON legal_sources(source_type);
CREATE INDEX idx_legal_sources_reference ON legal_sources(reference);

-- Índice vetorial para busca semântica (RAG)
CREATE INDEX idx_legal_sources_embedding ON legal_sources 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- 9. VÍNCULO ASSERTION <-> SOURCE
-- ============================================================================
-- ⚠️ LEI 2: Uma assertion só é válida se tiver pelo menos uma fonte

CREATE TABLE IF NOT EXISTS assertion_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assertion_id UUID NOT NULL REFERENCES legal_assertions(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES legal_sources(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Evitar duplicatas
    CONSTRAINT assertion_sources_unique UNIQUE (assertion_id, source_id)
);

-- Índices
CREATE INDEX idx_assertion_sources_assertion ON assertion_sources(assertion_id);
CREATE INDEX idx_assertion_sources_source ON assertion_sources(source_id);

-- ============================================================================
-- 10. RENDERIZAÇÕES (TEXTO DERIVADO)
-- ============================================================================
-- ⚠️ LEI 4: Texto final é DERIVADO, nunca primário
-- Este texto é sempre reconstruível a partir das assertions

CREATE TYPE render_format AS ENUM ('markdown', 'html', 'docx', 'pdf');

CREATE TABLE IF NOT EXISTS document_renderings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_version_id UUID NOT NULL REFERENCES legal_document_versions(id) ON DELETE CASCADE,
    rendered_text TEXT NOT NULL,
    render_format render_format NOT NULL DEFAULT 'markdown',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índice
CREATE INDEX idx_document_renderings_version ON document_renderings(document_version_id);

-- ============================================================================
-- 11. ANEXOS / AUTOS
-- ============================================================================
-- PDFs e outros documentos anexados ao caso

CREATE TABLE IF NOT EXISTS document_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL, -- Caminho no Supabase Storage
    file_size INTEGER,
    mime_type TEXT NOT NULL,
    -- Metadados extraídos
    extracted_text TEXT, -- Texto extraído via OCR
    embedding vector(1536), -- Para busca semântica
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_document_attachments_case ON document_attachments(case_id);

-- Índice vetorial para busca nos anexos
CREATE INDEX idx_document_attachments_embedding ON document_attachments 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- 12. LOGS DE AUDITORIA
-- ============================================================================
-- Permite responder: Quem fez o quê, quando?

CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- 'case', 'document', 'assertion', etc
    entity_id UUID NOT NULL,
    details JSONB, -- Detalhes adicionais
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para consultas de auditoria
CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_entity ON activity_logs(entity_type, entity_id);
CREATE INDEX idx_activity_logs_created ON activity_logs(created_at DESC);
CREATE INDEX idx_activity_logs_action ON activity_logs(action);

-- ============================================================================
-- 13. ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Cada usuário só vê seus próprios dados

-- Habilitar RLS em todas as tabelas
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_document_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_assertions ENABLE ROW LEVEL SECURITY;
ALTER TABLE assertion_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_renderings ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- Tabelas públicas (somente leitura)
ALTER TABLE legal_areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_piece_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_sources ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 14. POLÍTICAS DE ACESSO (RLS POLICIES)
-- ============================================================================

-- user_profiles: usuário vê apenas seu próprio perfil
CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
    ON user_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- legal_areas: todos podem ler (público)
CREATE POLICY "Anyone can read legal areas"
    ON legal_areas FOR SELECT
    USING (true);

-- legal_piece_types: todos podem ler (público)
CREATE POLICY "Anyone can read piece types"
    ON legal_piece_types FOR SELECT
    USING (true);

-- legal_sources: todos podem ler (público)
CREATE POLICY "Anyone can read sources"
    ON legal_sources FOR SELECT
    USING (true);

-- cases: usuário vê apenas seus próprios casos
CREATE POLICY "Users can view own cases"
    ON cases FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own cases"
    ON cases FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cases"
    ON cases FOR UPDATE
    USING (auth.uid() = user_id);

-- legal_documents: via case ownership
CREATE POLICY "Users can view own documents"
    ON legal_documents FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM cases 
            WHERE cases.id = legal_documents.case_id 
            AND cases.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own documents"
    ON legal_documents FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM cases 
            WHERE cases.id = legal_documents.case_id 
            AND cases.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own documents"
    ON legal_documents FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM cases 
            WHERE cases.id = legal_documents.case_id 
            AND cases.user_id = auth.uid()
        )
    );

-- legal_document_versions: via document -> case ownership
CREATE POLICY "Users can view own versions"
    ON legal_document_versions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM legal_documents ld
            JOIN cases c ON c.id = ld.case_id
            WHERE ld.id = legal_document_versions.document_id 
            AND c.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own versions"
    ON legal_document_versions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM legal_documents ld
            JOIN cases c ON c.id = ld.case_id
            WHERE ld.id = legal_document_versions.document_id 
            AND c.user_id = auth.uid()
        )
    );

-- ⚠️ LEI 3: NÃO há policy de UPDATE para versões (imutáveis)
-- ⚠️ LEI 3: NÃO há policy de DELETE para versões (histórico permanente)

-- legal_assertions: via version -> document -> case
CREATE POLICY "Users can view own assertions"
    ON legal_assertions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM legal_document_versions v
            JOIN legal_documents ld ON ld.id = v.document_id
            JOIN cases c ON c.id = ld.case_id
            WHERE v.id = legal_assertions.document_version_id 
            AND c.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own assertions"
    ON legal_assertions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM legal_document_versions v
            JOIN legal_documents ld ON ld.id = v.document_id
            JOIN cases c ON c.id = ld.case_id
            WHERE v.id = legal_assertions.document_version_id 
            AND c.user_id = auth.uid()
        )
    );

-- assertion_sources: via assertion chain
CREATE POLICY "Users can view own assertion sources"
    ON assertion_sources FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM legal_assertions a
            JOIN legal_document_versions v ON v.id = a.document_version_id
            JOIN legal_documents ld ON ld.id = v.document_id
            JOIN cases c ON c.id = ld.case_id
            WHERE a.id = assertion_sources.assertion_id 
            AND c.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own assertion sources"
    ON assertion_sources FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM legal_assertions a
            JOIN legal_document_versions v ON v.id = a.document_version_id
            JOIN legal_documents ld ON ld.id = v.document_id
            JOIN cases c ON c.id = ld.case_id
            WHERE a.id = assertion_sources.assertion_id 
            AND c.user_id = auth.uid()
        )
    );

-- document_renderings: via version chain
CREATE POLICY "Users can view own renderings"
    ON document_renderings FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM legal_document_versions v
            JOIN legal_documents ld ON ld.id = v.document_id
            JOIN cases c ON c.id = ld.case_id
            WHERE v.id = document_renderings.document_version_id 
            AND c.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own renderings"
    ON document_renderings FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM legal_document_versions v
            JOIN legal_documents ld ON ld.id = v.document_id
            JOIN cases c ON c.id = ld.case_id
            WHERE v.id = document_renderings.document_version_id 
            AND c.user_id = auth.uid()
        )
    );

-- document_attachments: via case
CREATE POLICY "Users can view own attachments"
    ON document_attachments FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM cases 
            WHERE cases.id = document_attachments.case_id 
            AND cases.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own attachments"
    ON document_attachments FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM cases 
            WHERE cases.id = document_attachments.case_id 
            AND cases.user_id = auth.uid()
        )
    );

-- activity_logs: usuário vê apenas seus próprios logs
CREATE POLICY "Users can view own logs"
    ON activity_logs FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================================================
-- 15. FUNCTIONS E TRIGGERS
-- ============================================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers de updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_cases_updated_at
    BEFORE UPDATE ON cases
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_legal_documents_updated_at
    BEFORE UPDATE ON legal_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Função para auto-incrementar version_number
CREATE OR REPLACE FUNCTION get_next_version_number(doc_id UUID)
RETURNS INTEGER AS $$
DECLARE
    next_version INTEGER;
BEGIN
    SELECT COALESCE(MAX(version_number), 0) + 1
    INTO next_version
    FROM legal_document_versions
    WHERE document_id = doc_id;
    
    RETURN next_version;
END;
$$ LANGUAGE plpgsql;

-- Função para verificar se assertion tem fontes
CREATE OR REPLACE FUNCTION assertion_has_sources(assertion_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM assertion_sources 
        WHERE assertion_id = assertion_uuid
    );
END;
$$ LANGUAGE plpgsql;

-- Função para busca semântica em fontes
CREATE OR REPLACE FUNCTION search_legal_sources(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    source_type source_type,
    reference TEXT,
    excerpt TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ls.id,
        ls.source_type,
        ls.reference,
        ls.excerpt,
        1 - (ls.embedding <=> query_embedding) AS similarity
    FROM legal_sources ls
    WHERE ls.embedding IS NOT NULL
    AND 1 - (ls.embedding <=> query_embedding) > match_threshold
    ORDER BY ls.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 16. VIEWS ÚTEIS
-- ============================================================================

-- View: Casos com contagem de documentos
CREATE OR REPLACE VIEW cases_with_stats AS
SELECT 
    c.*,
    la.slug AS legal_area_slug,
    la.name AS legal_area_name,
    COUNT(ld.id) AS documents_count
FROM cases c
JOIN legal_areas la ON la.id = c.legal_area_id
LEFT JOIN legal_documents ld ON ld.case_id = c.id
GROUP BY c.id, la.slug, la.name;

-- View: Documentos com informações completas
CREATE OR REPLACE VIEW documents_with_details AS
SELECT 
    ld.*,
    lpt.slug AS piece_type_slug,
    lpt.name AS piece_type_name,
    lpt.legal_basis,
    c.title AS case_title,
    c.user_id,
    (SELECT COUNT(*) FROM legal_document_versions WHERE document_id = ld.id) AS versions_count,
    (SELECT MAX(version_number) FROM legal_document_versions WHERE document_id = ld.id) AS latest_version
FROM legal_documents ld
JOIN legal_piece_types lpt ON lpt.id = ld.piece_type_id
JOIN cases c ON c.id = ld.case_id;

-- View: Assertions com status de validação
CREATE OR REPLACE VIEW assertions_with_validation AS
SELECT 
    la.*,
    assertion_has_sources(la.id) AS has_sources,
    (SELECT COUNT(*) FROM assertion_sources WHERE assertion_id = la.id) AS sources_count
FROM legal_assertions la;

-- ============================================================================
-- FIM DO SCHEMA
-- ============================================================================
-- 
-- Para verificar se tudo foi criado corretamente:
-- 
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name;
--
-- ============================================================================
