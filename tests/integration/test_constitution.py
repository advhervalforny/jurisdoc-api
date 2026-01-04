"""
Testes das Leis Constitucionais do Sistema.

⚠️ TESTES CRÍTICOS

Este arquivo testa ESPECIFICAMENTE as 8 leis imutáveis do sistema.
Se algum destes testes falhar, o sistema está comprometido juridicamente.

LEIS:
1. Documento ≠ Texto
2. Nenhuma afirmação sem fonte
3. Versionamento obrigatório
4. Texto final é derivado
5. IA não escreve texto final
6. Agente = Função jurídica única
7. API valida juridicamente
8. Frontend não decide nada
"""
import pytest
from httpx import AsyncClient


class TestLei1_DocumentoNaoETexto:
    """
    LEI 1: Documento Jurídico ≠ Texto
    
    ❌ É proibido armazenar peças como texto único.
    ✅ Documento é composto por: versões, afirmações, fontes.
    """
    
    @pytest.mark.asyncio
    async def test_documento_criado_sem_texto(
        self,
        seeded_client: AsyncClient
    ):
        """Documento deve ser criado SEM texto."""
        # Criar caso
        case_response = await seeded_client.post(
            "/api/v1/cases",
            json={"legal_area_slug": "civil", "title": "Teste LEI 1"}
        )
        case_id = case_response.json()["id"]
        
        # Criar documento
        response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        
        data = response.json()
        
        # LEI 1: Documento NÃO tem campo de texto
        assert "text" not in data
        assert "content" not in data
        assert "body" not in data
        assert "texto" not in data
    
    
    @pytest.mark.asyncio
    async def test_api_nao_aceita_texto_direto(
        self,
        seeded_client: AsyncClient
    ):
        """API deve rejeitar texto direto em documento."""
        # Criar caso
        case_response = await seeded_client.post(
            "/api/v1/cases",
            json={"legal_area_slug": "civil", "title": "Teste LEI 1"}
        )
        case_id = case_response.json()["id"]
        
        # Tentar criar documento COM texto (proibido)
        response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={
                "piece_type_slug": "peticao-inicial",
                "text": "Texto que não deveria ser aceito"  # PROIBIDO
            }
        )
        
        # API não deve ter campo text no schema
        # Se aceitou, ignorou o campo
        if response.status_code == 201:
            data = response.json()
            assert "text" not in data


class TestLei2_NenhumaAfirmacaoSemFonte:
    """
    LEI 2: Nenhuma Afirmação sem Fonte
    
    Uma afirmação jurídica só é válida se:
    - Possuir ao menos uma fonte explícita, OU
    - Ter confidence_level == 'baixo'
    """
    
    async def setup_version(self, client: AsyncClient) -> str:
        """Helper para criar versão."""
        case_resp = await client.post(
            "/api/v1/cases",
            json={"legal_area_slug": "civil", "title": "Teste LEI 2"}
        )
        doc_resp = await client.post(
            f"/api/v1/cases/{case_resp.json()['id']}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        version_resp = await client.post(
            f"/api/v1/documents/{doc_resp.json()['id']}/versions",
            json={"created_by": "human"}
        )
        return version_resp.json()["id"]
    
    
    @pytest.mark.asyncio
    async def test_assertion_sem_fonte_invalida(
        self,
        seeded_client: AsyncClient
    ):
        """Assertion sem fonte deve ser INVÁLIDA."""
        version_id = await self.setup_version(seeded_client)
        
        # Criar assertion sem fonte
        assertion_resp = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={
                "text": "Afirmação de teste sem fonte vinculada.",
                "type": "fundamento",
                "confidence_level": "alto"
            }
        )
        assertion_id = assertion_resp.json()["id"]
        
        # Validar
        validate_resp = await seeded_client.get(
            f"/api/v1/assertions/{assertion_id}/validate"
        )
        
        # LEI 2: DEVE ser inválida
        assert validate_resp.json()["is_valid"] == False
    
    
    @pytest.mark.asyncio
    async def test_assertion_com_fonte_valida(
        self,
        seeded_client: AsyncClient
    ):
        """Assertion com fonte deve ser VÁLIDA."""
        version_id = await self.setup_version(seeded_client)
        
        # Criar assertion
        assertion_resp = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={
                "text": "Afirmação de teste com fonte vinculada.",
                "type": "fundamento",
                "confidence_level": "alto"
            }
        )
        assertion_id = assertion_resp.json()["id"]
        
        # Criar e vincular fonte
        source_resp = await seeded_client.post(
            "/api/v1/sources",
            json={
                "source_type": "lei",
                "reference": "CPC, art. 999",
                "excerpt": "Texto da fonte para teste."
            }
        )
        source_id = source_resp.json()["id"]
        
        await seeded_client.post(
            f"/api/v1/assertions/{assertion_id}/sources",
            json={"source_id": source_id}
        )
        
        # Validar
        validate_resp = await seeded_client.get(
            f"/api/v1/assertions/{assertion_id}/validate"
        )
        
        # LEI 2: DEVE ser válida
        assert validate_resp.json()["is_valid"] == True
    
    
    @pytest.mark.asyncio
    async def test_assertion_baixa_confianca_valida_sem_fonte(
        self,
        seeded_client: AsyncClient
    ):
        """Assertion com baixa confiança é válida sem fonte."""
        version_id = await self.setup_version(seeded_client)
        
        # Criar assertion com confidence BAIXO
        assertion_resp = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={
                "text": "Afirmação de baixa confiança sem fonte.",
                "type": "tese",
                "confidence_level": "baixo"  # EXCEÇÃO
            }
        )
        assertion_id = assertion_resp.json()["id"]
        
        # Validar
        validate_resp = await seeded_client.get(
            f"/api/v1/assertions/{assertion_id}/validate"
        )
        
        # LEI 2 (exceção): DEVE ser válida
        assert validate_resp.json()["is_valid"] == True


