"""
Reliability patterns for the DataDog platform.

Implements circuit breaker pattern, retry mechanisms with exponential backoff,
and health monitoring for robust and resilient data pipeline operations.
"""

import asyncio
import logging
import time
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is broken, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation with automatic recovery.

    Prevents cascading failures by temporarily blocking operations to
    a failing service, giving it time to recover.

    Features:
    - Configurable failure threshold and timeout
    - Automatic state transitions
    - Half-open state for testing recovery
    - Failure and success callbacks
    - Metrics tracking
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        half_open_max_calls: int = 3,
        success_threshold: int = 2,
    ) -> None:
        """
        Initialize circuit breaker.

        Args:
            name: Circuit breaker name for logging/metrics
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Time to wait before attempting recovery
            half_open_max_calls: Max calls allowed in half-open state
            success_threshold: Successes needed in half-open to close circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_max_calls = half_open_max_calls
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0

        # Metrics
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.state_changes: list[tuple[datetime, CircuitState]] = []

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new circuit state."""
        if self.state != new_state:
            logger.info(
                f"Circuit breaker '{self.name}' transitioning from {self.state} to {new_state}"
            )
            self.state = new_state
            self.state_changes.append((datetime.now(), new_state))

            if new_state == CircuitState.OPEN:
                self.last_failure_time = time.time()
            elif new_state == CircuitState.HALF_OPEN:
                self.half_open_calls = 0
                self.success_count = 0

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False

        return (time.time() - self.last_failure_time) >= self.timeout_seconds

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception from func
        """
        self.total_calls += 1

        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable. Retry after {self.timeout_seconds}s."
                )

        # Check half-open call limit
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                self._transition_to(CircuitState.OPEN)
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' exceeded half-open call limit"
                )
            self.half_open_calls += 1

        # Execute the function
        try:
            result = (
                await func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            # Preserve exception context for better debugging and forensics
            logger.error(
                f"Circuit breaker '{self.name}' caught exception: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "circuit_breaker": self.name,
                    "state": self.state.value,
                    "failure_count": self.failure_count,
                },
            )
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        self.total_successes += 1
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.total_failures += 1
        self.failure_count += 1

        if self.state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
        elif self.failure_count >= self.failure_threshold:
            self._transition_to(CircuitState.OPEN)

    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.state

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self.state,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "failure_count": self.failure_count,
            "success_rate": (
                self.total_successes / self.total_calls if self.total_calls > 0 else 0.0
            ),
            "last_failure_time": (
                datetime.fromtimestamp(self.last_failure_time) if self.last_failure_time else None
            ),
        }

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        logger.info(f"Manually resetting circuit breaker '{self.name}'")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[tuple[type[Exception], ...]] = None,
    ) -> None:
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff calculation
            jitter: Whether to add random jitter to delays
            retryable_exceptions: Tuple of exception types that should trigger retry
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (Exception,)


class RetryPolicy:
    """
    Retry policy with exponential backoff and jitter.

    Implements robust retry logic with configurable backoff strategies
    to handle transient failures gracefully.
    """

    def __init__(self, config: RetryConfig) -> None:
        """Initialize retry policy with configuration."""
        self.config = config

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self.config.initial_delay * (self.config.exponential_base**attempt)

        # Cap at max delay
        delay = min(delay, self.config.max_delay)

        # Add jitter if enabled
        if self.config.jitter:
            import random

            delay *= random.uniform(0.5, 1.5)

        return delay

    async def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute (can be async or sync)
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func

        Raises:
            Exception: Last exception if all retries failed
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
            except self.config.retryable_exceptions as e:
                last_exception = e

                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.config.max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {self.config.max_attempts} retry attempts failed. " f"Last error: {e}"
                    )

        # If we get here, all attempts failed
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("Retry execution failed without exception")


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[tuple[type[Exception], ...]] = None,
) -> Callable:
    """
    Decorator to add retry logic to async functions.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        retryable_exceptions: Exception types that trigger retry

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            config = RetryConfig(
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                retryable_exceptions=retryable_exceptions,
            )
            policy = RetryPolicy(config)
            return await policy.execute(func, *args, **kwargs)

        return wrapper

    return decorator


def with_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout_seconds: int = 60,
) -> Callable:
    """
    Decorator to add circuit breaker protection to async functions.

    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening circuit
        timeout_seconds: Time before attempting recovery

    Returns:
        Decorated function with circuit breaker
    """
    circuit_breaker = CircuitBreaker(
        name=name,
        failure_threshold=failure_threshold,
        timeout_seconds=timeout_seconds,
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await circuit_breaker.call(func, *args, **kwargs)

        # Attach circuit breaker for inspection
        wrapper.circuit_breaker = circuit_breaker  # type: ignore
        return wrapper

    return decorator
