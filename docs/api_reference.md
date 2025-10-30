# DataDog Platform API Reference

## REST API

Base URL: `http://localhost:8000/api/v1`

### Authentication

Currently, the API does not require authentication. This will be added in future versions.

Future authentication header:
```
Authorization: Bearer <token>
```

## Core Resources

### Pipelines

#### List Pipelines

```http
GET /api/v1/pipelines
```

**Response:**
```json
[
  {
    "pipeline_id": "pipeline-001",
    "name": "example_pipeline",
    "status": "active",
    "created_at": "2025-10-30T06:00:00Z"
  }
]
```

#### Create Pipeline

```http
POST /api/v1/pipelines
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "my_pipeline",
  "description": "ETL pipeline for analytics",
  "processing_mode": "batch",
  "sources": [
    {
      "name": "postgres_source",
      "connector_type": "postgresql",
      "connection_config": {
        "host": "localhost",
        "database": "mydb",
        "table": "users"
      }
    }
  ],
  "transformations": [
    {
      "name": "clean_data",
      "function_name": "filter_nulls",
      "parameters": {
        "columns": ["id", "name"]
      }
    }
  ],
  "schedule": "0 */6 * * *",
  "enabled": true
}
```

**Response:** `201 Created`
```json
{
  "pipeline_id": "pipeline-123",
  "name": "my_pipeline",
  "status": "active",
  "created_at": "2025-10-30T12:00:00Z"
}
```

#### Get Pipeline

```http
GET /api/v1/pipelines/{pipeline_id}
```

**Response:**
```json
{
  "pipeline_id": "pipeline-123",
  "name": "my_pipeline",
  "description": "ETL pipeline for analytics",
  "processing_mode": "batch",
  "sources": [...],
  "transformations": [...],
  "tasks": [...],
  "schedule": "0 */6 * * *",
  "enabled": true,
  "created_at": "2025-10-30T12:00:00Z",
  "updated_at": "2025-10-30T12:00:00Z"
}
```

#### Execute Pipeline

```http
POST /api/v1/pipelines/{pipeline_id}/execute
Content-Type: application/json
```

**Request Body:**
```json
{
  "parameters": {
    "run_date": "2025-10-30",
    "mode": "full"
  }
}
```

**Response:**
```json
{
  "execution_id": "exec-456",
  "pipeline_id": "pipeline-123",
  "status": "pending",
  "started_at": "2025-10-30T12:05:00Z"
}
```

### Executions

#### Get Execution Status

```http
GET /api/v1/executions/{execution_id}/status
```

**Response:**
```json
{
  "execution_id": "exec-456",
  "pipeline_id": "pipeline-123",
  "status": "running",
  "started_at": "2025-10-30T12:05:00Z",
  "progress": 0.6,
  "tasks_completed": 3,
  "tasks_total": 5,
  "current_task": "transform_data",
  "metrics": {
    "rows_processed": 10000,
    "rows_failed": 0,
    "duration_seconds": 45
  }
}
```

#### Cancel Execution

```http
POST /api/v1/executions/{execution_id}/cancel
```

**Response:**
```json
{
  "execution_id": "exec-456",
  "status": "cancelled",
  "cancelled_at": "2025-10-30T12:10:00Z"
}
```

### Connectors

#### List Connector Types

```http
GET /api/v1/connectors
```

**Response:**
```json
[
  "postgresql",
  "mysql",
  "mongodb",
  "redis",
  "s3",
  "rest_api",
  "file_system",
  "kafka"
]
```

### System

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-10-30T12:00:00Z"
}
```

#### Metrics

```http
GET /api/v1/metrics
```

**Response:**
```json
{
  "pipelines_active": 10,
  "pipelines_total": 25,
  "executions_running": 3,
  "executions_completed_today": 150,
  "tasks_executed_total": 5000,
  "uptime_seconds": 86400,
  "workers_active": 5,
  "workers_idle": 2
}
```

## Python API

### Pipeline

```python
from datadog_platform import Pipeline, DataSource, Transformation
from datadog_platform.core.base import ConnectorType, ProcessingMode

# Create pipeline
pipeline = Pipeline(
    name="my_pipeline",
    description="ETL pipeline",
    processing_mode=ProcessingMode.BATCH
)

# Add data source
source = DataSource(
    name="input_db",
    connector_type=ConnectorType.POSTGRESQL,
    connection_config={
        "host": "localhost",
        "database": "mydb"
    }
)
pipeline.add_source(source)

# Add transformation
transform = Transformation(
    name="clean",
    function_name="filter_nulls",
    parameters={"columns": ["id"]}
)
pipeline.add_transformation(transform)

# Execute
context = pipeline.execute()
print(f"Status: {context.status}")
```

### DataSource

```python
from datadog_platform.core.data_source import DataSource
from datadog_platform.core.base import ConnectorType

