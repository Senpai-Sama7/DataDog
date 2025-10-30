"""
Unit tests for connector health monitoring.
"""

import pytest
import asyncio
from datetime import datetime
from datadog_platform.monitoring.health import (
    HealthStatus,
    HealthCheckResult,
    ConnectorHealth,
    ConnectorHealthMonitor,
)
from datadog_platform.core.base import BaseConnector, ConnectorType
from typing import Any, Dict, Optional


class MockConnector(BaseConnector):
    """Mock connector for testing."""

    def __init__(self, config: Dict[str, Any], should_fail: bool = False) -> None:
        super().__init__(config)
        self.should_fail = should_fail
        self.connect_called = False
        self.disconnect_called = False

    async def connect(self) -> None:
        self.connect_called = True
        self._connection = {"connected": True}

    async def disconnect(self) -> None:
        self.disconnect_called = True
        self._connection = None

    async def read(self, query: Optional[str] = None, **kwargs: Any) -> Any:
        return []

    async def write(self, data: Any, **kwargs: Any) -> None:
        pass

    async def validate_connection(self) -> bool:
        if self.should_fail:
            raise Exception("Connection validation failed")
        return self._connection is not None and self._connection.get("connected", False)


class TestHealthCheckResult:
    """Test health check result."""

    def test_health_check_result_creation(self) -> None:
        """Test creating health check result."""
        result = HealthCheckResult(
            connector_name="test",
            connector_type=ConnectorType.POSTGRESQL,
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            latency_ms=50.0,
        )

        assert result.connector_name == "test"
        assert result.connector_type == ConnectorType.POSTGRESQL
        assert result.status == HealthStatus.HEALTHY
        assert result.latency_ms == 50.0
        assert result.error is None

    def test_health_check_result_to_dict(self) -> None:
        """Test converting health check result to dictionary."""
        result = HealthCheckResult(
            connector_name="test",
            connector_type=ConnectorType.MONGODB,
            status=HealthStatus.DEGRADED,
            timestamp=datetime.now(),
            latency_ms=100.0,
            error="Slow response",
        )

        result_dict = result.to_dict()
        assert result_dict["connector_name"] == "test"
        assert result_dict["status"] == HealthStatus.DEGRADED
        assert result_dict["latency_ms"] == 100.0
        assert result_dict["error"] == "Slow response"


class TestConnectorHealth:
    """Test connector health metrics."""

    def test_connector_health_initialization(self) -> None:
        """Test connector health initialization."""
        health = ConnectorHealth(connector_name="test", connector_type=ConnectorType.REDIS)

        assert health.connector_name == "test"
        assert health.connector_type == ConnectorType.REDIS
        assert health.current_status == HealthStatus.UNKNOWN
        assert health.total_checks == 0
        assert health.uptime_percentage == 100.0

    def test_update_from_successful_result(self) -> None:
        """Test updating health from successful check."""
        health = ConnectorHealth(connector_name="test", connector_type=ConnectorType.S3)

        result = HealthCheckResult(
            connector_name="test",
            connector_type=ConnectorType.S3,
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            latency_ms=25.0,
        )

        health.update_from_result(result)

        assert health.current_status == HealthStatus.HEALTHY
        assert health.total_checks == 1
        assert health.total_successes == 1
        assert health.total_failures == 0
        assert health.consecutive_successes == 1
        assert health.consecutive_failures == 0
        assert health.average_latency_ms == 25.0
        assert health.uptime_percentage == 100.0

    def test_update_from_failed_result(self) -> None:
        """Test updating health from failed check."""
        health = ConnectorHealth(connector_name="test", connector_type=ConnectorType.KAFKA)

        result = HealthCheckResult(
            connector_name="test",
            connector_type=ConnectorType.KAFKA,
            status=HealthStatus.UNHEALTHY,
            timestamp=datetime.now(),
            latency_ms=200.0,
            error="Connection timeout",
        )

        health.update_from_result(result)

        assert health.current_status == HealthStatus.DEGRADED  # First failure is degraded
        assert health.total_checks == 1
        assert health.total_successes == 0
        assert health.total_failures == 1
        assert health.consecutive_failures == 1
        assert health.last_error == "Connection timeout"
        assert health.uptime_percentage == 0.0

    def test_consecutive_failures_mark_unhealthy(self) -> None:
        """Test that consecutive failures mark connector as unhealthy."""
        health = ConnectorHealth(connector_name="test", connector_type=ConnectorType.MYSQL)

        # Simulate 5 consecutive failures
        for i in range(5):
            result = HealthCheckResult(
                connector_name="test",
                connector_type=ConnectorType.MYSQL,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.now(),
                latency_ms=100.0,
                error=f"Failure {i+1}",
            )
            health.update_from_result(result)

        assert health.current_status == HealthStatus.UNHEALTHY
        assert health.consecutive_failures == 5
        assert health.total_failures == 5

    def test_health_recovery_resets_consecutive_failures(self) -> None:
        """Test that successful check resets consecutive failures."""
        health = ConnectorHealth(connector_name="test", connector_type=ConnectorType.CASSANDRA)

        # Fail twice
        for _ in range(2):
            health.update_from_result(
                HealthCheckResult(
                    connector_name="test",
                    connector_type=ConnectorType.CASSANDRA,
                    status=HealthStatus.UNHEALTHY,
                    timestamp=datetime.now(),
                    latency_ms=100.0,
                    error="Failure",
                )
            )

        assert health.consecutive_failures == 2

        # Then succeed
        health.update_from_result(
            HealthCheckResult(
                connector_name="test",
                connector_type=ConnectorType.CASSANDRA,
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                latency_ms=25.0,
            )
        )

        assert health.current_status == HealthStatus.HEALTHY
        assert health.consecutive_failures == 0
        assert health.consecutive_successes == 1


