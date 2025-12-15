"""Enhanced executor with PostgreSQL metadata store integration."""

from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from datadog_platform.core.base import (
    BaseExecutor,
    ExecutionContext,
    ExecutionStatus,
)
from datadog_platform.orchestration.metadata_service import MetadataService


class LocalExecutor(BaseExecutor):
    """
    Local executor for running tasks on a single machine with metadata persistence.

    Suitable for development and small-scale deployments with full metadata tracking.
    """

    def __init__(self, max_workers: int = 4, metadata_service: MetadataService = None) -> None:
        """
        Initialize the local executor.

        Args:
            max_workers: Maximum number of concurrent workers
            metadata_service: Optional metadata service for persistence
        """
        self.max_workers = max_workers
        self.executions: Dict[str, ExecutionContext] = {}
        self.metadata_service = metadata_service

    async def execute_task(self, task: Any, context: ExecutionContext) -> Any:
        """
        Execute a single task with metadata tracking.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Task execution result
        """
        context.status = ExecutionStatus.RUNNING
        
        # Update task status in metadata store if available
        if self.metadata_service:
            await self.metadata_service.update_task_status(
                execution_id=context.execution_id,
                task_name=getattr(task, 'name', 'unknown_task'),
                status=ExecutionStatus.RUNNING
            )

        try:
            # Placeholder for actual task execution
            # This will integrate with connectors and transformations
            result = {"task_id": getattr(task, 'task_id', 'unknown'), "status": "completed"}

            context.status = ExecutionStatus.SUCCESS
            context.ended_at = datetime.utcnow()
            
            # Update task status in metadata store if available
            if self.metadata_service:
                await self.metadata_service.update_task_status(
                    execution_id=context.execution_id,
                    task_name=getattr(task, 'name', 'unknown_task'),
                    status=ExecutionStatus.SUCCESS,
                    ended_at=context.ended_at
                )

            return result

        except Exception as e:
            context.status = ExecutionStatus.FAILED
            context.error = str(e)
            context.ended_at = datetime.utcnow()
            
            # Update task status in metadata store if available
            if self.metadata_service:
                await self.metadata_service.update_task_status(
                    execution_id=context.execution_id,
                    task_name=getattr(task, 'name', 'unknown_task'),
                    status=ExecutionStatus.FAILED,
                    ended_at=context.ended_at,
                    error_message=str(e)
                )
            
            raise

    async def execute_dag(self, dag: Any, context: ExecutionContext) -> Any:
        """
        Execute a directed acyclic graph of tasks with metadata tracking.

        Args:
            dag: DAG to execute
            context: Execution context

        Returns:
            DAG execution results
        """
        context.status = ExecutionStatus.RUNNING
        self.executions[context.execution_id] = context
        
        # Record execution start in metadata store if available
        if self.metadata_service:
            await self.metadata_service.start_execution(context)

        try:
            # Topological sort for execution order
            execution_order = self._topological_sort(dag)
            results = {}

            for task_id in execution_order:
                # In a real implementation, this would execute tasks in parallel
                # based on dependencies

                # Execute task (placeholder)
                results[task_id] = {"status": "completed"}

            context.status = ExecutionStatus.SUCCESS
            context.ended_at = datetime.utcnow()
            context.metrics["tasks_completed"] = len(results)
            
            # Update execution status in metadata store if available
            if self.metadata_service:
                await self.metadata_service.update_execution_status(
                    execution_id=context.execution_id,
                    status=ExecutionStatus.SUCCESS,
                    ended_at=context.ended_at
                )

            return results

        except Exception as e:
            context.status = ExecutionStatus.FAILED
            context.error = str(e)
            context.ended_at = datetime.utcnow()
            
            # Update execution status in metadata store if available
            if self.metadata_service:
                await self.metadata_service.update_execution_status(
                    execution_id=context.execution_id,
                    status=ExecutionStatus.FAILED,
                    ended_at=context.ended_at,
                    error_message=str(e)
                )
            
            raise

    def _topological_sort(self, dag: Dict[str, list[str]]) -> list[str]:
        """
        Perform topological sort on the DAG.

        Args:
            dag: Adjacency list representation of DAG

        Returns:
            list: Topologically sorted task IDs
        """
        visited = set()
        stack: list[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            for neighbor in dag.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
            stack.append(node)

        for node in dag:
            if node not in visited:
                dfs(node)

        return list(reversed(stack))

    async def get_status(self, execution_id: str) -> ExecutionStatus:
        """
        Get the status of an execution from memory or metadata store.

        Args:
            execution_id: Execution ID

        Returns:
            ExecutionStatus
        """
        # Check in-memory cache first
        context = self.executions.get(execution_id)
        if context:
            return context.status
            
        # If not in memory, check metadata store if available
        if self.metadata_service:
            try:
                execution = await self.metadata_service._get_execution(execution_id)
                if execution:
                    return ExecutionStatus(execution['status'])
            except Exception:
                pass  # Fallback to in-memory cache
                
        return ExecutionStatus.FAILED

    async def cancel(self, execution_id: str) -> bool:
        """
        Cancel an ongoing execution.

        Args:
            execution_id: Execution ID

        Returns:
            bool: True if cancellation was successful
        """
        context = self.executions.get(execution_id)
        if context and context.status == ExecutionStatus.RUNNING:
            context.status = ExecutionStatus.CANCELLED
            context.ended_at = datetime.utcnow()
            
            # Update execution status in metadata store if available
            if self.metadata_service:
                await self.metadata_service.update_execution_status(
                    execution_id=execution_id,
                    status=ExecutionStatus.CANCELLED,
                    ended_at=context.ended_at
                )
            
            return True
        return False


class DistributedExecutor(BaseExecutor):
    """
    Distributed executor for running tasks across multiple machines with metadata persistence.

    Suitable for production deployments with high scalability requirements.
    """

    def __init__(
        self, 
        broker_url: str, 
        result_backend: str, 
        max_workers: int = 10, 
        metadata_service: MetadataService = None
    ) -> None:
        """
        Initialize the distributed executor.

        Args:
            broker_url: Message broker URL (e.g., Redis, RabbitMQ)
            result_backend: Result storage backend URL
            max_workers: Maximum number of concurrent workers
            metadata_service: Optional metadata service for persistence
        """
        self.broker_url = broker_url
        self.result_backend = result_backend
        self.max_workers = max_workers
        self.executions: Dict[str, ExecutionContext] = {}
        self.metadata_service = metadata_service

    async def execute_task(self, task: Any, context: ExecutionContext) -> Any:
        """Execute a single task in distributed mode with metadata tracking."""
        if self.metadata_service:
            return await LocalExecutor(metadata_service=self.metadata_service).execute_task(task, context)
        else:
            return await LocalExecutor().execute_task(task, context)

    async def execute_dag(self, dag: Any, context: ExecutionContext) -> Any:
        """Execute a DAG in distributed mode with metadata tracking."""
        if self.metadata_service:
            return await LocalExecutor(metadata_service=self.metadata_service).execute_dag(dag, context)
        else:
            return await LocalExecutor().execute_dag(dag, context)

    async def get_status(self, execution_id: str) -> ExecutionStatus:
        """Get execution status from distributed system."""
        context = self.executions.get(execution_id)
        if context:
            return context.status
        return ExecutionStatus.FAILED

    async def cancel(self, execution_id: str) -> bool:
        """Cancel execution in distributed system."""
        context = self.executions.get(execution_id)
        if context and context.status == ExecutionStatus.RUNNING:
            context.status = ExecutionStatus.CANCELLED
            context.ended_at = datetime.utcnow()
            
            # Update execution status in metadata store if available
            if self.metadata_service:
                await self.metadata_service.update_execution_status(
                    execution_id=execution_id,
                    status=ExecutionStatus.CANCELLED,
                    ended_at=context.ended_at
                )
            
            return True
        return False


# Default executor
Executor = LocalExecutor