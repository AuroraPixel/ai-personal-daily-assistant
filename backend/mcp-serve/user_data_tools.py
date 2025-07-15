"""
User Data Tools Module
Contains user information query and service layer MCP tools

Author: Andrew Wang
"""

import json
import sys
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastmcp import FastMCP

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Import JSONPlaceholder client for user data
from remote_api.jsonplaceholder import JSONPlaceholderClient

# Import service layer components
from service.services.user_service import UserService
from service.services.preference_service import PreferenceService
from service.services.note_service import NoteService
from service.services.todo_service import TodoService

# Import database initialization
from core.database_core import DatabaseClient
from core.vector_core import ChromaVectorClient, VectorConfig

# Initialize clients
jsonplaceholder_client = JSONPlaceholderClient()
user_service = UserService()
preference_service = None
note_service = None
todo_service = None

def initialize_services():
    """Initialize database and services"""
    global preference_service, note_service, todo_service
    
    try:
        # Initialize database
        print("🔄 Initializing MySQL database...")
        db_client = DatabaseClient()
        if not db_client.initialize():
            print("❌ MySQL database initialization failed")
            return False
        
        # Create tables if they don't exist
        if not db_client.create_tables():
            print("❌ Failed to create database tables")
            return False
        
        print("✅ MySQL database initialized successfully")
        
        # Initialize vector database
        print("🔄 Initializing vector database...")
        try:
            vector_config = VectorConfig.from_env()
            vector_client = ChromaVectorClient(vector_config)
            print("✅ Vector database initialized successfully")
        except Exception as e:
            print(f"⚠️  Vector database initialization failed: {e}")
            vector_client = None
        
        # Initialize services
        preference_service = PreferenceService(db_client)
        note_service = NoteService(db_client, vector_client)
        todo_service = TodoService(db_client)
        
        print("✅ All services initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

def register_user_data_tools(mcp: FastMCP):
    """
    Register user data tools to MCP instance
    
    Args:
        mcp: FastMCP instance
    """
    
    # Initialize services before registering tools
    if not initialize_services():
        print("❌ Failed to initialize services, some tools may not work")
    
    # ========== JSONPlaceholder User Tools ==========
    
    @mcp.tool
    def get_user(user_id: int) -> str:
        """
        Get specific user information by ID from JSONPlaceholder API
        
        Args:
            user_id: User ID (1-10)
            
        Returns:
            JSON string containing user information including:
            - id: User ID
            - name: User full name
            - username: Username
            - email: User email
            - address: User address with city, street, zipcode, geo coordinates
            - phone: User phone number
            - website: User website
            - company: User company information
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            result = jsonplaceholder_client.get_user(user_id)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": f"User {user_id} not found"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting user {user_id}: {str(e)}"}, ensure_ascii=False)
    
    # ========== User Service Tools ==========
    
    @mcp.tool
    def search_users_by_name(name: str) -> str:
        """
        Search users by name from JSONPlaceholder API
        
        Args:
            name: Name to search for (partial match supported)
            
        Returns:
            JSON string containing list of matching users with their basic information
        """
        try:
            users = user_service.search_users_by_name(name)
            return json.dumps({
                "users": [user.model_dump() for user in users],
                "count": len(users)
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error searching users: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def get_user_summary(user_id: int) -> str:
        """
        Get user summary information
        
        Args:
            user_id: User ID (1-10)
            
        Returns:
            JSON string containing user summary with essential information:
            - id, name, username, email, phone, website, company, address
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            summary = user_service.get_user_summary(user_id)
            if summary:
                return json.dumps(summary, ensure_ascii=False)
            return json.dumps({"error": f"User {user_id} not found"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting user summary: {str(e)}"}, ensure_ascii=False)
    
    # ========== Preference Service Tools ==========
    
    @mcp.tool
    def get_user_preferences(user_id: int, category: str = 'general') -> str:
        """
        Get user preferences by category
        
        Args:
            user_id: User ID (1-10)
            category: Preference category (default: 'general')
            
        Returns:
            JSON string containing user preferences for the specified category
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            if preference_service is None:
                return json.dumps({"error": "Preference service not initialized"}, ensure_ascii=False)
            
            preferences = preference_service.get_user_preferences(user_id, category)
            if preferences is not None:
                return json.dumps({
                    "user_id": user_id,
                    "category": category,
                    "preferences": preferences
                }, ensure_ascii=False)
            return json.dumps({"error": f"No preferences found for user {user_id} in category {category}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting preferences: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def save_user_preferences(user_id: int, preferences: str, category: str = 'general') -> str:
        """
        Save user preferences
        
        Args:
            user_id: User ID (must be between 1 and 10)
            preferences: JSON string containing preferences data (must be valid JSON format, e.g., '{"theme": "dark", "language": "en"}')
            category: Preference category (optional, max 50 characters, default: 'general')
            
        Returns:
            JSON string indicating success or failure.
            Success format: {"success": true, "user_id": number, "category": string, "message": "Preferences saved successfully"}
            Error format: {"error": "error description"}
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            if preference_service is None:
                return json.dumps({"error": "Preference service not initialized"}, ensure_ascii=False)
            
            # Validate category length
            if len(category) > 50:
                return json.dumps({"error": "Category must be 50 characters or less"}, ensure_ascii=False)
            
            # Parse preferences JSON
            try:
                preferences_dict = json.loads(preferences)
            except json.JSONDecodeError as e:
                return json.dumps({"error": f"Invalid JSON format for preferences: {str(e)}"}, ensure_ascii=False)
            
            success = preference_service.save_user_preferences(user_id, preferences_dict, category)
            return json.dumps({
                "success": success,
                "user_id": user_id,
                "category": category,
                "message": "Preferences saved successfully" if success else "Failed to save preferences"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error saving preferences: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def get_all_user_preferences(user_id: int) -> str:
        """
        Get all user preferences across all categories
        
        Args:
            user_id: User ID (1-10)
            
        Returns:
            JSON string containing all preferences organized by category
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            if preference_service is None:
                return json.dumps({"error": "Preference service not initialized"}, ensure_ascii=False)
            
            all_preferences = preference_service.get_all_user_preferences(user_id)
            return json.dumps({
                "user_id": user_id,
                "preferences": all_preferences,
                "categories": list(all_preferences.keys())
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting all preferences: {str(e)}"}, ensure_ascii=False)
    
    # ========== Note Service Tools ==========
    
    @mcp.tool
    def create_note(user_id: int, title: str, content: str = '', tag: str = '', status: str = 'draft') -> str:
        """
        Create a new note for user
        
        Args:
            user_id: User ID (must be between 1 and 10)
            title: Note title (required, max 200 characters)
            content: Note content (optional, text content)
            tag: Note tag (optional, must be one of: 'lifestyle tips', 'cooking advice', 'weather interpretation', 'news context', or empty string)
            status: Note status (must be one of: 'draft', 'published', 'archived'. Default: 'draft')
            
        Returns:
            JSON string containing created note information or error message.
            Success format: {"success": true, "note": {...}}
            Error format: {"error": "error description"}
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            if note_service is None:
                return json.dumps({"error": "Note service not initialized"}, ensure_ascii=False)
            
            # Validate status
            if status not in ['draft', 'published', 'archived']:
                return json.dumps({"error": "Status must be 'draft', 'published', or 'archived'"}, ensure_ascii=False)
            
            # Validate tag
            allowed_tags = ['lifestyle tips', 'cooking advice', 'weather interpretation', 'news context']
            if tag and tag not in allowed_tags:
                return json.dumps({
                    "error": f"Invalid tag '{tag}'. Allowed tags are: {', '.join(allowed_tags)}"
                }, ensure_ascii=False)
            
            # Validate title length
            if len(title) > 200:
                return json.dumps({"error": "Title must be 200 characters or less"}, ensure_ascii=False)
            
            note = note_service.create_note(user_id, title, content, tag if tag else None, status)
            if note:
                return json.dumps({
                    "success": True,
                    "note": {
                        "id": note.id,
                        "user_id": note.user_id,
                        "title": note.title,
                        "content": note.content,
                        "tag": note.tag,
                        "status": note.status,
                        "created_at": note.created_at.isoformat() if note.created_at is not None else None,
                        "last_updated": note.last_updated.isoformat() if note.last_updated is not None else None
                    }
                }, ensure_ascii=False)
            return json.dumps({"error": "Failed to create note"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error creating note: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def get_user_notes(user_id: int, status: str = '', limit: int = 20, offset: int = 0) -> str:
        """
        Get user's notes with optional filtering
        
        Args:
            user_id: User ID (1-10)
            status: Filter by status ('draft', 'published', 'archived', or empty for all)
            limit: Maximum number of notes to return (default: 20)
            offset: Number of notes to skip (default: 0)
            
        Returns:
            JSON string containing list of notes and metadata
        """
        try:
            if note_service is None:
                return json.dumps({"error": "Note service not initialized"}, ensure_ascii=False)
            
            # Convert empty status to None for service call
            status_filter = status if status else None
            
            notes = note_service.get_user_notes(user_id, status_filter, None, None, limit, offset)
            notes_data = []
            
            for note in notes:
                notes_data.append({
                    "id": note.id,
                    "user_id": note.user_id,
                    "title": note.title,
                    "content": note.content,
                    "tag": note.tag,
                    "status": note.status,
                    "created_at": note.created_at.isoformat() if note.created_at is not None else None,
                    "last_updated": note.last_updated.isoformat() if note.last_updated is not None else None
                })
            
            return json.dumps({
                "user_id": user_id,
                "notes": notes_data,
                "count": len(notes_data),
                "limit": limit,
                "offset": offset,
                "status_filter": status
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting notes: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def search_notes(user_id: int, query: str, limit: int = 20) -> str:
        """
        Search user's notes by content
        
        Args:
            user_id: User ID (1-10)
            query: Search query text
            limit: Maximum number of results (default: 20)
            
        Returns:
            JSON string containing search results
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            if note_service is None:
                return json.dumps({"error": "Note service not initialized"}, ensure_ascii=False)
            
            notes = note_service.search_notes(user_id, query, True, True, None, None, limit)
            notes_data = []
            
            for note in notes:
                notes_data.append({
                    "id": note.id,
                    "user_id": note.user_id,
                    "title": note.title,
                    "content": note.content,
                    "tag": note.tag,
                    "status": note.status,
                    "created_at": note.created_at.isoformat() if note.created_at is not None else None,
                    "last_updated": note.last_updated.isoformat() if note.last_updated is not None else None
                })
            
            return json.dumps({
                "user_id": user_id,
                "query": query,
                "results": notes_data,
                "count": len(notes_data),
                "limit": limit
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error searching notes: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def update_note(note_id: int, title: str = '', content: str = '', tag: str = '', status: str = '') -> str:
        """
        Update an existing note
        
        Args:
            note_id: Note ID (required, must be a valid note ID)
            title: New title (optional, leave empty to keep current, max 200 characters)
            content: New content (optional, leave empty to keep current)
            tag: New tag (optional, leave empty to keep current, must be one of: 'lifestyle tips', 'cooking advice', 'weather interpretation', 'news context', or empty string)
            status: New status (optional, leave empty to keep current, must be one of: 'draft', 'published', 'archived')
            
        Returns:
            JSON string indicating success or failure.
            Success format: {"success": true, "note_id": number, "message": "Note updated successfully"}
            Error format: {"error": "error description"}
        """
        try:
            if note_service is None:
                return json.dumps({"error": "Note service not initialized"}, ensure_ascii=False)
            
            # Validate status if provided
            if status and status not in ['draft', 'published', 'archived']:
                return json.dumps({"error": "Status must be 'draft', 'published', or 'archived'"}, ensure_ascii=False)
            
            # Validate tag if provided
            allowed_tags = ['lifestyle tips', 'cooking advice', 'weather interpretation', 'news context']
            if tag and tag not in allowed_tags:
                return json.dumps({
                    "error": f"Invalid tag '{tag}'. Allowed tags are: {', '.join(allowed_tags)}"
                }, ensure_ascii=False)
            
            # Validate title length if provided
            if title and len(title) > 200:
                return json.dumps({"error": "Title must be 200 characters or less"}, ensure_ascii=False)
            
            success = note_service.update_note(note_id, title, content, tag, status)
            return json.dumps({
                "success": success,
                "note_id": note_id,
                "message": "Note updated successfully" if success else "Failed to update note"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error updating note: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def delete_note(note_id: int) -> str:
        """
        Delete a note
        
        Args:
            note_id: Note ID
            
        Returns:
            JSON string indicating success or failure
        """
        try:
            if note_service is None:
                return json.dumps({"error": "Note service not initialized"}, ensure_ascii=False)
            
            success = note_service.delete_note(note_id)
            return json.dumps({
                "success": success,
                "note_id": note_id,
                "message": "Note deleted successfully" if success else "Failed to delete note"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error deleting note: {str(e)}"}, ensure_ascii=False)
    
    # ========== Todo Service Tools ==========
    
    @mcp.tool
    def create_todo(user_id: int, title: str, description: str = '', priority: str = 'medium', due_date: str = '', note_id: int = 0) -> str:
        """
        Create a new todo item for user
        
        Args:
            user_id: User ID (must be between 1 and 10)
            title: Todo title (required, max 200 characters)
            description: Todo description (optional, text content)
            priority: Priority level (must be one of: 'high', 'medium', 'low'. Default: 'medium')
            due_date: Due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS), or empty for no due date
            note_id: Associated note ID (optional, 0 for no association, must be a valid note ID if provided)
            
        Returns:
            JSON string containing created todo information or error message.
            Success format: {"success": true, "todo": {...}}
            Error format: {"error": "error description"}
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            if todo_service is None:
                return json.dumps({"error": "Todo service not initialized"}, ensure_ascii=False)
            
            # Validate priority
            if priority not in ['high', 'medium', 'low']:
                return json.dumps({"error": "Priority must be 'high', 'medium', or 'low'"}, ensure_ascii=False)
            
            # Validate title length
            if len(title) > 200:
                return json.dumps({"error": "Title must be 200 characters or less"}, ensure_ascii=False)
            
            # Parse due date
            due_date_obj = None
            if due_date:
                try:
                    due_date_obj = datetime.fromisoformat(due_date)
                except ValueError:
                    return json.dumps({"error": "Invalid due date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"}, ensure_ascii=False)
            
            # Handle note_id
            note_id_param = note_id if note_id > 0 else None
            
            todo = todo_service.create_todo(user_id, title, description, priority, due_date_obj, note_id_param)
            if todo:
                return json.dumps({
                    "success": True,
                    "todo": {
                        "id": todo.id,
                        "user_id": todo.user_id,
                        "title": todo.title,
                        "description": todo.description,
                        "completed": todo.completed,
                        "priority": todo.priority,
                        "note_id": todo.note_id,
                        "due_date": todo.due_date.isoformat() if todo.due_date else None,
                        "created_at": todo.created_at.isoformat() if todo.created_at else None,
                        "last_updated": todo.last_updated.isoformat() if todo.last_updated else None
                    }
                }, ensure_ascii=False)
            return json.dumps({"error": "Failed to create todo"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error creating todo: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def get_user_todos(user_id: int, completed: str = '', priority: str = '', limit: int = 20, offset: int = 0) -> str:
        """
        Get user's todos with optional filtering
        
        Args:
            user_id: User ID (1-10)
            completed: Filter by completion status ('true', 'false', or empty for all)
            priority: Filter by priority ('high', 'medium', 'low', or empty for all)
            limit: Maximum number of todos to return (default: 20)
            offset: Number of todos to skip (default: 0)
            
        Returns:
            JSON string containing list of todos and metadata
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            if todo_service is None:
                return json.dumps({"error": "Todo service not initialized"}, ensure_ascii=False)
            
            # Convert completed filter
            completed_filter = None
            if completed == 'true':
                completed_filter = True
            elif completed == 'false':
                completed_filter = False
            
            # Convert priority filter
            priority_filter = priority if priority else None
            
            todos = todo_service.get_user_todos(user_id, completed_filter, priority_filter, limit, offset)
            todos_data = []
            
            for todo in todos:
                todos_data.append({
                    "id": todo.id,
                    "user_id": todo.user_id,
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "note_id": todo.note_id,
                    "due_date": todo.due_date.isoformat() if todo.due_date is not None else None,
                    "completed_at": todo.completed_at.isoformat() if todo.completed_at is not None else None,
                    "created_at": todo.created_at.isoformat() if todo.created_at is not None else None,
                    "last_updated": todo.last_updated.isoformat() if todo.last_updated is not None else None
                })
            
            return json.dumps({
                "user_id": user_id,
                "todos": todos_data,
                "count": len(todos_data),
                "limit": limit,
                "offset": offset,
                "filters": {
                    "completed": completed,
                    "priority": priority
                }
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting todos: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def complete_todo(todo_id: int) -> str:
        """
        Mark a todo as completed
        
        Args:
            todo_id: Todo ID
            
        Returns:
            JSON string indicating success or failure
        """
        try:
            if todo_service is None:
                return json.dumps({"error": "Todo service not initialized"}, ensure_ascii=False)
            
            success = todo_service.complete_todo(todo_id)
            return json.dumps({
                "success": success,
                "todo_id": todo_id,
                "message": "Todo marked as completed" if success else "Failed to complete todo"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error completing todo: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def search_todos(user_id: int, query: str, limit: int = 20) -> str:
        """
        Search user's todos by title and description
        
        Args:
            user_id: User ID (1-10)
            query: Search query text
            limit: Maximum number of results (default: 20)
            
        Returns:
            JSON string containing search results
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            if todo_service is None:
                return json.dumps({"error": "Todo service not initialized"}, ensure_ascii=False)
            
            todos = todo_service.search_todos(user_id, query, limit)
            todos_data = []
            
            for todo in todos:
                todos_data.append({
                    "id": todo.id,
                    "user_id": todo.user_id,
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "note_id": todo.note_id,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "completed_at": todo.completed_at.isoformat() if todo.completed_at else None,
                    "created_at": todo.created_at.isoformat() if todo.created_at else None,
                    "last_updated": todo.last_updated.isoformat() if todo.last_updated else None
                })
            
            return json.dumps({
                "user_id": user_id,
                "query": query,
                "results": todos_data,
                "count": len(todos_data),
                "limit": limit
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error searching todos: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def update_todo(todo_id: int, title: str = '', description: str = '', priority: str = '', due_date: str = '') -> str:
        """
        Update an existing todo
        
        Args:
            todo_id: Todo ID (required, must be a valid todo ID)
            title: New title (optional, leave empty to keep current, max 200 characters)
            description: New description (optional, leave empty to keep current)
            priority: New priority (optional, leave empty to keep current, must be one of: 'high', 'medium', 'low')
            due_date: New due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS), or empty to keep current
            
        Returns:
            JSON string indicating success or failure.
            Success format: {"success": true, "todo_id": number, "message": "Todo updated successfully"}
            Error format: {"error": "error description"}
        """
        try:
            if todo_service is None:
                return json.dumps({"error": "Todo service not initialized"}, ensure_ascii=False)
            
            # Validate priority if provided
            if priority and priority not in ['high', 'medium', 'low']:
                return json.dumps({"error": "Priority must be 'high', 'medium', or 'low'"}, ensure_ascii=False)
            
            # Validate title length if provided
            if title and len(title) > 200:
                return json.dumps({"error": "Title must be 200 characters or less"}, ensure_ascii=False)
            
            # Parse due date if provided
            due_date_obj = None
            if due_date:
                try:
                    due_date_obj = datetime.fromisoformat(due_date)
                except ValueError:
                    return json.dumps({"error": "Invalid due date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"}, ensure_ascii=False)
            
            success = todo_service.update_todo(todo_id, title, description, priority, due_date_obj)
            return json.dumps({
                "success": success,
                "todo_id": todo_id,
                "message": "Todo updated successfully" if success else "Failed to update todo"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error updating todo: {str(e)}"}, ensure_ascii=False)
    
    @mcp.tool
    def delete_todo(todo_id: int) -> str:
        """
        Delete a todo
        
        Args:
            todo_id: Todo ID
            
        Returns:
            JSON string indicating success or failure
        """
        try:
            if todo_service is None:
                return json.dumps({"error": "Todo service not initialized"}, ensure_ascii=False)
            
            success = todo_service.delete_todo(todo_id)
            return json.dumps({
                "success": success,
                "todo_id": todo_id,
                "message": "Todo deleted successfully" if success else "Failed to delete todo"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error deleting todo: {str(e)}"}, ensure_ascii=False)
    
    print("✅ User data tools registered") 