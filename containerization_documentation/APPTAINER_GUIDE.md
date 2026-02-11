# Apptainer Container Guide for RI-SCALE Dashboard

This guide explains how to build and run the RI-SCALE Dashboard using Apptainer (formerly Singularity).

## Prerequisites

- **Apptainer** >= 1.0 installed on your system
- For HPC clusters: Check with your system administrator for pre-installed Apptainer
- Build a container: Requires root access or `fakeroot` capability
- Run a container: Works unprivileged on most systems

### Install Apptainer (if needed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:apptainer/ppa
sudo apt-get update
sudo apt-get install -y apptainer
```

**CentOS/RHEL:**
```bash
sudo dnf install -y apptainer
```

**Or use conda:**
```bash
conda install -c conda-forge apptainer
```

## Building the Container

### Method 1: Build as Root (Recommended for reproducibility)

```bash
cd /path/to/ri-scale-dashboard
sudo apptainer build ri-scale-dashboard.sif Apptainer.def
```

### Method 2: Build with Fakeroot (No sudo required)

```bash
cd /path/to/ri-scale-dashboard
apptainer build --fakeroot ri-scale-dashboard.sif Apptainer.def
```

### Method 3: Build in Sandbox Mode (For development)

```bash
sudo apptainer build --sandbox ri-scale-dashboard.sandbox Apptainer.def
apptainer shell --writable ri-scale-dashboard.sandbox
```

## Running the Container

### Run the Backend API Server

```bash
apptainer run ri-scale-dashboard.sif
# or explicitly:
apptainer exec ri-scale-dashboard.sif python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Run the Frontend Development Server

```bash
apptainer exec ri-scale-dashboard.sif npm run dev --prefix /opt/ri-scale/frontend
```

The frontend will be available at `http://localhost:5173`

### Execute Python Commands

```bash
apptainer exec ri-scale-dashboard.sif python -c "import fastapi; print(fastapi.__version__)"
```

### Run DPS Service Pipeline

```bash
apptainer exec ri-scale-dashboard.sif python /opt/ri-scale/backend/app/services/dps_service/dps_service.py \
    -m /opt/ri-scale/backend/app/services/dps_service/example_manifest.yaml -v
```

### Interactive Shell

```bash
apptainer shell ri-scale-dashboard.sif
# Inside container:
cd /opt/ri-scale
python --version
npm --version
```

## Binding Host Directories

Mount your local directories into the container:

```bash
# Bind data directory
apptainer exec --bind /host/data:/data ri-scale-dashboard.sif ls /data

# Bind multiple directories
apptainer exec --bind /host/data:/data,/host/output:/output ri-scale-dashboard.sif bash
```

## Network Options

### Run with Network Access

```bash
apptainer run --net ri-scale-dashboard.sif
```

### Port Mapping (on some systems)

```bash
apptainer run --net --network=bridge ri-scale-dashboard.sif
```

## Performance Considerations

### GPU Support (NVIDIA)

If you need NVIDIA GPU support, add `--nv` flag:

```bash
apptainer exec --nv ri-scale-dashboard.sif python train_model.py
```

This requires:
- NVIDIA GPU
- NVIDIA Docker runtime installed
- Container built with NVIDIA support (modify Apptainer.def)

### HPC Job Submission

#### SLURM Example

Create `slurm_job.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=ri-scale-job
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --gpus-per-node=1

module load apptainer

apptainer run /path/to/ri-scale-dashboard.sif
```

Submit with:
```bash
sbatch slurm_job.sh
```

#### PBS/Torque Example

Create `pbs_job.sh`:

```bash
#!/bin/bash
#PBS -N ri-scale-job
#PBS -l select=1:ncpus=8:mem=32gb:ngpus=1
#PBS -l walltime=02:00:00
#PBS -q gpu

apptainer run /path/to/ri-scale-dashboard.sif
```

Submit with:
```bash
qsub pbs_job.sh
```

## Customizing the Container

### Modify Apptainer.def

Edit the `Apptainer.def` file to:
- Change Python/Node versions
- Add additional system packages
- Modify environment variables
- Add custom startup scripts

Then rebuild:
```bash
sudo apptainer build ri-scale-dashboard.sif Apptainer.def
```

### Adding Python Packages

Modify the requirements section in `Apptainer.def`:

```
pip install --no-cache-dir -r /tmp/requirements.txt
pip install --no-cache-dir additional-package==1.0.0
```

## Troubleshooting

### Permission Denied on Bind Mounts

Ensure the directory on the host is readable:
```bash
chmod 755 /host/data
apptainer exec --bind /host/data:/data ri-scale-dashboard.sif ls /data
```

### Out of Memory During Build

If building fails due to memory:
- Use a system with more RAM
- Use `--fakeroot` instead of `sudo`
- Build on an HPC cluster with more resources

### Container Won't Start

Check the build log:
```bash
apptainer build --verbose ri-scale-dashboard.sif Apptainer.def
```

Verify environment setup:
```bash
apptainer exec ri-scale-dashboard.sif env | grep -i python
```

### Module Not Found Errors

Verify Python packages are installed:
```bash
apptainer exec ri-scale-dashboard.sif pip list
```

## Container Details

### What's Inside

- **Base Image**: Python 3.11 slim (Debian-based)
- **Python Packages**: FastAPI, Uvicorn, NumPy, Pandas, Pillow, OpenSlide, etc.
- **Node.js**: v20 for frontend development
- **System Libraries**: OpenSlide tools, image processing libraries, development headers

### Installed in /opt/ri-scale

```
/opt/ri-scale/
├── backend/          # FastAPI application
│   └── app/
│       ├── main.py   # Main FastAPI app
│       └── services/ # DPS service
├── frontend/         # Vue.js application
└── configs/          # Configuration files
```

## Production Deployment

For production use:

1. **Reduce image size** (optional):
   ```bash
   apptainer build --compress ri-scale-dashboard-prod.sif Apptainer.def
   ```

2. **Use environment variables** for configuration:
   ```bash
   apptainer run \
     --env PYTHONUNBUFFERED=1 \
     --env LOG_LEVEL=INFO \
     ri-scale-dashboard.sif
   ```

3. **Mount volumes** for persistent data:
   ```bash
   apptainer run \
     --bind /data:/data \
     --bind /output:/output \
     ri-scale-dashboard.sif
   ```

4. **Run with resource limits** (where supported):
   ```bash
   apptainer run \
     --memory 8G \
     --cpus 4 \
     ri-scale-dashboard.sif
   ```

## Additional Resources

- [Apptainer Documentation](https://apptainer.org/docs/)
- [RI-SCALE Project](https://ri-scale.eu/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)

## Support

For issues related to:
- **Apptainer**: See [Apptainer GitHub Issues](https://github.com/apptainer/apptainer/issues)
- **RI-SCALE Dashboard**: Check project repository and documentation
- **HPC Integration**: Contact your cluster administrator
