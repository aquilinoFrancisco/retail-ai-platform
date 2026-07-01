import os
from typing import Optional
from crewai import Agent, LLM

def get_llm() -> Optional[LLM]:
    """
    Retrieve and configure the LLM for CrewAI agents.
    Uses LiteLLM's native integration for Gemini via the GEMINI_API_KEY.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    # CrewAI reads 'gemini/gemini-1.5-flash' using the GEMINI_API_KEY env var
    return LLM(model="gemini/gemini-1.5-flash", api_key=api_key)

def create_order_collector_agent() -> Agent:
    """
    Creates the Order Data Collector agent.
    Responsible for compiling and summarizing disjoint retail operational signals.
    """
    return Agent(
        role="Retail Operations Data Aggregator",
        goal="Gather, normalize, and summarize all operational data associated with a specific retail order ID.",
        backstory=(
            "An expert data pipeline agent who specializes in reading, structuring, and "
            "summarizing raw JSON feeds from inventory ledgers, shipping events, and support tickets."
        ),
        llm=get_llm(),
        verbose=True
    )

def create_risk_analyst_agent() -> Agent:
    """
    Creates the Retail Risk Analyst agent.
    Responsible for multi-vector operational risk triage and correlation.
    """
    return Agent(
        role="Senior Retail Risk Assessment Specialist",
        goal="Correlate billing, stockout, logistics transit exceptions, and negative customer sentiment to assign a risk rating.",
        backstory=(
            "A veteran retail risk forecaster and auditor. You have a sharp eye for fraud scores, "
            "severe fulfillment stock shortages, carrier delay codes, and customer sentiment signals."
        ),
        llm=get_llm(),
        verbose=True
    )

def create_operations_reporter_agent() -> Agent:
    """
    Creates the Operations Reporter agent.
    Responsible for constructing dynamic action plans and compliance dossiers.
    """
    return Agent(
        role="Senior Escalation and Operations Reporter",
        goal="Synthesize risk assessments, query local RAG policy files, and compile final action briefs.",
        backstory=(
            "A seasoned incident commander who bridges operational failures with "
            "clear executive incident briefings and SLA mitigation actions."
        ),
        llm=get_llm(),
        verbose=True
    )
