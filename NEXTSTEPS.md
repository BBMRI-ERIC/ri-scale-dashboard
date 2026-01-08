# Next Steps - RI-SCALE Dashboard Implementation

This document outlines the implementation roadmap for the RI-SCALE Dashboard, based on the workflow and functionality requirements described in the project documentation.

---

## 🎯 Overview

The dashboard will serve as the central operational control plane connecting:
- **BBMRI-ERIC Directory** (dataset discovery)
- **BBMRI-ERIC Negotiator** (access request management)
- **Secure Processing Environments (SPEs)** / HPC sites
- **Model repositories** (AI/ML models for analysis)

---

## 📋 Phase 1: Core Infrastructure Setup

### 1.1 Project Structure
- [ ] Create `dashboard/` directory structure:
  - `frontend/` - React/Next.js UI components
  - `backend/` - API server (Python/FastAPI or Node.js/Express)
  - `config/` - Environment configurations and deployment files
- [ ] Set up development environment and dependencies
- [ ] Configure authentication integration with **LifeScience AAI**
- [ ] Set up database schema for project metadata storage

### 1.2 Authentication & Authorization
- [ ] Integrate LifeScience AAI for user authentication
- [ ] Implement role-based access control (RBAC):
  - Project administrators
  - Data holders
  - Researchers/analysts
  - SPE operators
- [ ] Create session management and token handling

### 1.3 Service Layer Architecture
- [ ] Implement service abstraction layer for DEP integration:
  - Create abstract base classes (ABC) for service interfaces:
    - `DataTransferService` - Data transfer operations
    - `ComputationService` - Computation job management
    - `StatisticsService` - Statistics and metrics retrieval
    - `ModelService` - Model repository operations
  - Implement mock services for development:
    - `MockDataTransferService` - Simulated data transfers
    - `MockComputationService` - Simulated computation jobs
    - `MockStatisticsService` - Generated statistics data
    - `MockModelService` - Mock model catalog
  - Create service factory pattern for configuration-based service selection
  - Set up Pydantic models for all service data structures
  - Configure environment-based switching (mock/real services)
- [ ] Benefits:
  - Development can proceed without waiting for DEP services
  - Gradual migration from mock to real services
  - Easy testing with mock implementations
  - Consistent interface regardless of implementation

---

## 📋 Phase 2: Directory Integration

### 2.1 Directory API Integration
- [ ] Connect to BBMRI-ERIC Directory API
- [ ] Implement dataset discovery and search functionality
- [ ] Add **"REQUEST COMPUTE"** button/flag to dataset listings
  - This indicates that the dataset can be analyzed in a Secure Processing Environment (SPE) of BBMRI-ERIC
  - Store this attribute in the directory metadata

### 2.2 Dataset Metadata Display
- [ ] Display dataset information:
  - Dataset identifier
  - Data holder/site information
  - Available compute capabilities
  - Associated metadata and descriptions

---

## 📋 Phase 3: Negotiator Integration

### 3.1 Negotiation Form Integration
- [ ] Connect to BBMRI-ERIC Negotiator API
- [ ] Implement negotiation request creation workflow:
  - **PROJECT** section:
    - Title (e.g., "Generation of Synthetic Data")
    - Description
  - **REQUEST** section:
    - Description of data access request
  - **ETHICS VOTE** section:
    - Ethics vote status (Yes/No)
    - Attachment upload capability
  - Save draft and submit functionality

### 3.2 Project Creation & Management
- [ ] Handle approved negotiation requests
- [ ] Create **PROJECT** entities with unique IDs upon approval
- [ ] Store project metadata including:
  - Dataset identifiers (from LifeScience AAI)
  - Data transfer configuration (from data store A to HPC side B)
  - Validity period (request valid from date X to date Y)
  - User assignments with roles (via LifeScience AAI)
  - **Data Access Conditions**:
    - Data visibility restrictions
    - Model application restrictions (only selected models / no user models)
    - Contractual obligations
    - Ethics / DPIA documentation
    - Publishing agreements
    - Data return obligations

### 3.3 Project Status Tracking
- [ ] Display project approval status
- [ ] Show pending, approved, and rejected requests
- [ ] Link to negotiation details and review process

