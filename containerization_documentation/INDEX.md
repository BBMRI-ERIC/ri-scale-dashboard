# RI-SCALE Dashboard Container Setup - Complete Index

## 📋 Overview

Your RI-SCALE Dashboard project now has **complete containerization support** for both **Apptainer** (HPC clusters) and **Docker** (development/cloud).

**Total files created**: 9 files (4 container configs + 5 documentation)

---

## 🗂️ File Structure

```
ri-scale-dashboard/
│
├── Container Configuration Files
│   ├── Apptainer.def              ← HPC container definition
│   ├── Dockerfile                 ← Docker container definition  
│   ├── docker-compose.yml         ← Multi-service orchestration
│   └── apptainer.sh              ← Helper script (executable)
│
├── Documentation Files
│   ├── CONTAINER_SETUP_SUMMARY.md     ← START HERE!
│   ├── CONTAINER_SETUP.sh            ← Setup verification script
│   ├── APPTAINER_QUICKREF.md         ← Quick command reference
│   ├── APPTAINER_GUIDE.md            ← Complete Apptainer guide
│   ├── HPC_CLUSTER_INTEGRATION.md    ← HPC job examples
│   └── CONTAINER_DEPLOYMENT_GUIDE.md ← Deployment strategies
│
└── Existing Project Files
    ├── backend/                    ← FastAPI backend
    ├── frontend/                   ← Vue.js frontend
    ├── configs/                    ← Configuration files
    └── [other project files...]
```

---

## 📖 Documentation Guide

### 1. **START HERE** 👈
**[CONTAINER_SETUP_SUMMARY.md](CONTAINER_SETUP_SUMMARY.md)**
- Overview of what was created
- Quick start instructions
- Verification checklist
- Next steps

### 2. **Quick Reference**
**[APPTAINER_QUICKREF.md](APPTAINER_QUICKREF.md)**
- Common commands (1-page)
- Troubleshooting table
- One-liners
- Port mappings

### 3. **Complete Guide**
**[APPTAINER_GUIDE.md](APPTAINER_GUIDE.md)**
- Installation instructions
- Building containers
- Running services
- GPU support
- Production deployment

### 4. **HPC Integration**
**[HPC_CLUSTER_INTEGRATION.md](HPC_CLUSTER_INTEGRATION.md)**
- SLURM examples
- PBS/Torque examples
- LSF examples
- XSEDE/TACC examples
- Parallel job submission
- Data management

### 5. **Deployment Strategies**
**[CONTAINER_DEPLOYMENT_GUIDE.md](CONTAINER_DEPLOYMENT_GUIDE.md)**
- Apptainer vs Docker comparison
- When to use each
- HPC deployment
- Cloud deployment
- Hybrid approaches

---

## 🎯 Quick Start (Choose One Path)

### Path 1: Apptainer (HPC Clusters)
```bash
cd /home/wilfried/Documents/ri-scale-dashboard

# Option A: Using helper script
./apptainer.sh build
./apptainer.sh backend

# Option B: Direct command
sudo apptainer build ri-scale-dashboard.sif Apptainer.def
apptainer run ri-scale-dashboard.sif

# Frontend
./apptainer.sh frontend
```

### Path 2: Docker (Local Development)
```bash
cd /home/wilfried/Documents/ri-scale-dashboard

# Option A: Using docker-compose
docker-compose up

# Option B: Manual build
docker build -t ri-scale-dashboard:latest .
docker run -p 8000:8000 ri-scale-dashboard:latest
```

### Path 3: Docker Compose (All Services)
```bash
cd /home/wilfried/Documents/ri-scale-dashboard
docker-compose up

# In another terminal
docker-compose logs -f
```

---

## 📦 What's Inside Each Container

### System Base
- **OS**: Debian (slim image)
- **Python**: 3.11
- **Node.js**: 20.x

### Python Libraries
✅ FastAPI (web framework)
✅ Uvicorn (ASGI server)
✅ NumPy & Pandas (data processing)
✅ Pillow & OpenSlide (image processing)
✅ WSIDicomizer (medical imaging)
✅ PyYAML (configuration)

