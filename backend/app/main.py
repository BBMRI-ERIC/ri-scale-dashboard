"""
Minimal FastAPI backend exposing endpoints to upload manifests/data and execute the DPS service.
"""

from __future__ import annotations

import json
import logging
import shutil
import sys
import uuid
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional

from fastapi import Body, FastAPI, File, Form, HTTPException, Query, UploadFile
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

# In-memory job storage (use database in production)
JOBS_STORE: dict = {}
JOBS_STORE_FILE = BASE_DIR / ".jobs_store.json"

def load_jobs_store() -> None:
    """Load jobs from persistent storage on startup."""
    global JOBS_STORE
    if JOBS_STORE_FILE.exists():
        try:
            with JOBS_STORE_FILE.open("r") as f:
                JOBS_STORE = json.load(f)
            logger.info(f"Loaded {len(JOBS_STORE)} jobs from store")
        except Exception as exc:
            logger.warning(f"Failed to load jobs store: {exc}")
            JOBS_STORE = {}

def save_jobs_store() -> None:
    """Persist jobs to disk."""
    try:
        with JOBS_STORE_FILE.open("w") as f:
            json.dump(JOBS_STORE, f, indent=2, default=str)
    except Exception as exc:
        logger.error(f"Failed to save jobs store: {exc}")


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
async def run_dps(manifest_path: str = Form(...), simulated: bool = Form(False)) -> JSONResponse:
    if not HAS_DPS_SERVICE:
        raise HTTPException(status_code=503, detail="DPS service is not available. Please install dependencies")
    
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        raise HTTPException(status_code=404, detail="Manifest path does not exist")

    try:
        # Load manifest and set simulated flag
        with manifest_file.open("r", encoding="utf-8") as fh:
            manifest_data = yaml.safe_load(fh)
        
        # Add or update simulated flag in manifest
        manifest_data["simulated"] = simulated
        
        # Create temporary manifest file with simulated flag
        temp_manifest = manifest_file.parent / f"temp_{manifest_file.name}"
        with temp_manifest.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(manifest_data, fh, sort_keys=False, allow_unicode=False)
        
        try:
            service = DataPreparationForExploitationService(str(temp_manifest))
            service.run()
        finally:
            # Clean up temporary file
            if temp_manifest.exists():
                temp_manifest.unlink()
    except Exception as exc:
        logger.exception("DPS run failed")
        raise HTTPException(status_code=500, detail=f"DPS execution failed: {exc}") from exc

    mode = "simulated" if simulated else "production"
    return JSONResponse({"status": "completed", "manifest_path": str(manifest_file), "mode": mode})


