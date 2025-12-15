# PostgreSQL Metadata Store for DataDog Platform

## Overview

The PostgreSQL Metadata Store is a critical component of the DataDog Universal Data Orchestration Platform responsible for storing and managing metadata about data pipelines, executions, tasks, and data lineage. This implementation uses PostgreSQL as the backend database with async support for high-performance operations.

## Architecture

The metadata store follows a layered architecture:

- **Configuration Layer**: Manages database connection settings via `PostgreSQLConfig`
- **Connection Layer**: Handles database connections and session management via `DatabaseManager`
- **Model Layer**: Defines SQLAlchemy models for data persistence
- **Service Layer**: Provides the `PostgreSQLMetadataStore` class with high-level operations

## Components

### PostgreSQLConfig

Handles database configuration including:
- Host, port, database name, credentials
- Connection pool settings
- SSL configuration
- SQL logging options

### DatabaseManager

Manages database connections:
- Async engine initialization
- Session management
- Connection pooling
- Graceful closure

### PostgreSQLMetadataStore

Main service class providing metadata operations:
- Pipeline management (create, read, update, delete)
- Execution tracking
- Task monitoring
- Data lineage recording

## Setup and Configuration

### Dependencies

The PostgreSQL metadata store requires:
```bash
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.27.0
alembic>=1.10.0
```

### Database Initialization

```python
from datadog_platform.storage import PostgreSQLConfig, DatabaseManager, PostgreSQLMetadataStore

# Configure database connection
config = PostgreSQLConfig(
    host="localhost",
    port=5432,
    database="datadog",
    username="datadog_user",
    password="datadog_pass"
)

# Initialize components
db_manager = DatabaseManager(config)
await db_manager.initialize()

# Create metadata store
metadata_store = PostgreSQLMetadataStore(db_manager)
await metadata_store.initialize()  # Creates necessary tables
```

## Tables Schema

### Pipelines Table
- Stores pipeline definitions and metadata
- Includes name, description, JSON definition, tags, and status

### Executions Table
- Tracks pipeline execution history
- Contains status, timing, parameters, and metrics

### Tasks Table
- Records individual task executions within pipelines
- Stores task status, timing, and data flow information

### Data Lineage Table
- Captures data flow relationships between sources and destinations
- Enables data governance and impact analysis

## Usage Examples

### Creating a Pipeline
```python
pipeline_id = await metadata_store.create_pipeline(
    name="daily_etl",
    description="Daily ETL pipeline",
    definition={"steps": [...]},
    tags={"env": "production", "team": "data-eng"}
)
```

### Tracking an Execution
```python
from datadog_platform.core.base import ExecutionContext, ExecutionStatus

execution_context = ExecutionContext(
    pipeline_id=str(pipeline_id),
    status=ExecutionStatus.RUNNING
)
execution_id = await metadata_store.create_execution(execution_context)

# Update execution status
await metadata_store.update_execution_status(
    execution_id=execution_id,
    status=ExecutionStatus.SUCCESS
)
```

### Recording Task Execution
```python
task_id = await metadata_store.create_task(
    execution_id=execution_id,
    task_name="extract_data",
    task_type="connector",
    status=ExecutionStatus.PENDING
)

# Update task status
await metadata_store.update_task_status(
    task_id=task_id,
    status=ExecutionStatus.SUCCESS,
    output_data={"rows_processed": 10000}
)
```

### Data Lineage Tracking
```python
await metadata_store.record_data_lineage(
    source_id="source_postgres_table",
    source_type="postgresql",
    destination_id="dest_s3_bucket",
    destination_type="s3",
    pipeline_id=pipeline_id,
    execution_id=execution_id,
    data_flow={"columns": ["id", "name", "email"]}
)
```

## Best Practices

1. **Connection Management**: Always properly initialize and close the DatabaseManager
2. **Error Handling**: Implement proper retry logic and error handling around metadata operations
3. **Performance**: Use connection pooling and appropriate indexing strategies
4. **Security**: Use secure credentials management and SSL connections in production
5. **Monitoring**: Monitor database performance and connection pool metrics

## Testing

The metadata store includes comprehensive unit tests using pytest. To run tests:

```bash
pytest tests/unit/test_postgres_metadata_store.py
```

## Migration Strategy

For production deployments, consider using Alembic for database schema migrations to ensure zero-downtime schema updates.