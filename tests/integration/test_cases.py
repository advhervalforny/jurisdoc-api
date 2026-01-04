"""
Testes de integração para rotas de Cases.

Testa:
- CRUD de casos
- Validações de área jurídica
- Ownership de casos
"""
import pytest
from httpx import AsyncClient
from uuid import UUID


class TestCasesRoutes:
    """Testes para /api/v1/cases"""
    
    # ==================== CREATE ====================
    
    @pytest.mark.asyncio
    async def test_create_case_success(
        self,
        seeded_client: AsyncClient,
        case_payload: dict
    ):
        """Deve criar caso com sucesso."""
        response = await seeded_client.post(
            "/api/v1/cases",
            json=case_payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["title"] == case_payload["title"]
        assert data["description"] == case_payload["description"]
        assert UUID(data["id"])  # Válido UUID
    
    
    @pytest.mark.asyncio
    async def test_create_case_invalid_area(
        self,
        seeded_client: AsyncClient
    ):
        """Deve rejeitar área jurídica inválida."""
        response = await seeded_client.post(
            "/api/v1/cases",
            json={
                "legal_area_slug": "trabalhista",  # Não existe
                "title": "Caso de Teste"
            }
        )
        
        assert response.status_code == 400
        assert "não encontrada" in response.json()["detail"].lower()
    
    
    @pytest.mark.asyncio
    async def test_create_case_missing_title(
        self,
        seeded_client: AsyncClient
    ):
        """Deve rejeitar caso sem título."""
        response = await seeded_client.post(
            "/api/v1/cases",
            json={
                "legal_area_slug": "civil"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    
    # ==================== LIST ====================
    
    @pytest.mark.asyncio
    async def test_list_cases_empty(
        self,
        seeded_client: AsyncClient
    ):
        """Deve retornar lista vazia quando não há casos."""
        response = await seeded_client.get("/api/v1/cases")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["items"] == []
        assert data["total"] == 0
    
    
    @pytest.mark.asyncio
    async def test_list_cases_with_data(
        self,
        seeded_client: AsyncClient,
        case_payload: dict
    ):
        """Deve listar casos criados."""
        # Criar 3 casos
        for i in range(3):
            payload = case_payload.copy()
            payload["title"] = f"Caso {i+1}"
            await seeded_client.post("/api/v1/cases", json=payload)
        
        response = await seeded_client.get("/api/v1/cases")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 3
        assert data["total"] == 3
    
    
    @pytest.mark.asyncio
    async def test_list_cases_filter_by_area(
        self,
        seeded_client: AsyncClient
    ):
        """Deve filtrar casos por área jurídica."""
        # Criar caso civil
        await seeded_client.post("/api/v1/cases", json={
            "legal_area_slug": "civil",
            "title": "Caso Civil"
        })
        
        # Criar caso penal
        await seeded_client.post("/api/v1/cases", json={
            "legal_area_slug": "penal",
            "title": "Caso Penal"
        })
        
        # Filtrar por civil
        response = await seeded_client.get(
            "/api/v1/cases",
            params={"legal_area_slug": "civil"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Caso Civil"
    
    
    @pytest.mark.asyncio
    async def test_list_cases_pagination(
        self,
        seeded_client: AsyncClient,
        case_payload: dict
    ):
        """Deve paginar resultados."""
        # Criar 5 casos
        for i in range(5):
            payload = case_payload.copy()
            payload["title"] = f"Caso {i+1}"
            await seeded_client.post("/api/v1/cases", json=payload)
        
        # Página 1 (2 items)
        response = await seeded_client.get(
            "/api/v1/cases",
            params={"skip": 0, "limit": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["skip"] == 0
        assert data["limit"] == 2
    
    
    # ==================== GET ====================
    
    @pytest.mark.asyncio
    async def test_get_case_success(
        self,
        seeded_client: AsyncClient,
        case_payload: dict
    ):
        """Deve buscar caso por ID."""
        # Criar caso
        create_response = await seeded_client.post(
            "/api/v1/cases",
            json=case_payload
        )
        case_id = create_response.json()["id"]
        
        # Buscar
        response = await seeded_client.get(f"/api/v1/cases/{case_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == case_id
        assert data["title"] == case_payload["title"]
        assert "documents" in data  # Inclui documentos
    
    
    @pytest.mark.asyncio
    async def test_get_case_not_found(
        self,
        seeded_client: AsyncClient
    ):
        """Deve retornar 404 para caso inexistente."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await seeded_client.get(f"/api/v1/cases/{fake_id}")
        
        assert response.status_code == 404
    
    
    # ==================== UPDATE ====================
    
    @pytest.mark.asyncio
    async def test_update_case_success(
        self,
        seeded_client: AsyncClient,
        case_payload: dict
    ):
        """Deve atualizar caso."""
        # Criar caso
        create_response = await seeded_client.post(
            "/api/v1/cases",
            json=case_payload
        )
        case_id = create_response.json()["id"]
        
        # Atualizar
        response = await seeded_client.patch(
            f"/api/v1/cases/{case_id}",
            json={"title": "Título Atualizado"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "Título Atualizado"
    
    
    @pytest.mark.asyncio
    async def test_update_case_not_found(
        self,
        seeded_client: AsyncClient
    ):
        """Deve retornar 404 ao atualizar caso inexistente."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await seeded_client.patch(
            f"/api/v1/cases/{fake_id}",
            json={"title": "Novo"}
        )
        
        assert response.status_code == 404
    
    
    # ==================== DELETE ====================
    
    @pytest.mark.asyncio
    async def test_delete_case_success(
        self,
        seeded_client: AsyncClient,
        case_payload: dict
    ):
        """Deve deletar caso."""
        # Criar caso
        create_response = await seeded_client.post(
            "/api/v1/cases",
            json=case_payload
        )
        case_id = create_response.json()["id"]
        
        # Deletar
        response = await seeded_client.delete(f"/api/v1/cases/{case_id}")
        
        assert response.status_code == 204
        
        # Verificar que não existe mais
        get_response = await seeded_client.get(f"/api/v1/cases/{case_id}")
        assert get_response.status_code == 404
    
    
    @pytest.mark.asyncio
    async def test_delete_case_not_found(
        self,
        seeded_client: AsyncClient
    ):
        """Deve retornar 404 ao deletar caso inexistente."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await seeded_client.delete(f"/api/v1/cases/{fake_id}")
        
        assert response.status_code == 404
