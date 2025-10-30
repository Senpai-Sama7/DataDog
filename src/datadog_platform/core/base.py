"""
Core abstractions and base classes for the DataDog platform.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ExecutionStatus(str, Enum):
    """Status of pipeline/task execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class ProcessingMode(str, Enum):
    """Data processing mode."""

    BATCH = "batch"
    STREAMING = "streaming"
    MICRO_BATCH = "micro_batch"


class DataFormat(str, Enum):
    """Supported data formats."""

    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"
    XML = "xml"


class ConnectorType(str, Enum):
    """Types of data source connectors."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    KAFKA = "kafka"
    S3 = "s3"
    REST_API = "rest_api"
    FILE_SYSTEM = "file_system"
    CUSTOM = "custom"


class BaseConfig(BaseModel):
    """Base configuration for all components."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionContext(BaseModel):
    """Context for pipeline execution."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    pipeline_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class BaseConnector(ABC):
    """Base class for all data source connectors."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize connector with configuration."""
        self.config = config
        self._connection: Optional[Any] = None

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data source."""
        pass

    @abstractmethod
    async def read(self, query: Optional[str] = None, **kwargs: Any) -> Any:
        """Read data from the source."""
        pass

    @abstractmethod
    async def write(self, data: Any, **kwargs: Any) -> None:
        """Write data to the source."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate the connection to the data source."""
        pass

    async def __aenter__(self) -> "BaseConnector":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()


class BaseTransformer(ABC):
    """Base class for data transformations."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize transformer with configuration."""
        self.config = config

    @abstractmethod
    async def transform(self, data: Any, context: ExecutionContext) -> Any:
        """Transform input data and return transformed data."""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate input data."""
        pass


class BaseExecutor(ABC):
    """Base class for execution backends."""

    @abstractmethod
    async def execute_task(self, task: Any, context: ExecutionContext) -> Any:
        """Execute a single task."""
        pass

    @abstractmethod
    async def execute_dag(self, dag: Any, context: ExecutionContext) -> Any:
        """Execute a directed acyclic graph of tasks."""
        pass

    @abstractmethod
    async def get_status(self, execution_id: str) -> ExecutionStatus:
        """Get the status of an execution."""
        pass

    @abstractmethod
    async def cancel(self, execution_id: str) -> bool:
        """Cancel an ongoing execution."""
        pass
