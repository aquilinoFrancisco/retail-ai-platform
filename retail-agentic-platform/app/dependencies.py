from fastapi import Request
from graph.workflow import build_graph

def get_workflow():
    """
    Dependency to retrieve the compiled LangGraph state machine.
    """
    return build_graph()

def get_runtime(request: Request) -> dict:
    """
    Dependency to retrieve the current validated runtime information from app state.
    """
    return getattr(request.app.state, "runtime", {
        "gemini_enabled": False,
        "simulation_mode": True,
        "error": "State runtime not loaded yet"
    })
