import os
import json
from typing import Literal, Dict, Any, List
from langgraph.graph import StateGraph, START, END

from graph.state import RetailState
from agent_mcp.tools.read_orders import read_orders
from agent_mcp.tools.read_inventory import read_inventory
from agent_mcp.tools.read_delivery_events import read_delivery_events
from agent_mcp.tools.read_customer_tickets import read_customer_tickets
from agent_mcp.tools.calculate_operational_risk import calculate_operational_risk
from agent_mcp.tools.save_operations_briefing import save_operations_briefing
from rag.retriever import retrieve_escalation_rules
from crew.retail_crew import RetailCrew

# Node 1: Collect Data
def collect_data(state: RetailState) -> Dict[str, Any]:
    """
    Queries multi-source databases via the MCP Tools Gateway.
    Gathers order logs, inventory ledgers, shipping exceptions, and active support tickets.
    """
    order_id = state.get("order_id")
    if not order_id:
        return {"error": "Missing order_id in initial state"}
        
    execution_logs = state.get("execution_logs", []) or []
    
    execution_logs.append({
        "agent_name": "DataIngestionEngine",
        "action_taken": "Querying Order database",
        "thought_process": f"Initializing collection flow for order '{order_id}'. Retrieving metadata.",
        "result_summary": "Executing query."
    })
    
    try:
        # 1. Read Order Details
        order_res = read_orders(order_id)
        order_data = order_res.get("data", {})
        
        # Extract SKU and Tracking Number for downstream lookups
        sku = None
        tracking_number = None
        if order_data:
            items = order_data.get("items", [])
            if items:
                sku = items[0].get("sku")
            fulfillment = order_data.get("fulfillment", {})
            tracking_number = fulfillment.get("tracking_number")
            
        execution_logs.append({
            "agent_name": "DataIngestionEngine",
            "action_taken": "Querying Inventory and Carrier databases",
            "thought_process": f"Extracted SKU '{sku}' and Tracking Number '{tracking_number}'. Commencing child queries.",
            "result_summary": "Queries dispatched."
        })
        
        # 2. Read Inventory
        inventory_res = read_inventory(sku)
        
        # 3. Read Delivery Logs
        delivery_res = read_delivery_events(tracking_number)
        
        # 4. Read Active Customer Tickets
        tickets_res = read_customer_tickets(order_id=order_id)
        
        collected = {
            "order_data": order_res,
            "inventory_data": inventory_res,
            "delivery_data": delivery_res,
            "ticket_data": tickets_res
        }
        
        execution_logs.append({
            "agent_name": "DataIngestionEngine",
            "action_taken": "Fulfillment Telemetry Assembly Completed",
            "thought_process": "Data elements aggregated cleanly into core workflow state dictionary.",
            "result_summary": "Successfully cached all parameters."
        })
        
        return {
            "collected_data": collected,
            "execution_logs": execution_logs
        }
    except Exception as e:
        return {"error": f"Error during data collection: {str(e)}"}

# Node 2: Analyze Operational Risk
def analyze_operational_risk(state: RetailState) -> Dict[str, Any]:
    """
    Triggers CrewAI specialized agents to assess logistics vulnerability.
    """
    order_id = state.get("order_id")
    execution_logs = state.get("execution_logs", []) or []
    
    try:
        # Instantiating the RetailCrew class to run agent operations sequential logic
        crew = RetailCrew()
        crew_result = crew.run(order_id)
        
        # Merge execution logs from CrewAI
        if "execution_logs" in crew_result:
            execution_logs.extend(crew_result["execution_logs"])
            
        return {
            "risk_analysis": crew_result,
            "execution_logs": execution_logs
        }
    except Exception as e:
        return {"error": f"Error during CrewAI multi-agent risk assessment: {str(e)}"}

