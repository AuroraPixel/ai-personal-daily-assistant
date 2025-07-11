"""
Data Tools Module
Contains all JSONPlaceholder data-related MCP tools

Author: Andrew Wang
"""

import json
from fastmcp import FastMCP
from remote_api.jsonplaceholder import JSONPlaceholderClient

# Initialize jsonplaceholder client
data_client = JSONPlaceholderClient()


def register_data_tools(mcp: FastMCP):
    """
    Register data tools to MCP instance
    
    Args:
        mcp: FastMCP instance
    """
    
    # Get all users
    @mcp.tool
    def get_users() -> str:
        """
        Get all users from JSONPlaceholder
        
        Returns:
            JSON string of users in format:
            {
                "users": [
                    {
                        "id": 1,
                        "name": "Leanne Graham",
                        "username": "Bret",
                        "email": "Sincere@april.biz",
                        "address": {
                            "street": "Kulas Light",
                            "suite": "Apt. 556",
                            "city": "Gwenborough",
                            "zipcode": "92998-3874",
                            "geo": {
                                "lat": "-37.3159",
                                "lng": "81.1496"
                            }
                        },
                        "phone": "1-770-736-8031 x56442",
                        "website": "hildegard.org",
                        "company": {
                            "name": "Romaguera-Crona",
                            "catchPhrase": "Multi-layered client-server neural-net",
                            "bs": "harness real-time e-markets"
                        }
                    }
                ]
            }
        """
        try:
            result = data_client.get_users()
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": "Unable to get users"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting users: {str(e)}"}, ensure_ascii=False)

    # Get specific user
    @mcp.tool
    def get_user(user_id: int) -> str:
        """
        Get specific user by ID
        
        Args:
            user_id: User ID (1-10)
            
        Returns:
            JSON string of user in format:
            {
                "user": {
                    "id": 1,
                    "name": "Leanne Graham",
                    "username": "Bret",
                    "email": "Sincere@april.biz",
                    "address": {
                        "street": "Kulas Light",
                        "suite": "Apt. 556",
                        "city": "Gwenborough",
                        "zipcode": "92998-3874",
                        "geo": {
                            "lat": "-37.3159",
                            "lng": "81.1496"
                        }
                    },
                    "phone": "1-770-736-8031 x56442",
                    "website": "hildegard.org",
                    "company": {
                        "name": "Romaguera-Crona",
                        "catchPhrase": "Multi-layered client-server neural-net",
                        "bs": "harness real-time e-markets"
                    }
                }
            }
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            result = data_client.get_user(user_id)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": f"User {user_id} not found"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting user {user_id}: {str(e)}"}, ensure_ascii=False)

    # Get user's posts
    @mcp.tool
    def get_user_posts(user_id: int) -> str:
        """
        Get user's posts
        
        Args:
            user_id: User ID (1-10)
            
        Returns:
            JSON string of user's posts in format:
            {
                "posts": [
                    {
                        "id": 1,
                        "userId": 1,
                        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
                        "body": "quia et suscipit\\nsuscipit recusandae consequuntur expedita et cum\\nreprehenderit molestiae ut ut quas totam\\nnostrum rerum est autem sunt rem eveniet architecto"
                    }
                ]
            }
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            result = data_client.get_user_posts(user_id)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": f"No posts found for user {user_id}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting posts for user {user_id}: {str(e)}"}, ensure_ascii=False)

    # Get user's comments
    @mcp.tool
    def get_user_comments(user_id: int) -> str:
        """
        Get user's comments (comments on posts by the user)
        
        Args:
            user_id: User ID (1-10)
            
        Returns:
            JSON string of user's comments in format:
            {
                "comments": [
                    {
                        "id": 1,
                        "postId": 1,
                        "name": "id labore ex et quam laborum",
                        "email": "Eliseo@gardner.biz",
                        "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos\\ntempora quo necessitatibus\\ndolor quam autem quasi\\nreiciendis et nam sapiente accusantium"
                    }
                ]
            }
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            result = data_client.get_user_comments(user_id)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": f"No comments found for user {user_id}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting comments for user {user_id}: {str(e)}"}, ensure_ascii=False)

    # Get post's comments
    @mcp.tool
    def get_post_comments(post_id: int) -> str:
        """
        Get comments for a specific post
        
        Args:
            post_id: Post ID (1-100)
            
        Returns:
            JSON string of post's comments in format:
            {
                "comments": [
                    {
                        "id": 1,
                        "postId": 1,
                        "name": "id labore ex et quam laborum",
                        "email": "Eliseo@gardner.biz",
                        "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos\\ntempora quo necessitatibus\\ndolor quam autem quasi\\nreiciendis et nam sapiente accusantium"
                    }
                ]
            }
        """
        try:
            if post_id < 1 or post_id > 100:
                return json.dumps({"error": "Post ID must be between 1 and 100"}, ensure_ascii=False)
            
            result = data_client.get_post_comments(post_id)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": f"No comments found for post {post_id}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting comments for post {post_id}: {str(e)}"}, ensure_ascii=False)

    # Get user's todos
    @mcp.tool
    def get_user_todos(user_id: int) -> str:
        """
        Get user's todos
        
        Args:
            user_id: User ID (1-10)
            
        Returns:
            JSON string of user's todos in format:
            {
                "todos": [
                    {
                        "id": 1,
                        "userId": 1,
                        "title": "delectus aut autem",
                        "completed": false
                    }
                ]
            }
        """
        try:
            if user_id < 1 or user_id > 10:
                return json.dumps({"error": "User ID must be between 1 and 10"}, ensure_ascii=False)
            
            result = data_client.get_user_todos(user_id)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"error": f"No todos found for user {user_id}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Error getting todos for user {user_id}: {str(e)}"}, ensure_ascii=False)

    print("✅ Data tools registered")