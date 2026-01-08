"""
Example Service Layer Implementation

This file demonstrates the service abstraction pattern for DEP integration.
This is a reference implementation showing the structure and patterns to follow.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid
from faker import Faker

# ============================================================================
# 1. Pydantic Models (Data Structures)
# ============================================================================

class TransferStatus(BaseModel):
    """Data transfer status model"""
    transfer_id: str
    status: str  # "pending", "in_progress", "completed", "failed", "cancelled"
    progress_percentage: float
    source: str
    destination: str
    project_id: str
    dataset_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ComputationJob(BaseModel):
    """Computation job model"""
    job_id: str
    status: str  # "queued", "running", "completed", "failed", "cancelled"
    project_id: str
    model_id: Optional[str] = None
    dataset_id: str
    progress_percentage: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_location: Optional[str] = None
    error_message: Optional[str] = None

# ============================================================================
# 2. Abstract Service Interface
# ============================================================================

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
        """Initiate a data transfer from source to destination"""
        pass
    
    @abstractmethod
    def get_transfer_status(self, transfer_id: str) -> TransferStatus:
        """Get current status of a data transfer"""
        pass
    
    @abstractmethod
    def list_transfers(self, project_id: str) -> List[TransferStatus]:
        """List all transfers for a project"""
        pass
    
    @abstractmethod
    def cancel_transfer(self, transfer_id: str) -> bool:
        """Cancel a pending or in-progress transfer"""
        pass

# ============================================================================
# 3. Mock Implementation
# ============================================================================

class MockDataTransferService(DataTransferService):
    """
    Mock implementation of data transfer service.
    Uses in-memory storage and simulates transfer progress.
    """
    
    def __init__(self):
        self._transfers: dict[str, TransferStatus] = {}
        self.fake = Faker()
    
    def initiate_transfer(
        self,
        project_id: str,
        dataset_id: str,
        source_location: str,
        destination_location: str
    ) -> TransferStatus:
        """Mock: Create a new transfer with pending status"""
        transfer_id = str(uuid.uuid4())
        
        transfer = TransferStatus(
            transfer_id=transfer_id,
            status="pending",
            progress_percentage=0.0,
            source=source_location,
            destination=destination_location,
            project_id=project_id,
            dataset_id=dataset_id,
            started_at=datetime.utcnow()
        )
        
        self._transfers[transfer_id] = transfer
        return transfer
    
    def get_transfer_status(self, transfer_id: str) -> TransferStatus:
        """Mock: Get transfer status, simulating progress"""
        if transfer_id not in self._transfers:
            raise ValueError(f"Transfer {transfer_id} not found")
        
        transfer = self._transfers[transfer_id]
        
        # Simulate progress for pending/in-progress transfers
        if transfer.status == "pending":
            # Move to in_progress after first check
            transfer.status = "in_progress"
        elif transfer.status == "in_progress":
            # Simulate progress increase
            increment = self.fake.random_int(5, 25)
            transfer.progress_percentage = min(
                transfer.progress_percentage + increment,
                100.0
            )
            
            # Complete if at 100%
            if transfer.progress_percentage >= 100:
                transfer.status = "completed"
                transfer.completed_at = datetime.utcnow()
        
        return transfer
    
    def list_transfers(self, project_id: str) -> List[TransferStatus]:
        """Mock: List all transfers for a project"""
        return [
            transfer for transfer in self._transfers.values()
            if transfer.project_id == project_id
        ]
    
    def cancel_transfer(self, transfer_id: str) -> bool:
        """Mock: Cancel a transfer"""
        if transfer_id not in self._transfers:
            return False
        
        transfer = self._transfers[transfer_id]
        if transfer.status in ["pending", "in_progress"]:
            transfer.status = "cancelled"
            return True
        return False

# ============================================================================
# 4. Real DEP Implementation (Placeholder)
# ============================================================================

class DEPDataTransferService(DataTransferService):
    """
    Real DEP implementation of data transfer service.
    This will call actual DEP APIs when they become available.
    """
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        # In real implementation, use httpx.AsyncClient
        # self.client = httpx.AsyncClient(...)
    
    def initiate_transfer(
        self,
        project_id: str,
        dataset_id: str,
        source_location: str,
        destination_location: str
    ) -> TransferStatus:
        """
        Real: Initiate transfer via DEP API
        
        Example implementation:
        ```
        response = await self.client.post(
            f"{self.base_url}/transfers",
            json={
                "project_id": project_id,
                "dataset_id": dataset_id,
                "source": source_location,
                "destination": destination_location
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return TransferStatus(**response.json())
        ```
        """
        # Placeholder - implement when DEP API is ready
        raise NotImplementedError("DEP API integration not yet implemented")
    
    def get_transfer_status(self, transfer_id: str) -> TransferStatus:
        """Real: Get status from DEP API"""
        raise NotImplementedError("DEP API integration not yet implemented")
    
    def list_transfers(self, project_id: str) -> List[TransferStatus]:
        """Real: List transfers from DEP API"""
        raise NotImplementedError("DEP API integration not yet implemented")
    
    def cancel_transfer(self, transfer_id: str) -> bool:
        """Real: Cancel transfer via DEP API"""
        raise NotImplementedError("DEP API integration not yet implemented")

# ============================================================================
# 5. Service Factory
# ============================================================================

class ServiceFactory:
    """
    Factory for creating service instances.
    Switches between mock and real implementations based on configuration.
    """
    
    @staticmethod
    def create_data_transfer_service(
        use_mock: bool = True,
        dep_url: Optional[str] = None,
        dep_api_key: Optional[str] = None
    ) -> DataTransferService:
        """
        Create a data transfer service instance.
        
        Args:
            use_mock: If True, return mock service; if False, return real service
            dep_url: DEP API base URL (required for real service)
            dep_api_key: DEP API key (required for real service)
        
        Returns:
            DataTransferService instance (mock or real)
        """
        if use_mock:
            return MockDataTransferService()
        else:
            if not dep_url or not dep_api_key:
                raise ValueError(
                    "DEP URL and API key required for real service"
                )
            return DEPDataTransferService(dep_url, dep_api_key)

# ============================================================================
# 6. Usage Example
# ============================================================================

def example_usage():
    """Example of how to use the service layer"""
    
    # Create service (mock or real based on configuration)
    service = ServiceFactory.create_data_transfer_service(use_mock=True)
    
    # Use the service - interface is the same regardless of implementation
    transfer = service.initiate_transfer(
        project_id="proj-123",
        dataset_id="ds-456",
        source_location="s3://source-bucket/data",
        destination_location="hpc://compute-node/storage"
    )
    
    print(f"Initiated transfer: {transfer.transfer_id}")
    print(f"Status: {transfer.status}")
    
    # Get status
    status = service.get_transfer_status(transfer.transfer_id)
    print(f"Current progress: {status.progress_percentage}%")
    
    # List all transfers for project
    transfers = service.list_transfers("proj-123")
    print(f"Total transfers: {len(transfers)}")

if __name__ == "__main__":
    example_usage()

