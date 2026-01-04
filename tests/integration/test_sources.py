"""
Testes de integração para rotas de Sources.

Testa:
- CRUD de fontes jurídicas
- Hierarquia normativa
- Busca e filtros
"""
import pytest
from httpx import AsyncClient


class TestSourcesRoutes:
    """Testes para /api/v1/sources"""
    
    # ==================== CREATE ====================
    
    @pytest.mark.asyncio
    async def test_create_source_success(
        self,
        seeded_client: AsyncClient,
        source_payload: dict
    ):
        """Deve criar fonte com sucesso."""
        response = await seeded_client.post(
            "/api/v1/sources",
            json=source_payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["source_type"] == source_payload["source_type"]
        assert data["reference"] == source_payload["reference"]
    
    
    @pytest.mark.asyncio
    async def test_create_source_invalid_type(
        self,
        seeded_client: AsyncClient
    ):
        """Deve rejeitar tipo de fonte inválido."""
        response = await seeded_client.post(
            "/api/v1/sources",
            json={
                "source_type": "tipo_invalido",
                "reference": "Referência",
                "excerpt": "Texto suficiente para o teste."
            }
        )
        
        assert response.status_code == 422
    
    
    @pytest.mark.asyncio
    async def test_create_source_all_types(
        self,
        seeded_client: AsyncClient
    ):
        """Deve criar fontes de todos os tipos."""
        types = ["constituicao", "lei", "jurisprudencia", "doutrina", "argumentacao"]
        
        for source_type in types:
            response = await seeded_client.post(
                "/api/v1/sources",
                json={
                    "source_type": source_type,
                    "reference": f"Referência de {source_type}",
                    "excerpt": f"Texto de teste para fonte do tipo {source_type}."
                }
            )
            
            assert response.status_code == 201, f"Falhou para tipo: {source_type}"
            assert response.json()["source_type"] == source_type
    
    
    @pytest.mark.asyncio
    async def test_create_source_returns_existing(
        self,
        seeded_client: AsyncClient,
        source_payload: dict
    ):
        """Deve retornar fonte existente se duplicada."""
        # Criar primeira vez
        response1 = await seeded_client.post(
            "/api/v1/sources",
            json=source_payload
        )
        id1 = response1.json()["id"]
        
        # Criar segunda vez (mesmo payload)
        response2 = await seeded_client.post(
            "/api/v1/sources",
            json=source_payload
        )
        id2 = response2.json()["id"]
        
        # Deve retornar a mesma fonte
        assert id1 == id2
    
    
    # ==================== BULK CREATE ====================
    
    @pytest.mark.asyncio
    async def test_create_sources_bulk(
        self,
        seeded_client: AsyncClient
    ):
        """Deve criar múltiplas fontes de uma vez."""
        response = await seeded_client.post(
            "/api/v1/sources/bulk",
            json=[
                {
                    "source_type": "constituicao",
                    "reference": "CF, art. 1º",
                    "excerpt": "A República Federativa do Brasil..."
                },
                {
                    "source_type": "lei",
                    "reference": "CC, art. 1º",
                    "excerpt": "Toda pessoa é capaz de direitos e deveres..."
                }
            ]
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert len(data["items"]) == 2
    
    
    # ==================== SEARCH ====================
    
    @pytest.mark.asyncio
    async def test_search_sources_by_query(
        self,
        seeded_client: AsyncClient
    ):
        """Deve buscar fontes por texto."""
        # Criar algumas fontes
        await seeded_client.post(
            "/api/v1/sources",
            json={
                "source_type": "lei",
                "reference": "CPC, art. 319",
                "excerpt": "A petição inicial indicará..."
            }
        )
        await seeded_client.post(
            "/api/v1/sources",
            json={
                "source_type": "lei",
                "reference": "CPC, art. 320",
                "excerpt": "A petição será instruída..."
            }
        )
        await seeded_client.post(
            "/api/v1/sources",
            json={
                "source_type": "lei",
                "reference": "CC, art. 186",
                "excerpt": "Aquele que por ação ou omissão..."
            }
        )
        
        # Buscar por "CPC"
        response = await seeded_client.get(
            "/api/v1/sources",
            params={"query": "CPC"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve encontrar apenas as 2 do CPC
        assert len(data["items"]) >= 2
        for item in data["items"]:
            assert "CPC" in item["reference"] or "petição" in item["excerpt"].lower()
    
    
    @pytest.mark.asyncio
    async def test_search_sources_by_type(
        self,
        seeded_client: AsyncClient
    ):
        """Deve filtrar fontes por tipo."""
        # Criar fontes de tipos diferentes
        await seeded_client.post(
            "/api/v1/sources",
            json={
                "source_type": "constituicao",
                "reference": "CF, art. 5º",
                "excerpt": "Todos são iguais perante a lei..."
            }
        )
        await seeded_client.post(
            "/api/v1/sources",
            json={
                "source_type": "jurisprudencia",
                "reference": "STJ, REsp 123",
                "excerpt": "Ementa do julgado..."
            }
        )
        
        # Filtrar por constituição
        response = await seeded_client.get(
            "/api/v1/sources",
            params={"source_type": "constituicao"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for item in data["items"]:
            assert item["source_type"] == "constituicao"
    
    
    # ==================== GET ====================
    
    @pytest.mark.asyncio
    async def test_get_source_by_id(
        self,
        seeded_client: AsyncClient,
        source_payload: dict
    ):
        """Deve buscar fonte por ID."""
        # Criar
        create_response = await seeded_client.post(
            "/api/v1/sources",
            json=source_payload
        )
        source_id = create_response.json()["id"]
        
        # Buscar
        response = await seeded_client.get(f"/api/v1/sources/{source_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == source_id
        assert data["reference"] == source_payload["reference"]
    
    
    @pytest.mark.asyncio
    async def test_get_source_not_found(
        self,
        seeded_client: AsyncClient
    ):
        """Deve retornar 404 para fonte inexistente."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await seeded_client.get(f"/api/v1/sources/{fake_id}")
        
        assert response.status_code == 404
    
    
    @pytest.mark.asyncio
    async def test_get_source_by_reference(
        self,
        seeded_client: AsyncClient,
        source_payload: dict
    ):
        """Deve buscar fonte por tipo e referência."""
        # Criar
        await seeded_client.post(
            "/api/v1/sources",
            json=source_payload
        )
        
        # Buscar por referência
        response = await seeded_client.get(
            f"/api/v1/sources/by-reference/{source_payload['source_type']}/{source_payload['reference']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["reference"] == source_payload["reference"]
    
    
    # ==================== TYPES ====================
    
    @pytest.mark.asyncio
    async def test_list_source_types(
        self,
        seeded_client: AsyncClient
    ):
        """Deve listar tipos de fonte com hierarquia."""
        response = await seeded_client.get("/api/v1/sources/types")
        
        assert response.status_code == 200
        data = response.json()
        
        # Deve ter 5 tipos
        assert len(data) == 5
        
        # Verificar hierarquia
        types_by_order = {t["type"]: t["hierarchy_order"] for t in data}
        
        assert types_by_order["constituicao"] < types_by_order["lei"]
        assert types_by_order["lei"] < types_by_order["jurisprudencia"]
        assert types_by_order["jurisprudencia"] < types_by_order["doutrina"]
        assert types_by_order["doutrina"] < types_by_order["argumentacao"]
    
    
    # ==================== STATS ====================
    
    @pytest.mark.asyncio
    async def test_get_sources_stats(
        self,
        seeded_client: AsyncClient
    ):
        """Deve retornar estatísticas de fontes."""
        # Criar algumas fontes
        for i in range(3):
            await seeded_client.post(
                "/api/v1/sources",
                json={
                    "source_type": "lei",
                    "reference": f"Lei {i}",
                    "excerpt": f"Texto da lei número {i} para teste."
                }
            )
        
        response = await seeded_client.get("/api/v1/sources/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "by_type" in data
        assert "total" in data
        assert data["total"] >= 3