class TestConnectorHealthMonitor:
    """Test connector health monitor."""

    @pytest.mark.asyncio
    async def test_register_connector(self) -> None:
        """Test registering a connector for monitoring."""
        monitor = ConnectorHealthMonitor()
        connector = MockConnector({"test": "config"})

        monitor.register_connector("test", connector, ConnectorType.POSTGRESQL)

        assert "test" in monitor.connectors
        assert "test" in monitor.health_metrics
        assert monitor.health_metrics["test"].connector_type == ConnectorType.POSTGRESQL

    @pytest.mark.asyncio
    async def test_unregister_connector(self) -> None:
        """Test unregistering a connector."""
        monitor = ConnectorHealthMonitor()
        connector = MockConnector({"test": "config"})

        monitor.register_connector("test", connector, ConnectorType.MONGODB)
        monitor.unregister_connector("test")

        assert "test" not in monitor.connectors
        # Health metrics remain for historical data
        assert "test" in monitor.health_metrics

    @pytest.mark.asyncio
    async def test_check_healthy_connector(self) -> None:
        """Test health check on healthy connector."""
        monitor = ConnectorHealthMonitor()
        connector = MockConnector({"test": "config"})
        await connector.connect()

        monitor.register_connector("test", connector, ConnectorType.REDIS)

        result = await monitor.check_connector_health("test")

        assert result.status == HealthStatus.HEALTHY
        assert result.connector_name == "test"
        assert result.error is None
        assert result.latency_ms > 0

    @pytest.mark.asyncio
    async def test_check_unhealthy_connector(self) -> None:
        """Test health check on unhealthy connector."""
        monitor = ConnectorHealthMonitor()
        connector = MockConnector({"test": "config"}, should_fail=True)
        await connector.connect()

        monitor.register_connector("test", connector, ConnectorType.S3)

        result = await monitor.check_connector_health("test")

        assert result.status == HealthStatus.UNHEALTHY
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_check_all_connectors(self) -> None:
        """Test checking all registered connectors."""
        monitor = ConnectorHealthMonitor()

        # Register multiple connectors
        for i in range(3):
            connector = MockConnector({"test": f"config{i}"})
            await connector.connect()
            monitor.register_connector(f"connector{i}", connector, ConnectorType.KAFKA)

        results = await monitor.check_all_connectors()

        assert len(results) == 3
        assert all(r.status == HealthStatus.HEALTHY for r in results.values())

    @pytest.mark.asyncio
    async def test_get_health_status(self) -> None:
        """Test getting health status for a connector."""
        monitor = ConnectorHealthMonitor()
        connector = MockConnector({"test": "config"})
        await connector.connect()

        monitor.register_connector("test", connector, ConnectorType.GCS)
        await monitor.check_all_connectors()

        health = monitor.get_health_status("test")

        assert health is not None
        assert health.connector_name == "test"
        assert health.current_status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_get_unhealthy_connectors(self) -> None:
        """Test getting list of unhealthy connectors."""
        monitor = ConnectorHealthMonitor()

        # Register healthy connector
        healthy_connector = MockConnector({"test": "healthy"})
        await healthy_connector.connect()
        monitor.register_connector("healthy", healthy_connector, ConnectorType.POSTGRESQL)

        # Register unhealthy connector
        unhealthy_connector = MockConnector({"test": "unhealthy"}, should_fail=True)
        await unhealthy_connector.connect()
        monitor.register_connector("unhealthy", unhealthy_connector, ConnectorType.MONGODB)

        # Check all connectors multiple times to trigger unhealthy status
        for _ in range(5):
            await monitor.check_all_connectors()

        unhealthy = monitor.get_unhealthy_connectors()

        assert "unhealthy" in unhealthy
        assert "healthy" not in unhealthy

    @pytest.mark.asyncio
    async def test_get_summary(self) -> None:
        """Test getting health summary."""
        monitor = ConnectorHealthMonitor()

        # Register connectors with different health states
        healthy_connector = MockConnector({"test": "healthy"})
        await healthy_connector.connect()
        monitor.register_connector("healthy", healthy_connector, ConnectorType.REDIS)

        unhealthy_connector = MockConnector({"test": "unhealthy"}, should_fail=True)
        await unhealthy_connector.connect()
        monitor.register_connector("unhealthy", unhealthy_connector, ConnectorType.S3)

        # Check all connectors
        for _ in range(5):
            await monitor.check_all_connectors()

        summary = monitor.get_summary()

        assert summary["total_connectors"] == 2
        assert summary["healthy_count"] == 1
        assert summary["unhealthy_count"] == 1
        assert summary["overall_health_percentage"] == 50.0

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self) -> None:
        """Test starting and stopping background monitoring."""
        monitor = ConnectorHealthMonitor(check_interval_seconds=0.1)
        connector = MockConnector({"test": "config"})
        await connector.connect()

        monitor.register_connector("test", connector, ConnectorType.KAFKA)

        # Start monitoring
        await monitor.start()
        assert monitor.is_running is True
        assert monitor.monitoring_task is not None

        # Let it run for a bit
        await asyncio.sleep(0.3)

        # Stop monitoring
        await monitor.stop()
        assert monitor.is_running is False
        assert monitor.monitoring_task is None

        # Verify health was checked
        health = monitor.get_health_status("test")
        assert health.total_checks > 0
