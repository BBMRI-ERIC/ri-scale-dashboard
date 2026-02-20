# RI-SCALE Container Deployment Guide

This guide covers containerization options for the RI-SCALE Dashboard using both **Apptainer** (HPC-optimized) and **Docker** (general-purpose).

## Quick Comparison

| Feature | Apptainer | Docker |
|---------|-----------|--------|
| **Best For** | HPC clusters, sensitive data | Development, cloud, production |
| **Privileged Mode** | Not required | Often required |
| **Security** | Excellent (no privilege escalation) | Good (with caution) |
| **Portability** | HPC clusters | Anywhere |
| **Learning Curve** | Moderate | Easy |
| **Container Size** | Smaller (.sif files) | Larger (images) |
| **GPU Support** | Native (`--nv`) | Plugin-based |
| **Data Binding** | Built-in (`--bind`) | Volume mounts |

## Apptainer (Recommended for HPC)

### Why Apptainer?

- **HPC-Friendly**: Designed for high-performance computing
- **Security**: Runs as user (no privilege escalation)
- **Simplicity**: Single monolithic file
- **Performance**: Better for scientific computing
- **Data Privacy**: Excellent for sensitive biomedical data

### Quick Start with Apptainer

```bash
# Build
sudo apptainer build ri-scale-dashboard.sif Apptainer.def

# Or using helper script
./apptainer.sh build

# Run backend
./apptainer.sh backend

# Run frontend
./apptainer.sh frontend
```

### Full Documentation

- [APPTAINER_GUIDE.md](APPTAINER_GUIDE.md) - Complete guide
- [HPC_CLUSTER_INTEGRATION.md](HPC_CLUSTER_INTEGRATION.md) - Cluster examples
- [APPTAINER_QUICKREF.md](APPTAINER_QUICKREF.md) - Quick reference
- [apptainer.sh](apptainer.sh) - Helper script

## Docker (Recommended for Development/Cloud)

### Why Docker?

- **Developer-Friendly**: Largest container ecosystem
- **Cloud-Ready**: AWS, Google Cloud, Azure, etc.
- **Development**: Hot reload, easier debugging
- **Scaling**: Kubernetes, Docker Swarm support
- **Tools**: Docker Compose, docker-compose CLI

### Quick Start with Docker

```bash
# Build
docker build -t ri-scale-dashboard:latest .

# Run backend
docker run -p 8000:8000 ri-scale-dashboard:latest

# Or using docker-compose
docker-compose up

# Run frontend
docker-compose run frontend npm run dev
```

### With docker-compose (Recommended)

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Choosing Which to Use

### Use Apptainer if:
- ✅ Running on HPC clusters (SLURM, PBS, LSF)
- ✅ Working with sensitive data (HIPAA, GDPR compliance)
- ✅ Deploying to research institutions
- ✅ Need built-in data privacy
- ✅ Simple single-file distribution
- ✅ Performance-critical applications

### Use Docker if:
- ✅ Developing locally
- ✅ Deploying to cloud (AWS, GCP, Azure)
- ✅ Using Kubernetes
- ✅ Need extensive tooling ecosystem
- ✅ Building microservices architecture
- ✅ CI/CD pipeline integration

### Use Both if:
- ✅ Need flexibility for different environments
- ✅ HPC deployment + cloud backup
- ✅ Development (Docker) + Production (Apptainer)

## Installation Requirements

### Apptainer

```bash
# Ubuntu/Debian
sudo apt-get install apptainer

# CentOS/RHEL
sudo dnf install apptainer

# macOS (via conda)
conda install -c conda-forge apptainer

# Build requires
sudo apt-get install build-essential cryptsetup-bin uuid-dev libssl-dev
```

### Docker

```bash
# Ubuntu/Debian
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo dnf install docker docker-compose

# macOS
brew install docker docker-compose

# Or use Docker Desktop
# https://www.docker.com/products/docker-desktop
```

## HPC Cluster Deployment

### With Apptainer

```bash
# Copy container to cluster
scp ri-scale-dashboard.sif user@cluster:/path/to/container/

# Create SLURM job
sbatch submit_job.slurm

# Example job script
#!/bin/bash
#SBATCH --job-name=ri-scale
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1

apptainer exec --nv ri-scale-dashboard.sif python train.py
```

### With Singularity (Legacy)

For older HPC clusters with Singularity (not Apptainer):

```bash
# Apptainer .sif files are compatible with Singularity
singularity run ri-scale-dashboard.sif

# Or build with Singularity
singularity build ri-scale-dashboard.sif Apptainer.def
```

## Development Workflow

### Apptainer Development

```bash
# Edit code on host
vim backend/app/main.py

# Rebuild container
./apptainer.sh build

# Test changes
./apptainer.sh backend
```

### Docker Development

```bash
# With hot reload
docker-compose up

# Changes reflect automatically via volume mounts
# Edit code, changes appear instantly
```

## Production Deployment

### Apptainer Production

```bash
# Build on secure build machine
sudo apptainer build ri-scale-dashboard-prod.sif Apptainer.def

# Transfer to production
scp ri-scale-dashboard-prod.sif user@prod-server:/opt/containers/

# Run with data binding
apptainer run \
  --bind /data/input:/input \
  --bind /data/output:/output \
  /opt/containers/ri-scale-dashboard-prod.sif
```

### Docker Production

