from crewai import Task, Agent

def create_data_collection_task(agent: Agent, order_id: str) -> Task:
    """
    Task to aggregate and structure raw retail logs.
    """
    return Task(
        description=(
            f"Query databases using available tools to collect all data for order ID: '{order_id}'.\n"
            "This includes order metadata, inventory status of items in the order, logistics transit tracking events,\n"
            "and active customer support tickets. Summarize these inputs into a consolidated JSON/text profile."
        ),
        expected_output=(
            "A structured summary profile highlighting key telemetry points: billing amount, fraud score, "
            "shelving counts, logistics exceptions, and negative customer support logs."
        ),
        agent=agent
    )

def create_risk_analysis_task(agent: Agent, order_id: str) -> Task:
    """
    Task to correlate multi-vector operational signals.
    """
    return Task(
        description=(
            f"Review the data profile collected for order ID '{order_id}'.\n"
            "Run operational risk assessment rules cross-checking four primary vectors:\n"
            "1. Financial/Fraud Vector (order value vs payment risk indices)\n"
            "2. Inventory/Fulfillment Vector (shelving stock vs backorder delays)\n"
            "3. Carrier/Logistics Vector (transit exceptions, customs or weather holds)\n"
            "4. Customer Sentiment/CRM Vector (ticket quantity, extreme urgency, low sentiment score)\n\n"
            "Determine the overall operational risk score: NORMAL, MEDIUM, HIGH, or CRITICAL."
        ),
        expected_output=(
            "An audited operational risk summary that correlates all issues, names vulnerabilities found, "
            "and justifies the final risk rating of either NORMAL, MEDIUM, HIGH, or CRITICAL."
        ),
        agent=agent
    )

def create_operations_reporting_task(agent: Agent, order_id: str) -> Task:
    """
    Task to compile executive incident briefings and SLA mitigation actions.
    """
    return Task(
        description=(
            f"Take the operational risk analysis report for order ID '{order_id}'.\n"
            "If the risk rating is HIGH or CRITICAL, query the local knowledge base using search_knowledge_base\n"
            "to retrieve matching SLA policies, escalation guidelines, and key compliance contact emails.\n"
            "Construct a fully detailed markdown incident dossier and save it using save_operations_briefing tool."
        ),
        expected_output=(
            "A finalized operations briefing report including situation overview, mitigation plan, "
            "applicable SLA compliance terms, escalation email list, and saving operation status."
        ),
        agent=agent
    )
