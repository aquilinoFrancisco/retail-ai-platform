import os
import time
import json
import logging
import asyncio
from datetime import datetime
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from graph.workflow import build_graph
from graph.state import RetailState
from app.dependencies import get_workflow
from logging_config import log_workflow_event

# Define Router
router = APIRouter()
logger = logging.getLogger("retail_platform.api.stream")

class StreamRequest(BaseModel):
    order_id: str = Field(..., description="The unique order identifier to analyze", example="ORD-001")

def format_sse(event_name: str, data: dict) -> str:
    """Formats an event and JSON payload as a Server-Sent Event."""
    return f"event: {event_name}\ndata: {json.dumps(data)}\n\n"

# --- PART 6: Streaming Endpoint ---
@router.post("/analyze/stream", status_code=status.HTTP_200_OK)
async def analyze_stream_endpoint(request_data: StreamRequest, graph=Depends(get_workflow)):
    """
    Analyzes an order operational risk and streams real-time state transitions and
    agent tracing logs as Server-Sent Events (SSE) to the browser.
    """
    order_id = request_data.order_id
    start_time = time.time()
    
    logger.info(f"Initializing SSE analysis stream for order: {order_id}")
    log_workflow_event("/analyze/stream", order_id, "stream_started", "PENDING", 0.0)

    # 1. Define initial state matching RetailState
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

    async def sse_generator() -> AsyncGenerator[str, None]:
        # Emit: workflow_started
        yield format_sse("workflow_started", {
            "order_id": order_id,
            "status": "Initializing retail agentic workflow...",
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.5)

        use_native_astream = hasattr(graph, "astream")
        
        if use_native_astream:
            try:
                # Attempt native astream streaming
                logger.info(f"Using native astream execution for order {order_id}")
                
                # We'll collect cumulative states to emit complete context
                cumulative_state = initial_state.copy()
                
                async for chunk in graph.astream(initial_state):
                    # In LangGraph, chunk is usually Dict[node_name, node_output_state]
                    for node_name, node_output in chunk.items():
                        # Update our cumulative state with node output
                        if isinstance(node_output, dict):
                            cumulative_state.update(node_output)
                        
                        # Match node_name to expected SSE event
                        # Valid nodes in graph/workflow.py: collect_data, analyze_operational_risk,
                        # evaluate_risk_level, generate_briefing, save_report
                        event_type = node_name
                        
                        # Gather logs and output fields for the event payload
                        event_payload = {
                            "order_id": order_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "node": node_name,
                            "risk_level": cumulative_state.get("risk_level", "NORMAL"),
                            "escalation_triggered": cumulative_state.get("escalation_triggered", False),
                            "execution_logs": node_output.get("execution_logs", []) if isinstance(node_output, dict) else [],
                        }
                        
                        if node_name == "collect_data":
                            event_payload["collected_data"] = cumulative_state.get("collected_data")
                            status_msg = "Fulfillment telemetry, carrier logistics, and inventory logs retrieved successfully."
                        elif node_name == "analyze_operational_risk":
                            event_payload["risk_analysis"] = cumulative_state.get("risk_analysis")
                            status_msg = "Operational risk threat model finalized by CrewAI Multi-Agent Swarm."
                        elif node_name == "evaluate_risk_level":
                            status_msg = f"Operational triage evaluation complete. Threat Level: {cumulative_state.get('risk_level', 'NORMAL')}."
                        elif node_name == "generate_briefing":
                            event_payload["final_report"] = cumulative_state.get("final_report")
                            status_msg = "Custom SLA-driven operations briefing compiled successfully."
                        elif node_name == "save_report":
                            status_msg = "Completed operations briefing dossier written to database ledger."
                        else:
                            status_msg = f"Node '{node_name}' completed execution successfully."

                        event_payload["status"] = status_msg
                        
                        yield format_sse(event_type, event_payload)
                        await asyncio.sleep(0.8) # smooth UI transition buffer
                
                # Build final result response
                duration_ms = (time.time() - start_time) * 1000
                log_workflow_event("/analyze/stream", order_id, "workflow_completed", "SUCCESS", duration_ms)
                
                yield format_sse("workflow_completed", {
                    "order_id": order_id,
                    "status": "All automated retail triage pipeline operations concluded successfully.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "payload": {
                        "risk_level": cumulative_state.get("risk_level", "NORMAL"),
                        "escalation_triggered": cumulative_state.get("escalation_triggered", False),
                        "final_report": cumulative_state.get("final_report"),
                        "duration_ms": duration_ms
                    }
                })
                return

            except Exception as e:
                logger.warning(f"Native astream encountered an exception: {e}. Falling back to high-fidelity simulated streaming.")
                # We do not return here; we fall back to the invoke-based stream below!

        # Fallback path: Execute graph synchronously, then stream step-by-step
        try:
            logger.info(f"Using high-fidelity simulated stream for order {order_id}")
            
            # Invoke the graph synchronously
            run_start = time.time()
            result_state = graph.invoke(initial_state)
            run_duration_ms = (time.time() - run_start) * 1000
            
            # If the invocation resulted in an error state
            if result_state.get("error"):
                raise Exception(result_state.get("error"))
                
            # Now we stream the steps chronologically using the actual computed state
            steps = [
                "collect_data",
                "analyze_operational_risk",
                "evaluate_risk_level",
                "generate_briefing",
                "save_report"
            ]
            
            # Filter logs associated with each stage if possible, or distribute
            all_logs = result_state.get("execution_logs", [])
            
            for step in steps:
                step_payload = {
                    "order_id": order_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "node": step,
                    "risk_level": result_state.get("risk_level", "NORMAL"),
                    "escalation_triggered": result_state.get("escalation_triggered", False)
                }
                
                # Disaggregate logs and context to make the simulation highly authentic
                if step == "collect_data":
                    step_payload["collected_data"] = result_state.get("collected_data")
                    step_payload["execution_logs"] = [l for l in all_logs if "Collector" in l.get("agent_name", "") or "Ingestion" in l.get("agent_name", "")]
                    status_msg = "Fulfillment telemetry, carrier logistics, and inventory logs retrieved successfully."
                    
                elif step == "analyze_operational_risk":
                    step_payload["risk_analysis"] = result_state.get("risk_analysis")
                    step_payload["execution_logs"] = [l for l in all_logs if "Crew" in l.get("agent_name", "") or "Threat" in l.get("agent_name", "") or "Risk" in l.get("agent_name", "")]
                    status_msg = "Operational risk threat model finalized by CrewAI Multi-Agent Swarm."
                    
                elif step == "evaluate_risk_level":
                    step_payload["execution_logs"] = [l for l in all_logs if "Triage" in l.get("agent_name", "") or "Evaluate" in l.get("agent_name", "")]
                    status_msg = f"Operational triage evaluation complete. Threat Level: {result_state.get('risk_level', 'NORMAL')}."
                    
                elif step == "generate_briefing":
                    step_payload["final_report"] = result_state.get("final_report")
                    step_payload["execution_logs"] = [l for l in all_logs if "Brief" in l.get("agent_name", "") or "RAG" in l.get("agent_name", "")]
                    status_msg = "Custom SLA-driven operations briefing compiled successfully."
                    
                elif step == "save_report":
                    step_payload["execution_logs"] = [l for l in all_logs if "Save" in l.get("agent_name", "") or "Failsafe" in l.get("agent_name", "")]
                    status_msg = "Completed operations briefing dossier written to database ledger."
                
                step_payload["status"] = status_msg
                
                yield format_sse(step, step_payload)
                await asyncio.sleep(1.0) # beautiful readable flow delay
                
            # Emit: workflow_completed
            duration_ms = (time.time() - start_time) * 1000
            log_workflow_event("/analyze/stream", order_id, "workflow_completed", "SUCCESS", duration_ms)
            
            yield format_sse("workflow_completed", {
                "order_id": order_id,
                "status": "All automated retail triage pipeline operations concluded successfully.",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "risk_level": result_state.get("risk_level", "NORMAL"),
                    "escalation_triggered": result_state.get("escalation_triggered", False),
                    "final_report": result_state.get("final_report"),
                    "duration_ms": duration_ms
                }
            })
            
        except Exception as err:
            duration_ms = (time.time() - start_time) * 1000
            log_workflow_event("/analyze/stream", order_id, "workflow_failed", "ERROR", duration_ms, str(err))
            logger.exception(f"Exception during SSE simulation for order {order_id}: {err}")
            
            # Emit: workflow_error event
            yield format_sse("workflow_error", {
                "order_id": order_id,
                "status": "Operational analysis failed due to system exception.",
                "payload": {"error": "Workflow execution failed."},
                "timestamp": datetime.utcnow().isoformat()
            })

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
