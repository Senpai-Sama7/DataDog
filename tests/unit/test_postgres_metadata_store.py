"""Tests for PostgreSQL metadata store."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from datadog_platform.core.base import ExecutionContext, ExecutionStatus
from datadog_platform.storage.config import PostgreSQLConfig
from datadog_platform.storage.database import DatabaseManager
from datadog_platform.storage.postgres_metadata_store import PostgreSQLMetadataStore


@pytest.fixture
async def db_manager():
    """Create a test database manager."""
    config = PostgreSQLConfig(
        host="localhost",
        port=5432,
        database="test_datadog",
        username="test_user",
        password="test_pass",
        echo=True  # Enable for debugging
    )
    db_manager = DatabaseManager(config)
    # Mock the actual database connection for testing
    db_manager.initialize = AsyncMock()
    db_manager.close = AsyncMock()
    yield db_manager


@pytest.fixture
async def metadata_store(db_manager):
    """Create a test metadata store."""
    store = PostgreSQLMetadataStore(db_manager)
    # Mock the initialize method to avoid actual DB connection
    store.initialize = AsyncMock()
    yield store


@pytest.mark.asyncio
async def test_create_pipeline(metadata_store):
    """Test creating a pipeline."""
    # Mock the session and its methods
    session_mock = AsyncMock()
    session_context_mock = MagicMock()
    session_context_mock.__aenter__.return_value = session_mock
    session_context_mock.__aexit__.return_value = None
    metadata_store.db_manager.get_session.return_value = session_context_mock
    
    # Mock the pipeline object
    pipeline_mock = MagicMock()
    pipeline_mock.id = uuid4()
    pipeline_mock.name = "test_pipeline"
    pipeline_mock.description = "Test pipeline"
    pipeline_mock.definition = {"steps": []}
    pipeline_mock.tags = {"env": "test"}
    
    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock(return_value=pipeline_mock)
    
    # Execute test
    pipeline_id = await metadata_store.create_pipeline(
        name="test_pipeline",
        description="Test pipeline",
        definition={"steps": []},
        tags={"env": "test"}
    )
    
    # Verify
    assert isinstance(pipeline_id, UUID)
    session_mock.add.assert_called_once()
    session_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_pipeline(metadata_store):
    """Test retrieving a pipeline."""
    # Mock the session and its methods
    session_mock = AsyncMock()
    session_context_mock = MagicMock()
    session_context_mock.__aenter__.return_value = session_mock
    session_context_mock.__aexit__.return_value = None
    metadata_store.db_manager.get_session.return_value = session_context_mock
    
    # Mock the pipeline result
    pipeline_result = MagicMock()
    pipeline_result.id = uuid4()
    pipeline_result.name = "test_pipeline"
    pipeline_result.description = "Test pipeline"
    pipeline_result.definition = {"steps": []}
    pipeline_result.tags = {"env": "test"}
    pipeline_result.status = "active"
    
    execute_mock = AsyncMock()
    execute_mock.scalar_one_or_none.return_value = pipeline_result
    session_mock.execute.return_value = execute_mock
    
    # Execute test
    pipeline_id = uuid4()
    pipeline = await metadata_store.get_pipeline(pipeline_id)
    
    # Verify
    assert pipeline is not None
    assert pipeline['name'] == "test_pipeline"
    assert pipeline['description'] == "Test pipeline"
    assert pipeline['tags'] == {"env": "test"}


@pytest.mark.asyncio
async def test_update_pipeline(metadata_store):
    """Test updating a pipeline."""
    # Mock the session and its methods
    session_mock = AsyncMock()
    session_context_mock = MagicMock()
    session_context_mock.__aenter__.return_value = session_mock
    session_context_mock.__aexit__.return_value = None
    metadata_store.db_manager.get_session.return_value = session_context_mock
    
    execute_mock = AsyncMock()
    execute_mock.rowcount = 1  # Simulate one row updated
    session_mock.execute.return_value = execute_mock
    session_mock.commit = AsyncMock()
    
    # Execute test
    pipeline_id = uuid4()
    result = await metadata_store.update_pipeline(
        pipeline_id=pipeline_id,
        name="updated_pipeline"
    )
    
    # Verify
    assert result is True
    session_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_pipeline(metadata_store):
    """Test deleting a pipeline."""
    # Mock the session and its methods
    session_mock = AsyncMock()
    session_context_mock = MagicMock()
    session_context_mock.__aenter__.return_value = session_mock
    session_context_mock.__aexit__.return_value = None
    metadata_store.db_manager.get_session.return_value = session_context_mock
    
    execute_mock = AsyncMock()
    execute_mock.rowcount = 1  # Simulate one row deleted
    session_mock.execute.return_value = execute_mock
    session_mock.commit = AsyncMock()
    
    # Execute test
    pipeline_id = uuid4()
    result = await metadata_store.delete_pipeline(pipeline_id)
    
    # Verify
    assert result is True
    session_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_execution(metadata_store):
    """Test creating an execution."""
    # Mock the session and its methods
    session_mock = AsyncMock()
    session_context_mock = MagicMock()
    session_context_mock.__aenter__.return_value = session_mock
    session_context_mock.__aexit__.return_value = None
    metadata_store.db_manager.get_session.return_value = session_context_mock
    
    # Mock the execution object
    execution_mock = MagicMock()
    execution_mock.id = uuid4()
    
    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock()
    
    # Execute test
    execution_context = ExecutionContext(
        pipeline_id=str(uuid4()),
        status=ExecutionStatus.PENDING
    )
    execution_id = await metadata_store.create_execution(execution_context)
    
    # Verify
    assert execution_id == execution_context.execution_id
    session_mock.add.assert_called_once()


@pytest.mark.asyncio
async def test_create_task(metadata_store):
    """Test creating a task."""
    # Mock the session and its methods
    session_mock = AsyncMock()
    session_context_mock = MagicMock()
    session_context_mock.__aenter__.return_value = session_mock
    session_context_mock.__aexit__.return_value = None
    metadata_store.db_manager.get_session.return_value = session_context_mock
    
    # Mock the task object
    task_mock = MagicMock()
    task_mock.id = uuid4()
    
    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock(return_value=task_mock)
    
    # Execute test
    execution_id = str(uuid4())
    task_id = await metadata_store.create_task(
        execution_id=execution_id,
        task_name="test_task",
        task_type="connector"
    )
    
    # Verify
    assert isinstance(task_id, UUID)
    session_mock.add.assert_called_once()


@pytest.mark.asyncio
async def test_record_data_lineage(metadata_store):
    """Test recording data lineage."""
    # Mock the session and its methods
    session_mock = AsyncMock()
    session_context_mock = MagicMock()
    session_context_mock.__aenter__.return_value = session_mock
    session_context_mock.__aexit__.return_value = None
    metadata_store.db_manager.get_session.return_value = session_context_mock
    
    # Mock the lineage object
    lineage_mock = MagicMock()
    lineage_mock.id = uuid4()
    
    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock(return_value=lineage_mock)
    
    # Execute test
    source_id = "source1"
    source_type = "postgresql"
    destination_id = "dest1"
    destination_type = "s3"
    pipeline_id = uuid4()
    execution_id = str(uuid4())
    
    lineage_id = await metadata_store.record_data_lineage(
        source_id=source_id,
        source_type=source_type,
        destination_id=destination_id,
        destination_type=destination_type,
        pipeline_id=pipeline_id,
        execution_id=execution_id
    )
    
    # Verify
    assert isinstance(lineage_id, UUID)
    session_mock.add.assert_called_once()