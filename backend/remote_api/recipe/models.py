"""
食谱API数据模型
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class RecipeSearchRequest:
    """食谱搜索请求参数"""
    search_term: str
    search_type: str = "name"  # name, ingredient, category, area


@dataclass
class Recipe:
    """食谱详细信息"""
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
    """食谱列表项（简化版）"""
    id: str
    name: str
    image_url: Optional[str] = None


@dataclass
class RecipeSearchResponse:
    """食谱搜索响应"""
    meals: Optional[List[Recipe]] = None


@dataclass
class RecipeListResponse:
    """食谱列表响应"""
    meals: Optional[List[RecipeListItem]] = None


# 可用的食谱分类
RECIPE_CATEGORIES = [
    "Beef", "Breakfast", "Chicken", "Dessert", "Goat", "Lamb", 
    "Miscellaneous", "Pasta", "Pork", "Seafood", "Side", "Starter", 
    "Vegan", "Vegetarian"
]

# 可用的地区/菜系
RECIPE_AREAS = [
    "American", "British", "Canadian", "Chinese", "Croatian", "Dutch", 
    "Egyptian", "French", "Greek", "Indian", "Irish", "Italian", 
    "Jamaican", "Japanese", "Kenyan", "Malaysian", "Mexican", "Moroccan", 
    "Polish", "Portuguese", "Russian", "Spanish", "Thai", "Tunisian", 
    "Turkish", "Vietnamese"
]


def extract_ingredients_and_measures(meal_data: Dict) -> tuple[List[str], List[str]]:
    """从meal数据中提取成分和份量"""
    ingredients = []
    measures = []
    
    for i in range(1, 21):  # TheMealDB最多支持20个成分
        ingredient_key = f"strIngredient{i}"
        measure_key = f"strMeasure{i}"
        
        ingredient_raw = meal_data.get(ingredient_key, "")
        measure_raw = meal_data.get(measure_key, "")
        
        # 安全地处理可能为None的值
        ingredient = ingredient_raw.strip() if ingredient_raw else ""
        measure = measure_raw.strip() if measure_raw else ""
        
        if ingredient and ingredient.lower() != "null":
            ingredients.append(ingredient)
            measures.append(measure if measure and measure.lower() != "null" else "")
    
    return ingredients, measures


def recipe_from_dict(meal_data: Dict) -> Recipe:
    """从API响应字典创建Recipe对象"""
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
    """从API响应字典创建RecipeListItem对象"""
    return RecipeListItem(
        id=meal_data["idMeal"],
        name=meal_data["strMeal"],
        image_url=meal_data.get("strMealThumb")
    )


def recipe_search_response_from_dict(data: Dict) -> RecipeSearchResponse:
    """从API响应字典创建RecipeSearchResponse对象"""
    meals = None
    if data.get("meals"):
        meals = [recipe_from_dict(meal_data) for meal_data in data["meals"]]
    
    return RecipeSearchResponse(meals=meals)


def recipe_list_response_from_dict(data: Dict) -> RecipeListResponse:
    """从API响应字典创建RecipeListResponse对象"""
    meals = None
    if data.get("meals"):
        meals = [recipe_list_item_from_dict(meal_data) for meal_data in data["meals"]]
    
    return RecipeListResponse(meals=meals)


def format_recipe_summary(recipe: Recipe) -> str:
    """格式化食谱摘要"""
    summary = f"""
食谱名称: {recipe.name}
分类: {recipe.category}
地区: {recipe.area}
    """.strip()
    
    if recipe.tags:
        summary += f"\n标签: {recipe.tags}"
    
    if recipe.ingredients:
        summary += f"\n成分数量: {len(recipe.ingredients)}个"
    
    return summary


def format_recipe_details(recipe: Recipe) -> str:
    """格式化食谱详细信息"""
    details = format_recipe_summary(recipe)
    
    if recipe.ingredients and recipe.measures:
        details += "\n\n成分列表:"
        for ingredient, measure in zip(recipe.ingredients, recipe.measures):
            measure_text = f" - {measure}" if measure else ""
            details += f"\n• {ingredient}{measure_text}"
    
    if recipe.instructions:
        details += f"\n\n制作步骤:\n{recipe.instructions}"
    
    if recipe.youtube_url:
        details += f"\n\n视频教程: {recipe.youtube_url}"
    
    return details 