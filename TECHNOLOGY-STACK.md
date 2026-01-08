# Technology Stack - RI-SCALE Dashboard

This document outlines the technology stack for the RI-SCALE Dashboard implementation, including core technologies and recommended additions.

---

## 🎯 Core Technology Stack

### Frontend
- **Vue.js 3** (Composition API)
  - Modern, reactive framework for building user interfaces
  - Excellent ecosystem and community support
  - Good performance and developer experience

### Backend
- **Flask** (Python)
  - Lightweight and flexible web framework
  - Easy integration with scientific Python libraries
  - Good for RESTful API development
  - Compatible with BBMRI-ERIC ecosystem (Python-based tools)

### Deployment
- **Docker** & **Docker Compose**
  - Containerized deployment for consistency
  - Easy environment management
  - Scalable architecture

---

## 🗄️ Database & Data Management

### Primary Database
- **PostgreSQL** (recommended)
  - Robust relational database
  - Excellent for structured project metadata
  - Strong ACID compliance
  - Good performance for complex queries
  - ORM support via SQLAlchemy

  **Alternative:** MySQL/MariaDB (if preferred by infrastructure)

### Database Management
- **Adminer** (Docker container)
  - Lightweight database management tool
  - Web-based interface for database administration
  - Supports PostgreSQL, MySQL, and other databases
  - No installation required (runs in container)

### ORM (Object-Relational Mapping)
- **SQLAlchemy** (Python)
  - Flask-SQLAlchemy for Flask integration
  - Database abstraction layer
  - Migration support via Flask-Migrate
  - Type-safe queries

---

## 🔍 Monitoring & Observability

### Application Monitoring
- **Prometheus** (metrics collection)
  - Time-series database for metrics
  - Pull-based metrics collection
  - Industry standard for monitoring

- **Grafana** (visualization)
  - Rich dashboards for metrics visualization
  - Integration with Prometheus
  - Customizable alerts and notifications
  - Real-time monitoring capabilities

### Logging
- **ELK Stack** (Elasticsearch, Logstash, Kibana) - **Recommended**
  - Centralized logging solution
  - Log aggregation and analysis
  - Powerful search and visualization
  - Good for debugging and audit trails

  **Alternative (Lighter):**
  - **Loki + Grafana** (lightweight logging)
  - Simpler setup, good for smaller deployments
  - Integrated with Grafana dashboards

### Health Checks & Uptime
- **Health check endpoints** in Flask
- **Uptime monitoring** via Prometheus/Grafana
- **Alertmanager** (with Prometheus) for alerting

---

## 🔐 Authentication & Security

### Authentication
- **Flask-Login** or **Flask-Session**
  - Session management
  - User authentication state

- **OAuth2/OIDC Client** (for LifeScience AAI)
  - **Authlib** (Python) - OAuth2/OIDC client library
  - Integration with LifeScience AAI identity provider
  - JWT token handling

### Security
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Flask-Limiter** - Rate limiting for API protection
- **python-jose** - JWT token validation
- **cryptography** - Encryption utilities
- **bcrypt** - Password hashing (if needed for local accounts)

---

## 🌐 Frontend Ecosystem

### Vue.js Core Libraries
- **Vue Router** - Client-side routing
- **Pinia** (or Vuex) - State management
  - Pinia recommended (Vue 3 native, simpler API)
- **Axios** - HTTP client for API calls
- **VueUse** - Collection of Vue composition utilities

### UI Framework
- **Vuetify 3** (recommended)
  - Material Design components
  - Comprehensive component library
  - Good accessibility support
  - Responsive design built-in

  **Alternatives:**
  - **Quasar** - Full-featured Vue framework
  - **PrimeVue** - Enterprise-grade components
  - **Element Plus** - Popular component library

### Form Handling & Validation
- **VeeValidate** - Form validation
- **Yup** or **Zod** - Schema validation

### Data Visualization
- **Chart.js** with **vue-chartjs**
  - For statistics dashboards
  - Various chart types (line, bar, pie, etc.)

- **Apache ECharts** (via vue-echarts)
  - Advanced data visualization
  - Good for complex metrics displays

### HTTP & API Communication
- **Axios** - Promise-based HTTP client
- **Vue Query** (TanStack Query for Vue) - **Recommended**
  - Powerful data fetching and caching
  - Automatic refetching and synchronization
  - Great for dashboard real-time updates

---

## 🔌 Backend Ecosystem

### Flask Extensions
- **Flask-RESTful** or **Flask-RESTX** - RESTful API development
  - Flask-RESTX recommended (includes Swagger/OpenAPI docs)