### Frontend Tools
✅ Vue.js 3 (framework)
✅ Vite (build tool)
✅ Vuetify (UI components)
✅ SASS (styling)

### System Libraries
✅ OpenSlide tools (WSI support)
✅ Image processing libraries
✅ Development headers
✅ Build tools

---

## 🚀 Command Cheat Sheet

### Using the Helper Script (Easiest)
```bash
./apptainer.sh help              # Show all commands
./apptainer.sh build             # Build container
./apptainer.sh status            # Check status
./apptainer.sh backend           # Run API server
./apptainer.sh frontend          # Run frontend
./apptainer.sh shell             # Interactive shell
./apptainer.sh dps-pipeline      # Run DPS
./apptainer.sh exec python -c "import fastapi; print(fastapi.__version__)"
```

### Direct Apptainer Commands
```bash
apptainer build ri-scale-dashboard.sif Apptainer.def
apptainer run ri-scale-dashboard.sif
apptainer shell ri-scale-dashboard.sif
apptainer exec ri-scale-dashboard.sif python --version
apptainer exec --bind /data:/data ri-scale-dashboard.sif
apptainer exec --nv ri-scale-dashboard.sif python train.py  # GPU
```

### Docker Commands
```bash
docker build -t ri-scale-dashboard:latest .
docker run -p 8000:8000 ri-scale-dashboard:latest
docker run -p 5173:5173 -v ./frontend:/app node:20 npm run dev
docker-compose up
docker-compose down
docker-compose logs -f
```

### HPC Job Submission
```bash
# SLURM
sbatch submit_backend.slurm

# PBS
qsub submit_backend.pbs

# LSF
bsub < submit_backend.lsf
```

---

## 📊 Comparison Matrix

| Feature | Apptainer | Docker |
|---------|-----------|--------|
| **HPC Clusters** | ✅ Best | ⚠️ Possible |
| **Local Dev** | ✅ Good | ✅✅ Best |
| **Cloud** | ⚠️ Possible | ✅✅ Best |
| **Secure** | ✅✅ | ✅ |
| **Single File** | ✅ | ❌ |
| **Ecosystem** | ⚠️ Limited | ✅✅ Large |
| **Learning Curve** | Moderate | Easy |
| **Performance** | ✅✅ | ✅ |

---

## 🔧 Customization

### Add Python Package
1. Edit `backend/requirements.txt`
2. Rebuild:
   ```bash
   ./apptainer.sh build
   # or
   docker build -t ri-scale-dashboard .
   ```

### Change Port
1. Edit `Apptainer.def` or `docker-compose.yml`
2. Look for port numbers (8000 for backend, 5173 for frontend)
3. Rebuild

### Modify Base Image
1. Edit `Apptainer.def` (line: `From: python:3.11-slim`)
2. Or `Dockerfile` (line: `FROM python:3.11-slim`)
3. Rebuild

### Add System Package
1. Edit `apt-get install` line in definition
2. Add package name
3. Rebuild

---

## 📱 Access Points

Once running:

| Service | URL |
|---------|-----|
| **Backend API** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/docs |
| **Swagger UI** | http://localhost:8000/redoc |
| **Frontend** | http://localhost:5173 |

---

## ✅ Verification Checklist

After building:

- [ ] Container file exists (`.sif` for Apptainer or image for Docker)
- [ ] `apptainer inspect ri-scale-dashboard.sif` or `docker images` shows container
- [ ] `./apptainer.sh status` or `docker ps` shows running state
- [ ] Backend API responds at http://localhost:8000
- [ ] API docs available at http://localhost:8000/docs
- [ ] Frontend loads at http://localhost:5173

---

## 🆘 Troubleshooting

### Apptainer Not Found
```bash
# Install
sudo apt-get install apptainer
# Or check version
apptainer --version
```

### Build Fails
```bash
# Check with verbose output
apptainer build --verbose Apptainer.def ri-scale-dashboard.sif

# Or see logs
./apptainer.sh build
```

### Container Won't Start
```bash
# Inspect container
apptainer inspect ri-scale-dashboard.sif

# Run in shell
apptainer shell ri-scale-dashboard.sif
```

### Docker Issues
```bash
# Check if installed
docker --version

# See logs
docker logs <container-id>

# Rebuild without cache
docker build --no-cache -t ri-scale-dashboard .
```

