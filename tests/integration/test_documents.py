"""
Testes de integração para rotas de Documents.

⚠️ LEIS TESTADAS:
- LEI 1: Documento ≠ Texto (documento criado vazio)
- LEI 3: Versionamento obrigatório (versões imutáveis)

Testa:
- CRUD de documentos
- Criação de versões
- Proibição de delete de versões
"""
import pytest
from httpx import AsyncClient
from uuid import UUID


class TestDocumentsRoutes:
    """Testes para /api/v1/documents"""
    
    # ==================== HELPER ====================
    
    async def create_case(self, client: AsyncClient) -> str:
        """Cria caso e retorna ID."""
        response = await client.post(
            "/api/v1/cases",
            json={
                "legal_area_slug": "civil",
                "title": "Caso de Teste"
            }
        )
        return response.json()["id"]
    
    
    # ==================== CREATE DOCUMENT ====================
    
    @pytest.mark.asyncio
    async def test_create_document_success(
        self,
        seeded_client: AsyncClient,
        document_payload: dict
    ):
        """
        Deve criar documento com sucesso.
        
        ⚠️ LEI 1: Documento é criado VAZIO (sem texto).
        """
        case_id = await self.create_case(seeded_client)
        
        response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json=document_payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["case_id"] == case_id
        assert data["status"] == "draft"
        # LEI 1: Não há campo "text" no documento
        assert "text" not in data
        assert "content" not in data
    
    
    @pytest.mark.asyncio
    async def test_create_document_invalid_piece_type(
        self,
        seeded_client: AsyncClient
    ):
        """Deve rejeitar tipo de peça inválido."""
        case_id = await self.create_case(seeded_client)
        
        response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={"piece_type_slug": "tipo-invalido"}
        )
        
        assert response.status_code == 400
    
    
    @pytest.mark.asyncio
    async def test_create_document_wrong_area(
        self,
        seeded_client: AsyncClient
    ):
        """Deve rejeitar tipo de peça de outra área."""
        # Criar caso CIVIL
        case_id = await self.create_case(seeded_client)
        
        # Tentar criar documento PENAL no caso civil
        response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={"piece_type_slug": "denuncia"}  # Penal
        )
        
        assert response.status_code == 400
        assert "não pertence" in response.json()["detail"].lower()
    
    
    # ==================== LIST DOCUMENTS ====================
    
    @pytest.mark.asyncio
    async def test_list_case_documents(
        self,
        seeded_client: AsyncClient,
        document_payload: dict
    ):
        """Deve listar documentos do caso."""
        case_id = await self.create_case(seeded_client)
        
        # Criar 2 documentos
        await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json=document_payload
        )
        await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={"piece_type_slug": "contestacao"}
        )
        
        response = await seeded_client.get(
            f"/api/v1/cases/{case_id}/documents"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 2
        assert data["total"] == 2
    
    
    # ==================== GET DOCUMENT ====================
    
    @pytest.mark.asyncio
    async def test_get_document_with_versions(
        self,
        seeded_client: AsyncClient,
        document_payload: dict,
        version_payload: dict
    ):
        """Deve buscar documento com suas versões."""
        case_id = await self.create_case(seeded_client)
        
        # Criar documento
        doc_response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json=document_payload
        )
        doc_id = doc_response.json()["id"]
        
        # Criar versão
        await seeded_client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json=version_payload
        )
        
        # Buscar documento
        response = await seeded_client.get(f"/api/v1/documents/{doc_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == doc_id
        assert "versions" in data
        assert len(data["versions"]) == 1
    
    
    # ==================== CREATE VERSION ====================
    
    @pytest.mark.asyncio
    async def test_create_version_success(
        self,
        seeded_client: AsyncClient,
        document_payload: dict,
        version_payload: dict
    ):
        """
        Deve criar versão com sucesso.
        
        ⚠️ LEI 3: Sempre cria NOVA versão.
        """
        case_id = await self.create_case(seeded_client)
        
        # Criar documento
        doc_response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json=document_payload
        )
        doc_id = doc_response.json()["id"]
        
        # Criar versão 1
        response1 = await seeded_client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json=version_payload
        )
        
        assert response1.status_code == 201
        data1 = response1.json()
        assert data1["version_number"] == 1
        
        # Criar versão 2
        response2 = await seeded_client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json=version_payload
        )
        
        assert response2.status_code == 201
        data2 = response2.json()
        assert data2["version_number"] == 2  # LEI 3: Nova versão
    
    
    @pytest.mark.asyncio
    async def test_version_numbers_increment(
        self,
        seeded_client: AsyncClient,
        document_payload: dict,
        version_payload: dict
    ):
        """
        ⚠️ LEI 3: Versões têm números sequenciais.
        """
        case_id = await self.create_case(seeded_client)
        
        doc_response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json=document_payload
        )
        doc_id = doc_response.json()["id"]
        
        # Criar 5 versões
        for i in range(5):
            response = await seeded_client.post(
                f"/api/v1/documents/{doc_id}/versions",
                json=version_payload
            )
            assert response.json()["version_number"] == i + 1
    
    
    # ==================== DELETE VERSION (PROIBIDO) ====================
    
    @pytest.mark.asyncio
    async def test_delete_version_forbidden(
        self,
        seeded_client: AsyncClient,
        document_payload: dict,
        version_payload: dict
    ):
        """
        ⚠️ LEI 3: Versões são IMUTÁVEIS e NÃO podem ser deletadas.
        
        Este teste DEVE falhar com 403 Forbidden.
        """
        case_id = await self.create_case(seeded_client)
        
        # Criar documento
        doc_response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json=document_payload
        )
        doc_id = doc_response.json()["id"]
        
        # Criar versão
        version_response = await seeded_client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json=version_payload
        )
        version_id = version_response.json()["id"]
        
        # Tentar deletar versão
        response = await seeded_client.delete(
            f"/api/v1/document-versions/{version_id}"
        )
        
        # LEI 3: DEVE ser proibido
        assert response.status_code == 403
        assert "LEI 3" in response.json()["detail"] or "imutáv" in response.json()["detail"].lower()
    
    
    # ==================== UPDATE STATUS ====================
    
    @pytest.mark.asyncio
    async def test_update_document_status(
        self,
        seeded_client: AsyncClient,
        document_payload: dict
    ):
        """Deve atualizar status do documento."""
        case_id = await self.create_case(seeded_client)
        
        # Criar documento
        doc_response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json=document_payload
        )
        doc_id = doc_response.json()["id"]
        
        assert doc_response.json()["status"] == "draft"
        
        # Atualizar status
        response = await seeded_client.patch(
            f"/api/v1/documents/{doc_id}/status",
            json={"status": "generated"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "generated"
    
    
    # ==================== LIST VERSIONS ====================
    
    @pytest.mark.asyncio
    async def test_list_document_versions(
        self,
        seeded_client: AsyncClient,
        document_payload: dict,
        version_payload: dict
    ):
        """Deve listar versões do documento."""
        case_id = await self.create_case(seeded_client)
        
        # Criar documento
        doc_response = await seeded_client.post(
            f"/api/v1/cases/{case_id}/documents",
            json=document_payload
        )
        doc_id = doc_response.json()["id"]
        
        # Criar 3 versões
        for _ in range(3):
            await seeded_client.post(
                f"/api/v1/documents/{doc_id}/versions",
                json=version_payload
            )
        
        # Listar
        response = await seeded_client.get(
            f"/api/v1/documents/{doc_id}/versions"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 3
        assert data["total"] == 3
        
        # Verificar ordem (mais recente primeiro)
        versions = [v["version_number"] for v in data["items"]]
        assert versions == [3, 2, 1]
