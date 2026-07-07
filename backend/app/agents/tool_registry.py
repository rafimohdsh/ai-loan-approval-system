"""Tool registry and management for agent tools."""

import logging
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from .mcp_tools import get_sync_mcp_client, MCPToolError, MCPTimeoutError, MCPInvocationError
from .tools.analysis_tools import (
    calculate_debt_to_income_ratio,
    calculate_income_to_loan_ratio,
    calculate_monthly_payment,
    assess_employment_stability,
    interpret_credit_score,
)

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of a tool that agents can use."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category: str = Field(..., description="Tool category (analysis, mcp, etc.)")
    is_mcp: bool = Field(False, description="Whether this is an MCP tool")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")
    error_handling: str = Field("raise", description="Error handling strategy: raise, return_null, fallback")


class ToolRegistry:
    """Registry and manager for agent tools."""

    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.implementations: Dict[str, Callable] = {}
        self.mcp_client = get_sync_mcp_client()
        self._register_built_in_tools()

    def _register_built_in_tools(self):
        """Register built-in analysis tools."""
        tools = [
            (
                "calculate_dti",
                "Calculate debt-to-income ratio",
                "analysis",
                calculate_debt_to_income_ratio,
            ),
            (
                "calculate_itl",
                "Calculate income-to-loan ratio",
                "analysis",
                calculate_income_to_loan_ratio,
            ),
            (
                "calculate_payment",
                "Calculate estimated monthly payment",
                "analysis",
                calculate_monthly_payment,
            ),
            (
                "assess_employment",
                "Assess employment stability",
                "analysis",
                assess_employment_stability,
            ),
            (
                "interpret_credit",
                "Interpret credit score risk level",
                "analysis",
                interpret_credit_score,
            ),
        ]

        for name, desc, category, impl in tools:
            self.register_tool(
                name=name,
                description=desc,
                category=category,
                implementation=impl,
                is_mcp=False,
            )

    def register_tool(
        self,
        name: str,
        description: str,
        category: str,
        implementation: Optional[Callable] = None,
        is_mcp: bool = False,
        parameters: Optional[Dict[str, Any]] = None,
        error_handling: str = "raise",
    ):
        """Register a tool."""
        definition = ToolDefinition(
            name=name,
            description=description,
            category=category,
            is_mcp=is_mcp,
            parameters=parameters or {},
            error_handling=error_handling,
        )
        self.tools[name] = definition

        if implementation:
            self.implementations[name] = implementation

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition."""
        return self.tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """List tools, optionally filtered by category."""
        if category:
            return [t for t in self.tools.values() if t.category == category]
        return list(self.tools.values())

    def invoke_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> Any:
        """
        Invoke a tool with error handling.

        Args:
            tool_name: Name of tool to invoke
            **kwargs: Tool arguments

        Returns:
            Tool result

        Raises:
            ValueError: If tool not found
            MCPToolError: If MCP tool fails
        """
        tool_def = self.get_tool(tool_name)
        if not tool_def:
            raise ValueError(f"Tool not found: {tool_name}")

        try:
            if tool_def.is_mcp:
                return self._invoke_mcp_tool(tool_name, kwargs, tool_def)
            else:
                return self._invoke_local_tool(tool_name, kwargs, tool_def)
        except MCPTimeoutError:
            return self._handle_tool_error(tool_name, tool_def, "timeout")
        except MCPInvocationError as e:
            return self._handle_tool_error(tool_name, tool_def, str(e))
        except Exception as e:
            return self._handle_tool_error(tool_name, tool_def, str(e))

    def _invoke_local_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        tool_def: ToolDefinition,
    ) -> Any:
        """Invoke a local (non-MCP) tool."""
        impl = self.implementations.get(tool_name)
        if not impl:
            raise ValueError(f"No implementation found for tool: {tool_name}")

        try:
            return impl(**args)
        except TypeError as e:
            logger.error(f"Tool argument error {tool_name}: {str(e)}")
            raise ValueError(f"Invalid arguments for tool {tool_name}: {str(e)}")

    def _invoke_mcp_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        tool_def: ToolDefinition,
    ) -> Any:
        """Invoke an MCP tool with retry and timeout handling."""
        try:
            result = self.mcp_client.call_tool(tool_name, args, retry=True)
            return result.get("result") if isinstance(result, dict) else result
        except MCPTimeoutError:
            logger.warning(f"MCP tool timeout: {tool_name}")
            raise
        except MCPInvocationError as e:
            logger.warning(f"MCP tool invocation failed: {tool_name} - {str(e)}")
            raise

    def _handle_tool_error(
        self,
        tool_name: str,
        tool_def: ToolDefinition,
        error: str,
    ) -> Any:
        """Handle tool errors based on error handling strategy."""
        logger.error(f"Tool error {tool_name}: {error}")

        if tool_def.error_handling == "raise":
            raise MCPToolError(f"Tool failed: {tool_name} - {error}")
        elif tool_def.error_handling == "return_null":
            logger.warning(f"Tool {tool_name} failed, returning None")
            return None
        elif tool_def.error_handling == "fallback":
            logger.warning(f"Tool {tool_name} failed, using fallback")
            return {"error": error, "fallback": True}
        else:
            raise MCPToolError(f"Tool failed: {tool_name} - {error}")

    def close(self):
        """Close the tool registry."""
        if self.mcp_client:
            self.mcp_client.close()


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create global tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
