"""
Pipeline class for orchestrating data workflows.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import ConfigDict, Field

from datadog_platform.core.base import (
    BaseConfig,
    ExecutionContext,
    ExecutionStatus,
    ProcessingMode,
)
from datadog_platform.core.data_source import DataSource
from datadog_platform.core.transformation import Transformation


class Task(BaseConfig):
    """Represents a single task in a pipeline."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str = Field(default_factory=lambda: str(uuid4()))
    task_type: str  # "source", "transformation", "sink"
    dependencies: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: Optional[int] = None


class Pipeline(BaseConfig):
    """
    Represents a data pipeline in the orchestration platform.

    A pipeline is a DAG of tasks that processes data from sources,
    through transformations, to destinations.
    """

    model_config = ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)

    pipeline_id: str = Field(default_factory=lambda: str(uuid4()))
    processing_mode: ProcessingMode = ProcessingMode.BATCH
    sources: List[DataSource] = Field(default_factory=list)
    transformations: List[Transformation] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    schedule: Optional[str] = None  # Cron expression
    enabled: bool = True
    max_parallel_tasks: int = 4
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    def add_source(self, source: DataSource) -> None:
        """
        Add a data source to the pipeline.

        Args:
            source: DataSource to add
        """
        if not source.validate_config():
            raise ValueError(f"Invalid data source configuration: {source.name}")

        self.sources.append(source)

        # Create a task for this source
        task = Task(
            name=f"source_{source.name}",
            task_type="source",
            metadata={"source_id": source.source_id},
        )
        self.tasks.append(task)

    def add_transformation(self, transformation: Transformation) -> None:
        """
        Add a transformation to the pipeline.

        Args:
            transformation: Transformation to add
        """
        if not transformation.validate_parameters():
            raise ValueError(f"Invalid transformation configuration: {transformation.name}")

        self.transformations.append(transformation)

        # Create a task for this transformation
        dependencies = []
        if self.tasks:
            # Depend on the last task
            dependencies.append(self.tasks[-1].task_id)

        task = Task(
            name=f"transform_{transformation.name}",
            task_type="transformation",
            dependencies=dependencies,
            metadata={"transformation_id": transformation.transformation_id},
        )
        self.tasks.append(task)

    def build_dag(self) -> Dict[str, List[str]]:
        """
        Build the DAG representation of the pipeline.

        Returns:
            dict: Adjacency list representation of the DAG
        """
        dag: Dict[str, List[str]] = {}

        for task in self.tasks:
            dag[task.task_id] = task.dependencies

        return dag

    def validate_dag(self) -> bool:
        """
        Validate that the pipeline forms a valid DAG (no cycles).

        Returns:
            bool: True if DAG is valid
        """
        dag = self.build_dag()
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in dag.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in dag:
            if node not in visited:
                if has_cycle(node):
                    return False

        return True

    def execute(
        self, parameters: Optional[Dict[str, Any]] = None, executor: Optional[Any] = None
    ) -> ExecutionContext:
        """
        Execute the pipeline.

        Args:
            parameters: Execution parameters
            executor: Executor to use (defaults to LocalExecutor)

        Returns:
            ExecutionContext with execution results
        """
        if not self.validate_dag():
            raise ValueError(f"Invalid DAG in pipeline: {self.name}")

        context = ExecutionContext(
            pipeline_id=self.pipeline_id,
            parameters=parameters or {},
            status=ExecutionStatus.PENDING,
        )

        # Placeholder for actual execution
        # This will be implemented with proper executor
        if executor:
            # Use provided executor
            import asyncio
            if asyncio.iscoroutinefunction(executor.execute_dag):
                # If executor supports async execution
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    dag = self.build_dag()
                    result = loop.run_until_complete(executor.execute_dag(dag, context))
                    return context
                finally:
                    loop.close()
            else:
                # Use synchronous execution
                dag = self.build_dag()
                result = executor.execute_dag(dag, context)
                return context
        else:
            # Use default behavior
            context.status = ExecutionStatus.SUCCESS
            context.ended_at = datetime.now(timezone.utc)
            return context
