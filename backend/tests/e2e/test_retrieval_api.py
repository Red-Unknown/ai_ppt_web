import pytest
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from app.api.v1.endpoints import retrieval


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(retrieval.router)
    return app


class TestRetrievalAPI:

    @pytest.mark.asyncio
    async def test_retrieve_endpoint_returns_200(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/qa/retrieve",
                json={
                    "query": "什么是轴向拉伸",
                    "lesson_id": "lesson_mm_001",
                    "top_k": 3
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

    @pytest.mark.asyncio
    async def test_retrieve_missing_lesson_id(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/qa/retrieve",
                json={"query": "test"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 400
            assert "lesson_id" in data["message"]

    @pytest.mark.asyncio
    async def test_retrieve_missing_query(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/qa/retrieve",
                json={"lesson_id": "lesson_mm_001"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 400
            assert "query" in data["message"]

    @pytest.mark.asyncio
    async def test_retrieve_returns_request_id(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/qa/retrieve",
                json={
                    "query": "test",
                    "lesson_id": "lesson_mm_001"
                }
            )

            data = response.json()
            assert "request_id" in data
