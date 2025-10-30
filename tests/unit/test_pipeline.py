"""
Unit tests for Pipeline class.
"""

import pytest
from datetime import datetime

from datadog_platform.core.pipeline import Pipeline, Task
from datadog_platform.core.data_source import DataSource
from datadog_platform.core.transformation import Transformation
from datadog_platform.core.base import ConnectorType, ExecutionStatus


class TestPipeline:
    """Test cases for Pipeline class."""
    
    def test_pipeline_creation(self) -> None:
        """Test creating a basic pipeline."""
        pipeline = Pipeline(name="test_pipeline", description="Test pipeline")
        
        assert pipeline.name == "test_pipeline"
        assert pipeline.description == "Test pipeline"
        assert pipeline.pipeline_id is not None
        assert len(pipeline.sources) == 0
        assert len(pipeline.transformations) == 0
        assert pipeline.enabled is True
    
    def test_add_data_source(self) -> None:
        """Test adding a data source to pipeline."""
        pipeline = Pipeline(name="test_pipeline")
        
        source = DataSource(
            name="test_source",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={
                "host": "localhost",
                "database": "testdb"
            }
        )
        
        pipeline.add_source(source)
        
        assert len(pipeline.sources) == 1
        assert pipeline.sources[0].name == "test_source"
        assert len(pipeline.tasks) == 1
    
    def test_add_transformation(self) -> None:
        """Test adding a transformation to pipeline."""
        pipeline = Pipeline(name="test_pipeline")
        
        # Add source first
        source = DataSource(
            name="test_source",
            connector_type=ConnectorType.FILE_SYSTEM,
            connection_config={"path": "/tmp/data"}
        )
        pipeline.add_source(source)
        
        # Add transformation
        transform = Transformation(
            name="filter_data",
            function_name="filter_nulls",
            parameters={"columns": ["id", "name"]}
        )
        
        pipeline.add_transformation(transform)
        
        assert len(pipeline.transformations) == 1
        assert len(pipeline.tasks) == 2
    
    def test_build_dag(self) -> None:
        """Test building DAG from pipeline."""
        pipeline = Pipeline(name="test_pipeline")
        
        source = DataSource(
            name="source",
            connector_type=ConnectorType.FILE_SYSTEM,
            connection_config={"path": "/tmp"}
        )
        pipeline.add_source(source)
        
        transform = Transformation(
            name="transform",
            function_name="filter_nulls",
            parameters={"columns": ["id"]}
        )
        pipeline.add_transformation(transform)
        
        dag = pipeline.build_dag()
        
        assert len(dag) == 2
        # Second task should depend on first
        assert len(list(dag.values())[1]) > 0
    
    def test_validate_dag_no_cycle(self) -> None:
        """Test DAG validation with no cycles."""
        pipeline = Pipeline(name="test_pipeline")
        
        source = DataSource(
            name="source",
            connector_type=ConnectorType.FILE_SYSTEM,
            connection_config={"path": "/tmp"}
        )
        pipeline.add_source(source)
        
        assert pipeline.validate_dag() is True
    
    def test_pipeline_execution(self) -> None:
        """Test pipeline execution."""
        pipeline = Pipeline(name="test_pipeline")
        
        source = DataSource(
            name="source",
            connector_type=ConnectorType.FILE_SYSTEM,
            connection_config={"path": "/tmp"}
        )
        pipeline.add_source(source)
        
        context = pipeline.execute()
        
        assert context.pipeline_id == pipeline.pipeline_id
        assert context.status == ExecutionStatus.SUCCESS
        assert context.execution_id is not None
    
    def test_invalid_data_source_raises_error(self) -> None:
        """Test that invalid data source raises error."""
        pipeline = Pipeline(name="test_pipeline")
        
        # Missing required config fields
        source = DataSource(
            name="invalid_source",
            connector_type=ConnectorType.POSTGRESQL,
            connection_config={}  # Missing host and database
        )
        
        with pytest.raises(ValueError):
            pipeline.add_source(source)
    
    def test_invalid_transformation_raises_error(self) -> None:
        """Test that invalid transformation raises error."""
        pipeline = Pipeline(name="test_pipeline")
        
        # Missing required parameters
        transform = Transformation(
            name="invalid_transform",
            function_name="filter_nulls",
            parameters={}  # Missing columns parameter
        )
        
        with pytest.raises(ValueError):
            pipeline.add_transformation(transform)


class TestTask:
    """Test cases for Task class."""
    
    def test_task_creation(self) -> None:
        """Test creating a task."""
        task = Task(
            name="test_task",
            task_type="source",
            dependencies=[]
        )
        
        assert task.name == "test_task"
        assert task.task_type == "source"
        assert task.task_id is not None
        assert len(task.dependencies) == 0
        assert task.max_retries == 3
    
    def test_task_with_dependencies(self) -> None:
        """Test task with dependencies."""
        task1 = Task(name="task1", task_type="source")
        task2 = Task(
            name="task2",
            task_type="transformation",
            dependencies=[task1.task_id]
        )
        
        assert len(task2.dependencies) == 1
        assert task2.dependencies[0] == task1.task_id
