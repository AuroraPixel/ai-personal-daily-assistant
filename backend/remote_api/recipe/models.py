"""
Recipe API Data Models

Author: Andrew Wang
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class RecipeSearchRequest:
    """Recipe search request parameters"""
    search_term: str
    search_type: str = "name"  # name, ingredient, category, area


@dataclass
class Recipe:
    """Recipe detailed information"""
    id: str
    name: str
    category: str
    area: str
    instructions: str
    image_url: Optional[str] = None
    tags: Optional[str] = None
    youtube_url: Optional[str] = None
    ingredients: Optional[List[str]] = None
    measures: Optional[List[str]] = None


@dataclass
class RecipeListItem:
    """Recipe list item (simplified version)"""
    id: str
    name: str
    image_url: Optional[str] = None


@dataclass
class RecipeSearchResponse:
    """Recipe search response"""
    meals: Optional[List[Recipe]] = None


@dataclass
class RecipeListResponse:
    """Recipe list response"""
    meals: Optional[List[RecipeListItem]] = None


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


def extract_ingredients_and_measures(meal_data: Dict) -> tuple[List[str], List[str]]:
    """Extract ingredients and measures from meal data"""
    ingredients = []
    measures = []
    
    for i in range(1, 21):  # TheMealDB supports up to 20 ingredients
        ingredient_key = f"strIngredient{i}"
        measure_key = f"strMeasure{i}"
        
        ingredient_raw = meal_data.get(ingredient_key, "")
        measure_raw = meal_data.get(measure_key, "")
        
        # Safely handle potentially None values
        ingredient = ingredient_raw.strip() if ingredient_raw else ""
        measure = measure_raw.strip() if measure_raw else ""
        
        if ingredient and ingredient.lower() != "null":
            ingredients.append(ingredient)
            measures.append(measure if measure and measure.lower() != "null" else "")
    
    return ingredients, measures


def recipe_from_dict(meal_data: Dict) -> Recipe:
    """Create Recipe object from API response dictionary"""
    ingredients, measures = extract_ingredients_and_measures(meal_data)
    
    return Recipe(
        id=meal_data["idMeal"],
        name=meal_data["strMeal"],
        category=meal_data["strCategory"],
        area=meal_data["strArea"],
        instructions=meal_data["strInstructions"],
        image_url=meal_data.get("strMealThumb"),
        tags=meal_data.get("strTags"),
        youtube_url=meal_data.get("strYoutube"),
        ingredients=ingredients,
        measures=measures
    )


def recipe_list_item_from_dict(meal_data: Dict) -> RecipeListItem:
    """Create RecipeListItem object from API response dictionary"""
    return RecipeListItem(
        id=meal_data["idMeal"],
        name=meal_data["strMeal"],
        image_url=meal_data.get("strMealThumb")
    )


def recipe_search_response_from_dict(data: Dict) -> RecipeSearchResponse:
    """Create RecipeSearchResponse object from API response dictionary"""
    meals = None
    if data.get("meals"):
        meals = [recipe_from_dict(meal_data) for meal_data in data["meals"]]
    
    return RecipeSearchResponse(meals=meals)


def recipe_list_response_from_dict(data: Dict) -> RecipeListResponse:
    """Create RecipeListResponse object from API response dictionary"""
    meals = None
    if data.get("meals"):
        meals = [recipe_list_item_from_dict(meal_data) for meal_data in data["meals"]]
    
    return RecipeListResponse(meals=meals)


def format_recipe_summary(recipe: Recipe) -> str:
    """Format recipe summary"""
    summary = f"""
Recipe Name: {recipe.name}
Category: {recipe.category}
Area: {recipe.area}
    """.strip()
    
    if recipe.tags:
        summary += f"\nTags: {recipe.tags}"
    
    if recipe.ingredients:
        summary += f"\nIngredients: {len(recipe.ingredients)} items"
    
    return summary


def format_recipe_details(recipe: Recipe) -> str:
    """Format recipe detailed information"""
    details = format_recipe_summary(recipe)
    
    if recipe.ingredients and recipe.measures:
        details += "\n\nIngredients List:"
        for ingredient, measure in zip(recipe.ingredients, recipe.measures):
            measure_text = f" - {measure}" if measure else ""
            details += f"\n• {ingredient}{measure_text}"
    
    if recipe.instructions:
        details += f"\n\nInstructions:\n{recipe.instructions}"
    
    if recipe.youtube_url:
        details += f"\n\nVideo Tutorial: {recipe.youtube_url}"
    
    return details 