# Node 3: Evaluate Risk Level
def evaluate_risk_level(state: RetailState) -> Dict[str, Any]:
    """
    Triages calculated risk against operational thresholds.
    Classifies the situation as NORMAL or CRITICAL.
    """
    order_id = state.get("order_id")
    collected = state.get("collected_data", {})
    execution_logs = state.get("execution_logs", []) or []
    
    execution_logs.append({
        "agent_name": "TriageRuleEngine",
        "action_taken": "Run decision threshold matrices",
        "thought_process": "Evaluating core multi-vector numerical metrics and customer sentiment scales.",
        "result_summary": "Calculation run."
    })
    
    try:
        order_info = collected.get("order_data", {}).get("data", {})
        inv_info = collected.get("inventory_data", {}).get("data", {})
        
        deliv_events = collected.get("delivery_data", {}).get("data", [])
        if not isinstance(deliv_events, list):
            deliv_events = []
            
        ticket_data = collected.get("ticket_data", {}).get("data", [])
        if not isinstance(ticket_data, list):
            if isinstance(ticket_data, dict):
                ticket_data = [ticket_data]
            else:
                ticket_data = []
                
        # Invoke calculate_operational_risk tool
        risk_assessment = calculate_operational_risk(
            order_id=order_id,
            order_data=order_info,
            inventory_data=inv_info,
            delivery_data=deliv_events,
            ticket_data=ticket_data
        )
        
        risk_level = risk_assessment.get("calculated_risk_level", "NORMAL")
        
        execution_logs.append({
            "agent_name": "TriageRuleEngine",
            "action_taken": "Triage complete",
            "thought_process": f"Triaged overall risk for '{order_id}'. Resulting Level: {risk_level}.",
            "result_summary": f"Calculated state: {risk_level}"
        })
        
        return {
            "risk_level": risk_level,
            "risk_analysis": risk_assessment,
            "execution_logs": execution_logs
        }
    except Exception as e:
        return {"error": f"Error during operational risk evaluation: {str(e)}"}

# Node 4: Generate Briefing (Incident & Standard combined or branch matching)
def generate_briefing(state: RetailState) -> Dict[str, Any]:
    """
    Constructs the briefing dossier based on evaluated risk context.
    If the risk is CRITICAL, queries the local RAG knowledge base for escalation rules.
    """
    order_id = state.get("order_id")
    risk_level = state.get("risk_level", "NORMAL")
    risk_details = state.get("risk_analysis", {})
    execution_logs = state.get("execution_logs", []) or []
    
    try:
        if risk_level == "CRITICAL":
            execution_logs.append({
                "agent_name": "RAGRetrieverEngine",
                "action_taken": "Querying local SLA manual index",
                "thought_process": "Searching for high-value fraud and stockout SLA resolution criteria.",
                "result_summary": "Scanning files."
            })
            
            # Query terms based on matched vulnerabilities
            vulnerabilities = risk_details.get("matched_vulnerabilities", [])
            query = " ".join(vulnerabilities) if vulnerabilities else "SLA escalation contacts"
            
            # Retrieve policies
            rag_results = retrieve_escalation_rules(query, top_k=2)
            rag_context = [f"Source: {res['source']} - Section: {res['header']}\n{res['text']}" for res in rag_results]
            
            # Update risk details with RAG insights
            risk_details["escalation_triggered"] = True
            
            final_report = (
                f"# CRITICAL OPERATIONAL BRIEFING: ORDER {order_id}\n\n"
                f"**Risk Severity**: CRITICAL\n"
                f"**Friction Vectors Identified**: {', '.join(vulnerabilities)}\n\n"
                f"## 1. Executive Summary\n"
                f"{risk_details.get('summary_brief', 'N/A')}\n\n"
                f"## 2. Action and Mitigation Plan\n"
                + "\n".join(f"- [x] {item}" for item in risk_details.get("action_items", []))
                + "\n\n"
                f"## 3. SLA & Regulatory Compliance (RAG Context)\n"
                + "\n\n".join(rag_context)
                + "\n"
            )
            
            return {
                "rag_context": rag_context,
                "final_report": final_report,
                "escalation_triggered": True,
                "execution_logs": execution_logs
            }
        else:
            execution_logs.append({
                "agent_name": "StandardReporterEngine",
                "action_taken": "Compile Standard Release report",
                "thought_process": "Assembling standard logs as risk levels conform to baseline thresholds.",
                "result_summary": "Report created."
            })
            
            final_report = (
                f"# STANDARD FULFILLMENT STATUS BRIEFING: ORDER {order_id}\n\n"
                f"**Risk Severity**: NORMAL\n\n"
                f"## 1. Status Summary\n"
                f"{risk_details.get('summary_brief', 'N/A')}\n\n"
                f"## 2. Release Steps\n"
                + "\n".join(f"- [x] {item}" for item in risk_details.get("action_items", []))
                + "\n"
            )
            
            return {
                "final_report": final_report,
                "escalation_triggered": False,
                "execution_logs": execution_logs
            }
    except Exception as e:
        return {"error": f"Error during briefing generation: {str(e)}"}

