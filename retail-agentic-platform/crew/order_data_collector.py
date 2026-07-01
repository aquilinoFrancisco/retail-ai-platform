import os
import json
from crewai import Agent, LLM
from crewai.tools import tool
from agent_mcp.tools.read_orders import read_orders
from agent_mcp.tools.read_inventory import read_inventory
from agent_mcp.tools.read_delivery_events import read_delivery_events
from agent_mcp.tools.read_customer_tickets import read_customer_tickets

def get_llm() -> LLM:
    """Retrieve and configure the LLM for CrewAI."""
    api_key = os.environ.get("GEMINI_API_KEY", "mock_key")
    return LLM(model="gemini/gemini-1.5-flash", api_key=api_key)

@tool("read_orders")
def read_orders_tool(order_id: str) -> str:
    """Reads the order details from the database for a given order_id."""
    return json.dumps(read_orders(order_id))

@tool("read_inventory")
def read_inventory_tool(sku: str) -> str:
    """Reads the warehouse inventory levels and replenishment status for a given sku."""
    return json.dumps(read_inventory(sku))

@tool("read_delivery_events")
def read_delivery_events_tool(tracking_number: str) -> str:
    """Reads carrier logistics delay codes and real-time delivery tracking events for a given tracking_number."""
    return json.dumps(read_delivery_events(tracking_number))

@tool("read_customer_tickets")
def read_customer_tickets_tool(order_id: str) -> str:
    """Reads active customer ticketing logs and support issues matching a given order_id."""
    return json.dumps(read_customer_tickets(order_id=order_id))

def get_order_data_collector_agent() -> Agent:
    """Creates the Order Data Collector agent."""
    return Agent(
        role="Order Data Collector",
        goal="Gather, normalize, and summarize all operational data associated with a specific retail order ID.",
        backstory=(
            "An expert data pipeline agent who specializes in reading, structuring, and "
            "summarizing raw database feeds from inventory ledgers, shipping events, and support tickets."
        ),
        tools=[read_orders_tool, read_inventory_tool, read_delivery_events_tool, read_customer_tickets_tool],
        llm=get_llm(),
        verbose=True
    )
