"""
Testes de integração para rotas de Rendering.

⚠️ LEI 4: Texto final é DERIVADO, nunca primário.

Testa:
- Renderização de documentos
- Validação antes de renderizar
- Regeneração
"""
import pytest
from httpx import AsyncClient


class TestRenderingRoutes:
    """Testes para /api/v1/rendering"""
    
    # ==================== HELPERS ====================
    
    async def setup_valid_version(self, client: AsyncClient) -> str:
        """
        Cria caso → documento → versão → assertion → fonte vinculada.
        
        Retorna version_id com assertions válidas.
        """
        # Criar caso
        case_response = await client.post(
            "/api/v1/cases",
            json={
                "legal_area_slug": "civil",
                "title": "Caso de Teste para Renderização"
            }
        )
        case_id = case_response.json()["id"]
        
        # Criar documento
        doc_response = await client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        doc_id = doc_response.json()["id"]
        
        # Criar versão
        version_response = await client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json={
                "created_by": "agent",
                "agent_name": "Agente Teste"
            }
        )
        version_id = version_response.json()["id"]
        
        # Criar assertion
        assertion_response = await client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={
                "text": "Nos termos do art. 319 do CPC, a petição inicial deve conter a exposição dos fatos.",
                "type": "fundamento",
                "confidence_level": "alto"
            }
        )
        assertion_id = assertion_response.json()["id"]
        
        # Criar fonte
        source_response = await client.post(
            "/api/v1/sources",
            json={
                "source_type": "lei",
                "reference": "CPC, art. 319",
                "excerpt": "A petição inicial indicará o juízo a que é dirigida..."
            }
        )
        source_id = source_response.json()["id"]
        
        # Vincular fonte (torna assertion válida)
        await client.post(
            f"/api/v1/assertions/{assertion_id}/sources",
            json={"source_id": source_id}
        )
        
        return version_id
    
    async def setup_invalid_version(self, client: AsyncClient) -> str:
        """
        Cria versão com assertion SEM fonte (inválida).
        
        Retorna version_id com assertions INválidas.
        """
        # Criar caso
        case_response = await client.post(
            "/api/v1/cases",
            json={
                "legal_area_slug": "civil",
                "title": "Caso Inválido"
            }
        )
        case_id = case_response.json()["id"]
        
        # Criar documento
        doc_response = await client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        doc_id = doc_response.json()["id"]
        
        # Criar versão
        version_response = await client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json={
                "created_by": "human",
                "agent_name": None
            }
        )
        version_id = version_response.json()["id"]
        
        # Criar assertion SEM fonte
        await client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={
                "text": "Afirmação sem fonte vinculada - juridicamente inválida.",
                "type": "fato",
                "confidence_level": "alto"  # Alta confiança precisa de fonte
            }
        )
        
        return version_id
    
    
    # ==================== RENDER VERSION ====================
    
    @pytest.mark.asyncio
    async def test_render_version_success(
        self,
        seeded_client: AsyncClient
    ):
        """
        Deve renderizar versão válida.
        
        ⚠️ LEI 4: Texto é derivado das assertions.
        """
        version_id = await self.setup_valid_version(seeded_client)
        
        response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["render_format"] == "markdown"
        assert "rendered_text" in data
        assert len(data["rendered_text"]) > 0
        
        # LEI 4: Texto contém conteúdo das assertions
        assert "319" in data["rendered_text"] or "CPC" in data["rendered_text"]
    
    
    @pytest.mark.asyncio
    async def test_render_version_html(
        self,
        seeded_client: AsyncClient
    ):
        """Deve renderizar em HTML."""
        version_id = await self.setup_valid_version(seeded_client)
        
        response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "html"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["render_format"] == "html"
        assert "<" in data["rendered_text"]  # Contém tags HTML
    
    
    @pytest.mark.asyncio
    async def test_render_version_invalid_format(
        self,
        seeded_client: AsyncClient
    ):
        """Deve rejeitar formato inválido."""
        version_id = await self.setup_valid_version(seeded_client)
        
        response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "formato_invalido"}
        )
        
        assert response.status_code == 422 or response.status_code == 400
    
    
    # ==================== RENDER VALIDATION ====================
    
    @pytest.mark.asyncio
    async def test_render_version_without_sources_fails(
        self,
        seeded_client: AsyncClient
    ):
        """
        ⚠️ LEI 2 + LEI 4: Não pode renderizar sem fontes.
        
        Versão com assertions sem fonte NÃO pode ser renderizada.
        """
        version_id = await self.setup_invalid_version(seeded_client)
        
        response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        
        # Deve falhar com erro de validação jurídica
        assert response.status_code == 422
        data = response.json()
        
        assert data["detail"]["error"] == "JURIDICAL_VALIDATION_ERROR"
        assert "fonte" in data["detail"]["message"].lower() or "fonte" in data["detail"]["hint"].lower()
    
    
    # ==================== LIST RENDERINGS ====================
    
    @pytest.mark.asyncio
    async def test_list_version_renderings(
        self,
        seeded_client: AsyncClient
    ):
        """Deve listar renderizações de uma versão."""
        version_id = await self.setup_valid_version(seeded_client)
        
        # Criar renderização markdown
        await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        
        # Criar renderização html
        await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "html"}
        )
        
        # Listar
        response = await seeded_client.get(
            f"/api/v1/document-versions/{version_id}/renderings"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 2
        formats = [r["render_format"] for r in data["items"]]
        assert "markdown" in formats
        assert "html" in formats
    
    
    # ==================== GET RENDERING ====================
    
    @pytest.mark.asyncio
    async def test_get_specific_rendering(
        self,
        seeded_client: AsyncClient
    ):
        """Deve buscar renderização específica."""
        version_id = await self.setup_valid_version(seeded_client)
        
        # Criar renderização
        await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        
        # Buscar
        response = await seeded_client.get(
            f"/api/v1/document-versions/{version_id}/render/markdown"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["render_format"] == "markdown"
    
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_rendering(
        self,
        seeded_client: AsyncClient
    ):
        """Deve retornar 404 para renderização inexistente."""
        version_id = await self.setup_valid_version(seeded_client)
        
        response = await seeded_client.get(
            f"/api/v1/document-versions/{version_id}/render/markdown"
        )
        
        assert response.status_code == 404
    
    
    # ==================== REGENERATE ====================
    
    @pytest.mark.asyncio
    async def test_regenerate_rendering(
        self,
        seeded_client: AsyncClient
    ):
        """
        Deve regenerar renderização existente.
        
        ⚠️ LEI 4: Renderização pode ser regenerada a qualquer momento.
        """
        version_id = await self.setup_valid_version(seeded_client)
        
        # Criar renderização
        create_response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        rendering_id = create_response.json()["id"]
        original_text = create_response.json()["rendered_text"]
        
        # Regenerar
        response = await seeded_client.post(
            f"/api/v1/renderings/{rendering_id}/regenerate"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Texto pode ser igual (assertions não mudaram)
        assert "rendered_text" in data
    
    
    # ==================== DELETE ====================
    
    @pytest.mark.asyncio
    async def test_delete_rendering(
        self,
        seeded_client: AsyncClient
    ):
        """
        Deve deletar renderização.
        
        ⚠️ LEI 4: Isso é PERMITIDO porque texto é derivado.
        (Diferente de versões que são imutáveis)
        """
        version_id = await self.setup_valid_version(seeded_client)
        
        # Criar renderização
        create_response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/render",
            json={"format": "markdown"}
        )
        rendering_id = create_response.json()["id"]
        
        # Deletar
        response = await seeded_client.delete(
            f"/api/v1/renderings/{rendering_id}"
        )
        
        # LEI 4: Renderização PODE ser deletada
        assert response.status_code == 204
        
        # Verificar que não existe mais
        get_response = await seeded_client.get(
            f"/api/v1/document-versions/{version_id}/render/markdown"
        )
        assert get_response.status_code == 404