@app.get("/health")
async def healthcheck() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/jobs/submit")
async def submit_job(payload: dict = Body(...)) -> JSONResponse:
    """
    Submit a new HPC job.
    
    Payload:
    {
        "projectId": str,
        "jobType": str,  # "Training", "Inference", "Evaluation", "Generation", "Data Preparation"
        "modelId": str (optional, not required for Data Preparation),
        "datasetId": str (optional, not required for Data Preparation),
        "manifestId": str (optional, required for Data Preparation),
        "hpcSite": str,
        "nodes": int,
        "gpus": int,
        "memory": str,
        "notes": str (optional)
    }
    """
    try:
        project_id = payload.get("projectId")
        job_type = payload.get("jobType")
        manifest_id = payload.get("manifestId")
        model_id = payload.get("modelId")
        dataset_id = payload.get("datasetId")
        hpc_site = payload.get("hpcSite")
        nodes = payload.get("nodes")
        gpus = payload.get("gpus")
        memory = payload.get("memory")
        notes = payload.get("notes", "")
        simulated = payload.get("simulated", False)  # Default to production mode

        # Validate required fields
        if not project_id:
            raise HTTPException(status_code=400, detail="projectId is required")
        if not job_type:
            raise HTTPException(status_code=400, detail="jobType is required")
        if not hpc_site:
            raise HTTPException(status_code=400, detail="hpcSite is required")
        if nodes is None:
            raise HTTPException(status_code=400, detail="nodes is required")
        if gpus is None:
            raise HTTPException(status_code=400, detail="gpus is required")
        if not memory:
            raise HTTPException(status_code=400, detail="memory is required")

        # Validate job type specific requirements
        if job_type == "Data Preparation":
            if not manifest_id:
                raise HTTPException(status_code=400, detail="manifestId is required for Data Preparation jobs")
            # Verify manifest exists
            manifest_dir = get_project_manifest_dir(project_id)
            manifest_path = manifest_dir / manifest_id
            if not manifest_path.exists():
                raise HTTPException(status_code=404, detail=f"Manifest {manifest_id} not found")
        else:
            if not model_id:
                raise HTTPException(status_code=400, detail="modelId is required for non-Data Preparation jobs")
            if not dataset_id:
                raise HTTPException(status_code=400, detail="datasetId is required for non-Data Preparation jobs")

        # Create job record
        job_id = f"job-{uuid.uuid4().hex[:16]}"
        now = datetime.utcnow().isoformat()

        job = {
            "id": job_id,
            "projectId": project_id,
            "jobType": job_type,
            "modelId": model_id,
            "datasetId": dataset_id,
            "manifestId": manifest_id,
            "hpcSite": hpc_site,
            "nodes": nodes,
            "gpus": gpus,
            "memory": memory,
            "notes": notes,
            "simulated": simulated,
            "status": "queued",
            "submittedAt": now,
            "startedAt": None,
            "completedAt": None,
            "runtime": None,
            "error": None
        }

        JOBS_STORE[job_id] = job
        save_jobs_store()

        logger.info(f"Job submitted: {job_id} (type: {job_type}, project: {project_id})")

        return JSONResponse({
            "status": "success",
            "job": job
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error submitting job")
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(exc)}") from exc


@app.post("/jobs/{job_id}/execute")
async def execute_job(job_id: str, payload: dict = Body(default={})) -> JSONResponse:
    """
    Execute a Data Preparation job using its associated manifest.
    Supports both simulated and production modes - mode can be specified at execution time.
    """
    try:
        if job_id not in JOBS_STORE:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = JOBS_STORE[job_id]
        
        if job["jobType"] != "Data Preparation":
            raise HTTPException(status_code=400, detail="Only Data Preparation jobs can be executed via this endpoint")
        
        if job["status"] != "queued":
            raise HTTPException(status_code=400, detail=f"Job must be in queued status (current: {job['status']})")

        manifest_id = job["manifestId"]
        project_id = job["projectId"]
        # Get simulated mode from request body (defaults to false = production mode)
        simulated = payload.get("simulated", False)
        
        # Update job with execution mode
        job["simulated"] = simulated
        
        # Get manifest path
        manifest_dir = get_project_manifest_dir(project_id)
        manifest_path = manifest_dir / manifest_id
        
        if not manifest_path.exists():
            raise HTTPException(status_code=404, detail=f"Manifest {manifest_id} not found")

        # Update job status
        job["status"] = "running"
        job["startedAt"] = datetime.utcnow().isoformat()
        save_jobs_store()

        if not HAS_DPS_SERVICE:
            job["status"] = "failed"
            job["error"] = "DPS service is not available"
            save_jobs_store()
            raise HTTPException(status_code=503, detail="DPS service is not available. Please install dependencies")

        # Capture logs
        log_stream = StringIO()
        log_handler = logging.StreamHandler(log_stream)
        log_handler.setLevel(logging.INFO)
        log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        log_handler.setFormatter(log_formatter)
        
        # Get DPS logger and add handler
        dps_logger = logging.getLogger('dps_service')
        root_logger = logging.getLogger()
        dps_logger.addHandler(log_handler)
        root_logger.addHandler(log_handler)

        try:
            # Load manifest and set simulated flag
            with manifest_path.open("r", encoding="utf-8") as fh:
                manifest_data = yaml.safe_load(fh)
            
            # Add or update simulated flag in manifest
            manifest_data["simulated"] = simulated
            
            # Create temporary manifest file with simulated flag
            temp_manifest = manifest_path.parent / f"temp_{job_id}_{manifest_path.name}"
            with temp_manifest.open("w", encoding="utf-8") as fh:
                yaml.safe_dump(manifest_data, fh, sort_keys=False, allow_unicode=False)
            
            log_stream.write(f"[{datetime.utcnow().isoformat()}] INFO - Starting DPS service execution\n")
            log_stream.write(f"[{datetime.utcnow().isoformat()}] INFO - Mode: {'Simulated' if simulated else 'Production'}\n")
            log_stream.write(f"[{datetime.utcnow().isoformat()}] INFO - Manifest: {manifest_id}\n")
            log_stream.write(f"[{datetime.utcnow().isoformat()}] INFO - Project: {project_id}\n")
            
            try:
                service = DataPreparationForExploitationService(str(temp_manifest))
                service.run()
                
                log_stream.write(f"[{datetime.utcnow().isoformat()}] INFO - DPS service completed successfully\n")
                
                # Job completed successfully
                job["status"] = "completed"
                job["completedAt"] = datetime.utcnow().isoformat()
                # Calculate runtime
                if job["startedAt"]:
                    start = datetime.fromisoformat(job["startedAt"])
                    end = datetime.fromisoformat(job["completedAt"])
                    duration = end - start
                    hours, remainder = divmod(int(duration.total_seconds()), 3600)
                    minutes, _ = divmod(remainder, 60)
                    job["runtime"] = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                
            finally:
                # Clean up temporary file
                if temp_manifest.exists():
                    temp_manifest.unlink()
                    
        except Exception as exec_exc:
            logger.exception("DPS execution failed")
            log_stream.write(f"[{datetime.utcnow().isoformat()}] ERROR - DPS execution failed: {exec_exc}\n")
            job["status"] = "failed"
            job["error"] = str(exec_exc)
            save_jobs_store()
            raise HTTPException(status_code=500, detail=f"DPS execution failed: {exec_exc}") from exec_exc
        finally:
            # Remove log handler
            dps_logger.removeHandler(log_handler)
            root_logger.removeHandler(log_handler)
            log_handler.close()

        # Store logs in job
        job["logs"] = log_stream.getvalue()
        save_jobs_store()
        mode = "simulated" if simulated else "production"
        logger.info(f"Job {job_id} executed in {mode} mode")

        return JSONResponse({
            "status": "success",
            "message": f"Job executed in {mode} mode",
            "job": job,
            "logs": job["logs"]
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error executing job")
        raise HTTPException(status_code=500, detail=f"Failed to execute job: {str(exc)}") from exc


@app.get("/jobs")
async def list_jobs(project_id: Optional[str] = Query(None)) -> JSONResponse:
    """List all jobs, optionally filtered by project."""
    try:
        jobs = list(JOBS_STORE.values())
        
        if project_id:
            jobs = [j for j in jobs if j["projectId"] == project_id]

        # Sort by submitted date (newest first)
        jobs.sort(key=lambda x: x["submittedAt"], reverse=True)

        logger.info(f"Listed {len(jobs)} jobs" + (f" for project {project_id}" if project_id else ""))

        return JSONResponse({
            "status": "success",
            "jobs": jobs
        })

    except Exception as exc:
        logger.exception("Error listing jobs")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(exc)}") from exc


@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> JSONResponse:
    """Get details of a specific job."""
    try:
        if job_id not in JOBS_STORE:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = JOBS_STORE[job_id]

        logger.info(f"Retrieved job {job_id}")

        return JSONResponse({
            "status": "success",
            "job": job
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error retrieving job")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job: {str(exc)}") from exc


@app.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str) -> JSONResponse:
    """Cancel a queued or running job."""
    try:
        if job_id not in JOBS_STORE:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = JOBS_STORE[job_id]
        
        if job["status"] not in ["queued", "running"]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel job with status {job['status']}")

        job["status"] = "cancelled"
        save_jobs_store()

        logger.info(f"Job cancelled: {job_id}")

        return JSONResponse({
            "status": "success",
            "message": f"Job {job_id} cancelled",
            "job": job
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error cancelling job")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(exc)}") from exc


@app.post("/jobs/{job_id}/retry")
async def retry_job(job_id: str) -> JSONResponse:
    """Retry a failed job."""
    try:
        if job_id not in JOBS_STORE:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job = JOBS_STORE[job_id]
        
        if job["status"] != "failed":
            raise HTTPException(status_code=400, detail=f"Can only retry failed jobs (current status: {job['status']})")

        job["status"] = "queued"
        job["startedAt"] = None
        job["completedAt"] = None
        job["runtime"] = None
        job["error"] = None
        save_jobs_store()

        logger.info(f"Job retry: {job_id}")

        return JSONResponse({
            "status": "success",
            "message": f"Job {job_id} queued for retry",
            "job": job
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error retrying job")
        raise HTTPException(status_code=500, detail=f"Failed to retry job: {str(exc)}") from exc



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


@app.get("/pipeline/list")
async def list_pipelines(project_id: str) -> JSONResponse:
    """List all saved pipelines for a project."""
    try:
        if not project_id or not isinstance(project_id, str):
            raise HTTPException(status_code=400, detail="project_id is required and must be a string")

        project_manifest_dir = get_project_manifest_dir(project_id)
        
        pipelines = []
        if project_manifest_dir.exists():
            for yaml_file in sorted(project_manifest_dir.glob("*.yaml"), reverse=True):
                # Extract pipeline name from filename (remove UUID suffix)
                filename = yaml_file.stem
                # Find the last underscore to split name and UUID
                parts = filename.rsplit('_', 1)
                name = parts[0] if len(parts) > 1 else filename
                
                pipelines.append({
                    "id": yaml_file.name,
                    "name": name,
                    "path": str(yaml_file),
                    "created_at": yaml_file.stat().st_mtime
                })
        
        logger.info(f"Listed {len(pipelines)} pipelines for project {project_id}")
        return JSONResponse({
            "status": "success",
            "project_id": project_id,
            "pipelines": pipelines
        })
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error listing pipelines")
        raise HTTPException(status_code=500, detail=f"Failed to list pipelines: {str(exc)}") from exc


@app.get("/pipeline/load")
async def load_pipeline(project_id: str, pipeline_id: str) -> JSONResponse:
    """Load a saved pipeline manifest."""
    try:
        if not project_id or not isinstance(project_id, str):
            raise HTTPException(status_code=400, detail="project_id is required and must be a string")
        if not pipeline_id or not isinstance(pipeline_id, str):
            raise HTTPException(status_code=400, detail="pipeline_id is required and must be a string")

        project_manifest_dir = get_project_manifest_dir(project_id)
        pipeline_path = project_manifest_dir / pipeline_id

        if not pipeline_path.exists():
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")

        with pipeline_path.open("r", encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh)

        logger.info(f"Loaded pipeline {pipeline_id} for project {project_id}")
        return JSONResponse({
            "status": "success",
            "project_id": project_id,
            "pipeline_id": pipeline_id,
            "manifest": manifest
        })
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error loading pipeline")
        raise HTTPException(status_code=500, detail=f"Failed to load pipeline: {str(exc)}") from exc


@app.put("/pipeline/save")
async def update_pipeline(payload: dict = Body(...)) -> JSONResponse:
    """Update an existing pipeline manifest."""
    try:
        project_id = payload.get('project_id')
        pipeline_id = payload.get('pipeline_id')
        manifest = payload.get('manifest')
        
        logger.info(f"Update pipeline request: project_id={project_id}, pipeline_id={pipeline_id}")
        
        if not project_id or not isinstance(project_id, str):
            raise HTTPException(status_code=400, detail="project_id is required and must be a string")
        if not pipeline_id or not isinstance(pipeline_id, str):
            raise HTTPException(status_code=400, detail="pipeline_id is required and must be a string")
        if not isinstance(manifest, dict):
            raise HTTPException(status_code=400, detail="manifest must be an object")

        project_manifest_dir = get_project_manifest_dir(project_id)
        pipeline_path = project_manifest_dir / pipeline_id

        if not pipeline_path.exists():
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")

        with pipeline_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=False)

        logger.info("Pipeline updated at %s", pipeline_path)
        return JSONResponse({
            "status": "success",
            "pipeline_path": str(pipeline_path),
            "project_id": project_id,
            "pipeline_id": pipeline_id
        })
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error updating pipeline")
        raise HTTPException(status_code=500, detail=f"Failed to update pipeline: {str(exc)}") from exc


@app.get("/manifests")
async def list_manifests(project_id: str) -> JSONResponse:
    """List all manifest files available for a project (for Data Preparation jobs)."""
    try:
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        project_manifest_dir = get_project_manifest_dir(project_id)
        
        manifests = []
        if project_manifest_dir.exists():
            for yaml_file in sorted(project_manifest_dir.glob("*.yaml"), reverse=True):
                manifests.append({
                    "id": yaml_file.name,
                    "name": yaml_file.name,
                    "path": str(yaml_file),
                    "created_at": yaml_file.stat().st_mtime
                })
        
        logger.info(f"Listed {len(manifests)} manifests for project {project_id}")
        return JSONResponse({
            "status": "success",
            "project_id": project_id,
            "manifests": manifests
        })
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error listing manifests")
        raise HTTPException(status_code=500, detail=f"Failed to list manifests: {str(exc)}") from exc


@app.get("/projects/{project_id}/data-browser")
async def browse_data_directory(project_id: str, path: str = Query("")) -> JSONResponse:
    """
    Browse the data directory of a project.
    
    Query Parameters:
    - path: subdirectory path relative to the project's data folder
    
    Returns:
    {
        "current_path": str,
        "parent_path": str (or null),
        "entries": [
            {
                "name": str,
                "type": "file" | "directory",
                "path": str,
                "size": int (for files)
            }
        ],
        "error": str (if any)
    }
    """
    try:
        # Get the base data directory for the project
        data_dir = get_project_data_dir(project_id)
        
        # Normalize and validate the requested path
        if path:
            # Remove leading/trailing slashes and normalize
            path = path.strip("/")
            requested_dir = data_dir / path
        else:
            requested_dir = data_dir
        
        # Security check: ensure the resolved path is within data_dir
        try:
            requested_dir = requested_dir.resolve()
            data_dir = data_dir.resolve()
            if not str(requested_dir).startswith(str(data_dir)):
                raise HTTPException(status_code=403, detail="Access denied: path is outside project data directory")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid path: {exc}") from exc
        
        if not requested_dir.exists():
            raise HTTPException(status_code=404, detail=f"Path does not exist: {path}")
        
        if not requested_dir.is_dir():
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")
        
        # List directory contents
        entries = []
        try:
            for item in sorted(requested_dir.iterdir()):
                entry = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                }
                
                # Calculate relative path from data root for navigation
                try:
                    rel_path = item.relative_to(data_dir)
                    entry["path"] = str(rel_path).replace("\\", "/")
                except ValueError:
                    entry["path"] = item.name
                
                # Add absolute path for use in YAML/manifests
                entry["absolute_path"] = str(item.resolve()).replace("\\", "/")
                
                # Add file size for files
                if item.is_file():
                    try:
                        entry["size"] = item.stat().st_size
                    except OSError:
                        entry["size"] = 0
                
                entries.append(entry)
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied accessing directory")
        
        # Calculate parent path
        parent_path = None
        if requested_dir != data_dir:
            try:
                parent = requested_dir.parent
                if parent >= data_dir:
                    parent_rel = parent.relative_to(data_dir)
                    if str(parent_rel) != ".":
                        parent_path = str(parent_rel).replace("\\", "/")
            except ValueError:
                pass
        
        # Get current path relative to data root
        try:
            current_rel = requested_dir.relative_to(data_dir)
            current_path = str(current_rel).replace("\\", "/") if str(current_rel) != "." else ""
        except ValueError:
            current_path = ""
        
        return JSONResponse({
            "current_path": current_path,
            "parent_path": parent_path,
            "entries": entries,
        })
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error browsing data directory for project {project_id}")
        raise HTTPException(status_code=500, detail=f"Failed to browse directory: {str(exc)}") from exc


@app.post("/projects/{project_id}/data-browser/create-folder")
async def create_folder(project_id: str, payload: dict = Body(...)) -> JSONResponse:
    """
    Create a new folder in the project's data directory.
    
    Payload:
    {
        "path": str (parent directory path, relative to data folder),
        "folder_name": str (name of the new folder)
    }
    """
    try:
        path = payload.get("path", "")
        folder_name = payload.get("folder_name")
        
        if not folder_name:
            raise HTTPException(status_code=400, detail="folder_name is required")
        
        # Validate folder name (no path separators, no special chars)
        if "/" in folder_name or "\\" in folder_name or ".." in folder_name:
            raise HTTPException(status_code=400, detail="Invalid folder name")
        
        # Get the base data directory
        data_dir = get_project_data_dir(project_id).resolve()
        
        # Determine parent directory
        if path:
            path = path.strip("/")
            parent_dir = (data_dir / path).resolve()
        else:
            parent_dir = data_dir
        
        # Security check
        if not str(parent_dir).startswith(str(data_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not parent_dir.exists():
            raise HTTPException(status_code=404, detail="Parent directory not found")
        
        # Create the new folder
        new_folder = parent_dir / folder_name
        
        if new_folder.exists():
            raise HTTPException(status_code=409, detail="Folder already exists")
        
        new_folder.mkdir(parents=False, exist_ok=False)
        
        logger.info(f"Created folder: {new_folder}")
        
        return JSONResponse({
            "status": "success",
            "folder_name": folder_name,
            "path": str(new_folder.relative_to(data_dir)).replace("\\", "/")
        })
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error creating folder")
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(exc)}") from exc


@app.delete("/projects/{project_id}/data-browser/delete-folder")
async def delete_folder(project_id: str, path: str = Query(...)) -> JSONResponse:
    """
    Delete a folder from the project's data directory.
    
    Query Parameters:
    - path: folder path relative to data folder
    """
    try:
        if not path:
            raise HTTPException(status_code=400, detail="path is required")
        
        # Get the base data directory
        data_dir = get_project_data_dir(project_id).resolve()
        
        # Get the folder to delete
        path = path.strip("/")
        folder_to_delete = (data_dir / path).resolve()
        
        # Security checks
        if not str(folder_to_delete).startswith(str(data_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if folder_to_delete == data_dir:
            raise HTTPException(status_code=403, detail="Cannot delete data root directory")
        
        if not folder_to_delete.exists():
            raise HTTPException(status_code=404, detail="Folder not found")
        
        if not folder_to_delete.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        # Delete the folder and all its contents
        import shutil
        shutil.rmtree(folder_to_delete)
        
        logger.info(f"Deleted folder: {folder_to_delete}")
        
        return JSONResponse({
            "status": "success",
            "message": "Folder deleted successfully"
        })
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error deleting folder")
        raise HTTPException(status_code=500, detail=f"Failed to delete folder: {str(exc)}") from exc


@app.on_event("startup")
async def startup_event():
    """Load jobs store on application startup."""
    load_jobs_store()
    logger.info("Application startup complete")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
