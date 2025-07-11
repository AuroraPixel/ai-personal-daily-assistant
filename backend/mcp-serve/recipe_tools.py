"""
Recipe Tools Module
Contains all recipe-related MCP tools

Author: Andrew Wang
"""

import json
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
            JSON string of ApiResponse entity in format:
            {
                "meals": [
                    {
                        "idMeal": "recipe_id",
                        "strMeal": "Recipe Name",
                        "strMealAlternate": null,
                        "strCategory": "Category",
                        "strArea": "Area/Cuisine",
                        "strInstructions": "Cooking instructions...",
                        "strMealThumb": "image_url",
                        "strTags": "tag1,tag2",
                        "strYoutube": "youtube_url",
                        "strIngredient1": "ingredient1",
                        ...
                        "strIngredient20": "ingredient20",
                        "strMeasure1": "measure1",
                        ...
                        "strMeasure20": "measure20",
                        "strSource": "source_url",
                        "strImageSource": null,
                        "strCreativeCommonsConfirmed": null,
                        "dateModified": null
                    }
                ]
            }
        """
        try:
            result = recipe_client.search_by_name(name)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"meals": None}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # Search recipes by ingredient
    @mcp.tool
    def search_recipes_by_ingredient(ingredient: str) -> str:
        """
        Search recipes by ingredient
        
        Args:
            ingredient: Ingredient name
            
        Returns:
            JSON string of ApiResponse entity in format:
            {
                "meals": [
                    {
                        "strMeal": "Recipe Name",
                        "strMealThumb": "image_url",
                        "idMeal": "recipe_id"
                    }
                ]
            }
        """
        try:
            result = recipe_client.search_by_ingredient(ingredient)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"meals": None}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # Search recipes by category
    @mcp.tool
    def search_recipes_by_category(category: str) -> str:
        """
        Search recipes by category
        
        Args:
            category: Category name (Available Categories: Beef, Breakfast, Chicken, Dessert, Goat, Lamb, Miscellaneous, Pasta, 
                                     Pork, Seafood, Side, Starter, Vegan, Vegetarian)
            
        Returns:
            JSON string of ApiResponse entity in format:
            {
                "meals": [
                    {
                        "strMeal": "Recipe Name",
                        "strMealThumb": "image_url",
                        "idMeal": "recipe_id"
                    }
                ]
            }
        """
        try:
            result = recipe_client.search_by_category(category)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"meals": None}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # Search recipes by area/cuisine
    @mcp.tool
    def search_recipes_by_area(area: str) -> str:
        """
        Search recipes by area/cuisine
        
        Args:
            area: Area/cuisine name (Available Areas: American, British, Canadian, Chinese, Croatian, Dutch, 
                                     Egyptian, French, Greek, Indian, Irish, Italian, Jamaican, Japanese, Kenyan, Malaysian, Mexican, 
                                     Moroccan, Polish, Portuguese, Russian, Spanish, Thai, Tunisian, Turkish, Vietnamese)
            
        Returns:
            JSON string of ApiResponse entity in format:
            {
                "meals": [
                    {
                        "strMeal": "Recipe Name",
                        "strMealThumb": "image_url",
                        "idMeal": "recipe_id"
                    }
                ]
            }
        """
        try:
            result = recipe_client.search_by_area(area)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"meals": None}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # Get recipe details
    @mcp.tool
    def get_recipe_details(meal_id: str) -> str:
        """
        Get recipe details
        
        Args:
            meal_id: Recipe ID
            
        Returns:
            JSON string of ApiResponse entity in format:
            {
                "meals": [
                    {
                        "idMeal": "recipe_id",
                        "strMeal": "Recipe Name",
                        "strMealAlternate": null,
                        "strCategory": "Category",
                        "strArea": "Area/Cuisine",
                        "strInstructions": "Cooking instructions...",
                        "strMealThumb": "image_url",
                        "strTags": "tag1,tag2",
                        "strYoutube": "youtube_url",
                        "strIngredient1": "ingredient1",
                        ...
                        "strIngredient20": "ingredient20",
                        "strMeasure1": "measure1",
                        ...
                        "strMeasure20": "measure20",
                        "strSource": "source_url",
                        "strImageSource": null,
                        "strCreativeCommonsConfirmed": null,
                        "dateModified": null
                    }
                ]
            }
        """
        try:
            result = recipe_client.get_recipe_details(meal_id)
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"meals": None}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # Get random recipe
    @mcp.tool
    def get_random_recipe() -> str:
        """
        Get random recipe
        
        Returns:
            JSON string of ApiResponse entity in format:
            {
                "meals": [
                    {
                        "idMeal": "recipe_id",
                        "strMeal": "Recipe Name",
                        "strMealAlternate": null,
                        "strCategory": "Category",
                        "strArea": "Area/Cuisine",
                        "strInstructions": "Cooking instructions...",
                        "strMealThumb": "image_url",
                        "strTags": "tag1,tag2",
                        "strYoutube": "youtube_url",
                        "strIngredient1": "ingredient1",
                        ...
                        "strIngredient20": "ingredient20",
                        "strMeasure1": "measure1",
                        ...
                        "strMeasure20": "measure20",
                        "strSource": "source_url",
                        "strImageSource": null,
                        "strCreativeCommonsConfirmed": null,
                        "dateModified": null
                    }
                ]
            }
        """
        try:
            result = recipe_client.get_random_recipe()
            if result:
                return json.dumps(result.model_dump(), ensure_ascii=False)
            return json.dumps({"meals": None}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    print("✅ Recipe tools registered")