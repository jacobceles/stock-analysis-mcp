import os

import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

load_dotenv()

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
)

app.title = "Production ADK Agent - Stock MCP"
app.description = ""
app.version = "1.0.0"


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "production-adk-agent"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "Production ADK Agent - Stock MCP", "description": "", "docs": "/docs", "health": "/health"}


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")

    uvicorn.run(
        app,
        host=host,
        port=int(os.getenv("PORT", 8080)),
        log_level="debug",
    )
