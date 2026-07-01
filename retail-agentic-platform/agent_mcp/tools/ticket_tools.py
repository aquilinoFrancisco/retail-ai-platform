import json
import os
from typing import List, Dict, Any

MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mock_data")

def get_customer_tickets(order_id: str) -> List[Dict[str, Any]]:
    """
    Fetch support ticket histories, customer anger ratings, and recurring claims for an order.
    
    Args:
        order_id: Unique order ID (e.g. 'ORD-2026-9901')
    """
    path = os.path.join(MOCK_DATA_DIR, "tickets.json")
    if not os.path.exists(path):
        return [{"error": "Ticketing registry not initialized."}]
        
    try:
        with open(path, "r") as f:
            tickets = json.load(f)
        # Filter tickets by matching order_id
        matching_tickets = [t for t in tickets if t.get("order_id") == order_id]
        return matching_tickets if matching_tickets else [{"status": "none", "message": f"No active support tickets found for order {order_id}."}]
    except Exception as e:
        return [{"error": f"Ticketing registry read failure: {str(e)}"}]