# SQL database source
source = DataSource(
    name="postgres_source",
    connector_type=ConnectorType.POSTGRESQL,
    connection_config={
        "host": "localhost",
        "port": 5432,
        "database": "analytics",
        "username": "user",
        "password": "pass",
        "table": "events"
    },
    query="SELECT * FROM events WHERE date >= %(start_date)s",
    schema={
        "columns": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"}
        ]
    }
)

# Validate configuration
if source.validate_config():
    print("Configuration is valid")
```

### Transformation

```python
from datadog_platform.core.transformation import Transformation

# Filter transformation
filter_transform = Transformation(
    name="filter_valid",
    function_name="filter_nulls",
    parameters={"columns": ["id", "email"]}
)

# Aggregate transformation
agg_transform = Transformation(
    name="aggregate_data",
    function_name="aggregate",
    parameters={
        "group_by": ["user_id"],
        "aggregations": {
            "total": "sum(amount)",
            "count": "count(*)"
        }
    }
)

# Validate parameters
if agg_transform.validate_parameters():
    print("Parameters are valid")
```

### Connectors

```python
from datadog_platform.connectors import ConnectorFactory
from datadog_platform.core.base import ConnectorType
import asyncio

async def read_data():
    # Create connector
    connector = ConnectorFactory.create_connector(
        ConnectorType.POSTGRESQL,
        {
            "host": "localhost",
            "database": "mydb",
            "username": "user",
            "password": "pass"
        }
    )
    
    # Use async context manager
    async with connector:
        # Read data
        data = await connector.read(query="SELECT * FROM users LIMIT 10")
        print(f"Read {len(data)} rows")
        
        # Write data
        await connector.write(
            data=[{"id": 1, "name": "Alice"}],
            table="users"
        )

# Run async function
asyncio.run(read_data())
```

### Executors

```python
from datadog_platform.core.executor import LocalExecutor, DistributedExecutor
from datadog_platform.core.base import ExecutionContext
import asyncio

# Local executor
async def run_local():
    executor = LocalExecutor(max_workers=4)
    
    context = ExecutionContext(pipeline_id="my-pipeline")
    dag = {"task1": [], "task2": ["task1"]}
    
    result = await executor.execute_dag(dag, context)
    print(f"Status: {context.status}")

# Distributed executor
executor = DistributedExecutor(
    broker_url="redis://localhost:6379",
    result_backend="redis://localhost:6379",
    max_workers=10
)
```

## CLI Reference

### Pipeline Commands

```bash
# Create pipeline from config
datadog pipeline create --config pipeline.yaml

# List pipelines
datadog pipeline list

# Get pipeline details
datadog pipeline get my_pipeline

# Run pipeline
datadog pipeline run my_pipeline --params '{"date": "2025-10-30"}'

# Check pipeline status
datadog pipeline status my_pipeline

# Delete pipeline
datadog pipeline delete my_pipeline
```

### Connector Commands

```bash
# List connector types
datadog connector list

# Test connector configuration
datadog connector test --type postgresql --config db_config.yaml
```

### Server Commands

```bash
# Start API server
datadog-server

# Start with custom config
datadog-server --config config.yaml --port 8080

# Start worker
datadog-worker --concurrency 4
```

## Error Codes

### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_PIPELINE",
    "message": "Pipeline configuration is invalid",
    "details": {
      "field": "sources",
      "reason": "At least one source is required"
    }
  }
}
```

## Rate Limiting

Currently no rate limiting is enforced. Future versions will implement:

- **Rate Limit**: 60 requests per minute per IP
- **Burst Limit**: 10 requests per second
- **Headers**:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Pagination

List endpoints support pagination:

```http
GET /api/v1/pipelines?page=1&per_page=20
```

**Response Headers:**
```
X-Total-Count: 100
X-Page: 1
X-Per-Page: 20
X-Total-Pages: 5
Link: <http://api/v1/pipelines?page=2>; rel="next"
```

## Filtering and Sorting

```http
# Filter pipelines
GET /api/v1/pipelines?status=active&tags=production

# Sort pipelines
GET /api/v1/pipelines?sort=created_at&order=desc
```

## Webhooks

Configure webhooks for pipeline events:

```json
{
  "url": "https://myapp.com/webhooks/datadog",
  "events": ["pipeline.started", "pipeline.completed", "pipeline.failed"],
  "secret": "webhook_secret"
}
```

**Webhook Payload:**
```json
{
  "event": "pipeline.completed",
  "timestamp": "2025-10-30T12:00:00Z",
  "data": {
    "pipeline_id": "pipeline-123",
    "execution_id": "exec-456",
    "status": "success",
    "duration": 120
  }
}
```

## SDK Support

Official SDKs:
- **Python**: Built-in (primary)
- **JavaScript/TypeScript**: Coming soon
- **Go**: Coming soon
- **Java**: Planned

## OpenAPI Specification

Full OpenAPI/Swagger spec available at:
- **UI**: http://localhost:8000/docs
- **JSON**: http://localhost:8000/openapi.json
- **ReDoc**: http://localhost:8000/redoc
