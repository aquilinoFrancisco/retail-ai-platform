# Operational SLA and Escalation Protocols

This document details the retail fulfillment SLAs and escalation points of contact across geographic locations. Use this during critical incidents to route the generated dossier.

## 1. High-Value Order Fraud Triage
- **Trigger**: Any payment transaction where `fraud_score` exceeds **75** and order value is greater than **$1000**.
- **Action**: Place immediate hold on shipment in the WMS (Warehouse Management System). Do not print shipping label.
- **Primary Contact**: Director of Loss Prevention (lossprevention@retail-agentic.com)
- **Legal Mandate**: Hold order for 48 hours for billing verification before routing to cancellation team.

## 2. Warehouse Stockout Exceptions
- **Trigger**: Any high-priority customer order where warehouse allocation displays zero stock hand (`stock_on_hand == 0`) and replenishment is delayed.
- **Action**: Scan secondary warehouses within 500 miles. If not found, notify inventory planners.
- **Primary Contact**: Supply Chain Operations Manager (supplychain-lead@retail-agentic.com)
- **Fulfillment SLA**: Within 24 hours of stockout identification, customer loyalty tier VIP must be offered a premium alternative or a 20% discount coupon.

## 3. High-Priority Support Escalations
- **Trigger**: Tickets with `sentiment_score` below **0.20** and urgency is `CRITICAL`.
- **Action**: Alert Customer Success escalation managers and link the full delivery logs.
- **Primary Contact**: VP of Global Customer Experience (cx-escalations@retail-agentic.com)
