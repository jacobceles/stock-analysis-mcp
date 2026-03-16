import pytest
from fastapi.testclient import TestClient

from stock_analysis_mcp.api.adk_server import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "production-adk-agent"}

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "service": "Production ADK Agent - Stock MCP",
        "description": "",
        "docs": "/docs",
        "health": "/health"
    }

def test_app_metadata():
    assert app.title == "Production ADK Agent - Stock MCP"
    assert app.version == "1.0.0"
    assert app.description == ""
