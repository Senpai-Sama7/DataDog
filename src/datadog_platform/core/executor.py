"""
Executor classes for running pipelines and tasks.
"""

from datetime import datetime
from typing import Any, Dict

from datadog_platform.core.base import (
    BaseExecutor,
    ExecutionContext,
    ExecutionStatus,
)


class LocalExecutor(BaseExecutor):
    """
    Local executor for running tasks on a single machine.

    Suitable for development and small-scale deployments.
    """

    def __init__(self, max_workers: int = 4) -> None:
        """
        Initialize the local executor.

        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.executions: Dict[str, ExecutionContext] = {}

    async def execute_task(self, task: Any, context: ExecutionContext) -> Any:
        """
        Execute a single task.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Task execution result
        """
        context.status = ExecutionStatus.RUNNING

        try:
            # Placeholder for actual task execution
            # This will integrate with connectors and transformations
            result = {"task_id": task.task_id, "status": "completed"}

            context.status = ExecutionStatus.SUCCESS
            context.ended_at = datetime.utcnow()

            return result

        except Exception as e:
            context.status = ExecutionStatus.FAILED
            context.error = str(e)
            context.ended_at = datetime.utcnow()
            raise

    async def execute_dag(self, dag: Any, context: ExecutionContext) -> Any:
        """
        Execute a directed acyclic graph of tasks.

        Args:
            dag: DAG to execute
            context: Execution context

        Returns:
            DAG execution results
        """
        context.status = ExecutionStatus.RUNNING
        self.executions[context.execution_id] = context

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

            return results

        except Exception as e:
            context.status = ExecutionStatus.FAILED
            context.error = str(e)
            context.ended_at = datetime.utcnow()
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
        Get the status of an execution.

        Args:
            execution_id: Execution ID

        Returns:
            ExecutionStatus
        """
        context = self.executions.get(execution_id)
        if context:
            return context.status
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
            return True
        return False


class DistributedExecutor(BaseExecutor):
    """
    Distributed executor for running tasks across multiple machines.

    Suitable for production deployments with high scalability requirements.
    """

    def __init__(self, broker_url: str, result_backend: str, max_workers: int = 10) -> None:
        """
        Initialize the distributed executor.

        Args:
            broker_url: Message broker URL (e.g., Redis, RabbitMQ)
            result_backend: Result storage backend URL
            max_workers: Maximum number of concurrent workers
        """
        self.broker_url = broker_url
        self.result_backend = result_backend
        self.max_workers = max_workers
        self.executions: Dict[str, ExecutionContext] = {}

    async def execute_task(self, task: Any, context: ExecutionContext) -> Any:
        """Execute a single task in distributed mode."""
        # Placeholder - would integrate with Celery or similar
        return await LocalExecutor().execute_task(task, context)

    async def execute_dag(self, dag: Any, context: ExecutionContext) -> Any:
        """Execute a DAG in distributed mode."""
        # Placeholder - would implement distributed task scheduling
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
            return True
        return False


# Default executor
Executor = LocalExecutor
