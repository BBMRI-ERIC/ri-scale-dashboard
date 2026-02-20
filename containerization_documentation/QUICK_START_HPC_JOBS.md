# HPC Jobs Backend - Quick Start Guide

## Prerequisites

Ensure you have:
- Python 3.8+
- Node.js 14+
- FastAPI and dependencies installed in backend
- Node dependencies installed in frontend

## Starting the Application

### 1. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     Loaded X jobs from store (if jobs exist from previous run)
```

### 2. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

Frontend will start at `http://localhost:5173`

## Testing the Implementation

### Via UI

1. **Open the application** in browser: `http://localhost:5173`

2. **Navigate to HPC Jobs** from sidebar

3. **Submit a Data Preparation Job:**
   - Click "Submit New Job" button
   - Fill in form:
     - Project: Select any project
     - Job Type: Select "Data Preparation"
     - **Notice:** Manifest file selector appears, Model and Dataset selectors disappear
     - Manifest File: Select from dropdown (populated from project's saved manifests)
     - HPC Site: MUSICA or MUG-SX
     - Nodes: 2
     - GPUs/Node: 4
     - Memory: 128 GB
   - Click "Submit Job"
   - Job should appear in the jobs table

4. **Submit a Training Job:**
   - Click "Submit New Job"
   - Job Type: Select "Training"
   - **Notice:** Manifest selector disappears, Model and Dataset selectors appear
   - Fill in form and submit

5. **View Jobs:**
   - Jobs table shows all submitted jobs
   - For Data Preparation jobs: Model and Dataset columns show "—"
   - For other types: Model and Dataset are populated

6. **View Job Details:**
   - Click a job row to see details dialog
   - For Data Preparation: Shows manifest name
   - For others: Shows model and dataset names

7. **Cancel Job:**
   - Click cancel button on queued/running job
   - Job status changes to "cancelled"

8. **Retry Job:**
   - Click retry button on failed job
   - Job status resets to "queued"

### Via API (curl)

#### 1. List Available Manifests
```bash
curl "http://localhost:8000/manifests?project_id=proj-uc7-001"
```

Response:
```json
{
  "status": "success",
  "project_id": "proj-uc7-001",
  "manifests": [
    {
      "id": "pipelinewith2steps_3782fd1b154141c6b2ee27631fe32f8f.yaml",
      "name": "pipelinewith2steps_3782fd1b154141c6b2ee27631fe32f8f.yaml",
      "path": "/path/to/manifest/file.yaml",
      "created_at": 1702897800.0
    }
  ]
}
```

#### 2. Submit a Data Preparation Job
```bash
curl -X POST http://localhost:8000/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "proj-uc7-001",
    "jobType": "Data Preparation",
    "manifestId": "pipelinewith2steps_3782fd1b154141c6b2ee27631fe32f8f.yaml",
    "hpcSite": "MUSICA",
    "nodes": 2,
    "gpus": 4,
    "memory": "128 GB",
    "notes": "Test data preparation"
  }'
```

Response:
```json
{
  "status": "success",
  "job": {
    "id": "job-abc123def456",
    "projectId": "proj-uc7-001",
    "jobType": "Data Preparation",
    "modelId": null,
    "datasetId": null,
    "manifestId": "pipelinewith2steps_3782fd1b154141c6b2ee27631fe32f8f.yaml",
    "hpcSite": "MUSICA",
    "nodes": 2,
    "gpus": 4,
    "memory": "128 GB",
    "notes": "Test data preparation",
    "status": "queued",
    "submittedAt": "2024-12-18T14:30:00.123456",
    "startedAt": null,
    "completedAt": null,
    "runtime": null,
    "error": null
  }
}
```

#### 3. Submit a Training Job
```bash
curl -X POST http://localhost:8000/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "proj-uc7-001",
    "jobType": "Training",
    "modelId": "model-001",
    "datasetId": "ds-001",
    "hpcSite": "MUSICA",
    "nodes": 4,
    "gpus": 8,
    "memory": "256 GB"
  }'
```

#### 4. List All Jobs
```bash
curl "http://localhost:8000/jobs"
```

#### 5. List Jobs for Specific Project
```bash
curl "http://localhost:8000/jobs?project_id=proj-uc7-001"
```

#### 6. Get Job Details
```bash
curl "http://localhost:8000/jobs/job-abc123def456"
```

#### 7. Cancel a Job
```bash
curl -X POST "http://localhost:8000/jobs/job-abc123def456/cancel" \
  -H "Content-Type: application/json"
```

#### 8. Retry a Failed Job
```bash
curl -X POST "http://localhost:8000/jobs/job-abc123def456/retry" \
  -H "Content-Type: application/json"
```

## Validation Examples

### Missing Required Field
```bash
curl -X POST http://localhost:8000/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "proj-uc7-001",
    "jobType": "Data Preparation"
    # Missing other required fields
  }'
```

Response (400 Bad Request):
```json
{
  "detail": "manifestId is required for Data Preparation jobs"
}
```

### Invalid Manifest
```bash
curl -X POST http://localhost:8000/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "proj-uc7-001",
    "jobType": "Data Preparation",
    "manifestId": "nonexistent.yaml",
    "hpcSite": "MUSICA",
    "nodes": 2,
    "gpus": 4,
    "memory": "128 GB"
  }'
```

Response (404 Not Found):
```json
{
  "detail": "Manifest nonexistent.yaml not found"
}
```

## Job Persistence

Jobs are saved to `/backend/app/.jobs_store.json`. You can:

1. **View stored jobs:**
   ```bash
   cat backend/app/.jobs_store.json | python -m json.tool
   ```

2. **Manually delete jobs (for testing):**
   ```bash
   rm backend/app/.jobs_store.json
   ```
   Then restart the backend to start fresh.

3. **Jobs survive restarts:**
   - Stop backend (Ctrl+C)
   - Restart backend
   - Jobs are restored from `.jobs_store.json`

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Check Python version: `python --version` (should be 3.8+)
- Check FastAPI is installed: `pip list | grep fastapi`

### Frontend can't reach backend
- Ensure backend is running on port 8000
- Check CORS configuration in `backend/app/main.py`
- Check browser console for CORS errors
- Try accessing `http://localhost:8000/health` in browser

### Manifests not loading
- Verify manifests exist in project's manifest directory
- Check logs for file access errors
- Ensure project ID is correct

### Jobs not saving
- Check `.jobs_store.json` file has write permissions
- Check logs for write errors
- Ensure backend app directory is writable

## Next Steps

1. ✅ Test Data Preparation job submission
2. ✅ Test other job types
3. ✅ Test job cancellation and retry
4. ✅ Verify job persistence
5. 📝 Implement actual job execution (DPS service integration)
6. 📝 Add real-time job status monitoring
7. 📝 Integrate with actual HPC schedulers (SLURM, etc.)
8. 📝 Add database backend for production
9. 📝 Implement authentication and authorization
10. 📝 Add job results storage and download
