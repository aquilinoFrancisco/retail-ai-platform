import os
import time
import logging
import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field

from graph.workflow import build_graph
from graph.state import RetailState
from app.dependencies import get_workflow, get_runtime
from logging_config import log_workflow_event

# Define APIRouter
router = APIRouter()
logger = logging.getLogger("retail_platform.api")

# Pydantic Schemas for Requests and Responses
class AnalyzeRequest(BaseModel):
    order_id: str = Field(..., description="The unique order identifier to analyze", example="ORD-001")

class AnalyzeResponse(BaseModel):
    order_id: str
    calculated_risk_level: str
    matched_vulnerabilities: List[str]
    summary_brief: str
    action_items: List[str]
    escalation_triggered: bool
    escalation_contacts: List[str]
    final_report: str
    execution_logs: List[Dict[str, Any]]

# --- PART 4: Health Endpoint ---
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(request: Request):
    """
    Returns the general health status of the service along with active runtime configuration.
    """
    runtime = getattr(request.app.state, "runtime", {
        "gemini_enabled": False,
        "simulation_mode": True,
        "error": "Not initialized"
    })
    
    return {
        "status": "ok",
        "service": "retail-agentic-platform",
        "version": "0.1.0",
        "gemini_enabled": runtime.get("gemini_enabled", False),
        "simulation_mode": runtime.get("simulation_mode", True)
    }

# --- PART 7: Runtime Endpoint ---
@router.get("/runtime", status_code=status.HTTP_200_OK)
async def get_runtime_endpoint(runtime: dict = Depends(get_runtime)):
    """
    Exposes validated LLM and agent runtime connectivity status.
    """
    return {
        "gemini_enabled": runtime.get("gemini_enabled", False),
        "simulation_mode": runtime.get("simulation_mode", True),
        "error": runtime.get("error")
    }

# --- PART 5: Analyze Endpoint ---
@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_200_OK)
async def analyze_order(request_data: AnalyzeRequest, graph=Depends(get_workflow)):
    """
    Orchestrates the complete operational triage graph over a given order ID.
    Executes sequentially and returns the fully consolidated report and audit traces.
    """
    order_id = request_data.order_id
    start_time = time.time()
    
    logger.info(f"Received request to analyze order: {order_id}")
    log_workflow_event("/analyze", order_id, "workflow_started", "PENDING", 0.0)
    
    # 1. Build initial state matching RetailState
    initial_state: RetailState = {
        "order_id": order_id,
        "collected_data": {},
        "risk_analysis": {},
        "risk_level": "NORMAL",
        "rag_context": [],
        "final_report": "",
        "escalation_triggered": False,
        "execution_logs": [],
        "error": None
    }
    
    try:
        # 2. Invoke the compiled LangGraph workflow state machine
        result = graph.invoke(initial_state)
        
        # 3. Handle intermediate errors flagged in state
        if result.get("error"):
            err_msg = result.get("error")
            duration_ms = (time.time() - start_time) * 1000
            log_workflow_event("/analyze", order_id, "workflow_failed", "ERROR", duration_ms, err_msg)
            logger.error(f"Workflow execution reported error for {order_id}: {err_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Workflow execution failed."
            )
            
        # 4. Construct sanitized output response
        risk_analysis = result.get("risk_analysis", {})
        
        # Pull details from the risk assessment dictionary
        calculated_risk_level = result.get("risk_level", "NORMAL")
        matched_vulnerabilities = risk_analysis.get("matched_vulnerabilities", [])
        summary_brief = risk_analysis.get("summary_brief", "No operational issues identified.")
        action_items = risk_analysis.get("action_items", [])
        escalation_triggered = result.get("escalation_triggered", False)
        escalation_contacts = risk_analysis.get("escalation_contacts", [])
        final_report = result.get("final_report", "")
        execution_logs = result.get("execution_logs", [])
        
        response = AnalyzeResponse(
            order_id=order_id,
            calculated_risk_level=calculated_risk_level,
            matched_vulnerabilities=matched_vulnerabilities,
            summary_brief=summary_brief,
            action_items=action_items,
            escalation_triggered=escalation_triggered,
            escalation_contacts=escalation_contacts,
            final_report=final_report,
            execution_logs=execution_logs
        )
        
        duration_ms = (time.time() - start_time) * 1000
        log_workflow_event("/analyze", order_id, "workflow_completed", "SUCCESS", duration_ms)
        logger.info(f"Successfully completed risk analysis for order {order_id} in {duration_ms:.2f}ms")
        
        return response
        
    except HTTPException:
        # Re-raise HTTPExceptions to prevent wrapping
        raise
    except Exception as e:
        # Prevent leaking stack traces to client per requirements
        duration_ms = (time.time() - start_time) * 1000
        log_workflow_event("/analyze", order_id, "workflow_failed", "ERROR", duration_ms, str(e))
        logger.exception(f"Unhandled exception during order analysis for {order_id}: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workflow execution failed."
        )

# --- PART 8: Reports Endpoint ---
@router.get("/reports", status_code=status.HTTP_200_OK)
async def list_reports():
    """
    Scans the local mock database briefings directory and returns metadata
    for all persisted operational risk reports.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    briefings_dir = os.path.join(base_dir, "mock_data", "briefings")
    
    if not os.path.exists(briefings_dir):
        return []
        
    reports = []
    try:
        for filename in os.listdir(briefings_dir):
            if filename.endswith("_briefing.json"):
                filepath = os.path.join(briefings_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Extract clean metadata from the persisted JSON dossier
                        reports.append({
                            "order_id": data.get("order_id"),
                            "calculated_risk_level": data.get("calculated_risk_level"),
                            "matched_vulnerabilities": data.get("matched_vulnerabilities", []),
                            "escalation_triggered": data.get("escalation_triggered", False),
                            "file_name": filename,
                            "last_modified": os.path.getmtime(filepath)
                        })
                except Exception as file_err:
                    logger.warning(f"Failed to read report file {filename}: {file_err}")
                    
        # Sort reports by last modified time descending (newest first)
        reports.sort(key=lambda x: x.get("last_modified", 0.0), reverse=True)
        return reports
    except Exception as e:
        logger.error(f"Failed to list briefings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve persisted reports."
        )
