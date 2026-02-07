#!/usr/bin/env python3
"""Web UI server for PM Agentic AI Platform."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.web.routes import router
from src.utils.config import config
from src.utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(level=config.log_level)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PM Agentic AI Platform",
    description="Product management with AI agents",
    version="0.1.0"
)

# Include API routes
app.include_router(router)

# Templates
templates = Jinja2Templates(directory="src/web/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": config.app_name
    })


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {config.web_host}:{config.web_port}")
    uvicorn.run(app, host=config.web_host, port=config.web_port)
