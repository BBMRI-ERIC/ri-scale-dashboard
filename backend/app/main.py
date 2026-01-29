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
import yaml

# Ensure the DPS service modules are importable when running from the app root
BASE_DIR = Path(__file__).resolve().parent
DPS_SERVICE_DIR = BASE_DIR / "services" / "dps_service"
if str(DPS_SERVICE_DIR) not in sys.path:
    sys.path.append(str(DPS_SERVICE_DIR))

try:
    from dps_service import DataPreparationForExploitationService
except Exception as exc:  # pragma: no cover - defensive import guard
    raise RuntimeError(f"Unable to import DPS service: {exc}") from exc

logger = logging.getLogger("dps_api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="RI Scale DPS Service", version="0.1.0")

UPLOAD_ROOT = BASE_DIR / "uploads"
MANIFEST_DIR = UPLOAD_ROOT / "manifests"
DATA_DIR = UPLOAD_ROOT / "data"
for directory in (MANIFEST_DIR, DATA_DIR):
    directory.mkdir(parents=True, exist_ok=True)


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


def _save_manifest_dict(manifest: dict) -> Path:
    """Persist a manifest dict as YAML and return its path."""
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = MANIFEST_DIR / f"manifest_{uuid.uuid4().hex}.yaml"
    with saved_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=False)
    return saved_path


@app.post("/manifest")
async def upload_manifest(file: UploadFile = File(...)) -> JSONResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Manifest file is required")
    if not file.filename.lower().endswith((".yaml", ".yml")):
        raise HTTPException(status_code=400, detail="Manifest must be a YAML file")

    saved_path = _save_upload(file, MANIFEST_DIR)
    logger.info("Manifest saved to %s", saved_path)
    return JSONResponse({"manifest_path": str(saved_path)})


@app.post("/manifest/json")
async def upload_manifest_json(manifest: dict = Body(...)) -> JSONResponse:
    """Allow the frontend builder to send a manifest object directly."""
    if not isinstance(manifest, dict):
        raise HTTPException(status_code=400, detail="Manifest must be an object")

    saved_path = _save_manifest_dict(manifest)
    logger.info("Manifest (JSON) saved to %s", saved_path)
    return JSONResponse({"manifest_path": str(saved_path)})


@app.post("/data")
async def upload_data(file: UploadFile = File(...)) -> JSONResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Data file is required")

    saved_path = _save_upload(file, DATA_DIR)
    logger.info("Data file saved to %s", saved_path)
    return JSONResponse({"data_path": str(saved_path)})


@app.post("/run")
async def run_dps(manifest_path: str = Form(...)) -> JSONResponse:
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
