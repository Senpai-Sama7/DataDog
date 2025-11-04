"""
Example: Creating and executing a simple data pipeline.
"""

from datadog_platform import DataSource, Pipeline, Transformation
from datadog_platform.core.base import ConnectorType, ProcessingMode
from datadog_platform.core.executor import LocalExecutor


def main() -> None:
    """
    Demonstrate creating and executing a basic ETL pipeline.
    """
    print("DataDog Platform - Simple Pipeline Example\n")
    print("=" * 60)

    # Create a new pipeline
    pipeline = Pipeline(
        name="simple_etl",
        description="Simple ETL pipeline example",
        processing_mode=ProcessingMode.BATCH,
    )

    print(f"Created pipeline: {pipeline.name}")
    print(f"Pipeline ID: {pipeline.pipeline_id}\n")

    # Add a data source
    source = DataSource(
        name="input_files",
        connector_type=ConnectorType.FILE_SYSTEM,
        connection_config={"path": "/tmp/input_data", "format": "json"},
        description="Input data files in JSON format",
    )

    pipeline.add_source(source)
    print(f"Added data source: {source.name}")

    # Add transformations
    transform1 = Transformation(
        name="clean_data",
        function_name="filter_nulls",
        parameters={"columns": ["id", "name", "email"]},
        description="Remove rows with null values",
    )

    pipeline.add_transformation(transform1)
    print(f"Added transformation: {transform1.name}")

    transform2 = Transformation(
        name="deduplicate",
        function_name="deduplicate",
        parameters={"subset": ["id"]},
        description="Remove duplicate records",
    )

    pipeline.add_transformation(transform2)
    print(f"Added transformation: {transform2.name}\n")

    # Validate the pipeline
    print("Validating pipeline...")
    if pipeline.validate_dag():
        print("✓ Pipeline DAG is valid\n")
    else:
        print("✗ Pipeline DAG has errors\n")
        return

    # Display pipeline structure
    print("Pipeline Structure:")
    print(f"  Sources: {len(pipeline.sources)}")
    print(f"  Transformations: {len(pipeline.transformations)}")
    print(f"  Tasks: {len(pipeline.tasks)}\n")

    # Build and display DAG
    dag = pipeline.build_dag()
    print("DAG Structure:")
    for task_id, dependencies in dag.items():
        print(f"  {task_id}: depends on {len(dependencies)} tasks")
    print()

    # Execute the pipeline
    print("Executing pipeline...")
    executor = LocalExecutor(max_workers=2)

    execution_context = pipeline.execute(parameters={"run_date": "2025-10-30"}, executor=executor)

    print("\nExecution completed:")
    print(f"  Execution ID: {execution_context.execution_id}")
    print(f"  Status: {execution_context.status}")
    print(f"  Duration: {execution_context.ended_at - execution_context.started_at}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
