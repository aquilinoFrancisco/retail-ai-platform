from typing import Dict, Any, List, Optional

from models.schemas import OperationalRiskAssessment

def calculate_operational_risk(
    order_id: str,
    order_data: Optional[Dict[str, Any]] = None,
    inventory_data: Optional[Dict[str, Any]] = None,
    delivery_data: Optional[List[Dict[str, Any]]] = None,
    ticket_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Apply multi-vector operational rules to evaluate retail risk level.
    Correlates inventory shortages, delivery holds, billing fraud indicators, and active customer sentiment.
    
    Args:
        order_id (str): Unique order identifier.
        order_data (Dict[str, Any], optional): Order details.
        inventory_data (Dict[str, Any], optional): Inventory telemetry.
        delivery_data (List[Dict[str, Any]], optional): Carrier scan events list.
        ticket_data (List[Dict[str, Any]], optional): Customer support tickets list.
        
    Returns:
        Dict[str, Any]: A plain JSON-safe dictionary conforming to OperationalRiskAssessment.
    """
    matched_vulnerabilities = []
    calculated_risk_level = "NORMAL"
    summary_brief = "Order is processing normally with no detected operational friction."
    action_items = []
    escalation_triggered = False
    escalation_contacts = []
    
    # 1. Analyze Fraud score & Order amount
    fraud_score = 0
    order_amount = 0.0
    if order_data:
        payment = order_data.get("payment", {})
        fraud_score = payment.get("fraud_score", 0)
        order_amount = payment.get("amount", 0.0)
        
        if fraud_score > 75:
            matched_vulnerabilities.append("Suspicious Transaction - High Fraud Risk")
        elif fraud_score > 40:
            matched_vulnerabilities.append("Moderate Transaction Risk Profile")
            
    # 2. Analyze Inventory Stockout & Replenishment status
    stock_on_hand = 999
    replenishment_status = "Normal"
    if inventory_data:
        stock_on_hand = inventory_data.get("stock_on_hand", 999)
        replenishment_status = inventory_data.get("replenishment_status", "Normal")
        
        if stock_on_hand == 0:
            matched_vulnerabilities.append(f"Warehouse Stockout (Status: {replenishment_status})")
            
    # 3. Analyze Carrier Exceptions & Logistics hold
    has_transit_exception = False
    if delivery_data:
        for ev in delivery_data:
            activity = ev.get("activity", "").lower()
            if "exception" in activity or "hold" in activity or "delay" in activity:
                has_transit_exception = True
                matched_vulnerabilities.append(f"Logistics Exception: {ev.get('activity')}")
                break
                
    # 4. Analyze Ticket sentiment & urgency
    lowest_sentiment = 1.0
    has_critical_ticket = False
    if ticket_data:
        for ticket in ticket_data:
            if ticket.get("status") == "none":
                continue
            sentiment = ticket.get("sentiment_score", 1.0)
            urgency = ticket.get("urgency", "LOW")
            
            if sentiment < lowest_sentiment:
                lowest_sentiment = sentiment
                
            if urgency in ["HIGH", "CRITICAL"]:
                has_critical_ticket = True
                matched_vulnerabilities.append(f"Escalated Customer Grievance: {ticket.get('subject')}")
                
    # --- 5. Risk Assessment Decision Matrix ---
    
    # Check CRITICAL criteria
    is_fraud_critical = (fraud_score > 75 and order_amount > 1000)
    is_stockout_sentiment_critical = (stock_on_hand == 0 and lowest_sentiment < 0.20 and has_critical_ticket)
    
    if is_fraud_critical or is_stockout_sentiment_critical:
        calculated_risk_level = "CRITICAL"
        escalation_triggered = True
        
        if is_fraud_critical:
            summary_brief = (
                f"CRITICAL RISK MATCHED. Order {order_id} carries severe billing risk. "
                f"Transaction value of ${order_amount:.2f} flagged with high fraud probability index ({fraud_score}/100)."
            )
            action_items.append("LOSS PREVENTION MANDATE: Put immediate security hold on shipment.")
            action_items.append("Contact loss prevention squad for physical card verification.")
            escalation_contacts.append("lossprevention@retail-agentic.com")
        else:
            summary_brief = (
                f"CRITICAL RISK MATCHED. High-priority customer order {order_id} is facing an out-of-stock warehouse block "
                f"({replenishment_status}) coupled with an angry VIP sentiment ({lowest_sentiment}) threat."
            )
            action_items.append("Notify regional supply planners to route substitute inventory immediately.")
            action_items.append("Issue automated cx compensation of a 20% promotional coupon.")
            escalation_contacts.append("supplychain-lead@retail-agentic.com")
            escalation_contacts.append("cx-escalations@retail-agentic.com")
            
    # Check HIGH criteria
    elif (stock_on_hand == 0 and ("Delayed" in replenishment_status or "Hold" in replenishment_status)) or lowest_sentiment < 0.40 or has_critical_ticket:
        calculated_risk_level = "HIGH"
        summary_brief = f"HIGH RISK ASSIGNED. Order {order_id} exhibits logistics bottlenecks or customer agitation."
        action_items.append("Alert fulfillment coordinators to audit regional stocks.")
        action_items.append("Dispatch standard courtesy update advising of delayed timeline.")
        
    # Check MEDIUM criteria
    elif stock_on_hand == 0 or has_transit_exception or lowest_sentiment < 0.60:
        calculated_risk_level = "MEDIUM"
        summary_brief = f"MEDIUM RISK ASSIGNED. Minor supply lag or shipping re-routing found for {order_id}."
        action_items.append("Attach warning indicator badge in regional telemetry stream.")
        
    else:
        calculated_risk_level = "NORMAL"
        summary_brief = f"Order {order_id} matches all criteria for standard logistics operations."
        action_items.append("Release order to standard warehouse pipeline.")
        
    try:
        assessment = OperationalRiskAssessment(
            order_id=order_id,
            calculated_risk_level=calculated_risk_level,
            matched_vulnerabilities=matched_vulnerabilities,
            summary_brief=summary_brief,
            action_items=action_items,
            escalation_triggered=escalation_triggered,
            escalation_contacts=escalation_contacts
        )
        return assessment.model_dump() if hasattr(assessment, "model_dump") else assessment.dict()
    except Exception as e:
        return {
            "order_id": order_id,
            "calculated_risk_level": calculated_risk_level,
            "matched_vulnerabilities": matched_vulnerabilities,
            "summary_brief": summary_brief,
            "action_items": action_items,
            "escalation_triggered": escalation_triggered,
            "escalation_contacts": escalation_contacts,
            "validation_error": str(e)
        }
