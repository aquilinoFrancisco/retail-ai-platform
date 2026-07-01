import os
import json
from typing import Dict, Any, Optional

from models.schemas import InventorySignal

def read_inventory(sku: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve inventory metrics and stockout telemetry for a specific SKU or all SKUs.
    
    Args:
        sku (str, optional): Unique stock-keeping unit identifier. If None, returns all inventory records.
        
    Returns:
        Dict[str, Any]: Plain JSON-safe dict containing validated inventory telemetry or errors.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    inventory_path = os.path.join(base_dir, "mock_data", "inventory.json")
    
    if not os.path.exists(inventory_path):
        return {"success": False, "error": f"Mock inventory database not found at {inventory_path}"}
        
    try:
        with open(inventory_path, "r", encoding="utf-8") as f:
            raw_inventory = json.load(f)
    except Exception as e:
        return {"success": False, "error": f"Failed to read inventory database: {str(e)}"}
        
    if sku:
        inv_data = raw_inventory.get(sku)
        if not inv_data:
            return {"success": False, "error": f"SKU {sku} not found in inventory catalog."}
        try:
            validated = InventorySignal(**inv_data)
            result = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": f"Inventory validation failed for {sku}: {str(e)}"}
    else:
        validated_inventory = {}
        for s, idata in raw_inventory.items():
            try:
                validated = InventorySignal(**idata)
                validated_inventory[s] = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
            except Exception as e:
                validated_inventory[s] = {"error": f"Validation failed: {str(e)}", "raw": idata}
        return {"success": True, "data": validated_inventory}
