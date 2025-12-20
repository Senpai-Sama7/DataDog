
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import delete, select, update

from datadog_platform.core.base import ExecutionContext, ExecutionStatus
from datadog_platform.storage.database import DatabaseManager
from datadog_platform.storage.models import (
    Base,
    DataLineageModel,
    DataSourceModel,
    ExecutionContextModel,
    PipelineModel,
    TaskModel,
    TransformationModel,
)

from datadog_platform.utils.asyncio import maybe_await


class PostgreSQLMetadataStore:
    """Manages metadata persistence in a PostgreSQL database."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def _get_session(self) -> Tuple[Any, Any]:
        """Return a session and its context manager with flexible awaiting."""

        session_context = self.db_manager.get_session()
        session = await maybe_await(session_context.__aenter__())
        return session, session_context

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
        session, session_context = await self._get_session()
        try:
            pipeline = PipelineModel(
                name=name,
                description=description,
                processing_mode=definition.get("processing_mode") if definition else None,
                schedule=definition.get("schedule") if definition else None,
                enabled=definition.get("enabled", True) if definition else True,
                tags=tags or {},
                metadata_=definition or {},
                **kwargs,
            )
            session.add(pipeline)
            await maybe_await(session.commit())
            await maybe_await(session.refresh(pipeline))
            return UUID(pipeline.id)
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def get_pipeline(self, pipeline_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve a pipeline record by ID.
        """
        session, session_context = await self._get_session()
        try:
            stmt = select(PipelineModel).filter_by(id=str(pipeline_id))
            result = await maybe_await(session.execute(stmt))
            pipeline = getattr(result, "scalar_one_or_none", lambda: None)()
            if not pipeline:
                return None

            if hasattr(pipeline, "to_dict"):
                return pipeline.to_dict()

            return {
                "id": getattr(pipeline, "id", str(pipeline_id)),
                "name": getattr(pipeline, "name", ""),
                "description": getattr(pipeline, "description", None),
                "processing_mode": getattr(pipeline, "processing_mode", None),
                "schedule": getattr(pipeline, "schedule", None),
                "enabled": getattr(pipeline, "enabled", True),
                "tags": getattr(pipeline, "tags", {}),
                "metadata": getattr(pipeline, "definition", getattr(pipeline, "metadata_", {})),
            }
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def update_pipeline(
        self, pipeline_id: UUID, updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing pipeline record.
        """
        session, session_context = await self._get_session()
        try:
            stmt = (
                update(PipelineModel)
                .where(PipelineModel.id == str(pipeline_id))
                .values(**updates)
            )
            result = await maybe_await(session.execute(stmt))
            await maybe_await(session.commit())
            return bool(getattr(result, "rowcount", 0))
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def delete_pipeline(self, pipeline_id: UUID) -> bool:
        """
        Delete a pipeline record by ID.
        """
        session, session_context = await self._get_session()
        try:
            stmt = delete(PipelineModel).where(PipelineModel.id == str(pipeline_id))
            result = await maybe_await(session.execute(stmt))
            await maybe_await(session.commit())
            return bool(getattr(result, "rowcount", 0))
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def create_data_source(
        self, pipeline_id: UUID, data_source_data: Dict[str, Any]
    ) -> UUID:
        """
        Create a new data source record.
        """
        session, session_context = await self._get_session()
        try:
            data_source = DataSourceModel(
                pipeline_id=str(pipeline_id),
                name=data_source_data["name"],
                connector_type=data_source_data["connector_type"],
                connection_config=data_source_data.get("connection_config", {}),
                schema_=data_source_data.get("schema", {}),
                query=data_source_data.get("query"),
            )
            session.add(data_source)
            await maybe_await(session.commit())
            await maybe_await(session.refresh(data_source))
            return UUID(data_source.id)
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def create_transformation(
        self, pipeline_id: UUID, transformation_data: Dict[str, Any]
    ) -> UUID:
        """
        Create a new transformation record.
        """
        session, session_context = await self._get_session()
        try:
            transformation = TransformationModel(
                pipeline_id=str(pipeline_id),
                name=transformation_data["name"],
                function_name=transformation_data["function_name"],
                parameters=transformation_data.get("parameters", {}),
                order=transformation_data.get("order", 0),
            )
            session.add(transformation)
            await maybe_await(session.commit())
            await maybe_await(session.refresh(transformation))
            return UUID(transformation.id)
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def create_execution(
        self, execution_context: ExecutionContext
    ) -> UUID:
        """
        Create a new execution record.
        """
        session, session_context = await self._get_session()
        try:
            execution = ExecutionContextModel(
                id=execution_context.execution_id,
                pipeline_id=execution_context.pipeline_id,
                started_at=execution_context.started_at,
                ended_at=execution_context.ended_at,
                status=execution_context.status,
                parameters=execution_context.parameters,
                metrics=execution_context.metrics,
                error=execution_context.error,
            )
            session.add(execution)
            await maybe_await(session.commit())
            await maybe_await(session.refresh(execution))
            return UUID(execution_context.execution_id)
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

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
        session, session_context = await self._get_session()
        try:
            task = TaskModel(
                execution_id=str(execution_id),
                task_name=task_name,
                task_type=task_type,
                status=status,
                input_data=input_data or {},
                output_data=output_data or {},
            )
            session.add(task)
            await maybe_await(session.commit())
            await maybe_await(session.refresh(task))
            return UUID(task.id)
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

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
        session, session_context = await self._get_session()
        try:
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
            await maybe_await(session.commit())
            await maybe_await(session.refresh(lineage))
            return UUID(lineage.id)
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

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
        session, session_context = await self._get_session()
        try:
            updates = {"status": status}
            if ended_at is not None:
                updates["ended_at"] = ended_at
            if error_message is not None:
                updates["error"] = error_message

            stmt = (
                update(ExecutionContextModel)
                .where(ExecutionContextModel.id == str(execution_id))
                .values(**updates)
            )
            result = await maybe_await(session.execute(stmt))
            await maybe_await(session.commit())
            return bool(getattr(result, "rowcount", 0))
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an execution record by ID.
        """
        session, session_context = await self._get_session()
        try:
            stmt = select(ExecutionContextModel).filter_by(id=str(execution_id))
            result = await maybe_await(session.execute(stmt))
            execution = getattr(result, "scalar_one_or_none", lambda: None)()
            if not execution:
                return None

            if hasattr(execution, "to_dict"):
                return execution.to_dict()

            return {
                "id": getattr(execution, "id", str(execution_id)),
                "pipeline_id": getattr(execution, "pipeline_id", None),
                "started_at": getattr(execution, "started_at", None),
                "ended_at": getattr(execution, "ended_at", None),
                "status": getattr(execution, "status", None),
                "parameters": getattr(execution, "parameters", {}),
                "metrics": getattr(execution, "metrics", {}),
                "error": getattr(execution, "error", None),
            }
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def list_pipelines(self) -> List[Dict[str, Any]]:
        """
        List all pipeline records.
        """
        session, session_context = await self._get_session()
        try:
            stmt = select(PipelineModel)
            result = await maybe_await(session.execute(stmt))
            pipelines = result.scalars().all() if hasattr(result, "scalars") else []
            return [p.to_dict() for p in pipelines]
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def get_pipeline_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a pipeline record by name.
        """
        session, session_context = await self._get_session()
        try:
            stmt = select(PipelineModel).filter_by(name=name)
            result = await maybe_await(session.execute(stmt))
            pipeline = getattr(result, "scalar_one_or_none", lambda: None)()
            return pipeline.to_dict() if pipeline else None
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def list_data_sources(self, pipeline_id: UUID) -> List[Dict[str, Any]]:
        """
        List data sources for a given pipeline.
        """
        session, session_context = await self._get_session()
        try:
            stmt = select(DataSourceModel).filter_by(pipeline_id=str(pipeline_id))
            result = await maybe_await(session.execute(stmt))
            data_sources = result.scalars().all() if hasattr(result, "scalars") else []
            return [ds.to_dict() for ds in data_sources]
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def list_transformations(self, pipeline_id: UUID) -> List[Dict[str, Any]]:
        """
        List transformations for a given pipeline.
        """
        session, session_context = await self._get_session()
        try:
            stmt = select(TransformationModel).filter_by(pipeline_id=str(pipeline_id))
            result = await maybe_await(session.execute(stmt))
            if hasattr(result, "scalars"):
                transformations = result.scalars().all()
            elif hasattr(result, "fetchall"):
                transformations = [row[0] for row in result.fetchall()]
            else:
                raise RuntimeError(f"Unexpected execute() result type: {type(result)!r}")
            return [t.to_dict() for t in transformations]
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))

    async def list_execution_contexts(self, pipeline_id: UUID) -> List[Dict[str, Any]]:
        """
        List execution contexts for a given pipeline.
        """
        session, session_context = await self._get_session()
        try:
            stmt = select(ExecutionContextModel).filter_by(pipeline_id=str(pipeline_id))
            result = await maybe_await(session.execute(stmt))
            executions = result.scalars().all() if hasattr(result, "scalars") else []
            return [e.to_dict() for e in executions]
        finally:
            await maybe_await(session_context.__aexit__(None, None, None))
