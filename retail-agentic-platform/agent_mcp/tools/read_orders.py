import os
import json
from typing import Dict, Any, Optional

from models.schemas import OrderEvent

def read_orders(order_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve one or all order events from the mock database, validated against the OrderEvent Pydantic schema.
    
    Args:
        order_id (str, optional): Unique order identifier. If None, returns all orders.
        
    Returns:
        Dict[str, Any]: A JSON-safe dictionary containing the requested order(s) or an error/empty message.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    orders_path = os.path.join(base_dir, "mock_data", "orders.json")
    
    if not os.path.exists(orders_path):
        return {"success": False, "error": f"Mock orders database not found at {orders_path}"}
        
    try:
        with open(orders_path, "r", encoding="utf-8") as f:
            raw_orders = json.load(f)
    except Exception as e:
        return {"success": False, "error": f"Failed to read orders database: {str(e)}"}
        
    if order_id:
        order_data = raw_orders.get(order_id)
        if not order_data:
            return {"success": False, "error": f"Order {order_id} not found."}
        try:
            # Validate with Pydantic
            validated = OrderEvent(**order_data)
            # Convert to dictionary
            result = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": f"Order validation failed for {order_id}: {str(e)}"}
    else:
        # Validate all orders and return them
        validated_orders = {}
        for oid, odata in raw_orders.items():
            try:
                validated = OrderEvent(**odata)
                validated_orders[oid] = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
            except Exception as e:
                validated_orders[oid] = {"error": f"Validation failed: {str(e)}", "raw": odata}
        return {"success": True, "data": validated_orders}