---

## 📋 Phase 4: Dashboard Core Features

### 4.1 Login & Project Selection
- [ ] Implement login page with LifeScience AAI integration
- [ ] Create project selection interface:
  - List all projects user has access to
  - Filter by status (active, completed, pending)
  - Search and filter capabilities

### 4.2 Project Overview Dashboard
- [ ] **Resources and Roles** section:
  - Display datasets/resources associated with the project
  - Show sites involved (data holders / SPEs)
  - List users and their roles
  - Display project documents:
    - Data Transfer Agreements (DTA)
    - Ethics votes
    - DPIA documents
    - Publishing agreements
- [ ] **Project Metadata** display:
  - Project ID
  - Title and description
  - Validity period
  - Data access conditions
  - Contractual obligations

### 4.3 Actions & Workflow Management
- [ ] Implement action triggers (started/triggered in dashboard):
  - **Data Transfer** actions:
    - Initiate data transfer from data store to HPC/SPE
    - Monitor transfer status
    - Link to transfer tools with contextual login
    - Use `DataTransferService` from service layer (mock or real)
  - **Computation** actions:
    - Launch computation jobs
    - Monitor job status
    - Link to computation tools (HPC/SPE interfaces)
    - Use `ComputationService` from service layer (mock or real)
  - **Data Return** actions:
    - Initiate result return process
    - Monitor return status
    - Use `DataTransferService` for return operations
  - **Model Application** actions:
    - Select and apply approved models
    - Monitor model execution
    - Use `ModelService` from service layer (mock or real)

### 4.4 Statistics & Monitoring
- [ ] **Dashboard Statistics** (reported by DEP tools):
  - **Data Transfer** metrics:
    - Transfer volumes
    - Transfer status (pending, in progress, completed, failed)
    - Transfer history
  - **Computation** metrics:
    - Job counts and status
    - Compute resource usage
    - Execution times
  - **Results** metrics:
    - Generated result counts
    - Result sizes
    - Return status
- [ ] Use `StatisticsService` from service layer to aggregate metrics
- [ ] Real-time updates from DEP tools (via service layer)
- [ ] Historical data visualization (charts/graphs)
- [ ] Export capabilities for reports

### 4.5 External Tool Integration
- [ ] Create contextual login links to:
  - HPC/SPE interfaces
  - Data transfer tools
  - Computation platforms
  - Model repositories
- [ ] Implement single sign-on (SSO) where possible
- [ ] Pass project context and user roles to external tools

---

## 📋 Phase 5: Use Case Specific Features

### 5.1 UC7 - Colorectal Cancer Prediction
- [ ] Workflow interface for:
  - WSI dataset selection
  - Model selection (explainable AI models)
  - Training configuration
  - Result visualization (biomarker identification)
- [ ] Integration with weakly supervised learning pipelines
- [ ] Display of explainability results

### 5.2 UC8 - Synthetic Data Generation
- [ ] Workflow interface for:
  - Source dataset selection
  - Synthetic generation parameters
  - High-resolution generation settings (up to 100k × 100k pixels)
  - Generation job monitoring
- [ ] Result preview and download capabilities
- [ ] Synthetic data quality metrics

---

## 📋 Phase 6: Data Format & API Specifications

### 6.1 Project Data Structure
- [ ] Define structured data formats:
  - **Unstructured** (freetext) support
  - **Structured** formats (table, JSON)
  - **Human-readable** formats
  - **Machine-readable** formats (for API consumption)
- [ ] Create JSON schemas for project metadata
- [ ] Implement data validation

### 6.2 API Development
- [ ] RESTful API endpoints for:
  - Project CRUD operations
  - Dataset discovery
  - Negotiation integration
  - Statistics retrieval
  - Action triggering
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Authentication middleware for API calls

---

## 📋 Phase 7: User Interface & Experience

### 7.1 UI Components
- [ ] Design and implement:
  - Project dashboard view
  - Project detail view
  - Statistics visualization components
  - Action buttons and workflow wizards
  - Document viewer/manager
  - User and role management interface