- **Flask-CORS** - CORS handling
- **Flask-JWT-Extended** - JWT token management (if needed)
- **Flask-Migrate** - Database migrations (Alembic wrapper)
- **Flask-Caching** - Caching support (Redis integration)

### API Documentation
- **Flask-RESTX** (includes Swagger UI)
  - Auto-generated API documentation
  - Interactive API testing interface
  - OpenAPI 3.0 specification

### Task Queue (for async operations)
- **Celery** with **Redis** (recommended)
  - Background task processing
  - Long-running operations (data transfers, computations)
  - Scheduled tasks
  - Task status tracking

  **Alternative (Lighter):**
  - **RQ (Redis Queue)** - Simpler task queue
  - Good for smaller workloads

### Caching
- **Redis** (Docker container)
  - Session storage
  - Cache layer
  - Task queue backend (if using Celery/RQ)

### API Client Libraries
- **requests** - HTTP client for external API calls
  - Directory API integration
  - Negotiator API integration
  - DEP tools API integration

- **httpx** (recommended for async)
  - Async HTTP client
  - Good for concurrent API calls
  - Used in real DEP service implementations

### Service Layer Architecture
- **ABC (Abstract Base Classes)** - Define service interfaces
  - Service abstraction pattern for DEP integration
  - Allows gradual migration from mock to real services
- **typing.Protocol** - Structural subtyping (alternative to ABC)
- **Pydantic** - Data validation and models for service responses
  - Type-safe data structures
  - Service request/response models
- **Faker** - Generate realistic mock data for development
- **responses** or **httpx-mock** - Mock HTTP responses for testing
- **Service Factory Pattern** - Configuration-based service selection
  - Switch between mock and real implementations
  - Environment-based configuration

---

## 🐳 Docker & Containerization

### Core Containers
- **Application Container** (Flask backend)
- **Frontend Container** (Vue.js - built static files served by Nginx)
- **PostgreSQL Container** (database)
- **Redis Container** (caching/task queue)
- **Adminer Container** (database management)
- **Nginx Container** (reverse proxy, static file serving)

### Monitoring Containers
- **Prometheus Container** (metrics)
- **Grafana Container** (visualization)
- **Node Exporter** (system metrics)
- **cAdvisor** (container metrics)

### Optional Containers
- **Elasticsearch Container** (if using ELK)
- **Logstash Container** (if using ELK)
- **Kibana Container** (if using ELK)

### Docker Compose
- **docker-compose.yml** for orchestration
- Environment-specific configurations:
  - `docker-compose.dev.yml` (development)
  - `docker-compose.prod.yml` (production)

---

## 🔄 Development Tools

### Code Quality
- **Black** - Python code formatter
- **Flake8** or **Ruff** - Python linter
  - Ruff recommended (faster, modern)
- **ESLint** - JavaScript/Vue.js linter
- **Prettier** - Code formatter for Vue/JS
- **mypy** - Python type checking

### Testing
- **pytest** - Python testing framework
  - pytest-flask for Flask testing
- **Vitest** or **Jest** - Vue.js unit testing
- **Vue Test Utils** - Vue component testing
- **Playwright** or **Cypress** - E2E testing
  - Playwright recommended (modern, fast)

### Development Server
- **Vite** - Vue.js build tool and dev server
  - Fast HMR (Hot Module Replacement)
  - Modern build tooling

### API Testing
- **Postman** or **Insomnia** - API testing tools
- **HTTPie** - CLI HTTP client

---

## 📦 Package Management

### Python
- **pip** - Package installer
- **Poetry** (recommended) or **pip-tools**
  - Dependency management
  - Virtual environment management
  - Lock file for reproducible builds

### JavaScript/Node.js
- **npm** or **yarn** or **pnpm**
  - pnpm recommended (faster, disk-efficient)

---

## 🔐 Environment & Configuration

### Environment Variables
- **python-dotenv** - Environment variable management
- **docker-compose** environment files (.env)

### Configuration Management
- **Pydantic** - Settings management with validation
  - Type-safe configuration
  - Environment variable parsing

---

## 📡 API Integration & Communication

### WebSocket (for real-time updates)
- **Flask-SocketIO** - WebSocket support for Flask
  - Real-time statistics updates
  - Live job status notifications

### Message Queue (if needed for distributed systems)
- **RabbitMQ** (alternative to Redis for Celery)
  - More robust for complex messaging
  - Better for multi-server deployments

### Service Discovery (if needed)
- **Consul** or **etcd** (for microservices architecture)

---

## 📊 Additional Recommended Tools

### Documentation
- **Sphinx** - Python documentation generator
- **VitePress** or **VuePress** - Vue.js documentation
- **Swagger/OpenAPI** - API documentation (via Flask-RESTX)

### CI/CD
- **GitHub Actions** or **GitLab CI**
  - Automated testing
  - Docker image building
  - Deployment automation

