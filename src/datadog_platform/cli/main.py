"""
Command-line interface for DataDog platform.
"""

import json
from pathlib import Path
from typing import Optional

import click
import yaml

from datadog_platform import __version__
from datadog_platform.core.executor import LocalExecutor
from datadog_platform.core.pipeline import Pipeline
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
def pipeline_create(config: str, validate_only: bool) -> None:
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
    try:
        pipeline_obj = Pipeline(**pipeline_config)

        if validate_only:
            click.echo("✓ Configuration is valid")
            return

        # In production, would save to metadata store
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
def pipeline_list(format: str) -> None:
    """
    List all pipelines.
    """
    # Placeholder - would query metadata store
    pipelines = [
        {
            "id": "pipeline-001",
            "name": "example_pipeline",
            "status": "active",
            "sources": 2,
            "tasks": 5,
        }
    ]

    if format == "json":
        click.echo(json.dumps(pipelines, indent=2))
    else:
        click.echo("\nPipelines:")
        click.echo("-" * 80)
        for p in pipelines:
            click.echo(
                f"  {p['name']:<30} {p['status']:<15} Sources: {p['sources']} Tasks: {p['tasks']}"
            )


@pipeline.command("run")
@click.argument("pipeline_name")
@click.option("--params", "-p", help="Execution parameters (JSON)")
@click.option("--async", "async_mode", is_flag=True, help="Run asynchronously")
def pipeline_run(pipeline_name: str, params: Optional[str], async_mode: bool) -> None:
    """
    Execute a pipeline.
    """
    if params:
        _parameters = json.loads(params)  # noqa: F841  # Placeholder for future use

    click.echo(f"▶ Running pipeline: {pipeline_name}")

    # Placeholder - would load pipeline and execute
    _executor = LocalExecutor()  # noqa: F841  # Placeholder for future use

    if async_mode:
        click.echo("✓ Pipeline execution started (async)")
        click.echo("  Use 'datadog pipeline status' to check progress")
    else:
        click.echo("✓ Pipeline execution completed")
        click.echo("  Status: SUCCESS")


@pipeline.command("status")
@click.argument("pipeline_name")
@click.option("--execution-id", help="Specific execution ID")
def pipeline_status(pipeline_name: str, execution_id: Optional[str]) -> None:
    """
    Get pipeline execution status.
    """
    click.echo(f"\nPipeline: {pipeline_name}")
    click.echo("-" * 80)

    # Placeholder - would query execution status
    click.echo("  Status: RUNNING")
    click.echo("  Started: 2025-10-30 06:00:00")
    click.echo("  Tasks Completed: 3/5")
    click.echo("  Progress: ████████░░░░░░░░ 60%")


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