- [ ] Responsive design for various screen sizes
- [ ] Accessibility compliance (WCAG)

### 7.2 User Experience
- [ ] Intuitive navigation between:
  - Directory → Negotiator → Dashboard workflow
- [ ] Clear status indicators and progress tracking
- [ ] Error handling and user feedback
- [ ] Help documentation and tooltips

---

## 📋 Phase 8: Testing & Deployment

### 8.1 Testing
- [ ] Unit tests for backend APIs
- [ ] Integration tests for Directory/Negotiator connections
- [ ] End-to-end workflow tests
- [ ] User acceptance testing (UAT) with stakeholders

### 8.2 Deployment
- [ ] Production environment setup
- [ ] CI/CD pipeline configuration
- [ ] Monitoring and logging setup
- [ ] Documentation for deployment and operations

---

## 🔗 Integration Points Summary

### External Systems to Integrate:
1. **BBMRI-ERIC Directory**
   - Dataset discovery API
   - "REQUEST COMPUTE" attribute management

2. **BBMRI-ERIC Negotiator**
   - Negotiation request API
   - Project approval webhooks/notifications

3. **LifeScience AAI**
   - Authentication service
   - User identity and role management

4. **DEP Tools** (Secure Processing Environments)
   - Data transfer APIs
   - Computation job APIs
   - Statistics/metrics APIs
   - **Integration via Service Layer**: Abstract service interfaces allow gradual migration from mock to real DEP services

5. **Model Repositories**
   - Model catalog API
   - Model metadata retrieval
   - **Integration via Service Layer**: Model service abstraction for consistent interface

---

## 📝 Documentation Requirements

- [ ] Architecture documentation (`docs/architecture.md`)
  - Include service layer architecture and abstraction pattern
- [ ] Workflow documentation (`docs/workflows.md`)
- [ ] Service layer documentation (`SERVICE-LAYER-ARCHITECTURE.md`) ✅
- [ ] API documentation
- [ ] User guide
- [ ] Developer guide
- [ ] Deployment guide

---

## 🎯 Success Criteria

- ✅ Users can discover datasets in Directory and request compute access
- ✅ Negotiation requests flow seamlessly to dashboard upon approval
- ✅ Projects are created with complete metadata and access conditions
- ✅ Users can trigger and monitor data transfers, computations, and returns
- ✅ Statistics are accurately aggregated from DEP tools
- ✅ Role-based access control is enforced throughout
- ✅ UC7 and UC8 workflows are fully supported

---

## 📅 Priority Order

1. **Phase 1** - Core infrastructure (authentication, project structure, **service layer architecture**)
2. **Phase 2** - Directory integration (foundation for workflow)
3. **Phase 3** - Negotiator integration (project creation)
4. **Phase 4** - Dashboard core features (main functionality, using service layer)
5. **Phase 5** - Use case specific features (UC7/UC8)
6. **Phase 6** - Data formats and APIs (refinement)
7. **Phase 7** - UI/UX polish
8. **Phase 8** - Testing and deployment
9. **Phase 9** - Gradual migration from mock to real DEP services (ongoing)

---

---

## 🔄 Service Layer Migration Strategy

### Phase 1: Development with Mock Services
- All DEP services use mock implementations
- Dashboard functionality fully operational with simulated data
- Configuration: `USE_MOCK_SERVICES=true`

### Phase 2: Gradual Real Service Integration
- Enable real DEP services one-by-one as they become available
- Configuration per service:
  - `DEP_DATA_TRANSFER_ENABLED=true/false`
  - `DEP_COMPUTATION_ENABLED=true/false`
  - `DEP_STATISTICS_ENABLED=true/false`
  - `DEP_MODEL_SERVICE_ENABLED=true/false`
- Mix of mock and real services during transition

### Phase 3: Full Real Service Integration
- All services migrated to real DEP implementations
- Mock services retained for testing and development
- Configuration: `USE_MOCK_SERVICES=false` (all services enabled)

See `SERVICE-LAYER-ARCHITECTURE.md` for detailed implementation guide.

---

*Last updated: Based on RI-SCALE BBMRI-ERIC workflow and dashboard requirements, including service layer abstraction*

