"""
FastAPI server for DataDog platform API.
"""

from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, status, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from datadog_platform import __version__
from datadog_platform.core.base import ExecutionStatus
from datadog_platform.core.pipeline import Pipeline
from datadog_platform.orchestration.metadata_service import MetadataService
from datadog_platform.storage.config import PostgreSQLConfig


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

# Initialize MetadataService
config = PostgreSQLConfig()
metadata_service = MetadataService(config=config)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == "YOUR_SUPER_SECRET_API_KEY": # Replace with actual secure key management
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
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
    return HealthResponse(status="healthy", version=__version__, timestamp=datetime.now(timezone.utc))


@app.get("/api/v1/pipelines", response_model=List[PipelineResponse], dependencies=[Depends(get_api_key)])
async def list_pipelines() -> List[PipelineResponse]:
    """
    List all pipelines.

    Returns a list of all registered pipelines.
    """
    await metadata_service.initialize()
    pipelines_data = await metadata_service.metadata_store.list_pipelines()
    return [
        PipelineResponse(
            pipeline_id=p["id"],
            name=p["name"],
            status="active",  # Status will be derived from execution context later
            created_at=datetime.fromisoformat(p["created_at"]),
        )
        for p in pipelines_data
    ]


@app.post("/api/v1/pipelines", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
async def create_pipeline(pipeline: Pipeline) -> PipelineResponse:
    """
    Create a new pipeline.

    Accepts a pipeline configuration and creates a new pipeline.
    """
    if not pipeline.validate_dag():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pipeline DAG")

    await metadata_service.initialize()
    pipeline_id = await metadata_service.register_pipeline(pipeline)

    return PipelineResponse(
        pipeline_id=str(pipeline_id),
        name=pipeline.name,
        status="active",  # Status will be derived from execution context later
        created_at=pipeline.created_at,
    )


@app.get("/api/v1/pipelines/{pipeline_id}", response_model=Pipeline, dependencies=[Depends(get_api_key)])
async def get_pipeline(pipeline_id: str) -> Pipeline:
    """
    Get pipeline details.

    Returns detailed information about a specific pipeline.
    """
    await metadata_service.initialize()
    pipeline_data = await metadata_service.get_pipeline(UUID(pipeline_id))

    if not pipeline_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Pipeline {pipeline_id} not found"
        )
    
    # Reconstruct Pipeline object from stored metadata
    pipeline_obj = Pipeline(
        pipeline_id=pipeline_data["id"],
        name=pipeline_data["name"],
        description=pipeline_data["description"],
        processing_mode=pipeline_data["processing_mode"],
        schedule=pipeline_data["schedule"],
        enabled=pipeline_data["enabled"],
        max_parallel_tasks=pipeline_data["max_parallel_tasks"],
        created_at=datetime.fromisoformat(pipeline_data["created_at"]),
        updated_at=datetime.fromisoformat(pipeline_data["updated_at"]),
        tags=pipeline_data["tags"],
    )

    # Load associated data sources and transformations
    data_sources_data = await metadata_service.metadata_store.list_data_sources(UUID(pipeline_id))
    for ds_data in data_sources_data:
        pipeline_obj.add_source(DataSource(
            source_id=ds_data["id"],
            name=ds_data["name"],
            connector_type=ds_data["connector_type"],
            connection_config=ds_data["connection_config"],
            schema_config=ds_data["schema"],
            query=ds_data["query"],
            created_at=datetime.fromisoformat(ds_data["created_at"]),
            updated_at=datetime.fromisoformat(ds_data["updated_at"]),
        ))

    transformations_data = await metadata_service.metadata_store.list_transformations(UUID(pipeline_id))
    for tr_data in transformations_data:
        pipeline_obj.add_transformation(Transformation(
            transformation_id=tr_data["id"],
            name=tr_data["name"],
            function_name=tr_data["function_name"],
            parameters=tr_data["parameters"],
            order=tr_data["order"],
            created_at=datetime.fromisoformat(tr_data["created_at"]),
            updated_at=datetime.fromisoformat(tr_data["updated_at"]),
        ))

    return pipeline_obj


@app.post("/api/v1/pipelines/{pipeline_id}/execute", response_model=ExecutionResponse, dependencies=[Depends(get_api_key)])
async def execute_pipeline(pipeline_id: str, request: ExecutionRequest) -> ExecutionResponse:
    """
    Execute a pipeline.

    Triggers execution of the specified pipeline with provided parameters.
    """
    await metadata_service.initialize()
    pipeline_data = await metadata_service.get_pipeline(UUID(pipeline_id))

    if not pipeline_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Pipeline {pipeline_id} not found"
        )

    context = ExecutionContext(
        pipeline_id=pipeline_id, parameters=request.parameters, status=ExecutionStatus.PENDING
    )
    execution_id = await metadata_service.start_execution(context)
    context.execution_id = execution_id

    # Placeholder for actual execution
    # For now, simulate execution and update status
    context.status = ExecutionStatus.SUCCESS
    context.ended_at = datetime.now(timezone.utc)
    await metadata_service.update_execution_status(
        str(context.execution_id),
        context.status,
        context.ended_at
    )

    return ExecutionResponse(
        execution_id=str(context.execution_id),
        pipeline_id=context.pipeline_id,
        status=context.status,
        started_at=context.started_at,
    )


@app.get("/api/v1/executions/{execution_id}/status", dependencies=[Depends(get_api_key)])
async def get_execution_status(execution_id: str) -> Dict[str, Any]:
    """
    Get execution status.

    Returns the current status of a pipeline execution.
    """
    await metadata_service.initialize()
    execution_data = await metadata_service.get_execution(UUID(execution_id))

    if not execution_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Execution {execution_id} not found"
        )

    return {
        "execution_id": execution_data["id"],
        "status": execution_data["status"],
        "started_at": execution_data["started_at"],
        "ended_at": execution_data["ended_at"],
        "error": execution_data["error"],
    }


@app.post("/api/v1/executions/{execution_id}/cancel", dependencies=[Depends(get_api_key)])
async def cancel_execution(execution_id: str) -> Dict[str, str]:
    """
    Cancel a running execution.

    Attempts to cancel an ongoing pipeline execution.
    """
    await metadata_service.initialize()
    result = await metadata_service.update_execution_status(
        execution_id,
        ExecutionStatus.CANCELLED,
        datetime.now(timezone.utc),
        "Execution cancelled by user"
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Execution {execution_id} not found"
        )
    return {"execution_id": execution_id, "status": "cancelled"}


@app.get("/api/v1/connectors", dependencies=[Depends(get_api_key)])
async def list_connectors() -> List[str]:
    """
    List available connector types.

    Returns a list of all supported connector types.
    """
    from datadog_platform.connectors.factory import ConnectorFactory

    return [str(ct) for ct in ConnectorFactory.list_connectors()]


@app.get("/api/v1/metrics", dependencies=[Depends(get_api_key)])
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
