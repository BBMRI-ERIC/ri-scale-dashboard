# RI-SCALE Apptainer Quick Reference

## Quick Start (30 seconds)

```bash
cd /path/to/ri-scale-dashboard

# Build container (requires sudo or fakeroot)
sudo apptainer build ri-scale-dashboard.sif Apptainer.def

# Run backend
apptainer run ri-scale-dashboard.sif
# API at http://localhost:8000

# Run frontend (in another terminal)
apptainer exec ri-scale-dashboard.sif npm run dev --prefix /opt/ri-scale/frontend
# Frontend at http://localhost:5173

# Or use the helper script
./apptainer.sh build
./apptainer.sh backend  # Terminal 1
./apptainer.sh frontend # Terminal 2
```

## Using the Helper Script

```bash
./apptainer.sh build              # Build container
./apptainer.sh backend            # Run FastAPI backend
./apptainer.sh frontend           # Run Vue.js frontend
./apptainer.sh shell              # Interactive shell
./apptainer.sh dps-pipeline       # Run DPS with example
./apptainer.sh exec COMMAND       # Run arbitrary command
./apptainer.sh status             # Show container info
./apptainer.sh help               # Show help
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `apptainer build ri-scale-dashboard.sif Apptainer.def` | Build container |
| `apptainer run ri-scale-dashboard.sif` | Run backend (default) |
| `apptainer shell ri-scale-dashboard.sif` | Interactive shell |
| `apptainer exec ri-scale-dashboard.sif COMMAND` | Run command in container |
| `apptainer inspect ri-scale-dashboard.sif` | Show container info |

## Binding Directories (Mount Volumes)

```bash
# Single directory
apptainer exec --bind /host/data:/container/data ri-scale-dashboard.sif ls /container/data

# Multiple directories
apptainer exec \
  --bind /host/data:/data \
  --bind /host/output:/output \
  ri-scale-dashboard.sif bash

# Read-only binding
apptainer exec --bind /host/data:/data:ro ri-scale-dashboard.sif ls /data
```

## Running Services

```bash
# Backend API (port 8000)
apptainer run ri-scale-dashboard.sif
# or
apptainer exec ri-scale-dashboard.sif python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (port 5173)
apptainer exec ri-scale-dashboard.sif npm run dev --prefix /opt/ri-scale/frontend

# DPS Pipeline
apptainer exec ri-scale-dashboard.sif \
  python /opt/ri-scale/backend/app/services/dps_service/dps_service.py \
  -m /opt/ri-scale/backend/app/services/dps_service/example_manifest.yaml -v
```

## HPC Job Submission

### SLURM

```bash
#!/bin/bash
#SBATCH --job-name=ri-scale
#SBATCH --partition=batch
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00

apptainer run ri-scale-dashboard.sif
```

Submit: `sbatch job.slurm`

### SLURM with GPU

```bash
#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --mem=32G

apptainer exec --nv ri-scale-dashboard.sif python train.py
```

### PBS

```bash
#!/bin/bash
#PBS -l select=1:ncpus=4:mem=8gb
#PBS -l walltime=02:00:00

apptainer run ri-scale-dashboard.sif
```

Submit: `qsub job.pbs`

## Environment Variables

```bash
# Set in container
apptainer run --env VAR=value ri-scale-dashboard.sif

# Set multiple
apptainer run \
  --env VAR1=value1 \
  --env VAR2=value2 \
  ri-scale-dashboard.sif

# Set from host
export MY_VAR=something
apptainer run --env MY_VAR ri-scale-dashboard.sif
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "apptainer: command not found" | Install apptainer or check PATH |
| Build fails with permission denied | Use `sudo` or `--fakeroot` |
| Container won't start | Run `apptainer inspect ri-scale-dashboard.sif` |
| Module import errors | Check: `apptainer exec ri-scale-dashboard.sif pip list` |
| Bind mount permission denied | Run `chmod 755 /host/directory` |
| Out of memory during build | Use system with more RAM or `--fakeroot` |

## File Locations in Container

```
/opt/ri-scale/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app
│       ├── services/            # DPS service
│       └── uploads/             # Uploaded files
├── frontend/
│   ├── package.json
│   ├── src/
│   └── public/
└── configs/
    └── step_types_config.yaml
```

## Container Contents

- **Base**: Python 3.11 (Debian-based)
- **Python**: FastAPI, Uvicorn, NumPy, Pandas, Pillow, OpenSlide, etc.
- **Node.js**: v20 for frontend
- **System**: OpenSlide tools, image libraries, dev headers

## Port Mappings

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Frontend | 5173 | http://localhost:5173 |
| API Docs | 8000/docs | http://localhost:8000/docs |
| Redoc | 8000/redoc | http://localhost:8000/redoc |

## Performance Tips

1. **Pre-load container**: `apptainer exec ri-scale-dashboard.sif true`
2. **Use local cache**: `export APPTAINER_CACHEDIR=/tmp/.apptainer`
3. **Bind scratch**: `--bind /scratch/$USER:/scratch`
4. **Monitor with `squeue`**: `squeue -u $USER`

## Documentation

- [APPTAINER_GUIDE.md](APPTAINER_GUIDE.md) - Complete guide
- [HPC_CLUSTER_INTEGRATION.md](HPC_CLUSTER_INTEGRATION.md) - Cluster examples
- [Official Apptainer Docs](https://apptainer.org/docs/)

## Getting Help

```bash
# Container help
apptainer inspect ri-scale-dashboard.sif

# Apptainer help
apptainer help
apptainer run --help
apptainer exec --help

# Show built-in help message
apptainer run-help ri-scale-dashboard.sif
```

## One-Liners

```bash
# Check Python version
apptainer exec ri-scale-dashboard.sif python --version

# Check installed packages
apptainer exec ri-scale-dashboard.sif pip list

# Run Python command
apptainer exec ri-scale-dashboard.sif python -c "import fastapi; print(fastapi.__version__)"

# Interactive Python
apptainer exec ri-scale-dashboard.sif python

# Install additional package (in shell)
apptainer shell --writable ri-scale-dashboard.sif
# pip install package-name

# Copy file from container
apptainer exec ri-scale-dashboard.sif cat /opt/ri-scale/README.md > README.md
```

## Container Efficiency

```bash
# Show container size
du -h ri-scale-dashboard.sif

# Compress container (reduces size ~30%)
apptainer build --compress ri-scale-prod.sif Apptainer.def

# Build in sandbox (for development)
sudo apptainer build --sandbox ri-scale.sandbox Apptainer.def
apptainer shell --writable ri-scale.sandbox
```

---

**Need more help?** See [APPTAINER_GUIDE.md](APPTAINER_GUIDE.md) for detailed documentation.
