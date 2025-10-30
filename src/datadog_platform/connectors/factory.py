"""
Factory for creating connector instances.
"""

from typing import Any, Dict

from datadog_platform.core.base import BaseConnector, ConnectorType


class ConnectorFactory:
    """
    Factory for creating connector instances based on type.
    
    Implements the factory pattern for extensible connector creation.
    """
    
    _connectors: Dict[ConnectorType, type[BaseConnector]] = {}
    
    @classmethod
    def register_connector(
        cls,
        connector_type: ConnectorType,
        connector_class: type[BaseConnector]
    ) -> None:
        """
        Register a connector class for a given type.
        
        Args:
            connector_type: Type of connector
            connector_class: Connector class to register
        """
        cls._connectors[connector_type] = connector_class
    
    @classmethod
    def create_connector(
        cls,
        connector_type: ConnectorType,
        config: Dict[str, Any]
    ) -> BaseConnector:
        """
        Create a connector instance.
        
        Args:
            connector_type: Type of connector to create
            config: Configuration for the connector
            
        Returns:
            BaseConnector instance
            
        Raises:
            ValueError: If connector type is not registered
        """
        connector_class = cls._connectors.get(connector_type)
        
        if not connector_class:
            raise ValueError(f"Unknown connector type: {connector_type}")
        
        return connector_class(config)
    
    @classmethod
    def list_connectors(cls) -> list[ConnectorType]:
        """
        List all registered connector types.
        
        Returns:
            list: Registered connector types
        """
        return list(cls._connectors.keys())


# Auto-register built-in connectors
def _register_builtin_connectors() -> None:
    """Register built-in connector types."""
    from datadog_platform.connectors.sql_connector import SQLConnector
    from datadog_platform.connectors.file_connector import FileConnector
    from datadog_platform.connectors.rest_connector import RESTConnector
    
    ConnectorFactory.register_connector(ConnectorType.POSTGRESQL, SQLConnector)
    ConnectorFactory.register_connector(ConnectorType.MYSQL, SQLConnector)
    ConnectorFactory.register_connector(ConnectorType.FILE_SYSTEM, FileConnector)
    ConnectorFactory.register_connector(ConnectorType.REST_API, RESTConnector)


# Register connectors on module import
_register_builtin_connectors()
