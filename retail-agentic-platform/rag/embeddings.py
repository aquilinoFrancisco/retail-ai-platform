# RAG Chunking and Embeddings Helper
# Under Phase 2, this can utilize a local lightweight sentence-transformer or tf-idf model.

from typing import List, Dict, Any

def chunk_document(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split operational SLA markdown documents into standard semantic chunks.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks

def mock_get_embedding(text: str) -> List[float]:
    """
    Generates a high-dimensional vector for a string.
    Placeholder returns a 128-dim mock normalized float vector.
    """
    import random
    random.seed(len(text))
    vector = [random.random() for _ in range(128)]
    # Normalize
    norm = sum(x**2 for x in vector)**0.5
    return [x / norm for x in vector]
