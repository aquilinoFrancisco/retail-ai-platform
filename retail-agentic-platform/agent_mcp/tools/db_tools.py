import json
import os
from typing import Dict, Any, List

MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mock_data")

def get_order_details(order_id: str) -> Dict[str, Any]:
    """
    Retrieve structured financial, itemized, and shipping metadata for an order.
    
    Args:
        order_id: Unique order ID (e.g. 'ORD-2026-9901')
    """
    path = os.path.join(MOCK_DATA_DIR, "orders.json")
    if not os.path.exists(path):
        return {"error": "Mock database not initialized."}
        
    try:
        with open(path, "r") as f:
            orders = json.load(f)
        return orders.get(order_id, {"error": f"Order {order_id} not found."})
    except Exception as e:
        return {"error": f"Database read failure: {str(e)}"}


def get_inventory_levels(sku: str) -> Dict[str, Any]:
    """
    Check stock availability and warehouse allocation for a particular stock-keeping unit.
    
    Args:
        sku: Unique item SKU identifier (e.g. 'SKU-HEADSET-99')
    """
    path = os.path.join(MOCK_DATA_DIR, "inventory.json")
    if not os.path.exists(path):
        return {"error": "Mock inventory ledger not initialized."}
        
    try:
        with open(path, "r") as f:
            inventory = json.load(f)
        return inventory.get(sku, {"error": f"SKU {sku} not found in catalog."})
    except Exception as e:
        return {"error": f"Inventory ledger read failure: {str(e)}"}


def get_delivery_events(tracking_number: str) -> List[Dict[str, Any]]:
    """
    Fetch raw logistics logs, transit delay exceptions, and carrier timestamps.
    
    Args:
        tracking_number: Package transit carrier identifier
    """
    path = os.path.join(MOCK_DATA_DIR, "delivery_events.json")
    if not os.path.exists(path):
        return [{"error": "Delivery registry not initialized."}]
        
    try:
        with open(path, "r") as f:
            events = json.load(f)
        return events.get(tracking_number, [{"error": f"Tracking number {tracking_number} not found."}])
    except Exception as e:
        return [{"error": f"Logistics tracker read failure: {str(e)}"}]
