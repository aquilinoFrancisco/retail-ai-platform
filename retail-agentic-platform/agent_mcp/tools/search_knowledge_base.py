import os
from typing import Dict, Any, List

from models.schemas import AgentStep

def search_knowledge_base(query: str) -> Dict[str, Any]:
    """
    Search the local markdown knowledge base for SLA policies, compliance rules, and escalation contact details.
    
    Args:
        query (str): The search keyword or phrase (e.g., 'fraud', 'stockout', 'VIP').
        
    Returns:
        Dict[str, Any]: plain JSON-safe dict containing matched sections and source metadata.
    """
    # Create an AgentStep just to demonstrate importing and validating against models/schemas.py
    try:
        step = AgentStep(
            agent_name="KnowledgeBaseRetriever",
            action_taken=f"Search Query: {query}",
            thought_process="Scanning local markdown files for keywords to retrieve matching SLA protocols.",
            result_summary="Success"
        )
    except Exception:
        pass

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    kb_paths = [
        os.path.join(base_dir, "mock_data", "knowledge_base"),
        os.path.join(base_dir, "knowledge_base")
    ]
    
    matched_sections = []
    
    for kb_path in kb_paths:
        if not os.path.exists(kb_path):
            continue
            
        for filename in os.listdir(kb_path):
            if not filename.endswith(".md"):
                continue
                
            filepath = os.path.join(kb_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Split by markdown headers
                sections = content.split("\n## ")
                for index, section in enumerate(sections):
                    # Clean section header
                    header = section.split("\n")[0].strip("# ")
                    
                    # Basic term-matching check
                    keywords = query.lower().split()
                    if any(kw in section.lower() for kw in keywords):
                        matched_sections.append({
                            "header": header or "Overview",
                            "content": section.strip(),
                            "source_file": filename,
                            "section_index": index
                        })
            except Exception as e:
                return {"success": False, "error": f"Error reading {filename}: {str(e)}"}
                
    if not matched_sections:
        return {
            "success": True,
            "data": [],
            "message": f"No specific SLA escalation policies found matching search query: '{query}'."
        }
        
    return {
        "success": True,
        "data": matched_sections
    }
