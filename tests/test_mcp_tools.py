"""Tests for MCP tool integration."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.app.agents.mcp_tools import (
    MCPClient,
    SyncMCPClient,
    MCPTimeoutError,
    MCPInvocationError,
    MCPToolError,
    retry_on_failure,
    MCP_SERVER_URL,
    MCP_REQUEST_TIMEOUT,
)
from backend.app.agents.tool_registry import ToolRegistry, get_tool_registry


class TestMCPClientTimeouts:
    """Test MCP client timeout handling."""

    def test_timeout_error_instantiation(self):
        """Test that MCPTimeoutError can be instantiated."""
        error = MCPTimeoutError("Test timeout")
        assert str(error) == "Test timeout"
        assert isinstance(error, MCPToolError)

    def test_timeout_client_configuration(self):
        """Test MCP client timeout configuration."""
        client = MCPClient(timeout=1)
        assert client.timeout == 1

        client2 = MCPClient(timeout=60)
        assert client2.timeout == 60


class TestMCPClientErrors:
    """Test MCP client error handling."""

    def test_invocation_error_instantiation(self):
        """Test that MCPInvocationError can be instantiated."""
        error = MCPInvocationError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, MCPToolError)

    def test_mcp_client_initialization(self):
        """Test MCP client initialization."""
        client = MCPClient()
        assert client.base_url == MCP_SERVER_URL
        assert client.timeout == MCP_REQUEST_TIMEOUT

        client2 = MCPClient(base_url="http://custom:5000", timeout=60)
        assert client2.base_url == "http://custom:5000"
        assert client2.timeout == 60


class TestRetryDecorator:
    """Test retry decorator functionality."""

    def test_retry_decorator_instantiation(self):
        """Test that retry decorator can be instantiated."""
        decorator = retry_on_failure(max_retries=3, delay=1.0)
        assert decorator is not None

    def test_retry_decorator_parameters(self):
        """Test retry decorator parameters."""
        @retry_on_failure(max_retries=5, delay=0.5)
        def dummy_function():
            return "test"

        # Decorator should wrap function
        assert callable(dummy_function)


class TestSyncMCPClient:
    """Test synchronous MCP client."""

    def test_sync_client_initialization(self):
        """Test that sync client initializes properly."""
        client = SyncMCPClient()
        assert client.async_client is not None
        assert isinstance(client.async_client, MCPClient)


class TestToolRegistry:
    """Test tool registry functionality."""

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        def dummy_tool(x: int) -> int:
            return x * 2

        registry.register_tool(
            "test_tool",
            "Test tool",
            "test",
            implementation=dummy_tool
        )

        tool = registry.get_tool("test_tool")
        assert tool is not None
        assert tool.name == "test_tool"
        assert tool.description == "Test tool"

    def test_invoke_local_tool(self):
        """Test invoking a local tool."""
        registry = ToolRegistry()
        def add(a: int, b: int) -> int:
            return a + b

        registry.register_tool(
            "add",
            "Add two numbers",
            "math",
            implementation=add
        )

        result = registry.invoke_tool("add", a=5, b=3)
        assert result == 8

    def test_invoke_nonexistent_tool_raises_error(self):
        """Test that invoking nonexistent tool raises error."""
        registry = ToolRegistry()
        with pytest.raises(ValueError):
            registry.invoke_tool("nonexistent", x=1)

    def test_tool_with_wrong_args_raises_error(self):
        """Test that tool with wrong arguments raises error."""
        registry = ToolRegistry()
        def requires_args(x: int, y: int) -> int:
            return x + y

        registry.register_tool(
            "requires_args",
            "Requires arguments",
            "test",
            implementation=requires_args
        )

        with pytest.raises(Exception):  # MCPToolError or ValueError
            registry.invoke_tool("requires_args", x=5)  # Missing y

    def test_list_tools_by_category(self):
        """Test listing tools by category."""
        registry = ToolRegistry()
        tools = registry.list_tools(category="analysis")
        assert len(tools) > 0
        assert all(t.category == "analysis" for t in tools)

    def test_built_in_tools_registered(self):
        """Test that built-in tools are registered."""
        registry = ToolRegistry()
        assert registry.get_tool("calculate_dti") is not None
        assert registry.get_tool("calculate_itl") is not None
        assert registry.get_tool("calculate_payment") is not None


class TestMCPClientBatchCall:
    """Test batch tool calling."""

    def test_batch_call_structure(self):
        """Test batch call data structure."""
        calls = [
            ("tool1", {"arg": "value1"}),
            ("tool2", {"arg": "value2"}),
            ("tool3", {"arg": "value3"}),
        ]

        assert len(calls) == 3
        assert calls[0][0] == "tool1"
        assert calls[1][0] == "tool2"


class TestErrorHandlingStrategies:
    """Test different error handling strategies."""

    def test_error_handling_raise_strategy(self):
        """Test raise strategy for error handling."""
        registry = ToolRegistry()

        def failing_tool():
            raise ValueError("Tool failed")

        registry.register_tool(
            "failing",
            "Fails",
            "test",
            implementation=failing_tool,
            error_handling="raise"
        )

        with pytest.raises(Exception):
            registry.invoke_tool("failing")

    def test_error_handling_return_null_strategy(self):
        """Test return_null strategy for error handling."""
        registry = ToolRegistry()

        def failing_tool():
            raise ValueError("Tool failed")

        registry.register_tool(
            "failing",
            "Fails",
            "test",
            implementation=failing_tool,
            error_handling="return_null"
        )

        result = registry.invoke_tool("failing")
        assert result is None

    def test_error_handling_fallback_strategy(self):
        """Test fallback strategy for error handling."""
        registry = ToolRegistry()

        def failing_tool():
            raise ValueError("Tool failed")

        registry.register_tool(
            "failing",
            "Fails",
            "test",
            implementation=failing_tool,
            error_handling="fallback"
        )

        result = registry.invoke_tool("failing")
        assert isinstance(result, dict)
        assert "error" in result
        assert result.get("fallback") is True
