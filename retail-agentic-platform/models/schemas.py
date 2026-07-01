from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- 1. Base Domain Entities ---

class CustomerInfo(BaseModel):
    name: str = Field(..., description="Customer full name")
    email: str = Field(..., description="Customer contact email")
    loyalty_tier: str = Field(..., description="Customer loyalty tier (e.g., VIP, Regular, Guest)")

class PaymentInfo(BaseModel):
    amount: float = Field(..., description="Total transactional value of the purchase")
    method: str = Field(..., description="Payment instrument used (e.g., Credit Card, PayPal)")
    fraud_score: int = Field(..., description="Risk evaluation score from payment gateway (0-100)")
    ip_address: str = Field(..., description="Origin IP of the checkout request")
    risk_flag: bool = Field(..., description="Boolean flag raised by real-time fraud engines")

class LineItem(BaseModel):
    sku: str = Field(..., description="Stock Keeping Unit code")
    name: str = Field(..., description="Display name of the catalog product")
    quantity: int = Field(..., description="Quantity of items purchased")
    price: float = Field(..., description="Unit price of the item")

class FulfillmentStatus(BaseModel):
    status: str = Field(..., description="Fulfillment stage (e.g., Awaiting Stock, In Transit, Shipped, Delivered)")
    warehouse_id: str = Field(..., description="Allocated fulfillment hub identifier")
    tracking_number: Optional[str] = Field(None, description="Carrier shipping tracking number")


# --- 2. Phase 2 Mandatory Schemas ---

class OrderEvent(BaseModel):
    """
    Schema for a retail order events, containing comprehensive transaction,
    itemized line lists, and current logistics tracking states.
    """
    order_id: str = Field(..., description="Unique retail identifier (e.g., ORD-2026-1001)")
    customer: CustomerInfo
    payment: PaymentInfo
    items: List[LineItem]
    fulfillment: FulfillmentStatus


class InventorySignal(BaseModel):
    """
    Schema for inventory availability updates and regional warehouse supply telemetry.
    """
    sku: str = Field(..., description="Stock Keeping Unit identifier")
    allocated_warehouse: str = Field(..., description="Warehouse housing this stock")
    stock_on_hand: int = Field(..., description="Physical item units currently on shelves")
    reserved: int = Field(..., description="Item units committed to active orders")
    backorder_lead_days: int = Field(..., description="Days expected for replenishment of out-of-stock items")
    replenishment_status: str = Field(..., description="Current shipment restocking flag (e.g., Normal, Delayed, On Hold)")
    unit_cost: float = Field(..., description="Supplier unit cost of the SKU")


class DeliveryEvent(BaseModel):
    """
    Schema for carrier transit events, delays, and tracking updates.
    """
    tracking_number: str = Field(..., description="Fulfillment logistics tracking carrier ID")
    timestamp: datetime = Field(..., description="ISO 8601 log occurrence timestamp")
    location: str = Field(..., description="Carrier transit scanning facility location")
    activity: str = Field(..., description="Reported transit status details or delay exception logs")
    carrier: str = Field(..., description="Carrier name (e.g., FedEx, UPS, DHL)")


class CustomerTicket(BaseModel):
    """
    Schema representing active customer support tickets and sentiment analytics.
    """
    ticket_id: str = Field(..., description="Unique customer ticket identifier")
    order_id: str = Field(..., description="Order identifier associated with the ticket")
    customer_name: str = Field(..., description="Name of the customer lodging the support issue")
    created_at: datetime = Field(..., description="Time of ticket creation")
    subject: str = Field(..., description="Summarized concern subject header")
    description: str = Field(..., description="Raw text of customer support description and complaint")
    sentiment_score: float = Field(..., description="Computed sentiment valence score (0.0 extremely negative to 1.0 positive)")
    urgency: str = Field(..., description="Ticket classification triage level (e.g., LOW, MEDIUM, HIGH, CRITICAL)")


# --- 3. Operational Risk & System Orchestration Schemas ---

class OperationalRiskAssessment(BaseModel):
    """
    Dossier schema summarizing operational risk assessment findings for an order.
    """
    order_id: str = Field(..., description="Order under evaluation")
    calculated_risk_level: str = Field(..., description="Evaluated operational severity status (NORMAL, MEDIUM, HIGH, CRITICAL)")
    matched_vulnerabilities: List[str] = Field(default_factory=list, description="Categorized risks matched (e.g., Stockout, Carrier Hold, Credit Fraud)")
    summary_brief: str = Field(..., description="Narrative analysis brief explaining the friction indicators")
    action_items: List[str] = Field(default_factory=list, description="RAG SLA-driven escalation paths and steps to mitigate risk")
    escalation_triggered: bool = Field(default=False, description="Whether regional SLA escalation workflows were executed")
    escalation_contacts: List[str] = Field(default_factory=list, description="Relevant contact emails matched from operational manuals")


class AgentStep(BaseModel):
    """
    Tracing schema capturing individual agent execution cycles and tool invocation states.
    """
    agent_name: str = Field(..., description="Specialized CrewAI agent triggering this step")
    action_taken: str = Field(..., description="The tool or reasoning path undertaken")
    thought_process: str = Field(..., description="Underlying analysis logic of the agent")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Log creation timestamp")
    result_summary: str = Field(..., description="Brief outcome of tool execution or thought completion")


class StreamingEvent(BaseModel):
    """
    SSE Stream envelope format ensuring unified log formats down the async channel.
    """
    node: str = Field(..., description="Active state transition node inside LangGraph")
    status: str = Field(..., description="Human-readable event logs detailing agent progress")
    payload: Dict[str, Any] = Field(default_factory=dict, description="State variables, telemetry details, or risk briefs")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of event emit")
