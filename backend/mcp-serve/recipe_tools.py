"""
Recipe Tools Module
Contains all recipe-related MCP tools

Author: Andrew Wang
"""

from fastmcp import FastMCP
from remote_api.recipe import RecipeClient

# Initialize recipe client
recipe_client = RecipeClient()


def register_recipe_tools(mcp: FastMCP):
    """
    Register recipe tools to MCP instance
    
    Args:
        mcp: FastMCP instance
    """
    
    # Search recipes by name
    @mcp.tool
    def search_recipes_by_name(name: str) -> str:
        """
        Search recipes by name
            Args:
                name: Recipe name
            Returns:
                Recipe list | Error message
        """
        try:
            recipes = recipe_client.search_by_name(name)
            if recipes:
                return recipe_client.format_search_results(recipes)
            return f"No recipes found containing '{name}'"
        except Exception as e:
            return f"Error searching recipes: {str(e)}"

    # Search recipes by ingredient
    @mcp.tool
    def search_recipes_by_ingredient(ingredient: str) -> str:
        """
        Search recipes by ingredient
            Args:
                ingredient: Ingredient name
            Returns:
                Recipe list | Error message
        """
        try:
            recipes = recipe_client.search_by_ingredient(ingredient)
            if recipes:
                return recipe_client.format_list_results(recipes)
            return f"No recipes found containing '{ingredient}'"
        except Exception as e:
            return f"Error searching recipes: {str(e)}"

    # Search recipes by category
    @mcp.tool
    def search_recipes_by_category(category: str) -> str:
        """
        Search recipes by category
            Args:
                category: Category name (e.g. Beef, Chicken, Dessert)
            Returns:
                Recipe list | Error message
        """
        try:
            recipes = recipe_client.search_by_category(category)
            if recipes:
                return recipe_client.format_list_results(recipes)
            return f"No recipes found in '{category}' category"
        except Exception as e:
            return f"Error searching recipes: {str(e)}"

    # Search recipes by area/cuisine
    @mcp.tool
    def search_recipes_by_area(area: str) -> str:
        """
        Search recipes by area/cuisine
            Args:
                area: Area/cuisine name (e.g. Chinese, Italian, Mexican)
            Returns:
                Recipe list | Error message
        """
        try:
            recipes = recipe_client.search_by_area(area)
            if recipes:
                return recipe_client.format_list_results(recipes)
            return f"No recipes found in '{area}' cuisine"
        except Exception as e:
            return f"Error searching recipes: {str(e)}"

    # Get recipe details
    @mcp.tool
    def get_recipe_details(meal_id: str) -> str:
        """
        Get recipe details
            Args:
                meal_id: Recipe ID
            Returns:
                Recipe details | Error message
        """
        try:
            recipe = recipe_client.get_recipe_details(meal_id)
            if recipe:
                from remote_api.recipe.models import format_recipe_details
                return format_recipe_details(recipe)
            return f"No recipe found with ID '{meal_id}'"
        except Exception as e:
            return f"Error getting recipe details: {str(e)}"

    # Get random recipe
    @mcp.tool
    def get_random_recipe() -> str:
        """
        Get random recipe
            Returns:
                Random recipe details | Error message
        """
        try:
            recipe = recipe_client.get_random_recipe()
            if recipe:
                from remote_api.recipe.models import format_recipe_details
                return format_recipe_details(recipe)
            return "Unable to get random recipe"
        except Exception as e:
            return f"Error getting random recipe: {str(e)}"

    print("✅ Recipe tools registered")