---

## 📚 Additional Resources

### Apptainer
- [Official Documentation](https://apptainer.org/docs/)
- [GitHub Repository](https://github.com/apptainer/apptainer)
- [Quick Start Guide](https://apptainer.org/docs/quick-start/)

### Docker
- [Official Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### RI-SCALE Project
- [Project Website](https://ri-scale.eu/)
- [Biomedical Use Cases](https://ri-scale.eu/)
- [Project Repository](README.md)

### HPC Resources
- [SLURM Documentation](https://slurm.schedmd.com/)
- [PBS/Torque Documentation](https://www.pbsworks.com/)
- [LSF Documentation](https://www.ibm.com/products/hpc-workload-management)
- [XSEDE/TACC](https://www.xsede.org/)
- [NERSC](https://www.nersc.gov/)
- [ALCF](https://www.alcf.anl.gov/)

---

## 🎓 Learning Path

### Day 1: Setup & Basics
1. Read [CONTAINER_SETUP_SUMMARY.md](CONTAINER_SETUP_SUMMARY.md)
2. Read [APPTAINER_QUICKREF.md](APPTAINER_QUICKREF.md)
3. Build container: `./apptainer.sh build`
4. Run backend: `./apptainer.sh backend`

### Day 2: Detailed Understanding
1. Read [APPTAINER_GUIDE.md](APPTAINER_GUIDE.md)
2. Read [CONTAINER_DEPLOYMENT_GUIDE.md](CONTAINER_DEPLOYMENT_GUIDE.md)
3. Try different commands: `./apptainer.sh help`
4. Test volumes/binding

### Day 3: Deployment
1. Read [HPC_CLUSTER_INTEGRATION.md](HPC_CLUSTER_INTEGRATION.md)
2. Create job script for your cluster
3. Submit test job
4. Monitor and debug

### Optional: Docker
1. Explore [docker-compose.yml](docker-compose.yml)
2. Try `docker-compose up`
3. Compare with Apptainer

---

## 💡 Pro Tips

1. **Use the helper script**: `./apptainer.sh` makes life easier
2. **Read the quick ref first**: [APPTAINER_QUICKREF.md](APPTAINER_QUICKREF.md) is concise
3. **Bind directories**: Use `--bind` to access your data
4. **Check container info**: `apptainer inspect` tells you what's inside
5. **Test locally first**: Before HPC, test on your machine

---

## 📞 Getting Help

### For Apptainer Issues
1. Check [APPTAINER_QUICKREF.md](APPTAINER_QUICKREF.md) - Troubleshooting section
2. See [APPTAINER_GUIDE.md](APPTAINER_GUIDE.md) - Troubleshooting section
3. Run: `apptainer help`
4. Visit: [https://apptainer.org/](https://apptainer.org/)

### For Docker Issues
1. Check [docker-compose.yml](docker-compose.yml) examples
2. See [CONTAINER_DEPLOYMENT_GUIDE.md](CONTAINER_DEPLOYMENT_GUIDE.md)
3. Run: `docker help` or `docker-compose help`
4. Visit: [https://docs.docker.com/](https://docs.docker.com/)

### For RI-SCALE Issues
1. See [README.md](README.md)
2. Check [SERVICE-LAYER-ARCHITECTURE.md](SERVICE-LAYER-ARCHITECTURE.md)
3. See [HPC_JOBS_BACKEND.md](HPC_JOBS_BACKEND.md)

---

## ✨ Summary

You now have:
- ✅ **Production-ready Apptainer container** (HPC-optimized)
- ✅ **Production-ready Docker container** (development-friendly)
- ✅ **Docker Compose setup** (multi-service orchestration)
- ✅ **Helper script** (easy management)
- ✅ **5 comprehensive guides** (complete documentation)
- ✅ **HPC integration examples** (SLURM, PBS, LSF, etc.)

**Next step**: Start with [CONTAINER_SETUP_SUMMARY.md](CONTAINER_SETUP_SUMMARY.md)

---

**Created**: February 5, 2026  
**Project**: RI-SCALE Dashboard  
**Status**: ✅ Ready to Deploy
