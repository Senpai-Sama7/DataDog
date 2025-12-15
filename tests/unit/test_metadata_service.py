
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from datadog_platform.core.base import ExecutionContext, ExecutionStatus, ProcessingMode
from datadog_platform.core.pipeline import Pipeline
from datadog_platform.storage.config import PostgreSQLConfig
from datadog_platform.storage.database import DatabaseManager
from datadog_platform.orchestration.metadata_service import MetadataService


@pytest.fixture
def mock_db_manager():
    """Mock DatabaseManager for MetadataService tests."""
    mock = AsyncMock(spec=DatabaseManager)
    mock.initialize = AsyncMock()
    mock.close = AsyncMock()
    mock.engine = MagicMock()
    mock.engine.begin = MagicMock()
    mock.engine.begin.return_value.__aenter__.return_value.run_sync = AsyncMock()
    return mock


@pytest.fixture
def mock_metadata_store():
    """Mock PostgreSQLMetadataStore for MetadataService tests."""
    mock = AsyncMock()
    mock.initialize = AsyncMock()
    mock.create_pipeline = AsyncMock(return_value=uuid4())
    mock.get_pipeline = AsyncMock(return_value={
        "id": str(uuid4()),
        "name": "test_pipeline",
        "description": "A test pipeline",
        "processing_mode": ProcessingMode.BATCH.value,
        "schedule": None,
        "enabled": True,
        "max_parallel_tasks": 4,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "tags": {},
        "metadata": {},
    })
    mock.update_pipeline = AsyncMock(return_value=True)
    mock.create_execution = AsyncMock(return_value=uuid4())
    mock.update_execution_status = AsyncMock(return_value=True)
    mock.get_execution = AsyncMock(return_value={
        "id": str(uuid4()),
        "pipeline_id": str(uuid4()),
        "started_at": "2023-01-01T00:00:00Z",
        "ended_at": "2023-01-01T00:00:00Z",
        "status": ExecutionStatus.SUCCESS.value,
        "parameters": {},
        "metrics": {},
        "error": None,
    })
    mock.list_execution_contexts = AsyncMock(return_value=[])
    mock.get_pipeline_by_name = AsyncMock(return_value={
        "id": str(uuid4()),
        "name": "test_pipeline",
        "description": "A test pipeline",
        "processing_mode": ProcessingMode.BATCH.value,
        "schedule": None,
        "enabled": True,
        "max_parallel_tasks": 4,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "tags": {},
        "metadata": {},
    })
    mock.list_data_sources = AsyncMock(return_value=[])
    mock.list_transformations = AsyncMock(return_value=[])
    mock.update_task_status = AsyncMock(return_value=True)
    mock.record_data_lineage = AsyncMock(return_value=uuid4())
    return mock


@pytest.fixture
def metadata_service(mock_db_manager, mock_metadata_store):
    """Create a MetadataService instance with mocked dependencies."""
    service = MetadataService(config=PostgreSQLConfig())
    service.db_manager = mock_db_manager
    service.metadata_store = mock_metadata_store
    return service


@pytest.mark.asyncio
async def test_metadata_service_initialization(metadata_service, mock_db_manager, mock_metadata_store):
    """Test that the metadata service initializes correctly."""
    await metadata_service.initialize()
    mock_db_manager.initialize.assert_called_once()
    mock_metadata_store.initialize.assert_called_once()
    assert metadata_service._initialized is True


@pytest.mark.asyncio
async def test_metadata_service_shutdown(metadata_service, mock_db_manager):
    """Test that the metadata service shuts down correctly."""
    metadata_service._initialized = True  # Manually set to initialized for shutdown test
    await metadata_service.shutdown()
    mock_db_manager.close.assert_called_once()


@pytest.mark.asyncio
async def test_register_pipeline(metadata_service, mock_metadata_store):
    """Test registering a pipeline."""
    await metadata_service.initialize()
    pipeline = Pipeline(
        name="test_pipeline",
        description="A test pipeline",
        processing_mode=ProcessingMode.BATCH,
    )
    pipeline_id = await metadata_service.register_pipeline(pipeline)
    assert isinstance(pipeline_id, UUID)
    mock_metadata_store.create_pipeline.assert_called_once()


