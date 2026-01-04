"""
Testes de integração para rotas de Assertions.

⚠️ CORAÇÃO DO SISTEMA

LEIS TESTADAS:
- LEI 2: Nenhuma afirmação sem fonte
- LEI 5: IA produz assertions, não texto final

Testa:
- CRUD de assertions
- Vinculação de fontes
- Validação jurídica
"""
import pytest
from httpx import AsyncClient
from uuid import UUID


class TestAssertionsRoutes:
    """Testes para /api/v1/assertions"""
    
    # ==================== HELPERS ====================
    
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
    
    async def create_document(self, client: AsyncClient, case_id: str) -> str:
        """Cria documento e retorna ID."""
        response = await client.post(
            f"/api/v1/cases/{case_id}/documents",
            json={"piece_type_slug": "peticao-inicial"}
        )
        return response.json()["id"]
    
    async def create_version(self, client: AsyncClient, doc_id: str) -> str:
        """Cria versão e retorna ID."""
        response = await client.post(
            f"/api/v1/documents/{doc_id}/versions",
            json={
                "created_by": "agent",
                "agent_name": "Agente Teste"
            }
        )
        return response.json()["id"]
    
    async def create_source(self, client: AsyncClient) -> str:
        """Cria fonte e retorna ID."""
        response = await client.post(
            "/api/v1/sources",
            json={
                "source_type": "lei",
                "reference": "CPC, art. 999",
                "excerpt": "Texto de teste para fonte jurídica."
            }
        )
        return response.json()["id"]
    
    
    # ==================== CREATE ASSERTION ====================
    
    @pytest.mark.asyncio
    async def test_create_assertion_success(
        self,
        seeded_client: AsyncClient,
        assertion_payload: dict
    ):
        """Deve criar assertion com sucesso."""
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json=assertion_payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["assertion_type"] == assertion_payload["type"]
        assert data["confidence_level"] == assertion_payload["confidence_level"]
        assert data["position"] == 1
    
    
    @pytest.mark.asyncio
    async def test_create_assertion_positions_increment(
        self,
        seeded_client: AsyncClient,
        assertion_payload: dict
    ):
        """Posições das assertions devem incrementar."""
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        # Criar 3 assertions
        for i in range(3):
            payload = assertion_payload.copy()
            payload["text"] = f"Afirmação {i+1} com texto suficiente para validação."
            
            response = await seeded_client.post(
                f"/api/v1/document-versions/{version_id}/assertions",
                json=payload
            )
            
            assert response.json()["position"] == i + 1
    
    
    # ==================== BULK CREATE ====================
    
    @pytest.mark.asyncio
    async def test_create_assertions_bulk(
        self,
        seeded_client: AsyncClient
    ):
        """
        Deve criar múltiplas assertions de uma vez.
        
        ⚠️ LEI 5: Este é o método usado pelo pipeline de IA.
        """
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions/bulk",
            json={
                "document_version_id": version_id,
                "assertions": [
                    {
                        "text": "Primeira afirmação jurídica com texto suficiente.",
                        "type": "fato",
                        "confidence_level": "alto"
                    },
                    {
                        "text": "Segunda afirmação jurídica com texto suficiente.",
                        "type": "fundamento",
                        "confidence_level": "medio"
                    },
                    {
                        "text": "Terceira afirmação jurídica com texto suficiente.",
                        "type": "pedido",
                        "confidence_level": "alto"
                    }
                ]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["created_count"] == 3
        assert len(data["assertions"]) == 3
    
    
    # ==================== LIST ASSERTIONS ====================
    
    @pytest.mark.asyncio
    async def test_list_version_assertions(
        self,
        seeded_client: AsyncClient,
        assertion_payload: dict
    ):
        """Deve listar assertions da versão."""
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        # Criar 2 assertions
        for i in range(2):
            payload = assertion_payload.copy()
            payload["text"] = f"Afirmação {i+1} com texto suficiente para teste."
            await seeded_client.post(
                f"/api/v1/document-versions/{version_id}/assertions",
                json=payload
            )
        
        response = await seeded_client.get(
            f"/api/v1/document-versions/{version_id}/assertions"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 2
        assert data["total"] == 2
    
    
    # ==================== LINK SOURCE ====================
    
    @pytest.mark.asyncio
    async def test_link_source_to_assertion(
        self,
        seeded_client: AsyncClient,
        assertion_payload: dict
    ):
        """
        Deve vincular fonte a assertion.
        
        ⚠️ LEI 2: Este é o método que torna assertion válida.
        """
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        # Criar assertion
        assertion_response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json=assertion_payload
        )
        assertion_id = assertion_response.json()["id"]
        
        # Criar fonte
        source_id = await self.create_source(seeded_client)
        
        # Vincular
        response = await seeded_client.post(
            f"/api/v1/assertions/{assertion_id}/sources",
            json={"source_id": source_id}
        )
        
        assert response.status_code == 201
        assert "message" in response.json()
    
    
    @pytest.mark.asyncio
    async def test_unlink_source_from_assertion(
        self,
        seeded_client: AsyncClient,
        assertion_payload: dict
    ):
        """Deve desvincular fonte de assertion."""
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        # Criar assertion
        assertion_response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json=assertion_payload
        )
        assertion_id = assertion_response.json()["id"]
        
        # Criar e vincular fonte
        source_id = await self.create_source(seeded_client)
        await seeded_client.post(
            f"/api/v1/assertions/{assertion_id}/sources",
            json={"source_id": source_id}
        )
        
        # Desvincular
        response = await seeded_client.delete(
            f"/api/v1/assertions/{assertion_id}/sources/{source_id}"
        )
        
        assert response.status_code == 204
    
    
    # ==================== VALIDATION ====================
    
    @pytest.mark.asyncio
    async def test_validate_assertion_without_source(
        self,
        seeded_client: AsyncClient,
        assertion_payload: dict
    ):
        """
        ⚠️ LEI 2: Assertion sem fonte NÃO é válida.
        """
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        # Criar assertion SEM fonte
        assertion_response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json=assertion_payload
        )
        assertion_id = assertion_response.json()["id"]
        
        # Validar
        response = await seeded_client.get(
            f"/api/v1/assertions/{assertion_id}/validate"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # LEI 2: Deve ser INVÁLIDA
        assert data["is_valid"] == False
        assert data["error"] is not None
        assert "fonte" in data["error"].lower()
    
    
    @pytest.mark.asyncio
    async def test_validate_assertion_with_source(
        self,
        seeded_client: AsyncClient,
        assertion_payload: dict
    ):
        """
        ⚠️ LEI 2: Assertion COM fonte é válida.
        """
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        # Criar assertion
        assertion_response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json=assertion_payload
        )
        assertion_id = assertion_response.json()["id"]
        
        # Criar e vincular fonte
        source_id = await self.create_source(seeded_client)
        await seeded_client.post(
            f"/api/v1/assertions/{assertion_id}/sources",
            json={"source_id": source_id}
        )
        
        # Validar
        response = await seeded_client.get(
            f"/api/v1/assertions/{assertion_id}/validate"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # LEI 2: Deve ser VÁLIDA
        assert data["is_valid"] == True
        assert data["error"] is None
    
    
    @pytest.mark.asyncio
    async def test_validate_assertion_low_confidence_without_source(
        self,
        seeded_client: AsyncClient
    ):
        """
        ⚠️ LEI 2: Assertion com confidence=baixo é válida mesmo sem fonte.
        """
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        # Criar assertion com confidence BAIXO
        assertion_response = await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json={
                "text": "Afirmação com baixa confiança que não precisa de fonte.",
                "type": "tese",
                "confidence_level": "baixo"  # Baixa confiança
            }
        )
        assertion_id = assertion_response.json()["id"]
        
        # Validar
        response = await seeded_client.get(
            f"/api/v1/assertions/{assertion_id}/validate"
        )
        
        data = response.json()
        
        # LEI 2: Exceção - baixa confiança é válida sem fonte
        assert data["is_valid"] == True
    
    
    @pytest.mark.asyncio
    async def test_validate_version_juridically(
        self,
        seeded_client: AsyncClient,
        assertion_payload: dict
    ):
        """Deve validar todas as assertions de uma versão."""
        case_id = await self.create_case(seeded_client)
        doc_id = await self.create_document(seeded_client, case_id)
        version_id = await self.create_version(seeded_client, doc_id)
        
        # Criar assertion SEM fonte
        await seeded_client.post(
            f"/api/v1/document-versions/{version_id}/assertions",
            json=assertion_payload
        )
        
        # Validar versão
        response = await seeded_client.get(
            f"/api/v1/document-versions/{version_id}/validate"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Versão deve ser inválida (assertion sem fonte)
        assert data["is_valid"] == False
        assert data["can_render"] == False
        assert len(data["errors"]) > 0
