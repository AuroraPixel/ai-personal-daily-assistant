"""
食谱工具模块 (Recipe Tools Module)
包含所有食谱相关的MCP工具
"""

from fastmcp import FastMCP
from remote_api.recipe import RecipeClient

# 初始化食谱客户端 (Initialize recipe client)
recipe_client = RecipeClient()


def register_recipe_tools(mcp: FastMCP):
    """
    注册食谱工具到MCP实例
    Register recipe tools to MCP instance
    
    Args:
        mcp: FastMCP实例
    """
    
    # 按名称搜索食谱 (Search recipes by name)
    @mcp.tool
    def search_recipes_by_name(name: str) -> str:
        """
        Search recipes by name
            Args:
                name: recipe name
            Returns:
                recipe list | error message
        """
        try:
            recipes = recipe_client.search_by_name(name)
            if recipes:
                return recipe_client.format_search_results(recipes)
            return f"未找到名称包含'{name}'的食谱"
        except Exception as e:
            return f"搜索食谱时出错: {str(e)}"

    # 按成分搜索食谱 (Search recipes by ingredient)
    @mcp.tool
    def search_recipes_by_ingredient(ingredient: str) -> str:
        """
        Search recipes by ingredient
            Args:
                ingredient: ingredient name
            Returns:
                recipe list | error message
        """
        try:
            recipes = recipe_client.search_by_ingredient(ingredient)
            if recipes:
                return recipe_client.format_list_results(recipes)
            return f"未找到包含'{ingredient}'的食谱"
        except Exception as e:
            return f"搜索食谱时出错: {str(e)}"

    # 按分类搜索食谱 (Search recipes by category)
    @mcp.tool
    def search_recipes_by_category(category: str) -> str:
        """
        Search recipes by category
            Args:
                category: category name (e.g. Beef, Chicken, Dessert)
            Returns:
                recipe list | error message
        """
        try:
            recipes = recipe_client.search_by_category(category)
            if recipes:
                return recipe_client.format_list_results(recipes)
            return f"未找到'{category}'分类的食谱"
        except Exception as e:
            return f"搜索食谱时出错: {str(e)}"

    # 按地区搜索食谱 (Search recipes by area/cuisine)
    @mcp.tool
    def search_recipes_by_area(area: str) -> str:
        """
        Search recipes by area/cuisine
            Args:
                area: area/cuisine name (e.g. Chinese, Italian, Mexican)
            Returns:
                recipe list | error message
        """
        try:
            recipes = recipe_client.search_by_area(area)
            if recipes:
                return recipe_client.format_list_results(recipes)
            return f"未找到'{area}'菜系的食谱"
        except Exception as e:
            return f"搜索食谱时出错: {str(e)}"

    # 获取食谱详细信息 (Get recipe details)
    @mcp.tool
    def get_recipe_details(meal_id: str) -> str:
        """
        Get recipe details
            Args:
                meal_id: recipe id
            Returns:
                recipe details | error message
        """
        try:
            recipe = recipe_client.get_recipe_details(meal_id)
            if recipe:
                from remote_api.recipe.models import format_recipe_details
                return format_recipe_details(recipe)
            return f"未找到ID为'{meal_id}'的食谱"
        except Exception as e:
            return f"获取食谱详情时出错: {str(e)}"

    # 获取随机食谱 (Get random recipe)
    @mcp.tool
    def get_random_recipe() -> str:
        """
            Get random recipe
            Returns:
                random recipe details | error message
        """
        try:
            recipe = recipe_client.get_random_recipe()
            if recipe:
                from remote_api.recipe.models import format_recipe_details
                return format_recipe_details(recipe)
            return "无法获取随机食谱"
        except Exception as e:
            return f"获取随机食谱时出错: {str(e)}"

    print("✅ 食谱工具已注册 (Recipe tools registered)")