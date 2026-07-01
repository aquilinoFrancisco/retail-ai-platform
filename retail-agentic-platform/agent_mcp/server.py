"""
Model Context Protocol (MCP) Tool Gateway Server.
Acts as a unified routing center exposing decoupled tools as callable schemas.
"""

from typing import Dict, Any, Callable

from agent_mcp.tools.read_orders import read_orders
from agent_mcp.tools.read_inventory import read_inventory
from agent_mcp.tools.read_delivery_events import read_delivery_events
from agent_mcp.tools.read_customer_tickets import read_customer_tickets
from agent_mcp.tools.search_knowledge_base import search_knowledge_base
from agent_mcp.tools.calculate_operational_risk import calculate_operational_risk
from agent_mcp.tools.save_operations_briefing import save_operations_briefing

class MCPServer:
    """
    Core Model Context Protocol execution environment registry.
    """
    def __init__(self):
        self._registry: Dict[str, Callable[..., Dict[str, Any]]] = {
            "get_order_details": read_orders,
            "get_inventory_levels": read_inventory,
            "get_delivery_events": read_delivery_events,
            "get_customer_tickets": read_customer_tickets,
            "rag_query_retriever": search_knowledge_base,
            "calculate_operational_risk": calculate_operational_risk,
            "save_operations_briefing": save_operations_briefing
        }

    def list_tools(self) -> Dict[str, Any]:
        """Expose all available registry tools alongside descriptive instructions."""
        return {
            name: {
                "name": name,
                "description": func.__doc__.strip() if func.__doc__ else "No description provided.",
                "parameters": func.__annotations__
            }
            for name, func in self._registry.items()
        }

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Dynamically execute any registered tool by name with keyword parameters.
        """
        if tool_name not in self._registry:
            return {"success": False, "error": f"Tool '{tool_name}' not registered on server."}
        try:
            return self._registry[tool_name](**kwargs)
        except Exception as e:
            return {"success": False, "error": f"Runtime error in tool {tool_name}: {str(e)}"}

# Instantiate central server interface
mcp_server = MCPServer()
