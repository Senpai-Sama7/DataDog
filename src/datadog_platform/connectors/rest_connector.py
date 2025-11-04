"""
REST API connector implementation.
"""

import asyncio
from typing import Any, Dict, Optional

from datadog_platform.core.base import BaseConnector


class RESTConnector(BaseConnector):
    """
    Connector for REST API data sources.

    Provides async interface for making HTTP requests to REST APIs.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize REST API connector.

        Args:
            config: Configuration including URL, auth, headers, etc.
        """
        super().__init__(config)
        self.base_url = config.get("url", "")
        self.auth = config.get("auth")
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 30)
        self.verify_ssl = config.get("verify_ssl", True)

    async def connect(self) -> None:
        """
        Establish connection (validate API endpoint).

        In production, would create aiohttp session.
        """
        await asyncio.sleep(0.01)  # Simulate connection

        if not self.base_url:
            raise ValueError("Base URL is required")

        self._connection = {
            "base_url": self.base_url,
            "connected": True,
            "session": None,  # Would be aiohttp.ClientSession()
        }

    async def disconnect(self) -> None:
        """Close connection and cleanup session."""
        if self._connection:
            if self._connection.get("session"):
                # Would close aiohttp session
                await asyncio.sleep(0.01)
            self._connection = None

    async def read(
        self,
        query: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Read data from REST API.

        Args:
            query: Not used for REST connector
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            API response data
        """
        if not self._connection:
            raise RuntimeError("Not connected")

        # Placeholder for actual HTTP request
        # In production, would use aiohttp
        await asyncio.sleep(0.1)  # Simulate network request

        # Simulated response
        return {
            "status": "success",
            "data": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
            ],
            "metadata": {"total": 2, "page": 1},
        }

    async def write(
        self, data: Any, endpoint: Optional[str] = None, method: str = "POST", **kwargs: Any
    ) -> Any:
        """
        Write data to REST API.

        Args:
            data: Data to send in request body
            endpoint: API endpoint path
            method: HTTP method (POST, PUT, PATCH, etc.)
            **kwargs: Additional request parameters

        Returns:
            API response
        """
        if not self._connection:
            raise RuntimeError("Not connected")

        # Placeholder for actual HTTP request
        await asyncio.sleep(0.1)  # Simulate network request

        return {"status": "success", "message": "Data written successfully"}

    async def validate_connection(self) -> bool:
        """
        Validate API connection.

        Returns:
            bool: True if API is reachable
        """
        try:
            if not self._connection:
                await self.connect()

            # Placeholder for health check
            # In production: make OPTIONS or HEAD request
            return self._connection is not None

        except Exception:
            return False

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from base and endpoint.

        Args:
            endpoint: Endpoint path

        Returns:
            str: Full URL
        """
        base = self.base_url.rstrip("/")
        path = endpoint.lstrip("/")
        return f"{base}/{path}" if path else base

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data
        """
        return await self.read(endpoint=endpoint, method="GET", params=params)

    async def post(self, endpoint: str, data: Any) -> Any:
        """
        Make POST request.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Response data
        """
        return await self.write(data=data, endpoint=endpoint, method="POST")

    async def put(self, endpoint: str, data: Any) -> Any:
        """
        Make PUT request.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Response data
        """
        return await self.write(data=data, endpoint=endpoint, method="PUT")

    async def delete(self, endpoint: str) -> Any:
        """
        Make DELETE request.

        Args:
            endpoint: API endpoint

        Returns:
            Response data
        """
        return await self.read(endpoint=endpoint, method="DELETE")