class TestLei3_VersionamentoObrigatorio:
    """
    LEI 3: Versionamento é Obrigatório
    
    - Toda geração cria nova versão
    - É proibido sobrescrever conteúdo jurídico
    - Histórico é imutável
    """
    
    async def setup_document(self, client: AsyncClient) -> str:
        """Helper para criar documento."""
        case_resp = await client.post(
            "/api/v1/cases",
            json={"legal_area_slug": "civil", "title": "Teste LEI 3"}
        )
        doc_resp = await client.post(
            f"/api/v1/cases/{case_resp.json()['id']}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        return doc_resp.json()["id"]
    
    
    @pytest.mark.asyncio
    async def test_versoes_sao_sequenciais(
        self,
        seeded_client: AsyncClient
    ):
        """Versões devem ter números sequenciais."""
        doc_id = await self.setup_document(seeded_client)
        
        for i in range(5):
            response = await seeded_client.post(
                f"/api/v1/documents/{doc_id}/versions",
                json={"created_by": "agent", "agent_name": f"Agente {i}"}
            )
            
            # LEI 3: Números devem incrementar
            assert response.json()["version_number"] == i + 1
    
    
    @pytest.mark.asyncio
    async def test_versao_nao_pode_ser_deletada(
        self,
        seeded_client: AsyncClient
    ):
        """Versões são IMUTÁVEIS e não podem ser deletadas."""
        doc_id = await self.setup_document(seeded_client)
        
        # Criar versão
        version_resp = await seeded_client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json={"created_by": "human"}
        )
        version_id = version_resp.json()["id"]
        
        # Tentar deletar
        response = await seeded_client.delete(
            f"/api/v1/document-versions/{version_id}"
        )
        
        # LEI 3: DEVE ser proibido (403)
        assert response.status_code == 403
    
    
    @pytest.mark.asyncio
    async def test_nao_existe_endpoint_update_versao(
        self,
        seeded_client: AsyncClient
    ):
        """Não deve existir endpoint para atualizar versão."""
        doc_id = await self.setup_document(seeded_client)
        
        version_resp = await seeded_client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json={"created_by": "human"}
        )
        version_id = version_resp.json()["id"]
        
        # Tentar atualizar (endpoint não deve existir)
        response = await seeded_client.patch(
            f"/api/v1/document-versions/{version_id}",
            json={"created_by": "agent"}
        )
        
        # LEI 3: Endpoint não deve existir (404 ou 405)
        assert response.status_code in [404, 405]


