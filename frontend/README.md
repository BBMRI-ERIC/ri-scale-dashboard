# RI-SCALE Dashboard Frontend

Vue.js 3 frontend application for the RI-SCALE Data Exploitation Platform dashboard.

## Technology Stack

- **Vue.js 3** - Progressive JavaScript framework
- **Vuetify 3** - Material Design component library
- **Vite** - Fast build tool and development server
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Sass/SCSS** - CSS preprocessing

## Prerequisites

- **Node.js** >= 18.x
- **npm** >= 9.x (or pnpm/yarn)

## Getting Started

### Install Dependencies

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000` (or `http://localhost:5173` depending on Vite config).

### Backend Server (Required for Pipeline Builder)

The **Pipeline Builder** feature requires the backend server to be running. See [backend/README.md](../backend/README.md) for setup instructions.

**Quick start:**
```bash
# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
cd app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Build for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/                  # Static assets
│   ├── favicon.png          # Browser favicon (32x32)
│   ├── logo.png             # Full-size logo
│   ├── logo-32.png          # Logo for sidebar (32x32)
│   └── logo-48.png          # Logo for login page (48x48)
├── src/
│   ├── components/          # Reusable Vue components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   │   └── ProjectCard.vue
│   │   ├── layout/          # Layout components
│   │   │   ├── AppHeader.vue
│   │   │   └── AppSidebar.vue
│   │   └── settings/        # Settings components
│   │       └── SettingsDialog.vue
│   ├── plugins/             # Vue plugins
│   │   └── vuetify.js       # Vuetify configuration
│   ├── router/              # Vue Router configuration
│   │   └── index.js
│   ├── services/            # API services
│   │   └── auth.js          # Authentication service
│   ├── stores/              # Pinia stores
│   │   ├── auth.js          # Authentication state
│   │   ├── index.js         # Store exports
│   │   ├── projects.js      # Projects state
│   │   └── settings.js      # User settings state
│   ├── styles/              # Global styles
│   │   └── main.scss        # Global SCSS with unified layout system
│   ├── views/               # Page components
│   │   ├── AboutView.vue
│   │   ├── ComputationsView.vue      # HPC Jobs
│   │   ├── ComputeResourcesView.vue  # Compute Quotas
│   │   ├── DashboardView.vue
│   │   ├── DatasetsView.vue
│   │   ├── DataTransfersView.vue
│   │   ├── DirectoryView.vue
│   │   ├── LoginView.vue
│   │   ├── ModelsView.vue            # Model Hub
│   │   ├── NegotiatorView.vue
│   │   ├── NotFoundView.vue
│   │   └── ProjectDetailView.vue
│   ├── App.vue              # Root component
│   └── main.js              # Application entry point
├── index.html               # HTML entry point
├── package.json             # Dependencies and scripts
└── vite.config.js           # Vite configuration
```

## Available Pages

| Route | Page | Description |
|-------|------|-------------|
| `/login` | Login | User authentication |
| `/dashboard` | Dashboard | Overview with project cards/table, stats, and recent activity |
| `/directory` | Directory | BBMRI-ERIC dataset discovery and compute request |
| `/negotiator` | Negotiator | Access request management and tracking |
| `/datasets` | Datasets | View datasets across all projects with filtering |
| `/transfers` | Data Transfers | Monitor data transfers between storage and HPC sites |
| `/pipelines` | Pipeline Builder | Visual pipeline builder for data preparation workflows |
| `/computations` | HPC Jobs | Manage and monitor HPC computation jobs |
| `/models` | Model Hub | Browse and deploy AI models for pathology analysis |
| `/resources` | Compute Quotas | Monitor storage and GPU hour quotas per project |
| `/about` | About | Project information, partners, and platform capabilities |
| `/projects/:id` | Project Detail | Detailed view of a specific project |

## Features

### Dashboard
- Welcome section with user greeting
- Quick stats overview (projects, datasets, computations, transfers)
- Active projects with grid/table view toggle
- Recent activity feed

### Project Selection
- Sidebar project selector for filtering data across pages
- "All Projects" option to view aggregated data
- Project-specific filtering on HPC Jobs, Data Transfers, and Compute Quotas

