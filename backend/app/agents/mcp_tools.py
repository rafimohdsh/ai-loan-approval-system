"""MCP tool integration for loan agents."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from functools import wraps
import httpx

logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:3000"
MCP_REQUEST_TIMEOUT = 30


class MCPToolError(Exception):
    """Base exception for MCP tool errors."""
    pass


class MCPTimeoutError(MCPToolError):
    """Timeout error when calling MCP tool."""
    pass


class MCPInvocationError(MCPToolError):
    """Error when invoking MCP tool."""
    pass


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry MCP tool calls on failure."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except MCPTimeoutError as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
                except MCPInvocationError as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        raise
            if last_error:
                raise last_error
        return async_wrapper
    return decorator


class MCPClient:
    """Client for invoking MCP tools with error handling and timeouts."""

    def __init__(self, base_url: str = MCP_SERVER_URL, timeout: int = MCP_REQUEST_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        retry: bool = True
    ) -> Dict[str, Any]:
        """
        Call an MCP tool with error handling.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            retry: Whether to retry on failure

        Returns:
            Tool result dictionary

        Raises:
            MCPTimeoutError: If tool call times out
            MCPInvocationError: If tool call fails
        """
        if retry:
            return await self._call_with_retry(tool_name, arguments)
        else:
            return await self._invoke_tool(tool_name, arguments)

    async def _invoke_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke MCP tool directly."""
        try:
            url = f"{self.base_url}/tools/{tool_name}/call"
            response = await self.client.post(
                url,
                json={"arguments": arguments},
                timeout=self.timeout
            )

            if response.status_code == 408:
                raise MCPTimeoutError(f"MCP tool call timed out: {tool_name}")

            if response.status_code >= 400:
                error_data = response.json()
                raise MCPInvocationError(
                    f"MCP tool error: {tool_name} - {error_data.get('detail', 'Unknown error')}"
                )

            return response.json()

        except asyncio.TimeoutError:
            raise MCPTimeoutError(f"Request timeout calling MCP tool: {tool_name}")
        except httpx.TimeoutException:
            raise MCPTimeoutError(f"Request timeout calling MCP tool: {tool_name}")
        except httpx.RequestError as e:
            raise MCPInvocationError(f"Failed to call MCP tool {tool_name}: {str(e)}")
        except json.JSONDecodeError:
            raise MCPInvocationError(f"Invalid JSON response from MCP tool {tool_name}")

    @retry_on_failure(max_retries=3, delay=1.0)
    async def _call_with_retry(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke MCP tool with automatic retries."""
        return await self._invoke_tool(tool_name, arguments)

    async def batch_call(
        self,
        calls: List[tuple[str, Dict[str, Any]]],
        continue_on_error: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls concurrently.

        Args:
            calls: List of (tool_name, arguments) tuples
            continue_on_error: If True, continue on individual tool failures

        Returns:
            List of results
        """
        tasks = [self.call_tool(tool, args) for tool, args in calls]
        results = []

        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
            except MCPToolError as e:
                if continue_on_error:
                    logger.warning(f"Tool call failed: {str(e)}")
                    results.append({"error": str(e)})
                else:
                    raise

        return results

    async def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools."""
        try:
            response = await self.client.get(f"{self.base_url}/tools", timeout=self.timeout)
            if response.status_code == 200:
                return response.json().get("tools", [])
        except Exception as e:
            logger.warning(f"Failed to get tool list: {str(e)}")
        return []


# Synchronous wrapper for non-async contexts
class SyncMCPClient:
    """Synchronous wrapper around async MCP client."""

    def __init__(self, base_url: str = MCP_SERVER_URL, timeout: int = MCP_REQUEST_TIMEOUT):
        self.async_client = MCPClient(base_url, timeout)

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        retry: bool = True
    ) -> Dict[str, Any]:
        """Call MCP tool synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(
                self.async_client.call_tool(tool_name, arguments, retry)
            )
        finally:
            if loop.is_running():
                loop.close()

    def batch_call(
        self,
        calls: List[tuple[str, Dict[str, Any]]],
        continue_on_error: bool = False
    ) -> List[Dict[str, Any]]:
        """Call multiple tools synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(
                self.async_client.batch_call(calls, continue_on_error)
            )
        finally:
            if loop.is_running():
                loop.close()

    def close(self):
        """Close the client."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.async_client.close())
        finally:
            if loop.is_running():
                loop.close()


# Global client instance
_mcp_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """Get or create global MCP client."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


def get_sync_mcp_client() -> SyncMCPClient:
    """Get synchronous MCP client."""
    return SyncMCPClient()
