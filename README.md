# RI-SCALE Dashboard – Scientific Use Cases UC7 & UC8

This repository contains the **dashboard implementation and supporting material** for two scientific use cases developed within the **RI-SCALE (Unlocking RI potential with Scalable AI and Data)** project:

- **UC7 – Colorectal cancer prediction with explainable AI**
- **UC8 – Synthetic data generation for computational pathology**

The repository accompanies the RI-SCALE **Data Exploitation Platform (DEP)** concept and demonstrates how sensitive biomedical datasets, AI models, and high-performance computing (HPC) resources can be orchestrated through a unified dashboard.

---

## 📌 Project Context

**RI-SCALE** is a Horizon Europe project delivering **Data Exploitation Platforms (DEPs)** that:
- Co-host scientific data and AI frameworks
- Integrate secure data access, identity, and trust mechanisms
- Enable scalable AI workflows on national and European e-infrastructures

Within RI-SCALE, **BBMRI-ERIC** leads the biomedical use cases focusing on **digital pathology and sensitive health data**.

This repository focuses specifically on the **dashboard layer** connecting:
- BBMRI-ERIC Directory
- BBMRI-ERIC Negotiator
- Model repositories
- Secure Processing Environments (SPEs) / HPC sites

---

## 🧪 Scientific Use Cases Covered

### UC7 – Colorectal Cancer Prediction with Explainable AI
- Weakly supervised learning on lymph node whole-slide images (WSIs)
- Survival-guided training strategies
- Large-scale datasets (≈ 3,000 cases / 45,000 WSIs)
- Goal: identify novel, explainable digital biomarkers not detectable by conventional pathology

### UC8 – Synthetic Data for Computational Pathology
- Generation of synthetic whole-slide images to overcome:
  - Privacy restrictions
  - Consent limitations
  - Data sharing barriers
- Extremely high-resolution image synthesis (up to 100k × 100k pixels)
- Supports downstream AI training, benchmarking, and method development

---

## 🧩 Dashboard Scope

The dashboard acts as the **operational control plane** for RI-SCALE biomedical workflows.

### Key Capabilities
- Project-based overview of approved data access requests
- Monitoring of:
  - Data transfers
  - Computation jobs
  - Result generation and return
- Aggregation of metadata from DEP tools
- Role-based access via LifeScience AAI
- Links to external tools and services with contextual login

### Integrated Components
- **Directory**  
  Dataset discovery and indication of computability (e.g. “Request Compute” flag)

- **Negotiator**  
  Formalised access requests including:
  - Selected datasets
  - Selected AI models (optional)
  - Selected HPC / AI Factory sites
  - Ethics, DPIA, and contractual constraints

- **Model Store (conceptual)**  
  Reference to RI-SCALE / BBMRI-ERIC model repositories used for analysis

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** >= 18.x
- **Python** >= 3.10
- **pip** (Python package manager)

### 1. Start the Backend (required for Pipeline Builder)

```bash
cd backend
pip install -r requirements.txt
cd app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at `http://localhost:8000`

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Test Credentials

- **Username:** `test`
- **Password:** `test`

---

## 🏗 Repository Structure

```text
.
├── frontend/                # Vue.js 3 dashboard application
│   ├── src/
│   │   ├── views/           # Page components (Dashboard, Pipeline Builder, etc.)
│   │   ├── components/      # Reusable UI components
│   │   ├── services/        # API service layers
│   │   └── stores/          # Pinia state management
│   └── README.md            # Frontend documentation
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── main.py          # API entry point
│   │   └── services/
│   │       └── dps_service/ # Data Preparation Service
│   └── README.md            # Backend documentation
├── configs/                 # Shared configuration
│   └── step_types_config.yaml  # Pipeline step definitions
├── README.md
└── LICENSE