@pytest.mark.asyncio
async def test_get_pipeline(metadata_service, mock_metadata_store):
    """Test retrieving a pipeline."""
    await metadata_service.initialize()
    pipeline_id = uuid4()
    pipeline_data = await metadata_service.get_pipeline(pipeline_id)
    assert pipeline_data["name"] == "test_pipeline"
    mock_metadata_store.get_pipeline.assert_called_once_with(pipeline_id)


@pytest.mark.asyncio
async def test_update_pipeline_status(metadata_service, mock_metadata_store):
    """Test updating pipeline status."""
    await metadata_service.initialize()
    pipeline_id = uuid4()
    result = await metadata_service.update_pipeline_status(pipeline_id, "active")
    assert result is True
    mock_metadata_store.update_pipeline.assert_called_once()


@pytest.mark.asyncio
async def test_start_execution(metadata_service, mock_metadata_store):
    """Test starting an execution."""
    await metadata_service.initialize()
    execution_context = ExecutionContext(
        pipeline_id=str(uuid4()),
        status=ExecutionStatus.PENDING
    )
    execution_id = await metadata_service.start_execution(execution_context)
    assert isinstance(execution_id, UUID)
    mock_metadata_store.create_execution.assert_called_once_with(execution_context)


@pytest.mark.asyncio
async def test_update_execution_status(metadata_service, mock_metadata_store):
    """Test updating execution status."""
    await metadata_service.initialize()
    execution_id = uuid4()
    result = await metadata_service.update_execution_status(str(execution_id), ExecutionStatus.SUCCESS)
    assert result is True
    mock_metadata_store.update_execution_status.assert_called_once_with(
        execution_id=execution_id, status=ExecutionStatus.SUCCESS, ended_at=None, error_message=None
    )


@pytest.mark.asyncio
async def test_get_execution(metadata_service, mock_metadata_store):
    """Test retrieving an execution."""
    await metadata_service.initialize()
    execution_id = uuid4()
    execution_data = await metadata_service.get_execution(execution_id)
    assert execution_data["status"] == ExecutionStatus.SUCCESS.value
    mock_metadata_store.get_execution.assert_called_once_with(execution_id)


@pytest.mark.asyncio
async def test_list_execution_history(metadata_service, mock_metadata_store):
    """Test listing execution history."""
    await metadata_service.initialize()
    pipeline_id = uuid4()
    history = await metadata_service.get_execution_history(pipeline_id)
    assert isinstance(history, list)
    mock_metadata_store.list_execution_contexts.assert_called_once_with(pipeline_id)


@pytest.mark.asyncio
async def test_get_pipeline_by_name(metadata_service, mock_metadata_store):
    """Test retrieving a pipeline by name."""
    await metadata_service.initialize()
    pipeline_name = "test_pipeline"
    pipeline_data = await metadata_service.get_pipeline_by_name(pipeline_name)
    assert pipeline_data["name"] == pipeline_name
    mock_metadata_store.get_pipeline_by_name.assert_called_once_with(pipeline_name)


@pytest.mark.asyncio
async def test_update_task_status(metadata_service, mock_metadata_store):
    """Test updating task status."""
    await metadata_service.initialize()
    execution_id = uuid4()
    task_name = "test_task"
    result = await metadata_service.update_task_status(execution_id, task_name, ExecutionStatus.SUCCESS)
    assert result is True
    mock_metadata_store.update_task_status.assert_called_once_with(
        execution_id=execution_id, task_name=task_name, status=ExecutionStatus.SUCCESS, ended_at=None, error_message=None, input_data=None, output_data=None
    )


@pytest.mark.asyncio
async def test_record_data_lineage(metadata_service, mock_metadata_store):
    """Test recording data lineage."""
    await metadata_service.initialize()
    pipeline_id = uuid4()
    execution_id = uuid4()
    lineage_id = await metadata_service.record_data_lineage(
        source_id="source1",
        source_type="type1",
        destination_id="dest1",
        destination_type="type2",
        pipeline_id=pipeline_id,
        execution_id=execution_id
    )
    assert isinstance(lineage_id, UUID)
    mock_metadata_store.record_data_lineage.assert_called_once_with(
        source_id="source1",
        source_type="type1",
        destination_id="dest1",
        destination_type="type2",
        pipeline_id=pipeline_id,
        execution_id=execution_id,
        data_flow={}
    )
