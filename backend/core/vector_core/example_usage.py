"""
Vector Database Usage Example
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import List

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.vector_core.client import ChromaVectorClient
from core.vector_core.config import VectorConfig
from core.vector_core.models import VectorDocument, VectorQuery, VectorDeleteFilter
from dotenv import load_dotenv


async def main():
    """Example usage of the vector database"""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    load_dotenv()
    
    print("=== Vector Database Example Usage ===\n")
    
    try:
        # Initialize the vector client
        print("1. Initializing Vector Client...")
        config = VectorConfig.from_env()
        client = ChromaVectorClient(config)
        print("✓ Vector client initialized successfully\n")
        
        # Health check
        print("2. Health Check...")
        health = client.health_check()
        print(f"✓ Health Status: {health['status']}")
        print(f"✓ Collections Count: {health['collections_count']}")
        print(f"✓ Embedding Model: {health['embedding_model']}\n")
        
        # User IDs for isolation testing
        user1_id = "user_123"
        user2_id = "user_456"
        
        # 3. Adding documents with metadata
        print("3. Adding Documents...")
        documents = [
            VectorDocument(
                id="doc_1",
                text="Python is a powerful programming language used for web development, data science, and AI.",
                metadata={"category": "programming", "language": "python", "difficulty": "beginner"},
                user_id=user1_id,
                source="tutorial_docs"
            ),
            VectorDocument(
                id="doc_2", 
                text="Machine learning is a subset of artificial intelligence that uses algorithms to learn from data.",
                metadata={"category": "ai", "topic": "machine_learning", "difficulty": "intermediate"},
                user_id=user1_id,
                source="ai_docs"
            ),
            VectorDocument(
                id="doc_3",
                text="React is a JavaScript library for building user interfaces, especially single-page applications.",
                metadata={"category": "programming", "language": "javascript", "difficulty": "intermediate"},
                user_id=user1_id,
                source="frontend_docs"
            ),
            # Documents for user2 (isolation test)
            VectorDocument(
                id="doc_4",
                text="Database design is crucial for application performance and scalability.",
                metadata={"category": "database", "topic": "design", "difficulty": "advanced"},
                user_id=user2_id,
                source="backend_docs"
            )
        ]
        
        # Add documents
        doc_ids = client.add_documents(documents)
        print(f"✓ Added {len(doc_ids)} documents")
        print(f"✓ Document IDs: {doc_ids}\n")
        
        # 4. Query documents - basic search
        print("4. Basic Query...")
        query = VectorQuery(
            query_text="programming languages",
            user_id=user1_id,
            limit=3,
            similarity_threshold=None,
            metadata_filter=None,
            source_filter=None,
            include_metadata=True,
            include_distances=True
        )
        
        results = client.query_documents(query)
        print(f"✓ Found {len(results)} results for '{query.query_text}'")
        for i, result in enumerate(results, 1):
            print(f"  {i}. ID: {result.id}")
            print(f"     Text: {result.text[:80]}...")
            print(f"     Score: {result.score:.3f}")
            print(f"     Metadata: {result.metadata}")
            print()
        
        # 5. Query with metadata filter
        print("5. Query with Metadata Filter...")
        query_filtered = VectorQuery(
            query_text="programming",
            user_id=user1_id,
            limit=5,
            similarity_threshold=0.5,
            metadata_filter={"category": "programming"},
            source_filter=None,
            include_metadata=True,
            include_distances=True
        )
        
        results_filtered = client.query_documents(query_filtered)
        print(f"✓ Found {len(results_filtered)} results with metadata filter")
        for i, result in enumerate(results_filtered, 1):
            print(f"  {i}. ID: {result.id}")
            category = result.metadata.get('category', 'N/A') if result.metadata else 'N/A'
            print(f"     Category: {category}")
            print(f"     Score: {result.score:.3f}")
            print()
        
                 # 6. Query with source filter
        print("6. Query with Source Filter...")
        query_source = VectorQuery(
            query_text="development",
            user_id=user1_id,
            limit=5,
            similarity_threshold=None,
            metadata_filter=None,
            source_filter="tutorial_docs",
            include_metadata=True,
            include_distances=True
        )
        
        results_source = client.query_documents(query_source)
        print(f"✓ Found {len(results_source)} results with source filter")
        for result in results_source:
            source = result.metadata.get('source', 'N/A') if result.metadata else 'N/A'
            print(f"  - ID: {result.id}, Source: {source}")
        print()
        
        # 7. Test user isolation
        print("7. Testing User Isolation...")
        query_user2 = VectorQuery(
            query_text="programming",
            user_id=user2_id,
            limit=5,
            similarity_threshold=None,
            metadata_filter=None,
            source_filter=None,
            include_metadata=True,
            include_distances=True
        )
        
        results_user2 = client.query_documents(query_user2)
        print(f"✓ User2 found {len(results_user2)} results (should be different from user1)")
        for result in results_user2:
            print(f"  - ID: {result.id}, Text: {result.text[:50]}...")
        print()
        
        # 8. Get document by ID
        print("8. Get Document by ID...")
        doc = client.get_document_by_id("doc_1", user1_id)
        if doc:
            print(f"✓ Found document: {doc.id}")
            print(f"  Text: {doc.text[:80]}...")
            print(f"  Metadata: {doc.metadata}")
        print()
        
        # 9. Get statistics
        print("9. Get Statistics...")
        stats_user1 = client.get_stats(user1_id)
        stats_user2 = client.get_stats(user2_id)
        
        print(f"✓ User1 Stats:")
        print(f"  - Total documents: {stats_user1.total_documents}")
        print(f"  - Sources: {stats_user1.sources}")
        print(f"  - Collection: {stats_user1.collection_name}")
        
        print(f"✓ User2 Stats:")
        print(f"  - Total documents: {stats_user2.total_documents}")
        print(f"  - Sources: {stats_user2.sources}")
        print(f"  - Collection: {stats_user2.collection_name}")
        print()
        
        # 10. Update document
        print("10. Update Document...")
        success = client.update_document(
            document_id="doc_1",
            user_id=user1_id,
            metadata={"category": "programming", "language": "python", "difficulty": "beginner", "updated": True}
        )
        print(f"✓ Document update: {'Success' if success else 'Failed'}")
        
        # Verify update
        updated_doc = client.get_document_by_id("doc_1", user1_id)
        if updated_doc:
            print(f"✓ Updated metadata: {updated_doc.metadata}")
        print()
        
        # 11. Delete documents by source
        print("11. Delete Documents by Source...")
        delete_filter = VectorDeleteFilter(
            user_id=user1_id,
            source_filter="frontend_docs",
            metadata_filter=None,
            document_ids=None
        )
        
        deleted_count = client.delete_documents(delete_filter)
        print(f"✓ Deleted {deleted_count} documents from 'frontend_docs' source")
        
        # Verify deletion
        stats_after_delete = client.get_stats(user1_id)
        print(f"✓ Remaining documents for user1: {stats_after_delete.total_documents}")
        print(f"✓ Remaining sources: {stats_after_delete.sources}")
        print()
        
        # 12. Delete specific documents
        print("12. Delete Specific Documents...")
        delete_specific = VectorDeleteFilter(
            user_id=user1_id,
            source_filter=None,
            metadata_filter=None,
            document_ids=["doc_2"]
        )
        
        deleted_specific = client.delete_documents(delete_specific)
        print(f"✓ Deleted {deleted_specific} specific documents")
        
        # Final stats
        final_stats = client.get_stats(user1_id)
        print(f"✓ Final document count for user1: {final_stats.total_documents}")
        print()
        
        # 13. Clear user data (cleanup)
        print("13. Cleanup - Clear User Data...")
        # Uncomment below to clear all data for testing
        # success_clear = client.clear_user_data(user1_id)
        # print(f"✓ User1 data cleared: {'Success' if success_clear else 'Failed'}")
        
        print("=== Example completed successfully! ===")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 