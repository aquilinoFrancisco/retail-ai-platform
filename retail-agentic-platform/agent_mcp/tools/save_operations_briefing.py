import os
import json
from typing import Dict, Any

from models.schemas import OperationalRiskAssessment

def save_operations_briefing(briefing: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and commit the finalized operations briefing dossier to the logging database disk.
    
    Args:
        briefing (Dict[str, Any]): Dictionary conforming to the OperationalRiskAssessment model.
        
    Returns:
        Dict[str, Any]: plain JSON-safe dict confirming save execution status and file paths.
    """
    try:
        # Validate input
        validated = OperationalRiskAssessment(**briefing)
        briefing_dict = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
    except Exception as e:
        return {"success": False, "error": f"Invalid briefing structure: {str(e)}"}
        
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    briefings_dir = os.path.join(base_dir, "mock_data", "briefings")
    
    # Create briefings directory if not exists
    os.makedirs(briefings_dir, exist_ok=True)
    
    order_id = briefing_dict.get("order_id", "UNKNOWN")
    filepath = os.path.join(briefings_dir, f"{order_id}_briefing.json")
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(briefing_dict, f, indent=2)
            
        return {
            "success": True,
            "message": f"Successfully persisted incident dossier for order {order_id}.",
            "file_path": filepath,
            "data": briefing_dict
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to persist dossier file: {str(e)}"}
