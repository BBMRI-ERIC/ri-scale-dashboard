"""
Minimal FastAPI backend exposing endpoints to upload manifests/data and execute the DPS service.
"""

from __future__ import annotations

import logging
import shutil
import sys
import uuid
from pathlib import Path

from fastapi import Body, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yaml

from logging import Logger

logger = logging.getLogger(__name__)

# Ensure the DPS service modules are importable when running from the app root
BASE_DIR = Path(__file__).resolve().parent
DPS_SERVICE_DIR = BASE_DIR / "services" / "dps_service"
if str(DPS_SERVICE_DIR) not in sys.path:
    sys.path.append(str(DPS_SERVICE_DIR))

try:
    from dps_service import DataPreparationForExploitationService
    HAS_DPS_SERVICE = True
except Exception as exc:  # pragma: no cover - defensive import guard
    HAS_DPS_SERVICE = False
    logger.warning(f"DPS service not available: {exc}. Pipeline execution will not work, but save/manifest endpoints will.")

logger = logging.getLogger("dps_api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="RI Scale DPS Service", version="0.1.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev port
        "http://localhost:5174",  # Alternative Vite port
        "http://localhost:3000",  # Common dev port
        "http://localhost:4173",  # Vite preview
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_ROOT = BASE_DIR / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

def get_project_dir(project_id: str) -> Path:
    """Get the base directory for a project."""
    project_dir = UPLOAD_ROOT / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir

def get_project_manifest_dir(project_id: str) -> Path:
    """Get the manifests directory for a project."""
    manifest_dir = get_project_dir(project_id) / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    return manifest_dir

def get_project_data_dir(project_id: str) -> Path:
    """Get the data directory for a project."""
    data_dir = get_project_dir(project_id) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _save_upload(upload: UploadFile, target_dir: Path) -> Path:
    """Persist an uploaded file to disk and return the saved path."""
    target_dir.mkdir(parents=True, exist_ok=True)
    original_name = upload.filename or "upload"
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    saved_path = target_dir / f"{stem}_{uuid.uuid4().hex}{suffix}"

    with saved_path.open("wb") as out_file:
        shutil.copyfileobj(upload.file, out_file)
    return saved_path


@app.post("/data")
async def upload_data(file: UploadFile = File(...), project_id: str = Form("default")) -> JSONResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Data file is required")

    data_dir = get_project_data_dir(project_id)
    saved_path = _save_upload(file, data_dir)
    logger.info("Data file saved to %s", saved_path)
    return JSONResponse({"data_path": str(saved_path), "project_id": project_id})


@app.post("/run")
async def run_dps(manifest_path: str = Form(...)) -> JSONResponse:
    if not HAS_DPS_SERVICE:
        raise HTTPException(status_code=503, detail="DPS service is not available. Please install dependencies")
    
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        raise HTTPException(status_code=404, detail="Manifest path does not exist")

    try:
        service = DataPreparationForExploitationService(str(manifest_file))
        service.run()
    except Exception as exc:
        logger.exception("DPS run failed")
        raise HTTPException(status_code=500, detail=f"DPS execution failed: {exc}") from exc

    return JSONResponse({"status": "completed", "manifest_path": str(manifest_file)})


@app.get("/health")
async def healthcheck() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/pipeline/save")
async def save_pipeline(payload: dict = Body(...)) -> JSONResponse:
    """Save a pipeline manifest to a project-dependent folder."""
    try:
        project_id = payload.get('project_id')
        pipeline_name = payload.get('pipeline_name')
        manifest = payload.get('manifest')
        
        logger.info(f"Save pipeline request: project_id={project_id}, pipeline_name={pipeline_name}")
        
        if not project_id or not isinstance(project_id, str):
            raise HTTPException(status_code=400, detail="project_id is required and must be a string")
        if not pipeline_name or not isinstance(pipeline_name, str):
            raise HTTPException(status_code=400, detail="pipeline_name is required and must be a string")
        if not isinstance(manifest, dict):
            raise HTTPException(status_code=400, detail="manifest must be an object")

        # Get project-specific manifest directory
        project_manifest_dir = get_project_manifest_dir(project_id)

        # Sanitize pipeline name and generate filename
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in pipeline_name).strip()
        if not safe_name:
            safe_name = "pipeline"
        
        filename = f"{safe_name}_{uuid.uuid4().hex}.yaml"
        saved_path = project_manifest_dir / filename

        with saved_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=False)

        logger.info("Pipeline saved to %s", saved_path)
        return JSONResponse({
            "status": "success",
            "pipeline_path": str(saved_path),
            "project_id": project_id,
            "pipeline_name": pipeline_name
        })
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error saving pipeline")
        raise HTTPException(status_code=500, detail=f"Failed to save pipeline: {str(exc)}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
