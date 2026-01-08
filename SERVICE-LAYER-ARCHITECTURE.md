# Service Layer Architecture - DEP Integration

This document describes the service abstraction layer pattern for integrating with DEP (Data Exploitation Platform) services, allowing gradual migration from mock implementations to real services.

---

## 🎯 Overview

The service layer provides a **clean abstraction** between the dashboard application and external DEP services. This allows:

1. **Development without dependencies**: Work on dashboard features while DEP services are still in development
2. **Gradual migration**: Replace mock services one-by-one as real services become available
3. **Testing**: Easy unit testing with mock implementations
4. **Flexibility**: Switch between mock and real services via configuration

---

## 🏗️ Architecture Pattern

### Service Abstraction Layer

```
┌─────────────────────────────────────────────────┐
│           Dashboard Application                  │
│  (Flask Backend + Vue Frontend)                  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         Service Abstraction Layer                │
│  (Interfaces / Abstract Classes)                 │
└──────┬───────────┬───────────┬──────────────────┘
       │           │           │
   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
   │ Mock  │   │ Mock  │   │ Mock  │
   │ DEP   │   │ DEP   │   │ DEP   │
   │Service│   │Service│   │Service│
   └───────┘   └───────┘   └───────┘
       │           │           │
       └───────────┴───────────┘
                   │
       ┌───────────▼───────────┐
       │  Configuration        │
       │  (Mock/Real Switch)   │
       └───────────┬───────────┘
                   │
       ┌───────────▼───────────┐
       │   Real DEP Services    │
       │  (As they become ready) │
       └────────────────────────┘
```

---

## 🛠️ Technology Stack for Service Layer

### Python (Backend)

#### Core Technologies
- **ABC (Abstract Base Classes)** - Define service interfaces
- **typing.Protocol** - Structural subtyping (alternative to ABC)
- **Dependency Injection** - Flask-Injector or manual factory pattern
- **Pydantic** - Data validation and models for service responses
- **Faker** - Generate realistic mock data
- **httpx** or **requests-mock** - Mock HTTP responses

#### Recommended Libraries
- **pytest** - Testing with fixtures for service mocking
- **responses** - Mock HTTP library responses
- **freezegun** - Mock time for testing

### Configuration Management
- **python-dotenv** - Environment-based configuration
- **Pydantic Settings** - Type-safe configuration management

---

## 📁 Project Structure

```
ri-scale-dashboard/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── base/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data_transfer_service.py    # Abstract interface
│   │   │   │   ├── computation_service.py      # Abstract interface
│   │   │   │   ├── statistics_service.py       # Abstract interface
│   │   │   │   └── model_service.py            # Abstract interface
│   │   │   ├── mock/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mock_data_transfer.py       # Mock implementation
│   │   │   │   ├── mock_computation.py         # Mock implementation
│   │   │   │   ├── mock_statistics.py         # Mock implementation
│   │   │   │   ├── mock_model_service.py      # Mock implementation
│   │   │   │   └── mock_data_generator.py      # Mock data generation
│   │   │   ├── real/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dep_data_transfer.py        # Real DEP implementation
│   │   │   │   ├── dep_computation.py          # Real DEP implementation
│   │   │   │   ├── dep_statistics.py          # Real DEP implementation
│   │   │   │   └── dep_model_service.py        # Real DEP implementation
│   │   │   └── factory.py                      # Service factory
│   │   ├── models/
│   │   │   └── service_models.py               # Pydantic models
│   │   └── config.py                           # Configuration
│   └── tests/
│       └── services/
│           └── test_mock_services.py
```

---

## 💻 Implementation Pattern

### 1. Define Abstract Service Interface

```python
# backend/app/services/base/data_transfer_service.py
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class TransferStatus(BaseModel):
    """Data transfer status model"""
    transfer_id: str
    status: str  # "pending", "in_progress", "completed", "failed"
    progress_percentage: float
    source: str
    destination: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class DataTransferService(ABC):
    """Abstract interface for data transfer service"""
    
    @abstractmethod
    def initiate_transfer(
        self, 
        project_id: str,
        dataset_id: str,
        source_location: str,
        destination_location: str
    ) -> TransferStatus:
        """Initiate a data transfer"""
        pass
    
    @abstractmethod
    def get_transfer_status(self, transfer_id: str) -> TransferStatus:
        """Get status of a data transfer"""
        pass
    
    @abstractmethod
    def list_transfers(self, project_id: str) -> List[TransferStatus]:
        """List all transfers for a project"""
        pass
    
    @abstractmethod
    def cancel_transfer(self, transfer_id: str) -> bool:
        """Cancel a pending or in-progress transfer"""
        pass
```

