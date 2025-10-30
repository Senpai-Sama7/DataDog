"""
Unit tests for NoSQL, cloud storage, and message queue connectors.
"""

import pytest
from datadog_platform.connectors.factory import ConnectorFactory
from datadog_platform.core.base import ConnectorType


class TestNoSQLConnectors:
    """Test NoSQL database connectors."""

    @pytest.mark.asyncio
    async def test_mongodb_connector_creation(self) -> None:
        """Test creating MongoDB connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.MONGODB, {"database": "testdb"}
        )
        assert connector is not None
        assert connector.database == "testdb"

    @pytest.mark.asyncio
    async def test_mongodb_connect_disconnect(self) -> None:
        """Test MongoDB connection lifecycle."""
        from datadog_platform.connectors.nosql_connector import MongoDBConnector

        connector = MongoDBConnector({"database": "testdb"})
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None

    @pytest.mark.asyncio
    async def test_redis_connector_creation(self) -> None:
        """Test creating Redis connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.REDIS, {"host": "localhost"}
        )
        assert connector is not None
        assert connector.host == "localhost"

    @pytest.mark.asyncio
    async def test_redis_connect_disconnect(self) -> None:
        """Test Redis connection lifecycle."""
        from datadog_platform.connectors.nosql_connector import RedisConnector

        connector = RedisConnector({"host": "localhost"})
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None

    @pytest.mark.asyncio
    async def test_cassandra_connector_creation(self) -> None:
        """Test creating Cassandra connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.CASSANDRA, {"keyspace": "test_keyspace"}
        )
        assert connector is not None
        assert connector.keyspace == "test_keyspace"

    @pytest.mark.asyncio
    async def test_cassandra_connect_disconnect(self) -> None:
        """Test Cassandra connection lifecycle."""
        from datadog_platform.connectors.nosql_connector import CassandraConnector

        connector = CassandraConnector({"keyspace": "test_keyspace"})
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None


class TestCloudStorageConnectors:
    """Test cloud storage connectors."""

    @pytest.mark.asyncio
    async def test_s3_connector_creation(self) -> None:
        """Test creating S3 connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.S3, {"bucket": "my-bucket"}
        )
        assert connector is not None
        assert connector.bucket == "my-bucket"

    @pytest.mark.asyncio
    async def test_s3_connect_disconnect(self) -> None:
        """Test S3 connection lifecycle."""
        from datadog_platform.connectors.cloud_storage_connector import S3Connector

        connector = S3Connector({"bucket": "my-bucket"})
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None

    @pytest.mark.asyncio
    async def test_gcs_connector_creation(self) -> None:
        """Test creating GCS connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.GCS, {"bucket": "my-bucket"}
        )
        assert connector is not None
        assert connector.bucket == "my-bucket"

    @pytest.mark.asyncio
    async def test_gcs_connect_disconnect(self) -> None:
        """Test GCS connection lifecycle."""
        from datadog_platform.connectors.cloud_storage_connector import GCSConnector

        connector = GCSConnector({"bucket": "my-bucket"})
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None

    @pytest.mark.asyncio
    async def test_azure_blob_connector_creation(self) -> None:
        """Test creating Azure Blob connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.AZURE_BLOB,
            {"account_name": "myaccount", "container": "mycontainer"},
        )
        assert connector is not None
        assert connector.account_name == "myaccount"
        assert connector.container == "mycontainer"

    @pytest.mark.asyncio
    async def test_azure_blob_connect_disconnect(self) -> None:
        """Test Azure Blob connection lifecycle."""
        from datadog_platform.connectors.cloud_storage_connector import (
            AzureBlobConnector,
        )

        connector = AzureBlobConnector(
            {"account_name": "myaccount", "container": "mycontainer"}
        )
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None


class TestMessageQueueConnectors:
    """Test message queue connectors."""

    @pytest.mark.asyncio
    async def test_kafka_connector_creation(self) -> None:
        """Test creating Kafka connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.KAFKA, {"bootstrap_servers": "localhost:9092"}
        )
        assert connector is not None
        assert "localhost:9092" in connector.bootstrap_servers

    @pytest.mark.asyncio
    async def test_kafka_connect_disconnect(self) -> None:
        """Test Kafka connection lifecycle."""
        from datadog_platform.connectors.message_queue_connector import KafkaConnector

        connector = KafkaConnector({"bootstrap_servers": "localhost:9092"})
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None

    @pytest.mark.asyncio
    async def test_rabbitmq_connector_creation(self) -> None:
        """Test creating RabbitMQ connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.RABBITMQ, {"host": "localhost"}
        )
        assert connector is not None
        assert connector.host == "localhost"

    @pytest.mark.asyncio
    async def test_rabbitmq_connect_disconnect(self) -> None:
        """Test RabbitMQ connection lifecycle."""
        from datadog_platform.connectors.message_queue_connector import (
            RabbitMQConnector,
        )

        connector = RabbitMQConnector({"host": "localhost"})
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None

    @pytest.mark.asyncio
    async def test_pulsar_connector_creation(self) -> None:
        """Test creating Pulsar connector."""
        connector = ConnectorFactory.create_connector(
            ConnectorType.PULSAR, {"service_url": "pulsar://localhost:6650"}
        )
        assert connector is not None
        assert connector.service_url == "pulsar://localhost:6650"

    @pytest.mark.asyncio
    async def test_pulsar_connect_disconnect(self) -> None:
        """Test Pulsar connection lifecycle."""
        from datadog_platform.connectors.message_queue_connector import PulsarConnector

        connector = PulsarConnector({"service_url": "pulsar://localhost:6650"})
        await connector.connect()
        assert connector._connection is not None
        assert connector._connection["connected"] is True

        await connector.disconnect()
        assert connector._connection is None


class TestConnectorFactory:
    """Test connector factory with new connectors."""

    def test_list_all_connectors(self) -> None:
        """Test listing all registered connectors."""
        connectors = ConnectorFactory.list_connectors()
        assert len(connectors) >= 12  # All connectors should be registered

        # Verify all new connector types are registered
        assert ConnectorType.MONGODB in connectors
        assert ConnectorType.REDIS in connectors
        assert ConnectorType.CASSANDRA in connectors
        assert ConnectorType.KAFKA in connectors
        assert ConnectorType.RABBITMQ in connectors
        assert ConnectorType.PULSAR in connectors
        assert ConnectorType.S3 in connectors
        assert ConnectorType.GCS in connectors
        assert ConnectorType.AZURE_BLOB in connectors
