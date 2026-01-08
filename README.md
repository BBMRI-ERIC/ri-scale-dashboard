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

## 🏗 Repository Structure (expected)

```text
.
├── dashboard/
│   ├── frontend/        # UI components and views
│   ├── backend/         # APIs and integration logic
│   └── config/          # Environment and deployment configs
├── docs/
│   ├── architecture.md  # Dashboard & DEP architecture
│   ├── workflows.md     # UC7 / UC8 workflows
│   └── screenshots/     # Dashboard screenshots
├── assets/
│   └── diagrams/        # Architecture & workflow diagrams
├── README.md
└── LICENSE
Note: The structure may evolve as the dashboard prototype matures.
🔐 Data Protection & Ethics
This repository does not contain any sensitive data.
All real data access within UC7 and UC8 is governed by:

BBMRI-ERIC Negotiator workflows
Ethics approvals and DPIA documentation
Contractual data access conditions
Secure Processing Environments (SPEs)
The dashboard only visualises metadata, status information, and aggregated metrics.
📄 Reference Material
The conceptual and architectural basis for this repository is documented in:
RI-SCALE Grant Proposal (HORIZON-INFRA-2024-TECH-01)
BBMRI-ERIC RI-SCALE Workflow & Dashboard Presentation
These documents provide the authoritative description of:
Data Exploitation Platforms (DEPs)
Scientific use cases
Workflow orchestration
Governance and trust model
🤝 Contributors
BBMRI-ERIC Common Service IT
RI-SCALE project partners
Scientific use case teams (UC7 & UC8)