### 2. Mock Implementation

```python
# backend/app/services/mock/mock_data_transfer.py
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from faker import Faker

from ..base.data_transfer_service import DataTransferService, TransferStatus

fake = Faker()

class MockDataTransferService(DataTransferService):
    """Mock implementation of data transfer service"""
    
    def __init__(self):
        # In-memory storage for mock data
        self._transfers: dict[str, TransferStatus] = {}
    
    def initiate_transfer(
        self,
        project_id: str,
        dataset_id: str,
        source_location: str,
        destination_location: str
    ) -> TransferStatus:
        """Mock: Initiate a data transfer"""
        transfer_id = str(uuid.uuid4())
        
        transfer = TransferStatus(
            transfer_id=transfer_id,
            status="pending",
            progress_percentage=0.0,
            source=source_location,
            destination=destination_location,
            started_at=datetime.utcnow()
        )
        
        self._transfers[transfer_id] = transfer
        
        # Simulate async processing (in real implementation, this would be async)
        # For demo, we can set status to "in_progress" after a delay
        
        return transfer
    
    def get_transfer_status(self, transfer_id: str) -> TransferStatus:
        """Mock: Get status of a data transfer"""
        if transfer_id not in self._transfers:
            raise ValueError(f"Transfer {transfer_id} not found")
        
        transfer = self._transfers[transfer_id]
        
        # Simulate progress for in-progress transfers
        if transfer.status == "in_progress":
            # Simulate progress increase
            if transfer.progress_percentage < 100:
                transfer.progress_percentage = min(
                    transfer.progress_percentage + fake.random_int(5, 20),
                    100.0
                )
                if transfer.progress_percentage >= 100:
                    transfer.status = "completed"
                    transfer.completed_at = datetime.utcnow()
        
        return transfer
    
    def list_transfers(self, project_id: str) -> List[TransferStatus]:
        """Mock: List all transfers for a project"""
        # In real implementation, filter by project_id
        return list(self._transfers.values())
    
    def cancel_transfer(self, transfer_id: str) -> bool:
        """Mock: Cancel a transfer"""
        if transfer_id not in self._transfers:
            return False
        
        transfer = self._transfers[transfer_id]
        if transfer.status in ["pending", "in_progress"]:
            transfer.status = "cancelled"
            return True
        return False
```

### 3. Real DEP Implementation (Placeholder)

```python
# backend/app/services/real/dep_data_transfer.py
import httpx
from typing import List
from datetime import datetime

from ..base.data_transfer_service import DataTransferService, TransferStatus
from ...config import settings

class DEPDataTransferService(DataTransferService):
    """Real DEP implementation of data transfer service"""
    
    def __init__(self):
        self.base_url = settings.DEP_DATA_TRANSFER_URL
        self.api_key = settings.DEP_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0
        )
    
    async def initiate_transfer(
        self,
        project_id: str,
        dataset_id: str,
        source_location: str,
        destination_location: str
    ) -> TransferStatus:
        """Real: Initiate a data transfer via DEP API"""
        response = await self.client.post(
            "/transfers",
            json={
                "project_id": project_id,
                "dataset_id": dataset_id,
                "source": source_location,
                "destination": destination_location
            }
        )
        response.raise_for_status()
        data = response.json()
        
        return TransferStatus(**data)
    
    async def get_transfer_status(self, transfer_id: str) -> TransferStatus:
        """Real: Get status from DEP API"""
        response = await self.client.get(f"/transfers/{transfer_id}")
        response.raise_for_status()
        data = response.json()
        
        return TransferStatus(**data)
    
    async def list_transfers(self, project_id: str) -> List[TransferStatus]:
        """Real: List transfers from DEP API"""
        response = await self.client.get(
            "/transfers",
            params={"project_id": project_id}
        )
        response.raise_for_status()
        data = response.json()
        
        return [TransferStatus(**item) for item in data]
    
    async def cancel_transfer(self, transfer_id: str) -> bool:
        """Real: Cancel transfer via DEP API"""
        response = await self.client.post(f"/transfers/{transfer_id}/cancel")
        return response.status_code == 200
```

### 4. Service Factory

