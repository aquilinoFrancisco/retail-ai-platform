import os
import json
from typing import Dict, Any, Optional, List

from models.schemas import DeliveryEvent

def read_delivery_events(tracking_number: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve carrier tracking scans and routing delays for a tracking number or all tracking numbers.
    
    Args:
        tracking_number (str, optional): Carrier transit tracking number. If None, returns all logs.
        
    Returns:
        Dict[str, Any]: Plain JSON-safe dictionary containing validated delivery event lists.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    delivery_path = os.path.join(base_dir, "mock_data", "delivery_events.json")
    
    if not os.path.exists(delivery_path):
        return {"success": False, "error": f"Mock delivery database not found at {delivery_path}"}
        
    try:
        with open(delivery_path, "r", encoding="utf-8") as f:
            raw_delivery = json.load(f)
    except Exception as e:
        return {"success": False, "error": f"Failed to read delivery database: {str(e)}"}
        
    if tracking_number:
        events_list = raw_delivery.get(tracking_number)
        if not events_list:
            return {"success": False, "error": f"Tracking number {tracking_number} not found."}
        try:
            validated_events = []
            for ev in events_list:
                validated = DeliveryEvent(**ev)
                val_dict = json.loads(validated.model_dump_json()) if hasattr(validated, "model_dump_json") else json.loads(validated.json())
                validated_events.append(val_dict)
            return {"success": True, "data": validated_events}
        except Exception as e:
            return {"success": False, "error": f"Delivery logs validation failed for {tracking_number}: {str(e)}"}
    else:
        validated_all = {}
        for trk, events_list in raw_delivery.items():
            try:
                validated_events = []
                for ev in events_list:
                    validated = DeliveryEvent(**ev)
                    val_dict = json.loads(validated.model_dump_json()) if hasattr(validated, "model_dump_json") else json.loads(validated.json())
                    validated_events.append(val_dict)
                validated_all[trk] = validated_events
            except Exception as e:
                validated_all[trk] = {"error": f"Validation failed: {str(e)}", "raw": events_list}
        return {"success": True, "data": validated_all}