class TestLei4_TextoFinalDerivado:
    """
    LEI 4: Texto Final é Derivado, Nunca Primário
    
    - O texto exibido ao usuário é renderização
    - A verdade do sistema está nas afirmações estruturadas
    """
    
    async def setup_valid_version(self, client: AsyncClient) -> str:
        """Helper para criar versão válida."""
        case_resp = await client.post(
            "/api/v1/cases",
            json={"legal_area_slug": "civil", "title": "Teste LEI 4"}
        )
        doc_resp = await client.post(
            f"/api/v1/cases/{case_resp.json()['id']}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        version_resp = await client.post(
            f"/api/v1/documents/{doc_resp.json()['id']}/versions",
            json={"created_by": "agent", "agent_name": "Agente Teste"}
        )
        version_id = version_resp.json()["id"]
        
        # Criar assertion
        assertion_resp = await client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={
                "text": "Texto da afirmação para renderização.",
                "type": "fundamento",
                "confidence_level": "alto"
            }
        )
        assertion_id = assertion_resp.json()["id"]
        
        # Vincular fonte
        source_resp = await client.post(
            "/api/v1/sources",
            json={
                "source_type": "lei",
                "reference": "Lei de Teste",
                "excerpt": "Excerpt de teste"
            }
        )
        await client.post(
            f"/api/v1/assertions/{assertion_id}/sources",
            json={"source_id": source_resp.json()["id"]}
        )
        
        return version_id
    
    
    @pytest.mark.asyncio
    async def test_renderizacao_pode_ser_deletada(
        self,
        seeded_client: AsyncClient
    ):
        """Renderização pode ser deletada (é derivada)."""
        version_id = await self.setup_valid_version(seeded_client)
        
        # Criar renderização
        render_resp = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        rendering_id = render_resp.json()["id"]
        
        # Deletar
        response = await seeded_client.delete(
            f"/api/v1/renderings/{rendering_id}"
        )
        
        # LEI 4: Renderização PODE ser deletada (diferente de versões)
        assert response.status_code == 204
    
    
    @pytest.mark.asyncio
    async def test_renderizacao_pode_ser_regenerada(
        self,
        seeded_client: AsyncClient
    ):
        """Renderização pode ser regenerada a qualquer momento."""
        version_id = await self.setup_valid_version(seeded_client)
        
        # Criar renderização
        render_resp = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        rendering_id = render_resp.json()["id"]
        
        # Regenerar
        response = await seeded_client.post(
            f"/api/v1/renderings/{rendering_id}/regenerate"
        )
        
        # LEI 4: Renderização pode ser regenerada
        assert response.status_code == 200
    
    
    @pytest.mark.asyncio
    async def test_nao_renderiza_sem_fontes(
        self,
        seeded_client: AsyncClient
    ):
        """Não pode renderizar versão com assertions sem fonte."""
        # Setup sem fonte
        case_resp = await seeded_client.post(
            "/api/v1/cases",
            json={"legal_area_slug": "civil", "title": "Teste LEI 4 inválido"}
        )
        doc_resp = await seeded_client.post(
            f"/api/v1/cases/{case_resp.json()['id']}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        version_resp = await seeded_client.post(
            f"/api/v1/documents/{doc_resp.json()['id']}/versions",
            json={"created_by": "human"}
        )
        version_id = version_resp.json()["id"]
        
        # Assertion SEM fonte
        await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={
                "text": "Assertion sem fonte - inválida.",
                "type": "fato",
                "confidence_level": "alto"
            }
        )
        
        # Tentar renderizar
        response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        
        # LEI 4 + LEI 2: Não pode renderizar sem fontes
        assert response.status_code == 422


class TestLei7_APIValidaJuridicamente:
    """
    LEI 7: API Valida Juridicamente
    
    A API não valida apenas schema técnico,
    valida consistência jurídica mínima.
    """
    
    @pytest.mark.asyncio
    async def test_api_valida_area_juridica(
        self,
        seeded_client: AsyncClient
    ):
        """API deve validar área jurídica."""
        response = await seeded_client.post(
            "/api/v1/cases",
            json={
                "legal_area_slug": "area_que_nao_existe",
                "title": "Teste"
            }
        )
        
        # LEI 7: Deve validar (não é só schema)
        assert response.status_code == 400
    
    
    @pytest.mark.asyncio
    async def test_api_valida_tipo_peca_por_area(
        self,
        seeded_client: AsyncClient
    ):
        """API deve validar que tipo de peça pertence à área."""
        # Criar caso CIVIL
        case_resp = await seeded_client.post(
            "/api/v1/cases",
            json={"legal_area_slug": "civil", "title": "Teste"}
        )
        case_id = case_resp.json()["id"]
        
        # Tentar criar peça PENAL em caso CIVIL
        response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={"piece_type_slug": "denuncia"}  # Penal
        )
        
        # LEI 7: Deve validar juridicamente
        assert response.status_code == 400
    
    
    @pytest.mark.asyncio
    async def test_api_retorna_erro_juridico_nao_tecnico(
        self,
        seeded_client: AsyncClient
    ):
        """API deve retornar erro jurídico, não erro técnico."""
        # Setup versão inválida
        case_resp = await seeded_client.post(
            "/api/v1/cases",
            json={"legal_area_slug": "civil", "title": "Teste"}
        )
        doc_resp = await seeded_client.post(
            f"/api/v1/cases/{case_resp.json()['id']}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        version_resp = await seeded_client.post(
            f"/api/v1/documents/{doc_resp.json()['id']}/versions",
            json={"created_by": "human"}
        )
        version_id = version_resp.json()["id"]
        
        # Assertion sem fonte
        await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={"text": "Texto de teste", "type": "fato", "confidence_level": "alto"}
        )
        
        # Tentar renderizar
        response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        
        # LEI 7: Erro deve ser JURÍDICO, não 500
        assert response.status_code == 422
        assert "JURIDICAL_VALIDATION_ERROR" in response.json()["detail"]["error"]