```bash
# Build and push to registry
docker build -t myregistry/ri-scale:1.0 .
docker push myregistry/ri-scale:1.0

# Deploy with kubernetes
kubectl apply -f deployment.yaml

# Or with docker swarm
docker stack deploy -c docker-compose.yml ri-scale
```

## Volume/Data Management

### Apptainer

```bash
# Bind host directory
apptainer exec --bind /host/data:/container/data ri-scale-dashboard.sif

# Bind multiple directories
apptainer exec \
  --bind /host/input:/input \
  --bind /host/output:/output \
  --bind /host/models:/models:ro \
  ri-scale-dashboard.sif

# Read-only binding
apptainer exec --bind /data:/data:ro ri-scale-dashboard.sif
```

### Docker

```bash
# Volume mount in docker-compose
volumes:
  - ./data:/app/data
  - ./models:/app/models:ro

# Or using docker run
docker run -v /host/data:/container/data ri-scale-dashboard
```

## Networking

### Apptainer

```bash
# Enable network access
apptainer run --net ri-scale-dashboard.sif

# Expose ports (depends on host network access)
apptainer run --net --port 8000:8000 ri-scale-dashboard.sif
```

### Docker

```bash
# Port mapping
docker run -p 8000:8000 ri-scale-dashboard

# Network mode
docker run --network host ri-scale-dashboard

# docker-compose handles networks automatically
```

## GPU Support

### Apptainer

```bash
# NVIDIA GPU (built-in support)
apptainer exec --nv ri-scale-dashboard.sif python train.py

# No additional setup needed if NVIDIA driver installed
```

### Docker

```bash
# Requires NVIDIA Docker runtime
docker run --gpus all ri-scale-dashboard

# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Performance Comparison

| Operation | Apptainer | Docker |
|-----------|-----------|--------|
| Build time | ~2-3 min | ~2-3 min |
| Container size | ~1.2 GB | ~1.5 GB |
| Startup time | ~100ms | ~500ms |
| Runtime performance | Near-native | ~1-2% overhead |
| Disk I/O | Excellent | Good |
| Memory usage | Lower | Higher |

## Security Considerations

### Apptainer Security

```bash
# User namespace isolation (default)
apptainer run ri-scale-dashboard.sif
# Runs as your user, not root

# Read-only container
apptainer exec --userns ri-scale-dashboard.sif
```

### Docker Security

```bash
# Run as non-root user
docker run --user 1000:1000 ri-scale-dashboard

# Read-only root filesystem
docker run --read-only ri-scale-dashboard

# Security options
docker run --security-opt=no-new-privileges ri-scale-dashboard
```

## Migration Between Apptainer and Docker

### Docker Image → Apptainer Container

```bash
# Some tools can convert
docker run -v /var/run/docker.sock:/var/run/docker.sock \
  --privileged -d --name dind docker:dind

docker pull ri-scale-dashboard:latest
apptainer build ri-scale-dashboard.sif docker://ri-scale-dashboard:latest
```

### Apptainer → Docker (if needed)

```bash
# Convert sandbox to Docker
docker build -f Dockerfile .
```

## Troubleshooting

### Apptainer Issues

```bash
# Check container
apptainer inspect ri-scale-dashboard.sif

# Verbose output
apptainer --verbose run ri-scale-dashboard.sif

# Rebuild
./apptainer.sh build
```

### Docker Issues

```bash
# Check image
docker inspect ri-scale-dashboard

# View logs
docker logs container-id

# Rebuild
docker build --no-cache -t ri-scale-dashboard .
```

## Cost Considerations

| Factor | Apptainer | Docker |
|--------|-----------|--------|
| Infrastructure | HPC clusters (existing) | Cloud (per-hour billing) |
| Development | Minimal tools needed | Docker Desktop license |
| Distribution | Single file | Registry storage |
| Scaling | HPC job queue | Kubernetes/container service |

## Recommendation Summary

**For RI-SCALE (Biomedical AI on HPC):**

1. **Primary**: **Apptainer** for HPC clusters
   - Best for BBMRI-ERIC deployment
   - Secure for sensitive health data
   - Optimized for research environments

2. **Secondary**: **Docker** for development/testing
   - Easier development workflow
   - Testing cloud deployments
   - CI/CD integration

3. **Combined Approach**: Use Docker during development, Apptainer for HPC production

## Next Steps

1. **Choose your deployment target**:
   - HPC cluster → Use Apptainer
   - Local development → Use Docker
   - Both → Use both, in stages

2. **Follow the appropriate guide**:
   - [Apptainer → APPTAINER_GUIDE.md](APPTAINER_GUIDE.md)
   - [Docker → docker-compose.yml](docker-compose.yml)
   - [HPC → HPC_CLUSTER_INTEGRATION.md](HPC_CLUSTER_INTEGRATION.md)

3. **Test your deployment**:
   - Build container
   - Run services
   - Verify API endpoints
   - Test data binding/volumes

## Additional Resources

- [Apptainer Official Docs](https://apptainer.org/docs/)
- [Docker Official Docs](https://docs.docker.com/)
- [NVIDIA Container Guide](https://github.com/NVIDIA/nvidia-docker)
- [RI-SCALE Project](https://ri-scale.eu/)
- [Singularity/Apptainer Comparison](https://apptainer.org/)

---

**Questions?** See the detailed guides linked above or contact your system administrator.
