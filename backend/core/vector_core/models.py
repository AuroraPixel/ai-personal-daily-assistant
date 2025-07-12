"""
Vector Database Models
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class VectorDocument(BaseModel):
    """Vector document model for storing text with metadata"""
    
    id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., description="Document text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    user_id: str = Field(..., description="User identifier for isolation")
    source: Optional[str] = Field(None, description="Source identifier for filtering")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VectorQuery(BaseModel):
    """Vector query model for searching documents"""
    
    query_text: str = Field(..., description="Query text to search for")
    user_id: str = Field(..., description="User identifier for isolation")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Similarity threshold")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="Metadata filter conditions")
    source_filter: Optional[str] = Field(None, description="Source filter")
    include_metadata: bool = Field(True, description="Whether to include metadata in results")
    include_distances: bool = Field(True, description="Whether to include similarity distances")


class VectorQueryResult(BaseModel):
    """Vector query result model"""
    
    id: str = Field(..., description="Document identifier")
    text: str = Field(..., description="Document text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    distance: Optional[float] = Field(None, description="Similarity distance")
    score: Optional[float] = Field(None, description="Similarity score (1 - distance)")
    
    @classmethod
    def from_chroma_result(
        cls,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        distance: Optional[float] = None
    ) -> "VectorQueryResult":
        """Create result from Chroma query response"""
        score = None
        if distance is not None:
            score = 1.0 - distance  # Convert distance to similarity score
        
        return cls(
            id=document_id,
            text=text,
            metadata=metadata,
            distance=distance,
            score=score
        )


class VectorDeleteFilter(BaseModel):
    """Vector delete filter model"""
    
    user_id: str = Field(..., description="User identifier for isolation")
    source_filter: Optional[str] = Field(None, description="Source filter for deletion")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="Metadata filter for deletion")
    document_ids: Optional[List[str]] = Field(None, description="Specific document IDs to delete")


class VectorStats(BaseModel):
    """Vector database statistics"""
    
    total_documents: int = Field(..., description="Total number of documents")
    user_id: str = Field(..., description="User identifier")
    sources: List[str] = Field(..., description="Available sources")
    collection_name: str = Field(..., description="Collection name") 