# Node 5: Save Report
def save_report(state: RetailState) -> Dict[str, Any]:
    """
    Finalizes the state machine. Commits the risk report to disk.
    """
    order_id = state.get("order_id")
    risk_details = state.get("risk_analysis", {})
    execution_logs = state.get("execution_logs", []) or []
    
    execution_logs.append({
        "agent_name": "DatabaseWriter",
        "action_taken": "Saving Incident briefing dossier to DB",
        "thought_process": f"Committing full structured briefing logs for '{order_id}' to the operational ledger.",
        "result_summary": "Writing file."
    })
    
    try:
        # Build briefing dictionary conforming to OperationalRiskAssessment
        briefing_payload = {
            "order_id": order_id,
            "calculated_risk_level": state.get("risk_level", "NORMAL"),
            "matched_vulnerabilities": risk_details.get("matched_vulnerabilities", []),
            "summary_brief": risk_details.get("summary_brief", "No issues identified."),
            "action_items": risk_details.get("action_items", []),
            "escalation_triggered": state.get("escalation_triggered", False),
            "escalation_contacts": risk_details.get("escalation_contacts", [])
        }
        
        save_operations_briefing(briefing_payload)
        
        execution_logs.append({
            "agent_name": "DatabaseWriter",
            "action_taken": "State Machine Finalized",
            "thought_process": f"Successfully completed all operations for order '{order_id}'. Graph terminates.",
            "result_summary": "SUCCESS"
        })
        
        return {
            "execution_logs": execution_logs
        }
    except Exception as e:
        return {"error": f"Error saving report: {str(e)}"}

# Node 6: Handle Error
def handle_error(state: RetailState) -> Dict[str, Any]:
    """
    Failsafe node to catch exceptions, format logs, and terminate gracefully.
    """
    execution_logs = state.get("execution_logs", []) or []
    err = state.get("error", "Unknown error encountered.")
    
    execution_logs.append({
        "agent_name": "SystemFailSafeHandler",
        "action_taken": "Failsafe termination triggered",
        "thought_process": "Graph execution halted due to failure. Creating emergency trace log.",
        "result_summary": f"ERROR: {err}"
    })
    
    final_report = f"# SYSTEM EXCEPTION REPORT\n\nFailsafe execution triggered. Cause:\n\n`{err}`\n"
    
    return {
        "final_report": final_report,
        "execution_logs": execution_logs
    }

# Conditional Router Logic
def route_by_risk(state: RetailState) -> Literal["generate_briefing", "handle_error"]:
    """
    Conditional edge router checks if any node registered an error.
    Otherwise routes smoothly to generate briefing.
    """
    if state.get("error"):
        return "handle_error"
    return "generate_briefing"

# Conditional Edge router for state error or normal flow from collect/analyze
def route_check_error(state: RetailState) -> Literal["next_node", "handle_error"]:
    """Checks if an error has occurred at intermediate nodes."""
    if state.get("error"):
        return "handle_error"
    return "next_node"

def build_graph():
    """
    Assembles and compiles the full Stateful StateGraph.
    """
    builder = StateGraph(RetailState)
    
    # Add Nodes
    builder.add_node("collect_data", collect_data)
    builder.add_node("analyze_operational_risk", analyze_operational_risk)
    builder.add_node("evaluate_risk_level", evaluate_risk_level)
    builder.add_node("generate_briefing", generate_briefing)
    builder.add_node("save_report", save_report)
    builder.add_node("handle_error", handle_error)
    
    # Add Connections with error routes
    builder.add_edge(START, "collect_data")
    
    # Checks intermediate errors
    builder.add_conditional_edges(
        "collect_data",
        route_check_error,
        {
            "next_node": "analyze_operational_risk",
            "handle_error": "handle_error"
        }
    )
    
    builder.add_conditional_edges(
        "analyze_operational_risk",
        route_check_error,
        {
            "next_node": "evaluate_risk_level",
            "handle_error": "handle_error"
        }
    )
    
    # Conditional Edge from evaluate_risk_level to generate_briefing (or error)
    builder.add_conditional_edges(
        "evaluate_risk_level",
        route_by_risk,
        {
            "generate_briefing": "generate_briefing",
            "handle_error": "handle_error"
        }
    )
    
    # Standard edges to save and end
    builder.add_edge("generate_briefing", "save_report")
    builder.add_edge("save_report", END)
    builder.add_edge("handle_error", END)
    
    return builder.compile()

# Compile the singleton workflow
workflow = build_graph()
