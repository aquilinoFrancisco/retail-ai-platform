import os
import json
from typing import Dict, Any, List, Optional
from crewai import Agent, LLM
from crewai.tools import tool
from agent_mcp.tools.calculate_operational_risk import calculate_operational_risk

def get_llm() -> LLM:
    """Retrieve and configure the LLM for CrewAI."""
    api_key = os.environ.get("GEMINI_API_KEY", "mock_key")
    return LLM(model="gemini/gemini-1.5-flash", api_key=api_key)

@tool("calculate_operational_risk")
def calculate_operational_risk_tool(
    order_id: str,
    order_data: Optional[Dict[str, Any]] = None,
    inventory_data: Optional[Dict[str, Any]] = None,
    delivery_data: Optional[List[Dict[str, Any]]] = None,
    ticket_data: Optional[List[Dict[str, Any]]] = None
) -> str:
    """Calculates multi-vector operational risk across four vectors: Financial, Inventory, Logistics, and Customer Support."""
    res = calculate_operational_risk(
        order_id=order_id,
        order_data=order_data,
        inventory_data=inventory_data,
        delivery_data=delivery_data,
        ticket_data=ticket_data
    )
    return json.dumps(res)

def get_retail_risk_analyst_agent() -> Agent:
    """Creates the Retail Risk Analyst agent."""
    return Agent(
        role="Retail Risk Analyst",
        goal="Correlate billing, stockout, logistics transit exceptions, and negative customer sentiment to assign a risk rating.",
        backstory=(
            "A veteran retail risk forecaster and auditor. You have a sharp eye for fraud scores, "
            "severe fulfillment stock shortages, carrier delay codes, and customer sentiment signals."
        ),
        tools=[calculate_operational_risk_tool],
        llm=get_llm(),
        verbose=True
    )
