# DataDog Platform User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
4. [Creating Pipelines](#creating-pipelines)
5. [Data Sources](#data-sources)
6. [Transformations](#transformations)
7. [Execution](#execution)
8. [Monitoring](#monitoring)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Introduction

DataDog Platform is a universal data orchestration system designed to simplify complex data workflows. It provides:

- **Unified Interface**: Work with multiple data sources through a single API
- **Flexible Workflows**: Create complex data pipelines with ease
- **Scalable Execution**: From local development to distributed production
- **Rich Monitoring**: Track pipeline health and performance

## Getting Started

### Installation

```bash
# Install from PyPI
pip install datadog-platform

# Or install from source
git clone https://github.com/Senpai-Sama7/DataDog.git
cd DataDog
pip install -e .
```

### Quick Start

Create your first pipeline in 5 minutes:

```python
from datadog_platform import Pipeline, DataSource, Transformation
from datadog_platform.core.base import ConnectorType

# 1. Create a pipeline
pipeline = Pipeline(name="my_first_pipeline")

# 2. Add a data source
source = DataSource(
    name="input_data",
    connector_type=ConnectorType.FILE_SYSTEM,
    connection_config={"path": "./data/input.json"}
)
pipeline.add_source(source)

# 3. Add a transformation
transform = Transformation(
    name="clean_data",
    function_name="filter_nulls",
    parameters={"columns": ["id", "name"]}
)
pipeline.add_transformation(transform)

# 4. Execute
result = pipeline.execute()
print(f"Pipeline completed with status: {result.status}")
```

## Core Concepts

### Pipelines

A **Pipeline** is a directed acyclic graph (DAG) of tasks that process data from sources through transformations to destinations.

**Key Properties:**
- **Name**: Unique identifier for the pipeline
- **Processing Mode**: Batch, streaming, or micro-batch
- **Sources**: Input data sources
- **Transformations**: Data processing steps
- **Schedule**: When to run (cron expression)

### Data Sources

A **DataSource** represents an input to your pipeline. It encapsulates connection details and query logic.

**Supported Types:**
- SQL databases (PostgreSQL, MySQL)
- NoSQL stores (MongoDB, Redis)
- File systems (Local, S3, HDFS)
- REST APIs
- Message queues (Kafka, RabbitMQ)

### Transformations

A **Transformation** applies a specific operation to your data.

**Built-in Transformations:**
- `filter_nulls`: Remove rows with null values
- `select_columns`: Select specific columns
- `rename_columns`: Rename columns
- `aggregate`: Group and aggregate data
- `join`: Join with another dataset
- `deduplicate`: Remove duplicate rows

### Execution Context

An **ExecutionContext** tracks the state of a pipeline run:
- Execution ID
- Start/end times
- Status (pending, running, success, failed)
- Metrics (rows processed, duration, etc.)
- Error messages

## Creating Pipelines

### Method 1: Python API

```python
from datadog_platform import Pipeline, DataSource, Transformation
from datadog_platform.core.base import ConnectorType, ProcessingMode

pipeline = Pipeline(
    name="etl_pipeline",
    description="ETL pipeline for customer data",
    processing_mode=ProcessingMode.BATCH,
    max_parallel_tasks=4
)

# Add multiple sources
db_source = DataSource(
    name="postgres_db",
    connector_type=ConnectorType.POSTGRESQL,
    connection_config={
        "host": "localhost",
        "database": "customers",
        "table": "orders"
    }
)
pipeline.add_source(db_source)

# Add transformations in order
pipeline.add_transformation(Transformation(
    name="filter_active",
    function_name="filter",
    parameters={"condition": "status = 'active'"}
))

pipeline.add_transformation(Transformation(
    name="aggregate_sales",
    function_name="aggregate",
    parameters={
        "group_by": ["customer_id"],
        "aggregations": {"total_sales": "sum(amount)"}
    }
))
```

### Method 2: YAML Configuration

Create `pipeline.yaml`:

```yaml
name: etl_pipeline
description: ETL pipeline for customer data
processing_mode: batch
max_parallel_tasks: 4

sources:
  - name: postgres_db
    connector_type: postgresql
    connection_config:
      host: localhost
      database: customers
      table: orders

transformations:
  - name: filter_active
    function_name: filter
    parameters:
      condition: "status = 'active'"
    order: 1
    
  - name: aggregate_sales
    function_name: aggregate
    parameters:
      group_by: [customer_id]
      aggregations:
        total_sales: sum(amount)
    order: 2

schedule: "0 */6 * * *"  # Every 6 hours
enabled: true
```

Load and execute:

```python
import yaml
from datadog_platform import Pipeline

with open("pipeline.yaml") as f:
    config = yaml.safe_load(f)

pipeline = Pipeline(**config)
pipeline.execute()
```

### Method 3: CLI

```bash
# Create from config file
datadog pipeline create --config pipeline.yaml

# Execute
datadog pipeline run etl_pipeline
```

## Data Sources

### SQL Databases

```python
from datadog_platform.core.data_source import DataSource
from datadog_platform.core.base import ConnectorType

# PostgreSQL
postgres_source = DataSource(
    name="postgres_db",
    connector_type=ConnectorType.POSTGRESQL,
    connection_config={
        "host": "localhost",
        "port": 5432,
        "database": "analytics",
        "username": "user",
        "password": "pass",
        "table": "events"
    },
    # Optional: custom query
    query="""
        SELECT * FROM events 
        WHERE date >= %(start_date)s 
        AND date < %(end_date)s
    """
)

# MySQL
mysql_source = DataSource(
    name="mysql_db",
    connector_type=ConnectorType.MYSQL,
    connection_config={
        "host": "localhost",
        "database": "sales",
        "table": "transactions"
    }
)
```

### File Systems

```python
# JSON files
json_source = DataSource(
    name="json_files",
    connector_type=ConnectorType.FILE_SYSTEM,
    connection_config={
        "path": "/data/input",
        "format": "json",
        "pattern": "*.json"
    }
)

# CSV files
csv_source = DataSource(
    name="csv_files",
    connector_type=ConnectorType.FILE_SYSTEM,
    connection_config={
        "path": "/data/input.csv",
        "format": "csv",
        "delimiter": ",",
        "header": True
    }
)

# Parquet files
parquet_source = DataSource(
    name="parquet_files",
    connector_type=ConnectorType.FILE_SYSTEM,
    connection_config={
        "path": "/data/input.parquet",
        "format": "parquet"
    }
)
```

### REST APIs

```python
api_source = DataSource(
    name="rest_api",
    connector_type=ConnectorType.REST_API,
    connection_config={
        "url": "https://api.example.com",
        "endpoint": "/users",
        "method": "GET",
        "headers": {
            "Authorization": "Bearer token",
            "Content-Type": "application/json"
        },
        "params": {
            "page": 1,
            "per_page": 100
        }
    }
)
```

## Transformations

### Filtering

```python
# Filter null values
filter_nulls = Transformation(
    name="remove_nulls",
    function_name="filter_nulls",
    parameters={
        "columns": ["id", "email", "name"]
    }
)

# Custom filter
custom_filter = Transformation(
    name="filter_recent",
    function_name="filter",
    parameters={
        "condition": "date >= '2025-01-01'"
    }
)
```

### Selection and Projection

```python
# Select specific columns
select = Transformation(
    name="select_cols",
    function_name="select_columns",
    parameters={
        "columns": ["id", "name", "email", "created_at"]
    }
)

# Rename columns
rename = Transformation(
    name="rename_cols",
    function_name="rename_columns",
    parameters={
        "mapping": {
            "old_name": "new_name",
            "user_id": "customer_id"
        }
    }
)
```

### Aggregation

```python
aggregate = Transformation(
    name="aggregate_data",
    function_name="aggregate",
    parameters={
        "group_by": ["customer_id", "product_category"],
        "aggregations": {
            "total_sales": "sum(amount)",
            "order_count": "count(*)",
            "avg_order": "avg(amount)",
            "max_order": "max(amount)"
        }
    }
)
```

### Joining

```python
join = Transformation(
    name="join_customers",
    function_name="join",
    parameters={
        "right_data": "customers",
        "on": "customer_id",
        "how": "left"  # left, right, inner, outer
    }
)
```

### Data Quality

```python
# Deduplicate
dedup = Transformation(
    name="remove_duplicates",
    function_name="deduplicate",
    parameters={
        "subset": ["email"],
        "keep": "first"  # first, last
    }
)

# Fill missing values
fill = Transformation(
    name="fill_missing",
    function_name="fill_null",
    parameters={
        "columns": ["status"],
        "value": "unknown"
    }
)

# Type casting
cast = Transformation(
    name="cast_types",
    function_name="cast_types",
    parameters={
        "type_mapping": {
            "amount": "float",
            "quantity": "integer",
            "date": "datetime"
        }
    }
)
```

## Execution

### Synchronous Execution

```python
# Execute and wait for completion
context = pipeline.execute()

if context.status == ExecutionStatus.SUCCESS:
    print(f"Pipeline completed in {context.duration} seconds")
    print(f"Processed {context.metrics.get('rows_processed')} rows")
else:
    print(f"Pipeline failed: {context.error}")
```

### Asynchronous Execution

```python
import asyncio
from datadog_platform.core.executor import LocalExecutor

async def run_pipeline():
    executor = LocalExecutor(max_workers=4)
    context = pipeline.execute(executor=executor)
    
    # Poll for completion
    while context.status == ExecutionStatus.RUNNING:
        await asyncio.sleep(5)
        status = await executor.get_status(context.execution_id)
        print(f"Status: {status}")
    
    return context

# Run
result = asyncio.run(run_pipeline())
```

### Scheduled Execution

```python
# Set schedule in pipeline
pipeline.schedule = "0 */6 * * *"  # Every 6 hours

# Or via CLI
# datadog pipeline create --config pipeline.yaml --schedule "0 */6 * * *"
```

### Parametric Execution

```python
# Execute with parameters
context = pipeline.execute(
    parameters={
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "region": "US"
    }
)

# Access parameters in transformations
# They'll be available in the execution context
```

## Monitoring

### Pipeline Status

```python
# Check execution status
from datadog_platform.core.executor import LocalExecutor

executor = LocalExecutor()
status = await executor.get_status(execution_id)
print(f"Current status: {status}")
```

### Metrics

```python
# Access execution metrics
context = pipeline.execute()
metrics = context.metrics

print(f"Rows processed: {metrics.get('rows_processed', 0)}")
print(f"Duration: {metrics.get('duration_seconds', 0)} seconds")
print(f"Tasks completed: {metrics.get('tasks_completed', 0)}")
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs will show pipeline execution details
pipeline.execute()
```

### Health Checks

```bash
# Via CLI
datadog pipeline status my_pipeline

# Via API
curl http://localhost:8000/api/v1/pipelines/my_pipeline/status
```

## Best Practices

### 1. Pipeline Design

✅ **DO:**
- Keep pipelines focused on a single responsibility
- Use meaningful names for pipelines and tasks
- Document pipeline purpose and dependencies
- Version your pipeline configurations

❌ **DON'T:**
- Create overly complex pipelines
- Mix unrelated data processing
- Hardcode values (use parameters)

### 2. Error Handling

✅ **DO:**
- Set appropriate retry limits
- Use timeouts for long-running tasks
- Log errors with context
- Implement fallback strategies

```python
pipeline = Pipeline(
    name="my_pipeline",
    max_parallel_tasks=4,
    # Will be implemented in future versions
    retry_policy={
        "max_retries": 3,
        "backoff": "exponential",
        "initial_delay": 5
    }
)
```

### 3. Performance

✅ **DO:**
- Use batch processing for large datasets
- Leverage parallel execution
- Filter data early in the pipeline
- Use appropriate data formats (Parquet vs CSV)

❌ **DON'T:**
- Load entire datasets into memory
- Use nested loops in transformations
- Skip data validation

### 4. Security

✅ **DO:**
- Use environment variables for secrets
- Implement least privilege access
- Encrypt sensitive data
- Rotate credentials regularly

```python
import os

source = DataSource(
    name="secure_db",
    connector_type=ConnectorType.POSTGRESQL,
    connection_config={
        "host": os.getenv("DB_HOST"),
        "password": os.getenv("DB_PASSWORD"),
        "ssl": True
    }
)
```

### 5. Testing

✅ **DO:**
- Test pipelines with sample data
- Validate transformations independently
- Use staging environments
- Implement data quality checks

```python
# Test mode execution
context = pipeline.execute(
    parameters={"test_mode": True, "sample_size": 100}
)
```

## Troubleshooting

### Common Issues

#### Pipeline Fails Immediately

**Problem**: Pipeline status goes to FAILED right after starting

**Solutions**:
1. Check data source connectivity
2. Validate pipeline configuration
3. Review logs for error messages
4. Ensure required permissions

```bash
# Check logs
datadog pipeline logs my_pipeline

# Validate configuration
datadog pipeline validate --config pipeline.yaml
```

#### Slow Performance

**Problem**: Pipeline takes too long to execute

**Solutions**:
1. Add indexes to database tables
2. Increase parallel task limit
3. Optimize transformation logic
4. Use data sampling for testing

```python
# Increase parallelism
pipeline.max_parallel_tasks = 8

# Sample data
source.connection_config["limit"] = 1000
```

#### Connection Timeouts

**Problem**: Connector fails with timeout errors

**Solutions**:
1. Increase timeout values
2. Check network connectivity
3. Verify firewall rules
4. Use connection pooling

```python
source.connection_config["timeout"] = 60  # seconds
source.connection_config["pool_size"] = 10
```

#### Memory Issues

**Problem**: Pipeline runs out of memory

**Solutions**:
1. Process data in batches
2. Use streaming mode
3. Reduce parallel tasks
4. Optimize transformations

```python
pipeline.processing_mode = ProcessingMode.STREAMING
pipeline.max_parallel_tasks = 2
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Detailed execution logs
pipeline.execute()
```

### Getting Help

- **Documentation**: https://datadog-platform.readthedocs.io
- **GitHub Issues**: https://github.com/Senpai-Sama7/DataDog/issues
- **Community Forum**: https://github.com/Senpai-Sama7/DataDog/discussions
- **Stack Overflow**: Tag with `datadog-platform`

## Next Steps

- Explore [API Reference](api_reference.md) for detailed API documentation
- Read [Architecture Guide](architecture.md) to understand system design
- Check [Deployment Guide](deployment.md) for production setup
- See [Examples](../examples/) for more pipeline patterns

---

*Last Updated: October 2025*
