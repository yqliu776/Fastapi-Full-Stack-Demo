import sys
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.middleware import register_exception_handlers


@pytest.fixture
def app() -> FastAPI:
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/boom")
    async def boom():
        raise HTTPException(status_code=404, detail="资源不存在")

    @test_app.get("/items/{item_id}")
    async def read_item(item_id: int):
        return {"item_id": item_id}

    return test_app


@pytest.mark.asyncio
async def test_http_exception_uses_unified_response_template(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/boom")

    assert response.status_code == 404
    payload = response.json()
    assert payload["code"] == 404
    assert payload["message"] == "资源不存在"
    assert payload["data"] is None
    assert "timestamp" in payload
    assert "process_time" in payload


@pytest.mark.asyncio
async def test_validation_error_uses_unified_response_template(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/items/not-an-int")

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == 422
    assert payload["message"] == "请求数据验证失败"
    assert isinstance(payload["data"], list)
    assert "timestamp" in payload
    assert "process_time" in payload
