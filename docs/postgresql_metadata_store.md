# PostgreSQL Metadata Store Implementation

## Overview

The PostgreSQL metadata store is a core component of the DataDog Universal Data Orchestration Platform that provides persistent storage for pipeline definitions, execution history, task status, and data lineage information. This implementation enables enterprise-grade data orchestration with full audit trails and operational visibility.

## Architecture

### Components

1. **Database Manager** (`storage/database.py`): Handles PostgreSQL connection pooling and session management
2. **Configuration** (`storage/config.py`): Manages database connection parameters
3. **Data Models** (`storage/models.py`): SQLAlchemy ORM models for the metadata schema
4. **PostgreSQL Metadata Store** (`storage/postgres_metadata_store.py`): Core repository implementation
5. **Metadata Service** (`orchestration/metadata_service.py`): Higher-level service layer for orchestration integration
6. **Migrations** (`storage/alembic/versions/0001_initial_metadata_store.py`): Database schema migration scripts

## Data Schema

### Tables

#### `pipelines`
- `id`: UUID primary key
- `name`: Pipeline name (VARCHAR 255)
- `description`: Pipeline description (TEXT)
- `definition`: Full pipeline definition in JSONB format
- `created_at`: Timestamp when pipeline was created
- `updated_at`: Timestamp when pipeline was last updated (auto-updating)
- `version`: Version number (INTEGER)
- `tags`: Metadata tags in JSONB format
- `status`: Pipeline status (VARCHAR 50, default: "active")

#### `executions`
- `id`: UUID primary key
- `pipeline_id`: Foreign key to pipelines table
- `execution_id`: Unique execution identifier
- `started_at`: Execution start timestamp
- `ended_at`: Execution end timestamp
- `status`: Execution status (pending, running, success, failed, cancelled, retry)
- `parameters`: Execution parameters in JSONB format
- `metrics`: Execution metrics in JSONB format
- `error_message`: Error details if execution failed (TEXT)

#### `tasks`
- `id`: UUID primary key
- `execution_id`: Foreign key to executions table
- `task_name`: Task name (VARCHAR 255)
- `task_type`: Task type (VARCHAR 100, e.g., connector, transformation)
- `started_at`: Task start timestamp
- `ended_at`: Task end timestamp
- `status`: Task status (pending, running, success, failed, cancelled, retry)
- `input_data`: Task input data in JSONB format
- `output_data`: Task output data in JSONB format
- `error_message`: Error details if task failed (TEXT)

#### `data_lineage`
- `id`: UUID primary key
- `source_id`: Source identifier (VARCHAR 255)
- `source_type`: Source type (VARCHAR 100)
- `destination_id`: Destination identifier (VARCHAR 255)
- `destination_type`: Destination type (VARCHAR 100)
- `pipeline_id`: Foreign key to pipelines table (optional)
- `execution_id`: Foreign key to executions table (optional)
- `data_flow`: Details about data transformations in JSONB format
- `created_at`: Timestamp when lineage was recorded

## Features

### 1. Pipeline Management
- Create, read, update, and delete pipeline definitions
- Store pipeline configurations as structured JSON
- Track pipeline versions and metadata tags

### 2. Execution Tracking
- Record execution history with start/end times
- Track execution status throughout the lifecycle
- Store execution parameters and runtime metrics
- Capture error details for debugging

### 3. Task Monitoring
- Track individual task status within executions
- Record task input and output data
- Store task execution timestamps and errors

### 4. Data Lineage
- Track data flow between sources and destinations
- Record transformation details
- Enable impact analysis and compliance reporting

### 5. High Availability
- Connection pooling for optimal performance
- Transaction support for data consistency
- Proper error handling and rollback mechanisms

## Integration with Orchestration

The metadata store integrates with the orchestration engine through the MetadataService class, which provides:

- Automatic recording of pipeline execution start/end
- Real-time task status updates
- Data lineage tracking
- Execution history queries
- Pipeline registration and management

## Usage Examples

### Initializing the Metadata Service
```python
from datadog_platform.orchestration import MetadataService
from datadog_platform.storage.config import PostgreSQLConfig

config = PostgreSQLConfig(
    host="localhost",
    port=5432,
    database="datadog",
    username="datadog_user",
    password="datadog_pass"
)

metadata_service = MetadataService(config)
await metadata_service.initialize()
```

### Registering a Pipeline
```python
pipeline_id = await metadata_service.register_pipeline(pipeline)
```

### Starting an Execution
```python
execution_context = ExecutionContext(
    pipeline_id=str(pipeline_id),
    parameters={"date": "2023-01-01"}
)

execution_id = await metadata_service.start_execution(execution_context)
```

### Updating Task Status
```python
await metadata_service.update_task_status(
    execution_id=execution_id,
    task_name="extract_data",
    status=ExecutionStatus.SUCCESS
)
```

## Migration Management

The implementation includes proper Alembic migration support:

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description of changes"
```

## Security

- Connection strings are properly constructed with authentication
- SQL injection protection through SQLAlchemy ORM
- Secure credential handling through configuration
- Proper transaction isolation levels

## Performance

- Connection pooling with configurable size
- JSONB fields for flexible data storage
- Proper indexing on frequently queried columns
- Asynchronous operations for high throughput

## Testing

The implementation includes comprehensive testing at multiple levels:
- Unit tests for individual components
- Integration tests for database operations
- Edge case and error handling tests
- Performance considerations for concurrent operations

## Future Enhancements

- Sharding support for large-scale deployments
- Advanced query optimization
- Read replica support for high availability
- Time-series optimizations for execution metrics