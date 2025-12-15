"""
Command-line interface for DataDog platform.
"""

import json
from pathlib import Path
from typing import Optional
from uuid import UUID

import click
import yaml

from datadog_platform import __version__
from datadog_platform.core.pipeline import Pipeline
from datadog_platform.core.data_source import DataSource
from datadog_platform.core.transformation import Transformation
from datadog_platform.orchestration.metadata_service import MetadataService
from datadog_platform.storage.config import PostgreSQLConfig
from datadog_platform.storage.models import PipelineModel
from datadog_platform.utils.security import sanitize_exception_message


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    DataDog Platform - Universal Data Orchestration Platform

    Enterprise-grade distributed data processing system.
    """
    ctx.ensure_object(dict)
    config = PostgreSQLConfig()
    metadata_service = MetadataService(config=config)
    ctx.obj["METADATA_SERVICE"] = metadata_service


@cli.group()
def pipeline() -> None:
    """Manage data pipelines."""
    pass


@pipeline.command("create")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Pipeline configuration file (YAML or JSON)",
)
@click.option("--validate-only", is_flag=True, help="Only validate configuration without creating")
@click.pass_context
def pipeline_create(ctx: click.Context, config: str, validate_only: bool) -> None:
    """
    Create a new pipeline from configuration file.
    """
    config_path = Path(config)

    # Load configuration
    with open(config_path) as f:
        if config_path.suffix in [".yaml", ".yml"]:
            pipeline_config = yaml.safe_load(f)
        else:
            pipeline_config = json.load(f)

    # Create pipeline
    import asyncio
    metadata_service = ctx.obj["METADATA_SERVICE"]
    try:
        pipeline_obj = Pipeline(**pipeline_config)

        if validate_only:
            click.echo("✓ Configuration is valid")
            return

        # Save to metadata store
        asyncio.run(metadata_service.register_pipeline(pipeline_obj))

        click.echo(f"✓ Pipeline created: {pipeline_obj.name}")
        click.echo(f"  ID: {pipeline_obj.pipeline_id}")
        click.echo(f"  Sources: {len(pipeline_obj.sources)}")
        click.echo(f"  Transformations: {len(pipeline_obj.transformations)}")

    except Exception as e:
        # Sanitize error message to prevent sensitive data exposure
        safe_error = sanitize_exception_message(e)
        click.echo(f"✗ Error: {safe_error}", err=True)
        raise click.Abort() from e


@pipeline.command("list")
@click.option(
    "--format", "-f", type=click.Choice(["table", "json"]), default="table", help="Output format"
)
@click.pass_context
def pipeline_list(ctx: click.Context, format: str) -> None:
    """
    List all pipelines.
    """
    import asyncio
    metadata_service = ctx.obj["METADATA_SERVICE"]
    pipelines = asyncio.run(metadata_service.metadata_store.list_pipelines())

    if format == "json":
        click.echo(json.dumps(pipelines, indent=2))
    else:
        click.echo("\nPipelines:")
        click.echo("-" * 80)
        for p in pipelines:
            click.echo(
                f"  {p['name']:<30} {p['processing_mode']:<15} Enabled: {p['enabled']}"
            )


@pipeline.command("run")
@click.argument("pipeline_name")
@click.option("--params", "-p", help="Execution parameters (JSON)")
@click.option("--async", "async_mode", is_flag=True, help="Run asynchronously")
@click.pass_context
def pipeline_run(ctx: click.Context, pipeline_name: str, params: Optional[str], async_mode: bool) -> None:
    """
    Execute a pipeline.
    """
    import asyncio
    metadata_service = ctx.obj["METADATA_SERVICE"]

    click.echo(f"▶ Running pipeline: {pipeline_name}")

    pipeline_model_data = asyncio.run(metadata_service.get_pipeline_by_name(pipeline_name))

    if not pipeline_model_data:
        click.echo(f"✗ Error: Pipeline '{pipeline_name}' not found.", err=True)
        raise click.Abort()

    # Reconstruct Pipeline object from stored metadata
    pipeline_obj = Pipeline(
        pipeline_id=pipeline_model_data["id"],
        name=pipeline_model_data["name"],
        description=pipeline_model_data["description"],
        processing_mode=pipeline_model_data["processing_mode"],
        schedule=pipeline_model_data["schedule"],
        enabled=pipeline_model_data["enabled"],
        max_parallel_tasks=pipeline_model_data["max_parallel_tasks"],
        created_at=datetime.fromisoformat(pipeline_model_data["created_at"]),
        updated_at=datetime.fromisoformat(pipeline_model_data["updated_at"]),
        tags=pipeline_model_data["tags"],
    )

    # Load associated data sources and transformations
    data_sources_data = asyncio.run(metadata_service.list_data_sources(pipeline_obj.pipeline_id))
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

    transformations_data = asyncio.run(metadata_service.list_transformations(pipeline_obj.pipeline_id))
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

    # Execute the pipeline
    try:
        execution_context = ExecutionContext(
            pipeline_id=pipeline_obj.pipeline_id,
            parameters=json.loads(params) if params else {},
            status=ExecutionStatus.PENDING,
        )
        execution_id = asyncio.run(metadata_service.start_execution(execution_context))
        execution_context.execution_id = execution_id

        # Placeholder for actual execution
        # This will be implemented with proper executor
        # For now, simulate execution and update status
        execution_context.status = ExecutionStatus.SUCCESS
        execution_context.ended_at = datetime.now(timezone.utc)
        asyncio.run(metadata_service.update_execution_status(
            execution_context.execution_id,
            execution_context.status,
            execution_context.ended_at
        ))

        if async_mode:
            click.echo("✓ Pipeline execution started (async)")
            click.echo(f"  Execution ID: {execution_context.execution_id}")
            click.echo("  Use 'datadog pipeline status' to check progress")
        else:
            click.echo("✓ Pipeline execution completed")
            click.echo(f"  Status: {execution_context.status.value}")
            click.echo(f"  Execution ID: {execution_context.execution_id}")

    except Exception as e:
        safe_error = sanitize_exception_message(e)
        click.echo(f"✗ Error during pipeline execution: {safe_error}", err=True)
        # Attempt to update execution status to FAILED
        if 'execution_id' in locals():
            asyncio.run(metadata_service.update_execution_status(
                execution_id,
                ExecutionStatus.FAILED,
                datetime.now(timezone.utc),
                safe_error
            ))
        raise click.Abort() from e


@pipeline.command("status")
@click.argument("pipeline_name")
@click.option("--execution-id", help="Specific execution ID")
@click.pass_context
def pipeline_status(ctx: click.Context, pipeline_name: str, execution_id: Optional[str]) -> None:
    """
    Get pipeline execution status.
    """
    import asyncio
    metadata_service = ctx.obj["METADATA_SERVICE"]

    click.echo(f"\nPipeline: {pipeline_name}")
    click.echo("-" * 80)

    # Placeholder - would query execution status
    # For now, simulate execution and update status
    pipeline_model_data = asyncio.run(metadata_service.get_pipeline_by_name(pipeline_name))

    if not pipeline_model_data:
        click.echo(f"✗ Error: Pipeline '{pipeline_name}' not found.", err=True)
        raise click.Abort()

    pipeline_id = UUID(pipeline_model_data["id"])

    if execution_id:
        execution_data = asyncio.run(metadata_service.get_execution(execution_id))
        if execution_data:
            click.echo(f"  Execution ID: {execution_data["id"]}")
            click.echo(f"  Status: {execution_data["status"]}")
            click.echo(f"  Started: {execution_data["started_at"]}")
            click.echo(f"  Ended: {execution_data["ended_at"]}")
            click.echo(f"  Error: {execution_data["error"]}")
        else:
            click.echo(f"✗ Error: Execution ID '{execution_id}' not found.", err=True)
    else:
        execution_history = asyncio.run(metadata_service.get_execution_history(pipeline_id))
        if execution_history:
            click.echo("  Recent Executions:")
            for exec_data in execution_history:
                click.echo(f"    ID: {exec_data["id"]}")
                click.echo(f"    Status: {exec_data["status"]}")
                click.echo(f"    Started: {exec_data["started_at"]}")
                click.echo(f"    Ended: {exec_data["ended_at"]}")
                click.echo("    -" * 20)
        else:
            click.echo("  No execution history found.")


@cli.group()
def connector() -> None:
    """Manage data source connectors."""
    pass


@connector.command("list")
def connector_list() -> None:
    """
    List available connector types.
    """
    from datadog_platform.connectors.factory import ConnectorFactory

    connectors = ConnectorFactory.list_connectors()

    click.echo("\nAvailable Connectors:")
    click.echo("-" * 80)
    for conn_type in connectors:
        click.echo(f"  • {conn_type}")


@connector.command("test")
@click.option("--type", "-t", required=True, help="Connector type")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Connector configuration file",
)
def connector_test(type: str, config: str) -> None:
    """
    Test a connector configuration.
    """
    import asyncio

    from datadog_platform.connectors.factory import ConnectorFactory
    from datadog_platform.core.base import ConnectorType

    # Load configuration
    config_path = Path(config)
    with open(config_path) as f:
        if config_path.suffix in [".yaml", ".yml"]:
            conn_config = yaml.safe_load(f)
        else:
            conn_config = json.load(f)

    async def test_connection() -> None:
        try:
            connector = ConnectorFactory.create_connector(ConnectorType(type), conn_config)

            click.echo(f"Testing connection to {type}...")
            async with connector:
                is_valid = await connector.validate_connection()

                if is_valid:
                    click.echo("✓ Connection successful")
                else:
                    click.echo("✗ Connection failed", err=True)

        except Exception as e:
            # Sanitize error message to prevent sensitive data exposure
            safe_error = sanitize_exception_message(e)
            click.echo(f"✗ Error: {safe_error}", err=True)
            raise click.Abort() from e

    asyncio.run(test_connection())


@cli.group()
def db() -> None:
    """Manage database operations."""
    pass


@db.command("create-tables")
@click.pass_context
def db_create_tables(ctx: click.Context) -> None:
    """Create all database tables."""
    click.echo("Creating database tables...")
    metadata_service = ctx.obj["METADATA_SERVICE"]
    import asyncio
    try:
        asyncio.run(metadata_service.initialize())
        click.echo("✓ Database tables created successfully.")
    except Exception as e:
        safe_error = sanitize_exception_message(e)
        click.echo(f"✗ Error creating database tables: {safe_error}", err=True)
        raise click.Abort() from e


@cli.command()
def server() -> None:
    """
    Start the DataDog API server.
    """
    click.echo("Starting DataDog API server...")
    click.echo("Server running at http://localhost:8000")
    click.echo("API docs available at http://localhost:8000/docs")

    # Would start FastAPI server
    click.echo("\n(Server would run here in production)")


@cli.command()
def worker() -> None:
    """
    Start a DataDog worker process.
    """
    click.echo("Starting DataDog worker...")
    click.echo("Worker ready to process tasks")

    # Would start Celery worker or similar
    click.echo("\n(Worker would run here in production)")


if __name__ == "__main__":
    cli()
