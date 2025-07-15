"""
Vector Database Configuration
"""

import os
from typing import Optional
from pydantic import BaseModel


class VectorConfig(BaseModel):
    """Vector database configuration"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Chroma Configuration
    chroma_client_mode: str = "http"  # "http" or "local"
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_prefix: str = "ai_assistant"

    # --- New for HTTP Client ---
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    # --- End New ---
    
    # Vector Configuration
    vector_dimension: int = 1536  # For text-embedding-3-small
    similarity_threshold: float = 0.7
    default_query_limit: int = 10
    
    @classmethod
    def from_env(cls) -> "VectorConfig":
        """Load configuration from environment variables"""
        openai_api_key = os.getenv("EMBEDDING_OPENAI_API_KEY")
        if not openai_api_key:
            openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY or EMBEDDING_OPENAI_API_KEY environment variable is required")
        
        return cls(
            openai_api_key=openai_api_key,
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),

            # Chroma config
            chroma_client_mode=os.getenv("CHROMA_CLIENT_MODE", "http"),
            chroma_persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
            chroma_collection_prefix=os.getenv("CHROMA_COLLECTION_PREFIX", "ai_assistant"),

            # New HTTP client config
            chroma_host=os.getenv("CHROMA_HOST", "localhost"),
            chroma_port=int(os.getenv("CHROMA_PORT", "8000")),
            
            # Vector Configuration
            vector_dimension=int(os.getenv("VECTOR_DIMENSION", "1536")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.7")),
            default_query_limit=int(os.getenv("DEFAULT_QUERY_LIMIT", "10"))
        )
    
    def get_collection_name(self, user_id: str) -> str:
        """Generate collection name for user isolation"""
        return f"{self.chroma_collection_prefix}_user_{user_id}" 