### Version Control
- **Git** - Source control
- **GitHub** or **GitLab** - Repository hosting

### Backup & Recovery
- **pg_dump** - PostgreSQL backup
- **Automated backup scripts** (cron jobs in container)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                 │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
       ┌───────▼───────┐      ┌───────▼────────┐
       │  Vue.js       │      │  Flask         │
       │  Frontend     │      │  Backend       │
       │  (Static)     │      │  (API)         │
       └───────────────┘      └───────┬────────┘
                                       │
              ┌────────────────────────┼────────────────────┐
              │                        │                    │
       ┌──────▼──────┐        ┌───────▼──────┐   ┌────────▼──────┐
       │ PostgreSQL  │        │    Redis     │   │   Celery      │
       │   (DB)      │        │  (Cache/MQ)  │   │  (Workers)    │
       └─────────────┘        └──────────────┘   └───────────────┘
              │
       ┌──────▼──────┐
       │  Adminer    │
       │  (DB Admin) │
       └─────────────┘

┌─────────────────────────────────────────────────────────┐
│         Service Layer (DEP Integration)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Abstract   │  │    Mock     │  │    Real      │  │
│  │  Interfaces  │◀─│  Services   │  │  DEP Services│  │
│  │   (ABC)      │  │  (Dev/Test) │  │  (Production)│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ▲                    │              │          │
│         └────────────────────┴──────────────┘          │
│                    Service Factory                      │
│              (Config-based selection)                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Monitoring Stack                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │Prometheus│───▶│ Grafana  │    │  ELK/    │          │
│  │(Metrics) │    │(Dashboards)│  │  Loki   │          │
│  └──────────┘    └──────────┘    └──────────┘          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Technology Stack Summary

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Frontend** | Vue.js 3 | UI framework |
| **Frontend State** | Pinia | State management |
| **Frontend UI** | Vuetify 3 | Component library |
| **Frontend Build** | Vite | Build tool & dev server |
| **Backend** | Flask | API server |
| **Database** | PostgreSQL | Primary data storage |
| **DB Admin** | Adminer | Database management UI |
| **ORM** | SQLAlchemy | Database abstraction |
| **Caching** | Redis | Cache & session store |
| **Task Queue** | Celery + Redis | Background tasks |
| **Monitoring** | Prometheus + Grafana | Metrics & visualization |
| **Logging** | ELK Stack / Loki | Log aggregation |
| **Containerization** | Docker + Compose | Deployment |
| **Reverse Proxy** | Nginx | Static files & routing |
| **API Docs** | Flask-RESTX | Swagger/OpenAPI |
| **Service Layer** | ABC + Pydantic | DEP service abstraction |
| **Mock Services** | Faker + httpx-mock | Development & testing |
| **Testing** | pytest + Vitest | Unit & integration tests |
| **E2E Testing** | Playwright | End-to-end tests |

---

## 🚀 Getting Started Recommendations

1. **Start with core stack**: Vue.js + Flask + PostgreSQL + Docker
2. **Implement service layer early**: Set up service abstraction layer with mock implementations
   - Allows development without waiting for DEP services
   - See `SERVICE-LAYER-ARCHITECTURE.md` for detailed guide
3. **Add monitoring early**: Prometheus + Grafana for visibility
4. **Implement Adminer**: Quick database management during development
5. **Add Redis**: For caching and future task queue needs
6. **Set up CI/CD**: Automated testing and deployment
7. **Add logging**: ELK or Loki for production debugging
8. **Gradually migrate services**: Replace mock services with real DEP services as they become available

---

## 📝 Notes

- All technologies should be containerized using Docker for consistency
- Use Docker Compose for local development and testing
- Consider production orchestration (Kubernetes) if scaling is needed
- Keep dependencies up to date for security
- Follow security best practices for all components
- **Service Layer Pattern**: Use abstraction layer for all DEP integrations to enable gradual migration from mock to real services

---

## 🔄 Service Layer Integration

The service layer architecture enables:
- **Development independence**: Build dashboard features while DEP services are in development
- **Gradual migration**: Replace mock services one-by-one as real services become available
- **Easy testing**: Mock implementations simplify unit and integration testing
- **Configuration-based switching**: Toggle between mock and real services via environment variables

**Key Technologies:**
- ABC (Abstract Base Classes) for service interfaces
- Pydantic for type-safe data models
- Faker for realistic mock data generation
- Service Factory pattern for dependency injection
- httpx for async HTTP calls in real implementations

See `SERVICE-LAYER-ARCHITECTURE.md` for complete implementation guide and examples.

---

*Last updated: Technology stack specification for RI-SCALE Dashboard, including service layer architecture*

