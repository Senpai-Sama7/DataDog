"""
FastAPI server for DataDog platform API.
"""

from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from datadog_platform import __version__
from datadog_platform.core.pipeline import Pipeline
from datadog_platform.core.base import ExecutionStatus


# API Models
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime


class PipelineResponse(BaseModel):
    """Pipeline response model."""

    pipeline_id: str
    name: str
    status: str
    created_at: datetime


class ExecutionRequest(BaseModel):
    """Pipeline execution request."""

    parameters: Dict[str, Any] = {}


class ExecutionResponse(BaseModel):
    """Pipeline execution response."""

    execution_id: str
    pipeline_id: str
    status: ExecutionStatus
    started_at: datetime


# Create FastAPI app
app = FastAPI(
    title="DataDog Platform API",
    description="Universal Data Orchestration Platform API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"name": "DataDog Platform API", "version": __version__, "docs": "/docs"}


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns system health status and version information.
    """
    return HealthResponse(status="healthy", version=__version__, timestamp=datetime.utcnow())


@app.get("/api/v1/pipelines", response_model=List[PipelineResponse])
async def list_pipelines() -> List[PipelineResponse]:
    """
    List all pipelines.

    Returns a list of all registered pipelines.
    """
    # Placeholder - would query metadata store
    return [
        PipelineResponse(
            pipeline_id="pipeline-001",
            name="example_pipeline",
            status="active",
            created_at=datetime.utcnow(),
        )
    ]


@app.post("/api/v1/pipelines", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(pipeline: Pipeline) -> PipelineResponse:
    """
    Create a new pipeline.

    Accepts a pipeline configuration and creates a new pipeline.
    """
    if not pipeline.validate_dag():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pipeline DAG")

    # Placeholder - would save to metadata store
    return PipelineResponse(
        pipeline_id=pipeline.pipeline_id,
        name=pipeline.name,
        status="active",
        created_at=pipeline.created_at,
    )


@app.get("/api/v1/pipelines/{pipeline_id}", response_model=Pipeline)
async def get_pipeline(pipeline_id: str) -> Pipeline:
    """
    Get pipeline details.

    Returns detailed information about a specific pipeline.
    """
    # Placeholder - would query metadata store
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Pipeline {pipeline_id} not found"
    )


@app.post("/api/v1/pipelines/{pipeline_id}/execute", response_model=ExecutionResponse)
async def execute_pipeline(pipeline_id: str, request: ExecutionRequest) -> ExecutionResponse:
    """
    Execute a pipeline.

    Triggers execution of the specified pipeline with provided parameters.
    """
    # Placeholder - would load pipeline and execute
    from datadog_platform.core.base import ExecutionContext

    context = ExecutionContext(
        pipeline_id=pipeline_id, parameters=request.parameters, status=ExecutionStatus.PENDING
    )

    return ExecutionResponse(
        execution_id=context.execution_id,
        pipeline_id=context.pipeline_id,
        status=context.status,
        started_at=context.started_at,
    )


@app.get("/api/v1/executions/{execution_id}/status")
async def get_execution_status(execution_id: str) -> Dict[str, Any]:
    """
    Get execution status.

    Returns the current status of a pipeline execution.
    """
    # Placeholder - would query execution status
    return {
        "execution_id": execution_id,
        "status": "running",
        "progress": 0.6,
        "tasks_completed": 3,
        "tasks_total": 5,
    }


@app.post("/api/v1/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str) -> Dict[str, str]:
    """
    Cancel a running execution.

    Attempts to cancel an ongoing pipeline execution.
    """
    # Placeholder - would cancel execution
    return {"execution_id": execution_id, "status": "cancelled"}


@app.get("/api/v1/connectors")
async def list_connectors() -> List[str]:
    """
    List available connector types.

    Returns a list of all supported connector types.
    """
    from datadog_platform.connectors.factory import ConnectorFactory

    return [str(ct) for ct in ConnectorFactory.list_connectors()]


@app.get("/api/v1/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get platform metrics.

    Returns performance and operational metrics.
    """
    return {
        "pipelines_active": 10,
        "pipelines_total": 25,
        "executions_running": 3,
        "executions_completed_today": 150,
        "tasks_executed_total": 5000,
        "uptime_seconds": 86400,
    }


def main() -> None:
    """Run the API server."""
    import uvicorn

    uvicorn.run("datadog_platform.api.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
