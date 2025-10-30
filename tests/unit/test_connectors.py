"""
Unit tests for connectors.
"""

import pytest

from datadog_platform.connectors.factory import ConnectorFactory
from datadog_platform.core.base import ConnectorType


class TestConnectorFactory:
    """Test cases for ConnectorFactory."""

    def test_list_connectors(self) -> None:
        """Test listing available connectors."""
        connectors = ConnectorFactory.list_connectors()

        assert len(connectors) > 0
        assert ConnectorType.POSTGRESQL in connectors
        assert ConnectorType.FILE_SYSTEM in connectors
        assert ConnectorType.REST_API in connectors

    def test_create_sql_connector(self) -> None:
        """Test creating SQL connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.POSTGRESQL,
            {"host": "localhost", "database": "testdb", "username": "user", "password": "pass"},
        )

        assert connector is not None
        assert connector.config["host"] == "localhost"

    def test_create_file_connector(self) -> None:
        """Test creating file connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.FILE_SYSTEM, {"path": "/tmp/data", "format": "json"}
        )

        assert connector is not None
        assert connector.config["path"] == "/tmp/data"

    def test_create_rest_connector(self) -> None:
        """Test creating REST API connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.REST_API, {"url": "https://api.example.com"}
        )

        assert connector is not None
        assert connector.config["url"] == "https://api.example.com"

    def test_unknown_connector_type_raises_error(self) -> None:
        """Test that unknown connector type raises error."""
        with pytest.raises(ValueError):
            # Create a mock enum value that doesn't exist
            ConnectorFactory.create_connector("unknown_connector", {})  # type: ignore


@pytest.mark.asyncio
class TestSQLConnector:
    """Test cases for SQL connector."""

    async def test_connect_disconnect(self) -> None:
        """Test connecting and disconnecting."""
        from datadog_platform.connectors.sql_connector import SQLConnector

        connector = SQLConnector({"host": "localhost", "database": "testdb"})

        await connector.connect()
        assert connector._connection is not None

        await connector.disconnect()
        assert connector._connection is None

    async def test_context_manager(self) -> None:
        """Test using connector as context manager."""
        from datadog_platform.connectors.sql_connector import SQLConnector

        connector = SQLConnector({"host": "localhost", "database": "testdb"})

        async with connector:
            assert connector._connection is not None

        assert connector._connection is None

    async def test_read_data(self) -> None:
        """Test reading data."""
        from datadog_platform.connectors.sql_connector import SQLConnector

        connector = SQLConnector({"host": "localhost", "database": "testdb", "table": "users"})

        async with connector:
            data = await connector.read()
            assert isinstance(data, list)
            assert len(data) > 0


@pytest.mark.asyncio
class TestFileConnector:
    """Test cases for file connector."""

    async def test_connect_disconnect(self) -> None:
        """Test connecting and disconnecting."""
        from datadog_platform.connectors.file_connector import FileConnector

        connector = FileConnector({"path": "/tmp", "format": "json"})

        await connector.connect()
        assert connector._connection is not None

        await connector.disconnect()
        assert connector._connection is None


@pytest.mark.asyncio
class TestRESTConnector:
    """Test cases for REST API connector."""

    async def test_connect_disconnect(self) -> None:
        """Test connecting and disconnecting."""
        from datadog_platform.connectors.rest_connector import RESTConnector

        connector = RESTConnector({"url": "https://api.example.com"})

        await connector.connect()
        assert connector._connection is not None

        await connector.disconnect()
        assert connector._connection is None

    async def test_build_url(self) -> None:
        """Test URL building."""
        from datadog_platform.connectors.rest_connector import RESTConnector

        connector = RESTConnector({"url": "https://api.example.com"})

        url = connector._build_url("/users")
        assert url == "https://api.example.com/users"

        url = connector._build_url("users")
        assert url == "https://api.example.com/users"
