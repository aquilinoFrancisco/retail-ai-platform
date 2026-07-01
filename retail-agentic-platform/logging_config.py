import os
import logging
from logging.handlers import RotatingFileHandler

# Langfuse-ready extension point. 
# This module configures a structured and audit-ready logging framework 
# that can be easily plugged into LLM observability frameworks like Langfuse, 
# Arize Phoenix, or LangSmith.

LOGS_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "workflow.log")

# Define logging format
# We'll support both standard logs and structured format logging
log_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# File Handler for Rotating Logs
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Setup Logger
logger = logging.getLogger("retail_platform")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Specific workflow logger for Phase 5 auditing
workflow_logger = logging.getLogger("retail_platform.workflow")

def log_workflow_event(
    endpoint: str,
    order_id: str,
    event: str,
    status: str,
    duration_ms: float,
    exception: str = "None"
):
    """
    Log a structured operational workflow event to logs/workflow.log.
    Format: timestamp | endpoint | order_id | event | status | duration_ms | exception
    """
    msg = f"endpoint={endpoint} | order_id={order_id} | event={event} | status={status} | duration_ms={duration_ms:.2f} | exception={exception}"
    workflow_logger.info(msg)
