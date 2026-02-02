# RI-SCALE Dashboard Backend

FastAPI backend service for the RI-SCALE Data Exploitation Platform dashboard, providing the **Data Preparation for Exploitation Service (DPS)** and pipeline management APIs.

## Technology Stack

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pandas** - Data manipulation
- **PyYAML** - YAML manifest parsing

## Prerequisites

- **Python** >= 3.10
- **pip** (Python package manager)

## Getting Started

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Run Development Server

```bash
cd backend/app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API docs:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/data` | Upload data files |
| `POST` | `/run` | Execute a DPS pipeline |
| `POST` | `/pipeline/save` | Save a new pipeline manifest |
| `PUT` | `/pipeline/save` | Update an existing pipeline |
| `GET` | `/pipeline/list` | List saved pipelines for a project |
| `GET` | `/pipeline/load` | Load a saved pipeline manifest |

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── uploads/                   # Uploaded data and saved pipelines
│   └── services/
│       └── dps_service/           # Data Preparation Service
│           ├── dps_service.py     # Main DPS orchestrator
│           ├── dps_pipeline.py    # Pipeline execution engine
│           ├── step_types_config.py  # Config loader
│           ├── step/              # Step implementations
│           │   ├── step.py        # Base step class
│           │   ├── custom_command.py
│           │   ├── join.py
│           │   └── example_dps_step.py
│           └── dpsdataset/        # Data source handling
│               ├── source.py      # Source strategies
│               ├── lazy_dataframe.py
│               └── loaders.py     # Data loaders
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Configuration

### CORS Origins

The backend allows requests from these frontend origins by default:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:5174`
- `http://localhost:4173`

To add more origins, edit the `allow_origins` list in `app/main.py`.

### Shared Configuration

The DPS service uses a shared configuration file at `configs/step_types_config.yaml` that defines:
- Available step types (load, custom_command, join)
- Parameter schemas and validation rules
- UI metadata for the Pipeline Builder

This file is the **single source of truth** for both frontend and backend.

## Data Preparation Service (DPS)

The DPS is a pipeline-based system for preparing datasets. See the detailed documentation at:
- `app/services/dps_service/Readme.md`

### Supported Step Types

| Type | Description |
|------|-------------|
| `load` | Load data from files or CSV |
| `custom_command` | Execute shell commands |
| `join` | Merge data sources |

### Example Manifest

```yaml
manifest_id: "example-pipeline"
created_by: "user@example.org"
created_at: "2025-01-01T10:00:00Z"
simulated: true

job_steps:
  - step_name: Load WSI data
    type: load
    enabled: true
    params:
      output_source_name: wsi_source
      mode: "discovery"
      path: "./data"
      include: "*.svs"
```

## Development Notes

### Optional Dependencies

Some DPS features require additional packages not in `requirements.txt`:
- **openslide-python** - For whole-slide image handling
- **Pillow** - For image processing

Install if needed:
```bash
pip install openslide-python Pillow
```

### Running Tests

```bash
cd backend/app/services/dps_service
python -m dps_service -m example_manifest.yaml -v
```
