"""Metadata service integration for the DataDog platform."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from datadog_platform.core.base import ExecutionContext, ExecutionStatus
from datadog_platform.core.pipeline import Pipeline
from datadog_platform.storage.config import PostgreSQLConfig
from datadog_platform.storage.database import DatabaseManager
from datadog_platform.storage.postgres_metadata_store import PostgreSQLMetadataStore
from datadog_platform.storage.models import PipelineModel, DataSourceModel, TransformationModel, ExecutionContextModel


class MetadataService:
    """Service layer to integrate PostgreSQL metadata store with orchestrator."""
    
    def __init__(self, config: PostgreSQLConfig):
        """Initialize the metadata service."""
        self.db_manager = DatabaseManager(config)
        self.metadata_store = PostgreSQLMetadataStore(self.db_manager)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the metadata service."""
        await self.db_manager.initialize()
        await self.metadata_store.initialize()
        self._initialized = True
    
    async def shutdown(self):
        """Shutdown the metadata service."""
        await self.db_manager.close()
    
    async def register_pipeline(self, pipeline: Pipeline) -> UUID:
        """Register a pipeline in the metadata store."""
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        
        # Convert pipeline to the format expected by the metadata store
        pipeline_def = {
            "name": pipeline.name,
            "description": pipeline.description,
            "sources": [source.model_dump() for source in pipeline.sources],
            "transformations": [transform.model_dump() for transform in pipeline.transformations],
            "processing_mode": pipeline.processing_mode,
            "schedule": pipeline.schedule,
            "enabled": pipeline.enabled,
            "max_parallel_tasks": pipeline.max_parallel_tasks
        }
        
        pipeline_id = await self.metadata_store.create_pipeline(
            name=pipeline.name,
            description=pipeline.description,
            definition=pipeline.model_dump(mode='json'),  # Store full definition as JSON
            tags=pipeline.tags,
            processing_mode=pipeline.processing_mode,
            schedule=pipeline.schedule,
            enabled=pipeline.enabled,
            max_parallel_tasks=pipeline.max_parallel_tasks,
        )
        
        return pipeline_id
    
    async def get_pipeline(self, pipeline_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve a pipeline from the metadata store."""
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        
        return await self.metadata_store.get_pipeline(pipeline_id)
    
    async def update_pipeline_status(self, pipeline_id: UUID, status: str) -> bool:
        """Update the status of a pipeline."""
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        
        return await self.metadata_store.update_pipeline(
            pipeline_id=pipeline_id,
            updates={
                "status": status,
                "updated_at": datetime.now(timezone.utc)
            }
        )
    
    async def start_execution(self, execution_context: ExecutionContext) -> str:
        """Record the start of a pipeline execution."""
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        
        execution_id = await self.metadata_store.create_execution(execution_context)
        return execution_id
    
    async def update_execution_status(
        self, 
        execution_id: str, 
        status: ExecutionStatus, 
        ended_at: Optional[datetime] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update the status of an execution."""
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        
        return await self.metadata_store.update_execution_status(
            execution_id=UUID(execution_id),
            status=status,
            ended_at=ended_at,
            error_message=error_message
        )

    async def update_task_status(
        self,
        execution_id: UUID,
        task_name: str,
        status: ExecutionStatus,
        ended_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update the status of a specific task within an execution."""
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        
        # This is a simplified approach - in a real implementation, 
        # we'd need proper task identification
        # For now, we assume task_name is unique within an execution
        # and we can update it directly.
        return await self.metadata_store.update_task_status(
            execution_id=execution_id,
            task_name=task_name,
            status=status,
            ended_at=ended_at,
            error_message=error_message,
            input_data=input_data,
            output_data=output_data
        )

    async def record_data_lineage(
        self,
        source_id: str,
        source_type: str,
        destination_id: str,
        destination_type: str,
        pipeline_id: UUID,
        execution_id: UUID,
        data_flow: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Record data lineage information."""
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        
        if data_flow is None:
            data_flow = {}
        
        return await self.metadata_store.record_data_lineage(
            source_id=source_id,
            source_type=source_type,
            destination_id=destination_id,
            destination_type=destination_type,
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            data_flow=data_flow
        )
    
    async def _get_execution(self, execution_id: UUID) -> Optional[Dict[str, Any]]:
        return await self.metadata_store.get_execution(execution_id)

    async def get_execution(self, execution_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve an execution record by ID from the metadata store.
        """
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        return await self.metadata_store.get_execution(execution_id)

    async def get_pipeline_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a pipeline record by name from the metadata store.
        """
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        return await self.metadata_store.get_pipeline_by_name(name)
    
    async def get_execution_history(self, pipeline_id: UUID) -> List[Dict[str, Any]]:
        """Get execution history for a pipeline."""
        if not self._initialized:
            raise RuntimeError("Metadata service not initialized")
        
        execution_contexts = await self.metadata_store.list_execution_contexts(pipeline_id)
        return [
            {
                "id": exec_context["id"],
                "pipeline_id": exec_context["pipeline_id"],
                "started_at": exec_context["started_at"],
                "ended_at": exec_context["ended_at"],
                "status": exec_context["status"],
                "parameters": exec_context["parameters"],
                "metrics": exec_context["metrics"],
                "error": exec_context["error"],
            }
            for exec_context in execution_contexts
        ]