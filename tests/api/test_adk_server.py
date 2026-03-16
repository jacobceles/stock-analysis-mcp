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
    assert response.json() == {"service": "Production ADK Agent - Stock MCP", "description": "", "docs": "/docs", "health": "/health"}


def test_app_metadata():
    assert app.title == "Production ADK Agent - Stock MCP"
    assert app.version == "1.0.0"
    assert app.description == ""

def test_adk_server_main_execution(mocker):
    mock_run = mocker.patch("uvicorn.run")
    import runpy
    import os

    orig_host = os.environ.get("HOST")
    orig_port = os.environ.get("PORT")
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PORT"] = "8081"

    try:
        runpy.run_module("stock_analysis_mcp.api.adk_server", run_name="__main__")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert kwargs["host"] == "0.0.0.0"
        assert kwargs["port"] == 8081
        assert kwargs["log_level"] == "debug"
    finally:
        if orig_host is None:
            del os.environ["HOST"]
        else:
            os.environ["HOST"] = orig_host

        if orig_port is None:
            del os.environ["PORT"]
        else:
            os.environ["PORT"] = orig_port
