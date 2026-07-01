# Retail Operational Risk Framework

This framework outlines the risk evaluation matrix used by the `RetailRiskAnalyst` and `OperationsReporter` to categorize order failures.

## Risk Classification Levels

### 1. NORMAL RISK
- **Criteria**: All items in stock, carrier delivery on schedule, fraud score below 20, no active customer complaints.
- **SLA Action**: Process standard labeling and let order flow naturally through regional carrier. No reports required.

### 2. MEDIUM RISK
- **Criteria**: Short stockout (< 3 days delay) OR minor carrier routing exception (< 1 day delay). No fraud indicators.
- **SLA Action**: Append a warning badge to the order status. Automate restocking triggers.

### 3. HIGH RISK
- **Criteria**: Item out-of-stock for over 7 days, OR customer ticket expresses mild anger (sentiment < 0.40).
- **SLA Action**: Alert secondary carrier, send automated apology email with free shipping refund.

### 4. CRITICAL RISK
- **Criteria**: Order fraud rating > 75 AND order value > $1000, OR item out-of-stock with customs delay AND customer sentiment is low (sentiment < 0.20) with active chargeback threat.
- **SLA Action**: Immediately halt fulfillment pipeline, execute RAG Escalation Protocol, notify executive directors, and draft full risk audit.
