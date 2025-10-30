"""
Connector health monitoring system for the DataDog platform.

Provides real-time health checks, status tracking, and alerting for
all data source connectors with automatic recovery detection.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass, field
import logging

from datadog_platform.core.base import BaseConnector, ConnectorType

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status for connectors."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    connector_name: str
    connector_type: ConnectorType
    status: HealthStatus
    timestamp: datetime
    latency_ms: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "connector_name": self.connector_name,
            "connector_type": self.connector_type,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "latency_ms": self.latency_ms,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class ConnectorHealth:
    """Health metrics for a connector."""

    connector_name: str
    connector_type: ConnectorType
    current_status: HealthStatus = HealthStatus.UNKNOWN
    last_check_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    total_checks: int = 0
    total_failures: int = 0
    total_successes: int = 0
    average_latency_ms: float = 0.0
    last_error: Optional[str] = None
    uptime_percentage: float = 100.0
    check_history: List[HealthCheckResult] = field(default_factory=list)

    def update_from_result(self, result: HealthCheckResult, max_history: int = 100) -> None:
        """
        Update health metrics from check result.

        Args:
            result: Health check result
            max_history: Maximum number of results to keep in history
        """
        self.last_check_time = result.timestamp
        self.total_checks += 1

        # Update status and counters
        if result.status == HealthStatus.HEALTHY:
            self.total_successes += 1
            self.consecutive_successes += 1
            self.consecutive_failures = 0
            self.current_status = HealthStatus.HEALTHY
        else:
            self.total_failures += 1
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            self.last_error = result.error

            # Determine degraded vs unhealthy
            if self.consecutive_failures >= 5:
                self.current_status = HealthStatus.UNHEALTHY
            else:
                self.current_status = HealthStatus.DEGRADED

        # Update latency
        total_latency = self.average_latency_ms * (self.total_checks - 1)
        self.average_latency_ms = (total_latency + result.latency_ms) / self.total_checks

        # Update uptime percentage
        self.uptime_percentage = (
            (self.total_successes / self.total_checks) * 100 if self.total_checks > 0 else 0.0
        )

        # Add to history (keep last N results)
        self.check_history.append(result)
        if len(self.check_history) > max_history:
            self.check_history.pop(0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "connector_name": self.connector_name,
            "connector_type": self.connector_type,
            "current_status": self.current_status,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "total_checks": self.total_checks,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "average_latency_ms": self.average_latency_ms,
            "last_error": self.last_error,
            "uptime_percentage": self.uptime_percentage,
        }


class ConnectorHealthMonitor:
    """
    Monitor health of data source connectors.

    Performs periodic health checks, tracks metrics, and provides
    real-time status dashboards for all registered connectors.
    """

    def __init__(
        self,
        check_interval_seconds: int = 60,
        unhealthy_threshold: int = 3,
        healthy_threshold: int = 2,
    ) -> None:
        """
        Initialize health monitor.

        Args:
            check_interval_seconds: Seconds between health checks
            unhealthy_threshold: Consecutive failures to mark unhealthy
            healthy_threshold: Consecutive successes to mark healthy
        """
        self.check_interval_seconds = check_interval_seconds
        self.unhealthy_threshold = unhealthy_threshold
        self.healthy_threshold = healthy_threshold

        self.connectors: Dict[str, BaseConnector] = {}
        self.health_metrics: Dict[str, ConnectorHealth] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False

    def register_connector(
        self, name: str, connector: BaseConnector, connector_type: ConnectorType
    ) -> None:
        """
        Register a connector for health monitoring.

        Args:
            name: Unique connector name
            connector: Connector instance
            connector_type: Type of connector
        """
        self.connectors[name] = connector
        self.health_metrics[name] = ConnectorHealth(
            connector_name=name,
            connector_type=connector_type,
        )
        logger.info(f"Registered connector '{name}' for health monitoring")

    def unregister_connector(self, name: str) -> None:
        """
        Unregister a connector from monitoring.

        Args:
            name: Connector name to unregister
        """
        if name in self.connectors:
            del self.connectors[name]
            logger.info(f"Unregistered connector '{name}' from health monitoring")

    async def check_connector_health(self, name: str) -> HealthCheckResult:
        """
        Perform health check on a connector.

        Args:
            name: Connector name

        Returns:
            Health check result
        """
        connector = self.connectors.get(name)
        if not connector:
            return HealthCheckResult(
                connector_name=name,
                connector_type=ConnectorType.CUSTOM,
                status=HealthStatus.UNKNOWN,
                timestamp=datetime.now(timezone.utc),
                latency_ms=0.0,
                error="Connector not found",
            )

        health_metrics = self.health_metrics[name]
        start_time = time.time()

        try:
            # Attempt to validate connection
            is_valid = await asyncio.wait_for(
                connector.validate_connection(), timeout=10.0  # 10 second timeout
            )

            latency_ms = (time.time() - start_time) * 1000

            if is_valid:
                return HealthCheckResult(
                    connector_name=name,
                    connector_type=health_metrics.connector_type,
                    status=HealthStatus.HEALTHY,
                    timestamp=datetime.now(timezone.utc),
                    latency_ms=latency_ms,
                )
            else:
                return HealthCheckResult(
                    connector_name=name,
                    connector_type=health_metrics.connector_type,
                    status=HealthStatus.UNHEALTHY,
                    timestamp=datetime.now(timezone.utc),
                    latency_ms=latency_ms,
                    error="Connection validation failed",
                )

        except asyncio.TimeoutError:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                connector_name=name,
                connector_type=health_metrics.connector_type,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.now(timezone.utc),
                latency_ms=latency_ms,
                error="Health check timeout",
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                connector_name=name,
                connector_type=health_metrics.connector_type,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.now(timezone.utc),
                latency_ms=latency_ms,
                error=str(e),
            )

    async def check_all_connectors(self) -> Dict[str, HealthCheckResult]:
        """
        Check health of all registered connectors.

        Returns:
            Dictionary mapping connector names to check results
        """
        results = {}

        # Run checks concurrently
        tasks = {name: self.check_connector_health(name) for name in self.connectors.keys()}

        completed = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for name, result in zip(tasks.keys(), completed):
            if isinstance(result, Exception):
                logger.error(f"Health check failed for '{name}': {result}")
                result = HealthCheckResult(
                    connector_name=name,
                    connector_type=self.health_metrics[name].connector_type,
                    status=HealthStatus.UNHEALTHY,
                    timestamp=datetime.now(timezone.utc),
                    latency_ms=0.0,
                    error=str(result),
                )
    
            results[name] = result
            # Update health metrics for both success and failure cases
            self.health_metrics[name].update_from_result(result)

        return results

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        logger.info("Starting connector health monitoring loop")

        while self.is_running:
            try:
                await self.check_all_connectors()
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval_seconds)

        logger.info("Stopped connector health monitoring loop")

    async def start(self) -> None:
        """Start background health monitoring."""
        if self.is_running:
            logger.warning("Health monitor is already running")
            return

        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started connector health monitoring")

    async def stop(self) -> None:
        """Stop background health monitoring."""
        if not self.is_running:
            return

        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                # Expected when cancelling the monitoring task; safe to ignore.
                pass
            self.monitoring_task = None

        logger.info("Stopped connector health monitoring")

    def get_health_status(self, name: str) -> Optional[ConnectorHealth]:
        """
        Get health status for a connector.

        Args:
            name: Connector name

        Returns:
            Connector health metrics or None if not found
        """
        return self.health_metrics.get(name)

    def get_all_health_status(self) -> Dict[str, ConnectorHealth]:
        """
        Get health status for all connectors.

        Returns:
            Dictionary mapping connector names to health metrics
        """
        return self.health_metrics.copy()

    def get_unhealthy_connectors(self) -> List[str]:
        """
        Get list of unhealthy connector names.

        Returns:
            List of connector names with unhealthy status
        """
        return [
            name
            for name, health in self.health_metrics.items()
            if health.current_status == HealthStatus.UNHEALTHY
        ]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all connector health.

        Returns:
            Summary statistics
        """
        total = len(self.health_metrics)
        healthy = sum(
            1 for h in self.health_metrics.values() if h.current_status == HealthStatus.HEALTHY
        )
        degraded = sum(
            1 for h in self.health_metrics.values() if h.current_status == HealthStatus.DEGRADED
        )
        unhealthy = sum(
            1 for h in self.health_metrics.values() if h.current_status == HealthStatus.UNHEALTHY
        )
        unknown = sum(
            1 for h in self.health_metrics.values() if h.current_status == HealthStatus.UNKNOWN
        )

        return {
            "total_connectors": total,
            "healthy_count": healthy,
            "degraded_count": degraded,
            "unhealthy_count": unhealthy,
            "unknown_count": unknown,
            "overall_health_percentage": (healthy / total * 100) if total > 0 else 0.0,
        }
