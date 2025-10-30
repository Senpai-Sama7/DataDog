"""
Unit tests for reliability patterns (circuit breaker and retry).
"""

import pytest
import asyncio
from datadog_platform.core.reliability import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError,
    RetryConfig,
    RetryPolicy,
    with_retry,
    with_circuit_breaker,
)


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_starts_closed(self) -> None:
        """Test that circuit breaker starts in closed state."""
        cb = CircuitBreaker("test", failure_threshold=3)
        assert cb.get_state() == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self) -> None:
        """Test that circuit opens after threshold failures."""
        cb = CircuitBreaker("test", failure_threshold=3)

        async def failing_func() -> None:
            raise Exception("Test failure")

        # Should fail 3 times and open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.get_state() == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_rejects_calls_when_open(self) -> None:
        """Test that circuit rejects calls when open."""
        cb = CircuitBreaker("test", failure_threshold=2, timeout_seconds=10)

        async def failing_func() -> None:
            raise Exception("Test failure")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.get_state() == CircuitState.OPEN

        # Next call should be rejected with CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            await cb.call(failing_func)

    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open(self) -> None:
        """Test circuit transitions to half-open after timeout."""
        cb = CircuitBreaker("test", failure_threshold=2, timeout_seconds=0.1)

        async def failing_func() -> None:
            raise Exception("Test failure")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)

        assert cb.get_state() == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.2)

        # Circuit should attempt call and transition to half-open
        with pytest.raises(Exception):
            await cb.call(failing_func)

        # Note: After the failure in half-open, it goes back to OPEN
        assert cb.get_state() == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_closes_after_successful_calls_in_half_open(self) -> None:
        """Test circuit closes after successful calls in half-open state."""
        cb = CircuitBreaker("test", failure_threshold=2, timeout_seconds=0.1, success_threshold=2)
        call_count = [0]

        async def sometimes_failing_func() -> str:
            call_count[0] += 1
            # Fail first 2 times, then succeed
            if call_count[0] <= 2:
                raise Exception("Test failure")
            return "success"

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(sometimes_failing_func)

        assert cb.get_state() == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.2)

        # Now succeed to close circuit
        call_count[0] = 0  # Reset counter

        async def success_func() -> str:
            return "success"

        # First call transitions to half-open
        result = await cb.call(success_func)
        assert result == "success"

        # Second call should close circuit
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.get_state() == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_breaker_metrics(self) -> None:
        """Test circuit breaker metrics tracking."""
        cb = CircuitBreaker("test", failure_threshold=3)

        async def success_func() -> str:
            return "success"

        async def failing_func() -> None:
            raise Exception("Test failure")

        # Record some successes and failures
        await cb.call(success_func)
        await cb.call(success_func)

        with pytest.raises(Exception):
            await cb.call(failing_func)

        metrics = cb.get_metrics()
        assert metrics["name"] == "test"
        assert metrics["total_calls"] == 3
        assert metrics["total_successes"] == 2
        assert metrics["total_failures"] == 1


class TestRetryPolicy:
    """Test retry policy with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_first_attempt(self) -> None:
        """Test that retry succeeds immediately if no failure."""
        config = RetryConfig(max_attempts=3)
        policy = RetryPolicy(config)

        async def success_func() -> str:
            return "success"

        result = await policy.execute(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_failures(self) -> None:
        """Test that retry eventually succeeds after transient failures."""
        config = RetryConfig(max_attempts=3, initial_delay=0.01, jitter=False)
        policy = RetryPolicy(config)
        attempt_count = [0]

        async def sometimes_failing_func() -> str:
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise Exception("Transient failure")
            return "success"

        result = await policy.execute(sometimes_failing_func)
        assert result == "success"
        assert attempt_count[0] == 3

    @pytest.mark.asyncio
    async def test_retry_fails_after_max_attempts(self) -> None:
        """Test that retry gives up after max attempts."""
        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        policy = RetryPolicy(config)

        async def failing_func() -> None:
            raise ValueError("Permanent failure")

        with pytest.raises(ValueError, match="Permanent failure"):
            await policy.execute(failing_func)

    @pytest.mark.asyncio
    async def test_retry_respects_retryable_exceptions(self) -> None:
        """Test that retry only retries specified exceptions."""
        config = RetryConfig(max_attempts=3, initial_delay=0.01, retryable_exceptions=(ValueError,))
        policy = RetryPolicy(config)

        async def wrong_exception_func() -> None:
            raise TypeError("Not retryable")

        # Should fail immediately, not retry
        with pytest.raises(TypeError):
            await policy.execute(wrong_exception_func)

    @pytest.mark.asyncio
    async def test_retry_delay_increases_exponentially(self) -> None:
        """Test that retry delay increases exponentially."""
        config = RetryConfig(max_attempts=3, initial_delay=0.1, exponential_base=2.0, jitter=False)
        policy = RetryPolicy(config)

        delays = []
        for attempt in range(3):
            delay = policy._calculate_delay(attempt)
            delays.append(delay)

        # Delays should be: 0.1, 0.2, 0.4
        assert delays[0] == pytest.approx(0.1, rel=0.01)
        assert delays[1] == pytest.approx(0.2, rel=0.01)
        assert delays[2] == pytest.approx(0.4, rel=0.01)

    @pytest.mark.asyncio
    async def test_retry_decorator(self) -> None:
        """Test retry decorator."""
        attempt_count = [0]

        @with_retry(max_attempts=3, initial_delay=0.01)
        async def decorated_func() -> str:
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise Exception("Transient failure")
            return "success"

        result = await decorated_func()
        assert result == "success"
        assert attempt_count[0] == 2


class TestCircuitBreakerDecorator:
    """Test circuit breaker decorator."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_decorator(self) -> None:
        """Test circuit breaker decorator."""
        call_count = [0]

        @with_circuit_breaker(name="test", failure_threshold=2, timeout_seconds=10)
        async def decorated_func() -> str:
            call_count[0] += 1
            if call_count[0] <= 2:
                raise Exception("Failure")
            return "success"

        # First two calls should fail and open circuit
        with pytest.raises(Exception):
            await decorated_func()

        with pytest.raises(Exception):
            await decorated_func()

        # Circuit should be open now
        cb = decorated_func.circuit_breaker
        assert cb.get_state() == CircuitState.OPEN

        # Next call should be rejected
        with pytest.raises(CircuitBreakerOpenError):
            await decorated_func()


class TestIntegration:
    """Test integration of retry and circuit breaker."""

    @pytest.mark.asyncio
    async def test_retry_with_circuit_breaker(self) -> None:
        """Test combining retry logic with circuit breaker."""
        cb = CircuitBreaker("test", failure_threshold=5, timeout_seconds=10)
        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        policy = RetryPolicy(config)
        attempt_count = [0]

        async def flaky_func() -> str:
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise Exception("Transient failure")
            return "success"

        async def wrapped_call() -> str:
            return await cb.call(flaky_func)

        # Should retry and succeed
        result = await policy.execute(wrapped_call)
        assert result == "success"

        # Circuit should still be closed
        assert cb.get_state() == CircuitState.CLOSED