```python
# backend/app/services/factory.py
from typing import Type
from ..config import settings
from .base.data_transfer_service import DataTransferService
from .base.computation_service import ComputationService
from .base.statistics_service import StatisticsService
from .base.model_service import ModelService

# Import mock implementations
from .mock.mock_data_transfer import MockDataTransferService
from .mock.mock_computation import MockComputationService
from .mock.mock_statistics import MockStatisticsService
from .mock.mock_model_service import MockModelService

# Import real implementations
from .real.dep_data_transfer import DEPDataTransferService
from .real.dep_computation import DEPComputationService
from .real.dep_statistics import DEPStatisticsService
from .real.dep_model_service import DEPModelService

class ServiceFactory:
    """Factory for creating service instances (mock or real)"""
    
    @staticmethod
    def get_data_transfer_service() -> DataTransferService:
        """Get data transfer service (mock or real based on config)"""
        if settings.USE_MOCK_SERVICES or not settings.DEP_DATA_TRANSFER_ENABLED:
            return MockDataTransferService()
        return DEPDataTransferService()
    
    @staticmethod
    def get_computation_service() -> ComputationService:
        """Get computation service (mock or real based on config)"""
        if settings.USE_MOCK_SERVICES or not settings.DEP_COMPUTATION_ENABLED:
            return MockComputationService()
        return DEPComputationService()
    
    @staticmethod
    def get_statistics_service() -> StatisticsService:
        """Get statistics service (mock or real based on config)"""
        if settings.USE_MOCK_SERVICES or not settings.DEP_STATISTICS_ENABLED:
            return MockStatisticsService()
        return DEPStatisticsService()
    
    @staticmethod
    def get_model_service() -> ModelService:
        """Get model service (mock or real based on config)"""
        if settings.USE_MOCK_SERVICES or not settings.DEP_MODEL_SERVICE_ENABLED:
            return MockModelService()
        return DEPModelService()
```

### 5. Configuration

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Service mode: "mock" or "real" or "hybrid"
    USE_MOCK_SERVICES: bool = True
    
    # Individual service toggles (for gradual migration)
    DEP_DATA_TRANSFER_ENABLED: bool = False
    DEP_COMPUTATION_ENABLED: bool = False
    DEP_STATISTICS_ENABLED: bool = False
    DEP_MODEL_SERVICE_ENABLED: bool = False
    
    # DEP API endpoints (when real services are enabled)
    DEP_DATA_TRANSFER_URL: Optional[str] = None
    DEP_COMPUTATION_URL: Optional[str] = None
    DEP_STATISTICS_URL: Optional[str] = None
    DEP_MODEL_SERVICE_URL: Optional[str] = None
    
    # DEP API authentication
    DEP_API_KEY: Optional[str] = None
    DEP_API_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 6. Usage in Flask Routes

```python
# backend/app/routes/data_transfer.py
from flask import Blueprint, jsonify, request
from ..services.factory import ServiceFactory

data_transfer_bp = Blueprint('data_transfer', __name__)

@data_transfer_bp.route('/api/projects/<project_id>/transfers', methods=['POST'])
def initiate_transfer(project_id: str):
    """Initiate a data transfer"""
    data = request.get_json()
    
    # Get service from factory (mock or real)
    service = ServiceFactory.get_data_transfer_service()
    
    try:
        transfer = service.initiate_transfer(
            project_id=project_id,
            dataset_id=data['dataset_id'],
            source_location=data['source'],
            destination_location=data['destination']
        )
        return jsonify(transfer.dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@data_transfer_bp.route('/api/transfers/<transfer_id>', methods=['GET'])
def get_transfer_status(transfer_id: str):
    """Get transfer status"""
    service = ServiceFactory.get_data_transfer_service()
    
    try:
        status = service.get_transfer_status(transfer_id)
        return jsonify(status.dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

---

## 🔄 Migration Strategy

### Phase 1: All Mock Services
```env
USE_MOCK_SERVICES=true
DEP_DATA_TRANSFER_ENABLED=false
DEP_COMPUTATION_ENABLED=false
DEP_STATISTICS_ENABLED=false
DEP_MODEL_SERVICE_ENABLED=false
```

### Phase 2: Enable Real Service One-by-One
```env
USE_MOCK_SERVICES=false
DEP_DATA_TRANSFER_ENABLED=true    # Real service ready
DEP_COMPUTATION_ENABLED=false     # Still using mock
DEP_STATISTICS_ENABLED=false      # Still using mock
DEP_MODEL_SERVICE_ENABLED=false   # Still using mock
```

### Phase 3: All Real Services
```env
USE_MOCK_SERVICES=false
DEP_DATA_TRANSFER_ENABLED=true
DEP_COMPUTATION_ENABLED=true
DEP_STATISTICS_ENABLED=true
DEP_MODEL_SERVICE_ENABLED=true
```

---

## 🧪 Testing Strategy

### Unit Tests with Mocks

```python
# backend/tests/services/test_data_transfer.py
import pytest
from app.services.mock.mock_data_transfer import MockDataTransferService
from app.services.real.dep_data_transfer import DEPDataTransferService

