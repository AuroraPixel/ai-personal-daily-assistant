"""
Recipe API Client

Author: Andrew Wang
"""

from typing import Optional, List
from core.http_core.client import APIClient
from .models import (
    Recipe, RecipeListItem, RecipeSearchResponse, RecipeListResponse,
    recipe_search_response_from_dict, recipe_list_response_from_dict,
    format_recipe_summary, format_recipe_details,
    RECIPE_CATEGORIES, RECIPE_AREAS
)


class RecipeClient:
    """TheMealDB Recipe API Client"""
    
    def __init__(self):
        self.client = APIClient("https://www.themealdb.com/api/json/v1/1")
    
    def search_by_name(self, name: str) -> Optional[RecipeSearchResponse]:
        """
        Search recipes by name
        
        Args:
            name: Recipe name
            
        Returns:
            Recipe search response or None
        """
        params = {"s": name}
        data = self.client.get("/search.php", params=params)
        
        if data:
            return recipe_search_response_from_dict(data)
        return None
    
    def search_by_ingredient(self, ingredient: str) -> Optional[RecipeListResponse]:
        """
        Search recipes by main ingredient
        
        Args:
            ingredient: Ingredient name
            
        Returns:
            Recipe list response or None
        """
        params = {"i": ingredient}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return recipe_list_response_from_dict(data)
        return None
    
    def search_by_category(self, category: str) -> Optional[RecipeListResponse]:
        """
        Search recipes by category
        
        Args:
            category: Category name
            
        Returns:
            Recipe list response or None
        """
        if category not in RECIPE_CATEGORIES:
            print(f"Invalid category: {category}. Available categories: {RECIPE_CATEGORIES}")
            return None
        
        params = {"c": category}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return recipe_list_response_from_dict(data)
        return None
    
    def search_by_area(self, area: str) -> Optional[RecipeListResponse]:
        """
        Search recipes by area/cuisine
        
        Args:
            area: Area/cuisine name
            
        Returns:
            Recipe list response or None
        """
        if area not in RECIPE_AREAS:
            print(f"Invalid area: {area}. Available areas: {RECIPE_AREAS}")
            return None
        
        params = {"a": area}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return recipe_list_response_from_dict(data)
        return None
    
    def get_recipe_details(self, meal_id: str) -> Optional[Recipe]:
        """
        Get recipe detailed information
        
        Args:
            meal_id: Recipe ID
            
        Returns:
            Recipe details or None
        """
        params = {"i": meal_id}
        data = self.client.get("/lookup.php", params=params)
        
        if data and data.get("meals"):
            response = recipe_search_response_from_dict(data)
            return response.meals[0] if response.meals else None
        return None
    
    def get_random_recipe(self) -> Optional[Recipe]:
        """
        Get random recipe
        
        Returns:
            Random recipe or None
        """
        data = self.client.get("/random.php")
        
        if data and data.get("meals"):
            response = recipe_search_response_from_dict(data)
            return response.meals[0] if response.meals else None
        return None
    
    def get_categories(self) -> Optional[List[str]]:
        """
        Get available recipe categories
        
        Returns:
            Categories list
        """
        return RECIPE_CATEGORIES.copy()
    
    def get_areas(self) -> Optional[List[str]]:
        """
        Get available areas/cuisines
        
        Returns:
            Areas list
        """
        return RECIPE_AREAS.copy()
    
    def format_search_results(self, response: RecipeSearchResponse, 
                             max_results: int = 10) -> str:
        """
        Format search results
        
        Args:
            response: Search response
            max_results: Maximum number of results to display
            
        Returns:
            Formatted search results string
        """
        if not response.meals:
            return "No related recipes found"
        
        results = []
        for i, recipe in enumerate(response.meals[:max_results]):
            results.append(f"{i+1}. {format_recipe_summary(recipe)}")
        
        total_count = len(response.meals)
        if total_count > max_results:
            results.append(f"\n... {total_count - max_results} more results")
        
        return "\n\n".join(results)
    
    def format_list_results(self, response: RecipeListResponse, 
                           max_results: int = 10) -> str:
        """
        Format list results
        
        Args:
            response: List response
            max_results: Maximum number of results to display
            
        Returns:
            Formatted list results string
        """
        if not response.meals:
            return "No related recipes found"
        
        results = []
        for i, recipe in enumerate(response.meals[:max_results]):
            results.append(f"{i+1}. {recipe.name} (ID: {recipe.id})")
        
        total_count = len(response.meals)
        if total_count > max_results:
            results.append(f"\n... {total_count - max_results} more results")
        
        return "\n".join(results)
    
    def comprehensive_search(self, query: str, max_results: int = 5) -> str:
        """
        Comprehensive search (by name, ingredient, category, area)
        
        Args:
            query: Search keywords
            max_results: Maximum results per category
            
        Returns:
            Comprehensive search results string
        """
        results = []
        
        # Search by name
        name_results = self.search_by_name(query)
        if name_results and name_results.meals:
            results.append(f"Search by name '{query}':")
            results.append(self.format_search_results(name_results, max_results))
        
        # Search by ingredient
        ingredient_results = self.search_by_ingredient(query)
        if ingredient_results and ingredient_results.meals:
            results.append(f"\nSearch by ingredient '{query}':")
            results.append(self.format_list_results(ingredient_results, max_results))
        
        # Search by category (if matches)
        query_title = query.title()
        if query_title in RECIPE_CATEGORIES:
            category_results = self.search_by_category(query_title)
            if category_results and category_results.meals:
                results.append(f"\nSearch by category '{query_title}':")
                results.append(self.format_list_results(category_results, max_results))
        
        # Search by area (if matches)
        if query_title in RECIPE_AREAS:
            area_results = self.search_by_area(query_title)
            if area_results and area_results.meals:
                results.append(f"\nSearch by area '{query_title}':")
                results.append(self.format_list_results(area_results, max_results))
        
        return "\n\n".join(results) if results else f"No recipes found related to '{query}'" 