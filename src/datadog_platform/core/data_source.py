"""
DataSource class for representing data sources in pipelines.
"""

from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import ConfigDict, Field

from datadog_platform.core.base import BaseConfig, ConnectorType


class DataSource(BaseConfig):
    """
    Represents a data source in the orchestration platform.

    A data source encapsulates the configuration needed to connect to
    and interact with external data systems.
    """

    model_config = ConfigDict(use_enum_values=True)

    source_id: str = Field(default_factory=lambda: str(uuid4()))
    connector_type: ConnectorType
    connection_config: Dict[str, Any] = Field(default_factory=dict)
    schema_config: Optional[Dict[str, Any]] = Field(default=None, alias="schema")
    query: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True

    def validate_config(self) -> bool:
        """
        Validate the data source configuration.

        Returns:
            bool: True if configuration is valid
        """
        if not self.name:
            return False

        if not self.connector_type:
            return False

        # Connector-specific validation
        required_fields = self._get_required_fields()
        for field in required_fields:
            if field not in self.connection_config:
                return False

        return True

    def _get_required_fields(self) -> list[str]:
        """
        Get required configuration fields for the connector type.

        Returns:
            list: Required field names
        """
        required_map = {
            # SQL databases
            ConnectorType.POSTGRESQL: ["host", "database"],
            ConnectorType.MYSQL: ["host", "database"],
            # NoSQL databases
            ConnectorType.MONGODB: ["database"],
            ConnectorType.REDIS: ["host"],
            ConnectorType.CASSANDRA: ["keyspace"],
            # Message queues
            ConnectorType.KAFKA: ["bootstrap_servers"],
            ConnectorType.RABBITMQ: ["host"],
            ConnectorType.PULSAR: ["service_url"],
            # Cloud storage
            ConnectorType.S3: ["bucket"],
            ConnectorType.GCS: ["bucket"],
            ConnectorType.AZURE_BLOB: ["account_name", "container"],
            # Other
            ConnectorType.REST_API: ["url"],
            ConnectorType.FILE_SYSTEM: ["path"],
            ConnectorType.CUSTOM: [],
        }
        return required_map.get(self.connector_type, [])

    def to_connector_config(self) -> Dict[str, Any]:
        """
        Convert to connector configuration format.

        Returns:
            dict: Configuration for connector initialization
        """
        return {
            "type": self.connector_type,
            "name": self.name,
            "config": self.connection_config,
            "schema": self.schema_config,
            "query": self.query,
            "filters": self.filters,
        }
