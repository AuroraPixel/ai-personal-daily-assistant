"""
Vector Database Utilities
"""

import re
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime


def create_collection_name(prefix: str, user_id: str) -> str:
    """Create a valid collection name for user isolation"""
    # Chroma collection names must be alphanumeric with underscores
    sanitized_user_id = re.sub(r'[^a-zA-Z0-9_]', '_', user_id)
    return f"{prefix}_user_{sanitized_user_id}"


def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize metadata for Chroma storage"""
    if not metadata:
        return {}
    
    validated_metadata = {}
    
    for key, value in metadata.items():
        # Ensure key is string and valid
        if not isinstance(key, str):
            continue
            
        # Sanitize key name
        sanitized_key = re.sub(r'[^a-zA-Z0-9_]', '_', key)
        
        # Validate value types (Chroma supports str, int, float, bool)
        if isinstance(value, (str, int, float, bool)):
            validated_metadata[sanitized_key] = value
        elif isinstance(value, datetime):
            validated_metadata[sanitized_key] = value.isoformat()
        elif value is None:
            validated_metadata[sanitized_key] = ""
        else:
            # Convert other types to string
            validated_metadata[sanitized_key] = str(value)
    
    return validated_metadata


def generate_document_id(text: str, user_id: str, source: Optional[str] = None) -> str:
    """Generate a unique document ID based on content and user"""
    content = f"{user_id}:{source or 'default'}:{text}"
    return hashlib.md5(content.encode()).hexdigest()


def build_chroma_filter(
    source_filter: Optional[str] = None,
    metadata_filter: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Build a Chroma-compatible filter for handling multiple conditions."""
    conditions = []

    if source_filter:
        conditions.append({"source": {"$eq": source_filter}})

    if metadata_filter:
        validated_metadata = validate_metadata(metadata_filter)
        for key, value in validated_metadata.items():
            conditions.append({key: {"$eq": value}})

    if not conditions:
        return None
    
    if len(conditions) == 1:
        return conditions[0]

    return {"$and": conditions}


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into chunks for better vector storage"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to find a good break point (sentence end)
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            search_start = max(end - 100, start)
            sentence_end = text.rfind('.', search_start, end)
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def calculate_similarity_score(distance: float) -> float:
    """Convert distance to similarity score (0-1)"""
    return max(0.0, 1.0 - distance)


def filter_results_by_threshold(
    results: List[tuple],
    threshold: float,
    distance_index: int = 2
) -> List[tuple]:
    """Filter results by similarity threshold"""
    filtered = []
    
    for result in results:
        if len(result) > distance_index and result[distance_index] is not None:
            distance = result[distance_index]
            score = calculate_similarity_score(distance)
            if score >= threshold:
                filtered.append(result)
        else:
            # Include results without distance information
            filtered.append(result)
    
    return filtered 