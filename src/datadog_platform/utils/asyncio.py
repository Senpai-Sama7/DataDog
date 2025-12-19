"""Async utility helpers."""

import inspect
from typing import Any, Awaitable, TypeVar, Union

T = TypeVar("T")


async def maybe_await(value: Union[T, Awaitable[T]]) -> T:
    """Return awaited result when value is awaitable otherwise return value."""

    return await value if inspect.isawaitable(value) else value