def test_mock_transfer_initiation():
    """Test mock service"""
    service = MockDataTransferService()
    transfer = service.initiate_transfer(
        project_id="proj-1",
        dataset_id="ds-1",
        source_location="source://data",
        destination_location="dest://hpc"
    )
    
    assert transfer.status == "pending"
    assert transfer.progress_percentage == 0.0

@pytest.mark.asyncio
async def test_real_transfer_initiation(httpx_mock):
    """Test real service with mocked HTTP"""
    httpx_mock.add_response(
        method="POST",
        url="https://dep.example.com/transfers",
        json={
            "transfer_id": "transfer-123",
            "status": "pending",
            "progress_percentage": 0.0,
            "source": "source://data",
            "destination": "dest://hpc"
        }
    )
    
    service = DEPDataTransferService()
    transfer = await service.initiate_transfer(
        project_id="proj-1",
        dataset_id="ds-1",
        source_location="source://data",
        destination_location="dest://hpc"
    )
    
    assert transfer.status == "pending"
```

---

## 📊 Service Interfaces to Implement

### 1. Data Transfer Service
- Initiate transfer
- Get transfer status
- List transfers
- Cancel transfer

### 2. Computation Service
- Submit computation job
- Get job status
- List jobs
- Cancel job
- Get job results

### 3. Statistics Service
- Get transfer statistics
- Get computation statistics
- Get result statistics
- Get aggregated metrics

### 4. Model Service
- List available models
- Get model details
- Apply model to dataset
- Get model execution status

---

## 🎯 Best Practices

1. **Consistent Interfaces**: All service implementations must follow the same interface
2. **Error Handling**: Define common exception types for service errors
3. **Logging**: Log all service calls (mock and real) for debugging
4. **Type Safety**: Use Pydantic models for all data structures
5. **Async Support**: Consider async/await for real services (use `httpx` async client)
6. **Retry Logic**: Implement retry logic in real service implementations
7. **Circuit Breaker**: Consider circuit breaker pattern for real services
8. **Caching**: Cache responses where appropriate (especially for statistics)

---

## 🔧 Additional Tools & Libraries

### For Mock Data Generation
- **Faker** - Generate realistic fake data
- **factory-boy** - Create test data factories

### For HTTP Mocking
- **responses** - Mock requests library
- **httpx-mock** - Mock httpx library
- **vcrpy** - Record and replay HTTP interactions

### For Testing
- **pytest-asyncio** - Async test support
- **pytest-mock** - Mocking utilities
- **freezegun** - Time mocking

### For Dependency Injection (Optional)
- **Flask-Injector** - Dependency injection for Flask
- **dependency-injector** - Standalone DI container

---

## 📝 Example: Hybrid Mode

You can also implement a hybrid mode where some operations use real services and others use mocks:

```python
class HybridDataTransferService(DataTransferService):
    """Hybrid: Use real service for reads, mock for writes during testing"""
    
    def __init__(self):
        self.real_service = DEPDataTransferService()
        self.mock_service = MockDataTransferService()
    
    def initiate_transfer(self, ...):
        # Use mock during development
        if settings.USE_MOCK_FOR_WRITES:
            return self.mock_service.initiate_transfer(...)
        return self.real_service.initiate_transfer(...)
    
    def get_transfer_status(self, transfer_id: str):
        # Always use real service for reads
        return self.real_service.get_transfer_status(transfer_id)
```

---

## 🚀 Implementation Steps

1. **Define all service interfaces** (abstract base classes)
2. **Create Pydantic models** for all data structures
3. **Implement mock services** with realistic data generation
4. **Create service factory** with configuration-based switching
5. **Integrate into Flask routes** using factory pattern
6. **Add configuration** for service toggles
7. **Write tests** for both mock and real implementations
8. **Implement real services** as DEP APIs become available
9. **Gradually migrate** from mock to real via configuration

---

*Last updated: Service layer architecture for DEP integration*

