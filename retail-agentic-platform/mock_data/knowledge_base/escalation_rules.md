# Operational SLA and Escalation Protocols

This operational reference manual details retail fulfillment SLAs and explicit points of contact across geographic locations. Use this during critical incidents to route the generated dossier.

## 1. High-Value Order Fraud Triage
- **Trigger Condition**: Any payment transaction where `fraud_score` exceeds **75** and order value is greater than **$1000**.
- **System Action**: Place immediate security hold on shipment in the Warehouse Management System (WMS). Do not generate tracking labels.
- **Primary Contact**: Director of Loss Prevention (lossprevention@retail-agentic.com)
- **Legal Mandate**: Hold order for 48 hours for manual customer verification before initiating order cancellation and refund.

## 2. Warehouse Stockout Exceptions
- **Trigger Condition**: Any high-priority customer order where warehouse allocation displays zero stock on hand (`stock_on_hand == 0`) and replenishment lead days are greater than 7.
- **System Action**: Scan alternate warehouses within a 500-mile geographic radius. If no alternate inventory exists, trigger direct procurement alerts.
- **Primary Contact**: Supply Chain Operations Manager (supplychain-lead@retail-agentic.com)
- **Fulfillment SLA**: Within 24 hours of stockout detection, customer loyalty VIPs must be sent an automated apology alongside a 20% promotional coupon or equivalent item substitution.

## 3. High-Priority Support Escalations
- **Trigger Condition**: Any active support ticket where customer sentiment falls below **0.20** and urgency is tagged as `CRITICAL` or `HIGH`.
- **System Action**: Flag customer profile, dispatch immediate alerts to regional support directors, and append shipment transit logs.
- **Primary Contact**: VP of Global Customer Experience (cx-escalations@retail-agentic.com)
- **Escalation Window**: Mandatory executive contact or live representative callback within 2 business hours of ticket ingestion.
