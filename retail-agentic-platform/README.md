# Retail Agentic Platform

An enterprise-grade, stateful AI orchestration system designed to detect and triage operational risks in retail fulfillment, order processing, and customer support.

This project is built as a backend portfolio demonstrating clean architecture for a **Senior Backend Engineer — AI Agentic Platform** role.

## Technical Stack
- **Python 3.11** - Main backend runtime
- **FastAPI** - High-performance async API framework with streaming endpoints
- **LangGraph** - Deterministic state machine and agent workflow orchestration
- **CrewAI** - Multi-agent collaboration swarm for specialized sub-tasks
- **MCP-style Tools** - Decoupled Model Context Protocol tools for data retrieval
- **Local RAG** - Text similarity knowledge retrieval for dynamic SLA escalations
- **Mock Data Layer** - Pre-configured retail schemas simulating production anomalies

## Repository Structure
```
retail-agentic-platform/
├── app/
│   └── main.py                  # FastAPI entry point & streaming router
├── graph/
│   ├── __init__.py
│   ├── state.py                 # LangGraph state schema definition
│   └── workflow.py              # Workflows, routing, and graph compilation
├── crew/
│   ├── __init__.py
│   ├── agents.py                # Specialized CrewAI Agent definitions
│   └── tasks.py                 # Multi-agent task configurations
├── agent_mcp/
│   ├── __init__.py
│   └── tools/
│       ├── __init__.py
│       ├── db_tools.py          # Database, shipping, & inventory tools
│       └── ticket_tools.py      # Customer support ticketing tools
├── rag/
│   ├── __init__.py
│   ├── embeddings.py            # Local document chunking & indexing
│   └── retriever.py             # Knowledge retrieval mechanism
├── mock_data/
│   ├── orders.json              # Mock orders (with fraud & delays)
│   ├── inventory.json           # Stockout & replenishment telemetry
│   ├── delivery_events.json     # Carrier delay logs & exceptions
│   └── tickets.json             # High-priority customer tickets
└── knowledge_base/
    ├── escalation_rules.md      # SLA protocols and contact matrix
    └── risk_framework.md        # Operational risk evaluation tiers
```

## Workflow Pipeline
1. **`collect_data`**: Aggregates order info, inventory statuses, carrier tracking events, and active customer support tickets using MCP tools.
2. **`analyze_operational_risk`**: Spins up the CrewAI swarm to identify correlation between stockouts, delivery exceptions, and fraud flags.
3. **`evaluate_risk_level`**: Evaluates whether the calculated exposure exceeds SLA limits, classifying it as `CRITICAL` or `NORMAL`.
4. **Branching**:
   - `CRITICAL` ➔ **`incident_briefing`**: Invokes the RAG retrieval engine to extract exact escalation rules, warehouse contacts, and legal compliance workflows.
   - `NORMAL` ➔ **`standard_briefing`**: Compiles standard resolution summaries and templates.
5. **`save_report`**: Commits findings to the operational logging database and triggers streaming notifications.
