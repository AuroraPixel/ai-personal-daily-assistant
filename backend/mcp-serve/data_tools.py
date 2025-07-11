"""
Data Tools Module
Contains all JSON placeholder data related MCP tools

Author: Andrew Wang
"""

from fastmcp import FastMCP
from remote_api.jsonplaceholder import JSONPlaceholderClient

# Initialize JSON placeholder client
json_client = JSONPlaceholderClient()


def register_data_tools(mcp: FastMCP):
    """
    Register data tools to MCP instance
    
    Args:
        mcp: FastMCP instance
    """
    
    # Get all users
    @mcp.tool
    def get_all_users() -> str:
        """
        Get all users list
            Returns:
                Users list | Error message
        """
        try:
            users = json_client.get_users()
            if users:
                return json_client.format_users_list(users)
            return "Unable to get users list"
        except Exception as e:
            return f"Error getting users list: {str(e)}"

    # Get specific user
    @mcp.tool
    def get_user_info(user_id: int) -> str:
        """
        Get specific user detailed information
            Args:
                user_id: User ID
            Returns:
                User detailed information | Error message
        """
        try:
            user = json_client.get_user(user_id)
            if user:
                from remote_api.jsonplaceholder.models import format_user
                return format_user(user)
            return f"No user found with ID {user_id}"
        except Exception as e:
            return f"Error getting user information: {str(e)}"

    # Get all posts
    @mcp.tool
    def get_all_posts() -> str:
        """
        Get all posts list
            Returns:
                Posts list | Error message
        """
        try:
            posts = json_client.get_posts()
            if posts:
                return json_client.format_posts_list(posts)
            return "Unable to get posts list"
        except Exception as e:
            return f"Error getting posts list: {str(e)}"

    # Get specific post
    @mcp.tool
    def get_post_info(post_id: int) -> str:
        """
        Get specific post detailed information
            Args:
                post_id: Post ID
            Returns:
                Post detailed information | Error message
        """
        try:
            post = json_client.get_post(post_id)
            if post:
                from remote_api.jsonplaceholder.models import format_post
                return format_post(post)
            return f"No post found with ID {post_id}"
        except Exception as e:
            return f"Error getting post information: {str(e)}"

    # Get user posts
    @mcp.tool
    def get_user_posts(user_id: int) -> str:
        """
        Get all posts by specific user
            Args:
                user_id: User ID
            Returns:
                User's posts list | Error message
        """
        try:
            posts = json_client.get_user_posts(user_id)
            if posts:
                return json_client.format_posts_list(posts)
            return f"User {user_id} has no published posts"
        except Exception as e:
            return f"Error getting user posts: {str(e)}"

    # Get all todos
    @mcp.tool
    def get_all_todos() -> str:
        """
        Get all todos list
            Returns:
                Todos list | Error message
        """
        try:
            todos = json_client.get_todos()
            if todos:
                return json_client.format_todos_list(todos)
            return "Unable to get todos list"
        except Exception as e:
            return f"Error getting todos: {str(e)}"

    # Get user todos
    @mcp.tool
    def get_user_todos(user_id: int) -> str:
        """
        Get specific user's todos
            Args:
                user_id: User ID
            Returns:
                User's todos list | Error message
        """
        try:
            todos = json_client.get_user_todos(user_id)
            if todos:
                return json_client.format_todos_list(todos)
            return f"User {user_id} has no todos"
        except Exception as e:
            return f"Error getting user todos: {str(e)}"

    print("✅ Data tools registered")