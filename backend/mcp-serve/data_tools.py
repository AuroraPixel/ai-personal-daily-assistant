"""
数据工具模块 (Data Tools Module)
包含所有JSON占位符数据相关的MCP工具
"""

from fastmcp import FastMCP
from remote_api.jsonplaceholder import JSONPlaceholderClient

# 初始化JSON占位符客户端 (Initialize JSON placeholder client)
json_client = JSONPlaceholderClient()


def register_data_tools(mcp: FastMCP):
    """
    注册数据工具到MCP实例
    Register data tools to MCP instance
    
    Args:
        mcp: FastMCP实例
    """
    
    # 获取所有用户 (Get all users)
    @mcp.tool
    def get_all_users() -> str:
        """
        获取所有用户列表
            Returns:
                用户列表 | 错误信息
        """
        try:
            users = json_client.get_users()
            if users:
                return json_client.format_users_list(users)
            return "无法获取用户列表"
        except Exception as e:
            return f"获取用户列表时出错: {str(e)}"

    # 获取指定用户信息 (Get specific user)
    @mcp.tool
    def get_user_info(user_id: int) -> str:
        """
        获取指定用户的详细信息
            Args:
                user_id: 用户ID
            Returns:
                用户详细信息 | 错误信息
        """
        try:
            user = json_client.get_user(user_id)
            if user:
                from remote_api.jsonplaceholder.models import format_user
                return format_user(user)
            return f"未找到ID为{user_id}的用户"
        except Exception as e:
            return f"获取用户信息时出错: {str(e)}"

    # 获取所有帖子 (Get all posts)
    @mcp.tool
    def get_all_posts() -> str:
        """
        获取所有帖子列表
            Returns:
                帖子列表 | 错误信息
        """
        try:
            posts = json_client.get_posts()
            if posts:
                return json_client.format_posts_list(posts)
            return "无法获取帖子列表"
        except Exception as e:
            return f"获取帖子列表时出错: {str(e)}"

    # 获取指定帖子 (Get specific post)
    @mcp.tool
    def get_post_info(post_id: int) -> str:
        """
        获取指定帖子的详细信息
            Args:
                post_id: 帖子ID
            Returns:
                帖子详细信息 | 错误信息
        """
        try:
            post = json_client.get_post(post_id)
            if post:
                from remote_api.jsonplaceholder.models import format_post
                return format_post(post)
            return f"未找到ID为{post_id}的帖子"
        except Exception as e:
            return f"获取帖子信息时出错: {str(e)}"

    # 获取用户帖子 (Get user posts)
    @mcp.tool
    def get_user_posts(user_id: int) -> str:
        """
        获取指定用户的所有帖子
            Args:
                user_id: 用户ID
            Returns:
                用户的帖子列表 | 错误信息
        """
        try:
            posts = json_client.get_user_posts(user_id)
            if posts:
                return json_client.format_posts_list(posts)
            return f"用户{user_id}没有发布任何帖子"
        except Exception as e:
            return f"获取用户帖子时出错: {str(e)}"

    # 获取所有待办事项 (Get all todos)
    @mcp.tool
    def get_all_todos() -> str:
        """
        获取所有待办事项列表
            Returns:
                待办事项列表 | 错误信息
        """
        try:
            todos = json_client.get_todos()
            if todos:
                return json_client.format_todos_list(todos)
            return "无法获取待办事项列表"
        except Exception as e:
            return f"获取待办事项时出错: {str(e)}"

    # 获取用户待办事项 (Get user todos)
    @mcp.tool
    def get_user_todos(user_id: int) -> str:
        """
        获取指定用户的待办事项
            Args:
                user_id: 用户ID
            Returns:
                用户的待办事项列表 | 错误信息
        """
        try:
            todos = json_client.get_user_todos(user_id)
            if todos:
                return json_client.format_todos_list(todos)
            return f"用户{user_id}没有任何待办事项"
        except Exception as e:
            return f"获取用户待办事项时出错: {str(e)}"

    print("✅ 数据工具已注册 (Data tools registered)")