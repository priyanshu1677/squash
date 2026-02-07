"""FastAPI routes for web UI."""

import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

from ..agent import run_agent
from ..processors import DocumentParser
from ..generators import FeatureSpecGenerator, UIProposalGenerator, TaskBreakdownGenerator
from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a customer interview document."""
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.docx', '.doc')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

        # Save file
        file_path = config.upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse document
        doc_data = DocumentParser.parse(file_path)

        if "error" in doc_data:
            return JSONResponse(
                status_code=400,
                content={"error": doc_data["error"]}
            )

        logger.info(f"File uploaded: {file.filename}")

        return {
            "success": True,
            "filename": file.filename,
            "file_type": doc_data.get("file_type"),
            "details": {
                "num_pages": doc_data.get("num_pages"),
                "num_paragraphs": doc_data.get("num_paragraphs"),
            }
        }

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/files")
async def list_files():
    """List all uploaded files."""
    try:
        files = []
        for file_path in config.upload_dir.glob("*.*"):
            if file_path.suffix.lower() in ['.pdf', '.docx', '.doc']:
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                })

        return {"files": files}

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/query")
async def query(query: str = Form(...), files: List[str] = Form(default=[])):
    """Run a query against the agent."""
    try:
        logger.info(f"Query received: {query}")

        # Resolve file paths
        file_paths = []
        for filename in files:
            path = config.upload_dir / filename
            if path.exists():
                file_paths.append(str(path))

        # Run agent
        result = run_agent(query, file_paths)

        if result.get("error"):
            return JSONResponse(
                status_code=500,
                content={"error": result["error"]}
            )

        # Format results for web display
        response = format_results(result)

        return response

    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def format_results(result: dict) -> dict:
    """Format agent results for web display."""
    response = {
        "query_type": result.get("query_type"),
        "completed": result.get("completed"),
    }

    # Top feature
    if result.get("top_feature"):
        response["top_feature"] = result["top_feature"]

    # Feature spec (as markdown)
    if result.get("feature_spec"):
        spec_gen = FeatureSpecGenerator()
        response["feature_spec_markdown"] = spec_gen.format_spec_markdown(result["feature_spec"])
        response["feature_spec"] = result["feature_spec"]

    # UI proposals (as markdown)
    if result.get("ui_proposals"):
        ui_gen = UIProposalGenerator()
        response["ui_proposals_markdown"] = ui_gen.format_proposals_markdown(result["ui_proposals"])
        response["ui_proposals"] = result["ui_proposals"]

    # Task breakdown (as markdown)
    if result.get("task_breakdown"):
        task_gen = TaskBreakdownGenerator()
        response["task_breakdown_markdown"] = task_gen.format_tasks_markdown(result["task_breakdown"])
        response["task_breakdown"] = result["task_breakdown"]

    # All opportunities
    if result.get("scored_features"):
        response["all_opportunities"] = result["scored_features"][:10]  # Top 10

    return response
