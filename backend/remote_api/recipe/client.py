"""
Recipe API Client

Author: Andrew Wang
"""

from typing import Optional, List
from core.http_core.client import APIClient
from .models import (
    ApiResponse,
    RECIPE_CATEGORIES, RECIPE_AREAS
)


class RecipeClient:
    """TheMealDB Recipe API Client"""
    
    def __init__(self):
        self.client = APIClient("https://www.themealdb.com/api/json/v1/1")
    
    def search_by_name(self, name: str) -> Optional[ApiResponse]:
        """
        Search recipes by name
        
        Args:
            name: Recipe name
            
        Returns:
            ApiResponse entity or None
        """
        params = {"s": name}
        data = self.client.get("/search.php", params=params)
        
        if data:
            return ApiResponse.from_dict(data)
        return None
    
    def search_by_ingredient(self, ingredient: str) -> Optional[ApiResponse]:
        """
        Search recipes by main ingredient
        
        Args:
            ingredient: Ingredient name
            
        Returns:
            ApiResponse entity or None
        """
        params = {"i": ingredient}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return ApiResponse.from_dict(data)
        return None
    
    def search_by_category(self, category: str) -> Optional[ApiResponse]:
        """
        Search recipes by category
        
        Args:
            category: Category name
            
        Returns:
            ApiResponse entity or None
        """
        if category not in RECIPE_CATEGORIES:
            print(f"Invalid category: {category}. Available categories: {RECIPE_CATEGORIES}")
            return None
        
        params = {"c": category}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return ApiResponse.from_dict(data)
        return None
    
    def search_by_area(self, area: str) -> Optional[ApiResponse]:
        """
        Search recipes by area/cuisine
        
        Args:
            area: Area/cuisine name
            
        Returns:
            ApiResponse entity or None
        """
        if area not in RECIPE_AREAS:
            print(f"Invalid area: {area}. Available areas: {RECIPE_AREAS}")
            return None
        
        params = {"a": area}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return ApiResponse.from_dict(data)
        return None
    
    def get_recipe_details(self, meal_id: str) -> Optional[ApiResponse]:
        """
        Get recipe detailed information
        
        Args:
            meal_id: Recipe ID
            
        Returns:
            ApiResponse entity or None
        """
        params = {"i": meal_id}
        data = self.client.get("/lookup.php", params=params)
        
        if data and data.get("meals"):
            return ApiResponse.from_dict(data)
        return None
    
    def get_random_recipe(self) -> Optional[ApiResponse]:
        """
        Get random recipe
        
        Returns:
            ApiResponse entity or None
        """
        data = self.client.get("/random.php")
        
        if data and data.get("meals"):
            return ApiResponse.from_dict(data)
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