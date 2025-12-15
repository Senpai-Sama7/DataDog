
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from datadog_platform.core.base import ExecutionContext, ExecutionStatus
from datadog_platform.storage.database import DatabaseManager
from datadog_platform.storage.models import (
    Base,
    DataSourceModel,
    ExecutionContextModel,
    PipelineModel,
    TransformationModel,
)


class PostgreSQLMetadataStore:
    """Manages metadata persistence in a PostgreSQL database."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def initialize(self):
        """
        Ensure all tables are created in the database.
        """
        async with self.db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_pipeline(
        self,
        name: str,
        description: Optional[str] = None,
        definition: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> UUID:
        """
        Create a new pipeline record.
        """
        async with self.db_manager.get_session() as session:
            pipeline = PipelineModel(
                name=name,
                description=description,
                processing_mode=definition.get("processing_mode"),
                schedule=definition.get("schedule"),
                enabled=definition.get("enabled", True),
                tags=tags or {},
                metadata_=definition,  # Store full definition in metadata_
                **kwargs
            )
            session.add(pipeline)
            await session.commit()
            await session.refresh(pipeline)
            return UUID(pipeline.id)

    async def get_pipeline(self, pipeline_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve a pipeline record by ID.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(PipelineModel).filter_by(id=str(pipeline_id))
            result = await session.execute(stmt)
            pipeline = result.scalar_one_or_none()
            return pipeline.to_dict() if pipeline else None

    async def update_pipeline(
        self, pipeline_id: UUID, updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing pipeline record.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(PipelineModel).filter_by(id=str(pipeline_id))
            result = await session.execute(stmt)
            pipeline = result.scalar_one_or_none()
            if pipeline:
                for key, value in updates.items():
                    setattr(pipeline, key, value)
                await session.commit()
                return True
            return False

    async def delete_pipeline(self, pipeline_id: UUID) -> bool:
        """
        Delete a pipeline record by ID.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(PipelineModel).filter_by(id=str(pipeline_id))
            result = await session.execute(stmt)
            pipeline = result.scalar_one_or_none()
            if pipeline:
                await session.delete(pipeline)
                await session.commit()
                return True
            return False

    async def create_data_source(
        self, pipeline_id: UUID, data_source_data: Dict[str, Any]
    ) -> UUID:
        """
        Create a new data source record.
        """
        async with self.db_manager.get_session() as session:
            data_source = DataSourceModel(
                pipeline_id=str(pipeline_id),
                name=data_source_data["name"],
                connector_type=data_source_data["connector_type"],
                connection_config=data_source_data["connection_config"],
                schema_=data_source_data.get("schema", {}),
                query=data_source_data.get("query"),
            )
            session.add(data_source)
            await session.commit()
            await session.refresh(data_source)
            return UUID(data_source.id)

    async def create_transformation(
        self, pipeline_id: UUID, transformation_data: Dict[str, Any]
    ) -> UUID:
        """
        Create a new transformation record.
        """
        async with self.db_manager.get_session() as session:
            transformation = TransformationModel(
                pipeline_id=str(pipeline_id),
                name=transformation_data["name"],
                function_name=transformation_data["function_name"],
                parameters=transformation_data.get("parameters", {}),
                order=transformation_data.get("order", 0),
            )
            session.add(transformation)
            await session.commit()
            await session.refresh(transformation)
            return UUID(transformation.id)

    async def create_execution(
        self, execution_context: ExecutionContext
    ) -> UUID:
        """
        Create a new execution record.
        """
        async with self.db_manager.get_session() as session:
            execution = ExecutionContextModel(
                pipeline_id=execution_context.pipeline_id,
                started_at=execution_context.started_at,
                ended_at=execution_context.ended_at,
                status=execution_context.status,
                parameters=execution_context.parameters,
                metrics=execution_context.metrics,
                error=execution_context.error,
            )
            session.add(execution)
            await session.commit()
            await session.refresh(execution)
            return UUID(execution.id)

    async def create_task(
        self,
        execution_id: UUID,
        task_name: str,
        task_type: str,
        status: ExecutionStatus,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """
        Create a new task record.
        """
        async with self.db_manager.get_session() as session:
            task = TaskModel(
                execution_id=str(execution_id),
                task_name=task_name,
                task_type=task_type,
                status=status,
                input_data=input_data or {},
                output_data=output_data or {},
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return UUID(task.id)

    async def record_data_lineage(
        self,
        pipeline_id: UUID,
        execution_id: UUID,
        source_id: str,
        source_type: str,
        destination_id: str,
        destination_type: str,
        data_flow: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """
        Record data lineage information.
        """
        async with self.db_manager.get_session() as session:
            lineage = DataLineageModel(
                pipeline_id=str(pipeline_id),
                execution_id=str(execution_id),
                source_id=source_id,
                source_type=source_type,
                destination_id=destination_id,
                destination_type=destination_type,
                data_flow=data_flow or {},
            )
            session.add(lineage)
            await session.commit()
            await session.refresh(lineage)
            return UUID(lineage.id)

    async def update_execution_status(
        self,
        execution_id: str,
        status: ExecutionStatus,
        ended_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Update the status of an execution record.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(ExecutionContextModel).filter_by(id=execution_id)
            result = await session.execute(stmt)
            execution = result.scalar_one_or_none()
            if execution:
                execution.status = status
                if ended_at:  # Only update if provided
                    execution.ended_at = ended_at
                if error_message:  # Only update if provided
                    execution.error = error_message
                await session.commit()
                return True
            return False

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an execution record by ID.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(ExecutionContextModel).filter_by(id=execution_id)
            result = await session.execute(stmt)
            execution = result.scalar_one_or_none()
            return execution.to_dict() if execution else None

    async def list_pipelines(self) -> List[Dict[str, Any]]:
        """
        List all pipeline records.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(PipelineModel)
            result = await session.execute(stmt)
            pipelines = result.scalars().all()
            return [p.to_dict() for p in pipelines]

    async def get_pipeline_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a pipeline record by name.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(PipelineModel).filter_by(name=name)
            result = await session.execute(stmt)
            pipeline = result.scalar_one_or_none()
            return pipeline.to_dict() if pipeline else None

    async def list_data_sources(self, pipeline_id: UUID) -> List[Dict[str, Any]]:
        """
        List data sources for a given pipeline.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(DataSourceModel).filter_by(pipeline_id=str(pipeline_id))
            result = await session.execute(stmt)
            data_sources = result.scalars().all()
            return [ds.to_dict() for ds in data_sources]

    async def list_transformations(self, pipeline_id: UUID) -> List[Dict[str, Any]]:
        """
        List transformations for a given pipeline.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(TransformationModel).filter_by(pipeline_id=str(pipeline_id))
            result = await session.execute(stmt)
            transformations = result.scalars().all()
            return [t.to_dict() for t in transformations]

    async def list_execution_contexts(self, pipeline_id: UUID) -> List[Dict[str, Any]]:
        """
        List execution contexts for a given pipeline.
        """
        async with self.db_manager.get_session() as session:
            stmt = select(ExecutionContextModel).filter_by(pipeline_id=str(pipeline_id))
            result = await session.execute(stmt)
            executions = result.scalars().all()
            return [e.to_dict() for e in executions]
