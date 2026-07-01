import os
import logging
from typing import Dict, Any
from crew.retail_crew import RetailCrew

logger = logging.getLogger("retail_platform.startup")

def validate_runtime() -> Dict[str, Any]:
    """
    Validates the execution environment during application startup.
    Tests the RetailCrew runtime to verify if live Gemini LLM integration is
    fully functional or if the system should seamlessly use the high-fidelity 
    deterministic simulation mode.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    gemini_enabled = bool(api_key)
    simulation_mode = not gemini_enabled
    error_msg = None

    try:
        # Try to instantiate the RetailCrew and run a test execution
        crew = RetailCrew()
        # Test-run the crew to ensure it doesn't fail catastrophically
        res = crew.run("ORD-001")
        
        # If we reached here, instantiation and execution succeeded.
        # Now let's check what mode was actually used by the crew.
        # RetailCrew.run return dict includes 'mode': 'live_crewai' or 'simulated_crewai'
        mode = res.get("mode", "simulated_crewai")
        if mode == "live_crewai":
            gemini_enabled = True
            simulation_mode = False
        else:
            # Even if API key is present, if the crew opted for simulated, respect that
            gemini_enabled = False
            simulation_mode = True

    except Exception as e:
        logger.warning(
            f"Startup validation check for live Gemini/CrewAI execution failed: {e}. "
            f"Falling back to high-fidelity rule-grounded simulation mode."
        )
        gemini_enabled = False
        simulation_mode = True
        error_msg = str(e)

    return {
        "gemini_enabled": gemini_enabled,
        "simulation_mode": simulation_mode,
        "error": error_msg
    }
