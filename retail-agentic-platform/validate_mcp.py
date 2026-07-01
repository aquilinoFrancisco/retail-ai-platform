import os
import sys
import glob
import py_compile
import json

def run_compilation():
    print("=== Step 1: Compiling Python Files ===")
    py_files = []
    for root, _, files in os.walk("."):
        # Skip virtual env or cache directories if any
        if any(ignored in root for ignored in ["venv", ".git", "__pycache__"]):
            continue
        for file in files:
            if file.endswith(".py") and file != "validate_mcp.py":
                py_files.append(os.path.join(root, file))
                
    success = True
    for py_file in py_files:
        try:
            py_compile.compile(py_file, doraise=True)
            print(f"  [OK] Compiled: {py_file}")
        except py_compile.PyCompileError as e:
            print(f"  [ERROR] Compilation failed for {py_file}: {e}")
            success = False
            
    return success

def run_tool_tests():
    print("\n=== Step 2: Importing MCPServer ===")
    try:
        from agent_mcp.server import mcp_server
        print("  [OK] Successfully imported mcp_server from agent_mcp.server")
    except Exception as e:
        print(f"  [ERROR] Failed to import mcp_server: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n=== Step 3: Executing One Call Per Tool ===")
    
    # Define test calls for each registered tool
    test_cases = [
        {
            "name": "get_order_details",
            "kwargs": {"order_id": "ORD-2026-9901"}
        },
        {
            "name": "get_inventory_levels",
            "kwargs": {"sku": "SKU-HEADSET-99"}
        },
        {
            "name": "get_delivery_events",
            "kwargs": {"tracking_number": "TRK-FEDEX-9910"}
        },
        {
            "name": "get_customer_tickets",
            "kwargs": {"ticket_id": "TCK-4491"}
        },
        {
            "name": "rag_query_retriever",
            "kwargs": {"query": "fraud"}
        },
        {
            "name": "calculate_operational_risk",
            "kwargs": {
                "order_id": "ORD-2026-9901",
                "order_data": {
                    "payment": {
                        "fraud_score": 87,
                        "amount": 1499.00
                    }
                },
                "inventory_data": {
                    "stock_on_hand": 0,
                    "replenishment_status": "Delayed - Customs Hold"
                },
                "delivery_data": [
                    {
                        "tracking_number": "TRK-FEDEX-9910",
                        "activity": "Shipment exception - Weather delay"
                    }
                ],
                "ticket_data": [
                    {
                        "ticket_id": "TCK-4491",
                        "sentiment_score": 0.12,
                        "urgency": "CRITICAL",
                        "subject": "Fulfillment Delay and Billing Dispute"
                    }
                ]
            }
        },
        {
            "name": "save_operations_briefing",
            "kwargs": {
                "briefing": {
                    "order_id": "ORD-2026-9901",
                    "calculated_risk_level": "CRITICAL",
                    "matched_vulnerabilities": ["Suspicious Transaction - High Fraud Risk"],
                    "summary_brief": "CRITICAL RISK MATCHED: High fraud probability.",
                    "action_items": ["LOSS PREVENTION MANDATE: Hold shipment."],
                    "escalation_triggered": True,
                    "escalation_contacts": ["lossprevention@retail-agentic.com"]
                }
            }
        }
    ]

    all_ok = True
    for tc in test_cases:
        tool_name = tc["name"]
        kwargs = tc["kwargs"]
        print(f"\nExecuting tool: '{tool_name}'...")
        try:
            result = mcp_server.execute_tool(tool_name, **kwargs)
            # Verify it returns a dict
            if not isinstance(result, dict):
                print(f"  [ERROR] '{tool_name}' returned non-dict result: {type(result)}")
                all_ok = False
                continue
                
            # Verify it is JSON-safe by dumps/loads
            try:
                serialized = json.dumps(result)
                json.loads(serialized)
                print(f"  [OK] '{tool_name}' executed and returned JSON-safe dict.")
                # Print a slice of the output for visual confirmation
                print(f"       Result preview: {str(result)[:160]}...")
            except Exception as je:
                print(f"  [ERROR] '{tool_name}' returned non-JSON-serializable data: {je}")
                all_ok = False
        except Exception as e:
            print(f"  [ERROR] Execution of '{tool_name}' threw exception: {e}")
            import traceback
            traceback.print_exc()
            all_ok = False

    return all_ok

if __name__ == "__main__":
    compilation_ok = run_compilation()
    if not compilation_ok:
        sys.exit(1)
        
    tests_ok = run_tool_tests()
    if not tests_ok:
        sys.exit(1)
        
    print("\n=== Validation Completed Successfully! ===")
    sys.exit(0)
