from typing import Dict, Any, List, TypedDict, Optional

class RetailState(TypedDict, total=False):
    """
    State definition for the LangGraph workflow.
    Ensures safe, type-safe data propagation between different nodes.
    """
    # Inputs
    order_id: str
    
    # Aggregated Data (from collect_data node via MCP Tools)
    collected_data: Dict[str, Any]
    
    # Risk Assessment (from analyze_operational_risk node via CrewAI)
    risk_analysis: Dict[str, Any]
    
    # Risk Classification (from evaluate_risk_level node)
    # Options: "NORMAL", "CRITICAL"
    risk_level: str
    
    # Retrieved SLA Compliance Escalation Rules (from RAG retriever)
    rag_context: List[str]
    
    # Final Executive Summary and Incident Dossier
    final_report: str
    
    # Flag indicating if immediate slack / pagerduty alerts were triggered
    escalation_triggered: bool
    
    # Trace logs representing agent thoughts and active tool usage
    execution_logs: List[Dict[str, str]]
    
    # Error state tracker
    error: Optional[str]
