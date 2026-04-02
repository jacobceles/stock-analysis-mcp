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

app.title = "Stock Analysis Agent"
app.description = ""
app.version = "1.0.0"

# Remove default ADK routes that shadow our custom endpoints
routes_to_keep = []
for route in app.routes:
    if getattr(route, "path", "") in ["/health", "/"]:
        continue
    routes_to_keep.append(route)
app.router.routes = routes_to_keep


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "production-adk-agent"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "Stock Analysis Agent", "description": "", "docs": "/docs", "health": "/health"}


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")

    uvicorn.run(
        app,
        host=host,
        port=int(os.getenv("PORT", 8080)),
        log_level="debug",
    )
