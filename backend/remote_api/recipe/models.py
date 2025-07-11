"""
Recipe API Data Models

Author: Andrew Wang
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


class RecipeSearchRequest(BaseModel):
    """Recipe search request parameters"""
    search_term: str
    search_type: str = "name"  # name, ingredient, category, area


class Meal(BaseModel):
    """Universal meal entity for all API endpoints"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    # Required fields (present in all responses)
    idMeal: str
    strMeal: str
    
    # Optional fields (present in detailed responses)
    strMealAlternate: Optional[str] = None
    strCategory: Optional[str] = None
    strArea: Optional[str] = None
    strInstructions: Optional[str] = None
    strMealThumb: Optional[str] = None
    strTags: Optional[str] = None
    strYoutube: Optional[str] = None
    
    # Ingredients (1-20)
    strIngredient1: Optional[str] = None
    strIngredient2: Optional[str] = None
    strIngredient3: Optional[str] = None
    strIngredient4: Optional[str] = None
    strIngredient5: Optional[str] = None
    strIngredient6: Optional[str] = None
    strIngredient7: Optional[str] = None
    strIngredient8: Optional[str] = None
    strIngredient9: Optional[str] = None
    strIngredient10: Optional[str] = None
    strIngredient11: Optional[str] = None
    strIngredient12: Optional[str] = None
    strIngredient13: Optional[str] = None
    strIngredient14: Optional[str] = None
    strIngredient15: Optional[str] = None
    strIngredient16: Optional[str] = None
    strIngredient17: Optional[str] = None
    strIngredient18: Optional[str] = None
    strIngredient19: Optional[str] = None
    strIngredient20: Optional[str] = None
    
    # Measures (1-20)
    strMeasure1: Optional[str] = None
    strMeasure2: Optional[str] = None
    strMeasure3: Optional[str] = None
    strMeasure4: Optional[str] = None
    strMeasure5: Optional[str] = None
    strMeasure6: Optional[str] = None
    strMeasure7: Optional[str] = None
    strMeasure8: Optional[str] = None
    strMeasure9: Optional[str] = None
    strMeasure10: Optional[str] = None
    strMeasure11: Optional[str] = None
    strMeasure12: Optional[str] = None
    strMeasure13: Optional[str] = None
    strMeasure14: Optional[str] = None
    strMeasure15: Optional[str] = None
    strMeasure16: Optional[str] = None
    strMeasure17: Optional[str] = None
    strMeasure18: Optional[str] = None
    strMeasure19: Optional[str] = None
    strMeasure20: Optional[str] = None
    
    # Additional fields (present in detailed responses)
    strSource: Optional[str] = None
    strImageSource: Optional[str] = None
    strCreativeCommonsConfirmed: Optional[str] = None
    dateModified: Optional[str] = None


class ApiResponse(BaseModel):
    """Universal API response for all endpoints"""
    model_config = ConfigDict(extra='allow', use_enum_values=True)
    
    meals: Optional[List[Meal]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiResponse":
        """Create ApiResponse from dictionary using Pydantic's automatic mapping"""
        return cls(**data)


# Available recipe categories
RECIPE_CATEGORIES = [
    "Beef", "Breakfast", "Chicken", "Dessert", "Goat", "Lamb", 
    "Miscellaneous", "Pasta", "Pork", "Seafood", "Side", "Starter", 
    "Vegan", "Vegetarian"
]

# Available areas/cuisines
RECIPE_AREAS = [
    "American", "British", "Canadian", "Chinese", "Croatian", "Dutch", 
    "Egyptian", "French", "Greek", "Indian", "Irish", "Italian", 
    "Jamaican", "Japanese", "Kenyan", "Malaysian", "Mexican", "Moroccan", 
    "Polish", "Portuguese", "Russian", "Spanish", "Thai", "Tunisian", 
    "Turkish", "Vietnamese"
] 