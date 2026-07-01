import os
import json
from typing import Dict, Any, Optional, List

from models.schemas import CustomerTicket

def read_customer_tickets(ticket_id: Optional[str] = None, order_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve support ticketing logs and customer sentiment analytics from tickets database.
    
    Args:
        ticket_id (str, optional): Specific support ticket ID.
        order_id (str, optional): Filter tickets linked to a specific retail order ID.
        
    Returns:
        Dict[str, Any]: Plain JSON-safe dictionary containing validated support tickets.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    tickets_path = os.path.join(base_dir, "mock_data", "tickets.json")
    
    if not os.path.exists(tickets_path):
        return {"success": False, "error": f"Mock tickets database not found at {tickets_path}"}
        
    try:
        with open(tickets_path, "r", encoding="utf-8") as f:
            raw_tickets = json.load(f)
    except Exception as e:
        return {"success": False, "error": f"Failed to read tickets database: {str(e)}"}
        
    validated_tickets = []
    for tk in raw_tickets:
        try:
            validated = CustomerTicket(**tk)
            val_dict = json.loads(validated.model_dump_json()) if hasattr(validated, "model_dump_json") else json.loads(validated.json())
            validated_tickets.append(val_dict)
        except Exception as e:
            tk_err = dict(tk)
            tk_err["validation_error"] = str(e)
            validated_tickets.append(tk_err)
            
    if ticket_id:
        match = [t for t in validated_tickets if t.get("ticket_id") == ticket_id]
        if not match:
            return {"success": False, "error": f"Ticket {ticket_id} not found."}
        return {"success": True, "data": match[0]}
        
    if order_id:
        matches = [t for t in validated_tickets if t.get("order_id") == order_id]
        return {"success": True, "data": matches}
        
    return {"success": True, "data": validated_tickets}
