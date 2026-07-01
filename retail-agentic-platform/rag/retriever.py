import os
from typing import List, Dict, Any

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")

def retrieve_escalation_rules(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    Scans markdown operational SLA policy documents in the knowledge_base folder,
    searches for matching keywords, and returns matching policy sections.
    """
    results = []
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        return [{"text": "Knowledge base folder missing.", "source": "error"}]
        
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Perform a simplified term-matching scan for Phase 1/2
            sections = content.split("\n## ")
            for section in sections:
                header = section.split("\n")[0]
                # If query keywords exist in section header or body text
                keywords = query.lower().split()
                if any(kw in section.lower() for kw in keywords):
                    results.append({
                        "header": header,
                        "text": section,
                        "source": filename
                    })
                    if len(results) >= top_k:
                        break
        except Exception as e:
            results.append({"text": f"Error loading {filename}: {str(e)}", "source": "error"})
            
    # Default fallback if no custom rules match the exact terms
    if not results:
        results.append({
            "header": "Default Operational SLA Escalarion",
            "text": "For critical errors with no specific regional SLA match, route directly to fulfillment division head.",
            "source": "fallback"
        })
        
    return results[:top_k]
