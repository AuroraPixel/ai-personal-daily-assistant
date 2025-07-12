"""
Chroma Vector Database Client with OpenAI Embeddings
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import openai

from .config import VectorConfig
from .models import (
    VectorDocument,
    VectorQuery,
    VectorQueryResult,
    VectorDeleteFilter,
    VectorStats
)
from .utils import (
    create_collection_name,
    validate_metadata,
    generate_document_id,
    build_chroma_filter,
    chunk_text,
    filter_results_by_threshold
)


logger = logging.getLogger(__name__)


class ChromaVectorClient:
    """Chroma Vector Database Client with OpenAI Embeddings"""
    
    def __init__(self, config: Optional[VectorConfig] = None):
        """Initialize Chroma client"""
        self.config = config or VectorConfig.from_env()
        self._client = None
        self._embedding_function = None
        self._collections = {}  # Cache for collections
        
        # Set OpenAI API key
        openai.api_key = self.config.openai_api_key
        
        self._init_client()
        self._init_embedding_function()
    
    def _init_client(self):
        """Initialize Chroma client based on configuration mode."""
        if self.config.chroma_client_mode.lower() == "http":
            self._init_http_client()
        else:
            self._init_local_client()

    def _init_http_client(self):
        """Initialize Chroma HTTP client to connect to a remote server."""
        try:
            logger.info(f"Initializing Chroma HTTP client to connect to {self.config.chroma_host}:{self.config.chroma_port}...")
            
            self._client = chromadb.HttpClient(
                host=self.config.chroma_host,
                port=self.config.chroma_port,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Verify connection
            version = self._client.heartbeat()
            logger.info(f"Successfully connected to Chroma server. Version: {version}")

        except Exception as e:
            logger.error(f"Failed to initialize Chroma HTTP client: {e}")
            raise

    def _init_local_client(self):
        """Initialize Chroma client with persistent storage."""
        try:
            logger.info(f"Initializing Chroma client with local persistence at {self.config.chroma_persist_directory}")
            # Ensure persist directory exists
            os.makedirs(self.config.chroma_persist_directory, exist_ok=True)
            
            # Initialize Chroma client with persistent storage
            self._client = chromadb.PersistentClient(
                path=self.config.chroma_persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info(f"Chroma client initialized with persistence at {self.config.chroma_persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chroma client: {e}")
            raise
    
    def _init_embedding_function(self):
        """Initialize OpenAI embedding function"""
        try:
            self._embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=self.config.openai_api_key,
                model_name=self.config.openai_embedding_model
            )
            
            logger.info(f"OpenAI embedding function initialized with model: {self.config.openai_embedding_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embedding function: {e}")
            raise
    
    def _get_collection(self, user_id: str):
        """Get or create collection for user"""
        collection_name = create_collection_name(self.config.chroma_collection_prefix, user_id)
        
        if collection_name not in self._collections:
            try:
                # Try to get existing collection
                collection = self._client.get_collection(
                    name=collection_name,
                    embedding_function=self._embedding_function
                )
                logger.info(f"Retrieved existing collection: {collection_name}")
                
            except Exception:
                # Create new collection if it doesn't exist
                collection = self._client.create_collection(
                    name=collection_name,
                    embedding_function=self._embedding_function,
                    metadata={"user_id": user_id, "created_at": datetime.now().isoformat()}
                )
                logger.info(f"Created new collection: {collection_name}")
            
            self._collections[collection_name] = collection
        
        return self._collections[collection_name]
    
    def add_document(self, document: VectorDocument) -> str:
        """Add a document to the vector database"""
        try:
            collection = self._get_collection(document.user_id)
            
            # Generate document ID if not provided
            if not document.id:
                document.id = generate_document_id(document.text, document.user_id, document.source)
            
            # Prepare metadata
            metadata = validate_metadata(document.metadata)
            metadata.update({
                "user_id": document.user_id,
                "source": document.source or "default",
                "created_at": document.created_at.isoformat()
            })
            
            # Add document to collection
            collection.add(
                documents=[document.text],
                metadatas=[metadata],
                ids=[document.id]
            )
            
            logger.info(f"Added document {document.id} for user {document.user_id}")
            return document.id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    def add_documents(self, documents: List[VectorDocument]) -> List[str]:
        """Add multiple documents to the vector database"""
        document_ids = []
        
        # Group documents by user_id for efficient batch operations
        user_documents = {}
        for doc in documents:
            if doc.user_id not in user_documents:
                user_documents[doc.user_id] = []
            user_documents[doc.user_id].append(doc)
        
        # Process documents by user
        for user_id, user_docs in user_documents.items():
            try:
                logger.info(f"Getting collection for user {user_id}...")
                collection = self._get_collection(user_id)
                
                texts = []
                metadatas = []
                ids = []
                
                for doc in user_docs:
                    # Generate document ID if not provided
                    if not doc.id:
                        doc.id = generate_document_id(doc.text, doc.user_id, doc.source)
                    
                    # Prepare metadata
                    metadata = validate_metadata(doc.metadata)
                    metadata.update({
                        "user_id": doc.user_id,
                        "source": doc.source or "default",
                        "created_at": doc.created_at.isoformat()
                    })
                    
                    texts.append(doc.text)
                    metadatas.append(metadata)
                    ids.append(doc.id)
                    document_ids.append(doc.id)
                
                logger.info(f"Calling collection.add() for {len(texts)} documents. This involves a network call to OpenAI and may take a moment...")
                # Batch add documents
                collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.info(f"Successfully added {len(user_docs)} documents for user {user_id}")
                
            except Exception as e:
                logger.error(f"Failed to add documents for user {user_id}: {e}")
                raise
        
        return document_ids
    
    def query_documents(self, query: VectorQuery) -> List[VectorQueryResult]:
        """Query documents using vector similarity"""
        try:
            collection = self._get_collection(query.user_id)
            
            # Build filter
            where_filter = build_chroma_filter(
                source_filter=query.source_filter,
                metadata_filter=query.metadata_filter
            )
            
            # Perform query
            results = collection.query(
                query_texts=[query.query_text],
                n_results=query.limit,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            query_results = []
            
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    document = results['documents'][0][i]
                    metadata = results['metadatas'][0][i] if query.include_metadata else None
                    distance = results['distances'][0][i] if query.include_distances else None
                    
                    # Apply similarity threshold if specified
                    if query.similarity_threshold is not None and distance is not None:
                        score = 1.0 - distance
                        if score < query.similarity_threshold:
                            continue
                    
                    result = VectorQueryResult.from_chroma_result(
                        document_id=doc_id,
                        text=document,
                        metadata=metadata,
                        distance=distance
                    )
                    query_results.append(result)
            
            logger.info(f"Query returned {len(query_results)} results for user {query.user_id}")
            return query_results
            
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            raise
    
    def delete_documents(self, delete_filter: VectorDeleteFilter) -> int:
        """Delete documents based on filter criteria"""
        try:
            collection = self._get_collection(delete_filter.user_id)
            
            deleted_count = 0
            
            # Delete by specific document IDs
            if delete_filter.document_ids:
                try:
                    collection.delete(ids=delete_filter.document_ids)
                    deleted_count = len(delete_filter.document_ids)
                    logger.info(f"Deleted {deleted_count} documents by ID for user {delete_filter.user_id}")
                except Exception as e:
                    logger.warning(f"Some documents may not exist: {e}")
            
            # Delete by filter criteria
            elif delete_filter.source_filter or delete_filter.metadata_filter:
                where_filter = build_chroma_filter(
                    source_filter=delete_filter.source_filter,
                    metadata_filter=delete_filter.metadata_filter
                )
                
                # First, get documents to delete to count them
                # Note: ChromaDB's delete does not return a count, so this is best-effort.
                results = collection.get(where=where_filter)
                if results['ids']:
                    deleted_count = len(results['ids'])
                    collection.delete(where=where_filter)
                    logger.info(f"Deleted {deleted_count} documents by filter for user {delete_filter.user_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise
    
    def get_document_by_id(self, document_id: str, user_id: str) -> Optional[VectorQueryResult]:
        """Get a specific document by ID"""
        try:
            collection = self._get_collection(user_id)
            
            results = collection.get(
                ids=[document_id],
                where={"user_id": user_id},
                include=["documents", "metadatas"]
            )
            
            if results['ids'] and results['ids'][0]:
                return VectorQueryResult.from_chroma_result(
                    document_id=results['ids'][0],
                    text=results['documents'][0],
                    metadata=results['metadatas'][0]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {e}")
            raise
    
    def get_stats(self, user_id: str) -> VectorStats:
        """Get statistics for user's collection"""
        try:
            collection = self._get_collection(user_id)
            
            # Get all documents for the user
            results = collection.get(where={"user_id": user_id})
            
            total_documents = len(results['ids']) if results['ids'] else 0
            
            # Extract unique sources
            sources = set()
            if results['metadatas']:
                for metadata in results['metadatas']:
                    source = metadata.get('source', 'default')
                    sources.add(source)
            
            collection_name = create_collection_name(self.config.chroma_collection_prefix, user_id)
            
            return VectorStats(
                total_documents=total_documents,
                user_id=user_id,
                sources=list(sources),
                collection_name=collection_name
            )
            
        except Exception as e:
            logger.error(f"Failed to get stats for user {user_id}: {e}")
            raise
    
    def update_document(self, document_id: str, user_id: str, 
                       text: Optional[str] = None, 
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update an existing document"""
        try:
            collection = self._get_collection(user_id)
            
            # Get existing document
            existing = collection.get(
                ids=[document_id],
                where={"user_id": user_id},
                include=["documents", "metadatas"]
            )
            
            if not existing['ids'] or not existing['ids'][0]:
                return False
            
            # Prepare update data
            update_data = {}
            
            if text is not None:
                update_data['documents'] = [text]
            
            if metadata is not None:
                existing_metadata = existing['metadatas'][0]
                validated_metadata = validate_metadata(metadata)
                existing_metadata.update(validated_metadata)
                update_data['metadatas'] = [existing_metadata]
            
            # Update document
            collection.update(
                ids=[document_id],
                **update_data
            )
            
            logger.info(f"Updated document {document_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {e}")
            raise
    
    def clear_user_data(self, user_id: str) -> bool:
        """Clear all data for a specific user"""
        try:
            collection_name = create_collection_name(self.config.chroma_collection_prefix, user_id)
            
            # Delete the entire collection
            self._client.delete_collection(collection_name)
            
            # Remove from cache
            if collection_name in self._collections:
                del self._collections[collection_name]
            
            logger.info(f"Cleared all data for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear data for user {user_id}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the vector database"""
        try:
            # Try to list collections
            collections = self._client.list_collections()
            
            return {
                "status": "healthy",
                "collections_count": len(collections),
                "persist_directory": self.config.chroma_persist_directory,
                "embedding_model": self.config.openai_embedding_model
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            } 