### Data Management
- **Directory**: Discover BBMRI-ERIC datasets and request compute access
- **Datasets**: View all datasets with project assignments and primary storage info
- **Data Transfers**: Monitor transfers between BBMRI-AT Storage, MUG Storage → MUSICA, MUG-SX

### Compute Management
- **HPC Jobs**: Create, monitor, and manage computation jobs with resource allocation (nodes, GPUs, memory)
- **Model Hub**: Browse AI models (Virchow2, Tissue Segmentation, Synthetic Image Generation, Lymph Node Survival Prediction)
- **Compute Quotas**: Track storage (TB) and GPU hour quotas per project with usage visualization

### Access Requests
- **Negotiator**: Full workflow for creating and managing data access requests
- Request wizard with dataset selection and justification
- Status tracking (pending, in review, approved, rejected)

### Pipeline Builder
- **Visual Pipeline Designer**: Drag-and-drop interface for building data preparation workflows
- **Stage Library**: Pre-configured step types (Data Loader, Run Command, Join)
- **Command Chains**: Composite pipelines for common tasks (e.g., DICOM conversion)
- **YAML Editor**: View and edit pipeline manifests directly
- **Save/Load**: Persist pipelines per project to the backend
- **Requires Backend**: The Pipeline Builder requires the backend server to be running on port 8000

## Test Credentials

For development, use the following test credentials:

- **Username:** `test`
- **Password:** `test`

## Test Data

The application includes mock data for demonstration:

### Projects
- UC7 - CRC Prediction (Colorectal Cancer Prediction Study)
- UC8 - Synthetic Data (Synthetic WSI Generation Pipeline)
- UC7 - XAI Validation (Explainable AI Biomarker Validation)
- UC8 - MR Benchmark (Multi-Resolution Synthesis Benchmark)

### Compute Quotas
| Project | Storage Quota | GPU Hours Quota |
|---------|---------------|-----------------|
| UC7 - CRC Prediction | 20 TB | 10,000 hrs |
| UC8 - Synthetic Data | 15 TB | 5,000 hrs |
| UC7 - XAI Validation | 10 TB | 3,000 hrs |
| UC8 - MR Benchmark | 25 TB | 10,000 hrs |

## Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory (see `.env.example`):

```env
# DPS (Data Preparation Service) API URL for Pipeline Builder
# Default: http://localhost:8000 (for local development)
VITE_DPS_API_URL=http://localhost:8000

# API Base URL (when backend is available)
VITE_API_BASE_URL=http://localhost:8000/api

# Feature flags
VITE_USE_MOCK_SERVICES=true
```

### Theme

The application uses a custom dark theme with:
- **Primary/Accent Color**: `#E69830` (amber/orange)
- **Background**: Dark gradient (`#0a0f1a` to `#111827`)
- **Font**: DM Sans (UI), JetBrains Mono (code/data)

Theme configuration is in `src/plugins/vuetify.js` and `src/styles/main.scss`.

## Development Notes

### Mock Data

The frontend currently uses mock data for all services. Mock data is defined in:
- `src/stores/projects.js` - Project data with owners, sites, and stats
- `src/views/*.vue` - Page-specific mock data (transfers, jobs, models, datasets, quotas)

### Adding New Pages

1. Create a new view component in `src/views/`
2. Add the route in `src/router/index.js`
3. Add navigation item in `src/components/layout/AppSidebar.vue`

### Unified Page Styling

All pages share common layout styles defined in `src/styles/main.scss`:
- `.dashboard-layout` - Gradient background
- `.page-container` - Content wrapper with max-width
- `.page-header`, `.page-title`, `.title-icon` - Page headers with icons
- `.stat-card`, `.stat-icon` - Stats cards with status variants
- `.glass` - Glassmorphism card effect

### State Management

Pinia stores are located in `src/stores/`:
- `auth.js` - Authentication state and user info
- `projects.js` - Project list, selected project, and filtering
- `settings.js` - User preferences (persisted to localStorage)

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint and fix issues |
