import os
import json
from typing import Dict, Any
from crewai import Agent, LLM
from crewai.tools import tool
from agent_mcp.tools.search_knowledge_base import search_knowledge_base
from agent_mcp.tools.save_operations_briefing import save_operations_briefing

def get_llm() -> LLM:
    """Retrieve and configure the LLM for CrewAI."""
    api_key = os.environ.get("GEMINI_API_KEY", "mock_key")
    return LLM(model="gemini/gemini-1.5-flash", api_key=api_key)

@tool("search_knowledge_base")
def search_knowledge_base_tool(query: str) -> str:
    """Search the local markdown knowledge base for SLA policies, compliance rules, and escalation contact details."""
    return json.dumps(search_knowledge_base(query))

@tool("save_operations_briefing")
def save_operations_briefing_tool(briefing: Dict[str, Any]) -> str:
    """Validate and commit the finalized operations briefing dossier to the logging database disk."""
    return json.dumps(save_operations_briefing(briefing))

def get_operations_reporter_agent() -> Agent:
    """Creates the Operations Reporter agent."""
    return Agent(
        role="Operations Reporter",
        goal="Synthesize risk assessments, query local RAG policy files, and compile final action briefs.",
        backstory=(
            "A seasoned incident commander who bridges operational failures with "
            "clear executive incident briefings and SLA mitigation actions."
        ),
        tools=[search_knowledge_base_tool, save_operations_briefing_tool],
        llm=get_llm(),
        verbose=True
    )
