"""
食谱API客户端
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
    """TheMealDB食谱API客户端"""
    
    def __init__(self):
        self.client = APIClient("https://www.themealdb.com/api/json/v1/1")
    
    def search_by_name(self, name: str) -> Optional[RecipeSearchResponse]:
        """
        按名称搜索食谱
        
        Args:
            name: 食谱名称
            
        Returns:
            食谱搜索响应或None
        """
        params = {"s": name}
        data = self.client.get("/search.php", params=params)
        
        if data:
            return recipe_search_response_from_dict(data)
        return None
    
    def search_by_ingredient(self, ingredient: str) -> Optional[RecipeListResponse]:
        """
        按主要成分搜索食谱
        
        Args:
            ingredient: 成分名称
            
        Returns:
            食谱列表响应或None
        """
        params = {"i": ingredient}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return recipe_list_response_from_dict(data)
        return None
    
    def search_by_category(self, category: str) -> Optional[RecipeListResponse]:
        """
        按分类搜索食谱
        
        Args:
            category: 分类名称
            
        Returns:
            食谱列表响应或None
        """
        if category not in RECIPE_CATEGORIES:
            print(f"无效分类: {category}. 可用分类: {RECIPE_CATEGORIES}")
            return None
        
        params = {"c": category}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return recipe_list_response_from_dict(data)
        return None
    
    def search_by_area(self, area: str) -> Optional[RecipeListResponse]:
        """
        按地区/菜系搜索食谱
        
        Args:
            area: 地区/菜系名称
            
        Returns:
            食谱列表响应或None
        """
        if area not in RECIPE_AREAS:
            print(f"无效地区: {area}. 可用地区: {RECIPE_AREAS}")
            return None
        
        params = {"a": area}
        data = self.client.get("/filter.php", params=params)
        
        if data:
            return recipe_list_response_from_dict(data)
        return None
    
    def get_recipe_details(self, meal_id: str) -> Optional[Recipe]:
        """
        获取食谱详细信息
        
        Args:
            meal_id: 食谱ID
            
        Returns:
            食谱详细信息或None
        """
        params = {"i": meal_id}
        data = self.client.get("/lookup.php", params=params)
        
        if data and data.get("meals"):
            response = recipe_search_response_from_dict(data)
            return response.meals[0] if response.meals else None
        return None
    
    def get_random_recipe(self) -> Optional[Recipe]:
        """
        获取随机食谱
        
        Returns:
            随机食谱或None
        """
        data = self.client.get("/random.php")
        
        if data and data.get("meals"):
            response = recipe_search_response_from_dict(data)
            return response.meals[0] if response.meals else None
        return None
    
    def get_categories(self) -> Optional[List[str]]:
        """
        获取可用的食谱分类
        
        Returns:
            分类列表
        """
        return RECIPE_CATEGORIES.copy()
    
    def get_areas(self) -> Optional[List[str]]:
        """
        获取可用的地区/菜系
        
        Returns:
            地区列表
        """
        return RECIPE_AREAS.copy()
    
    def format_search_results(self, response: RecipeSearchResponse, 
                             max_results: int = 10) -> str:
        """
        格式化搜索结果
        
        Args:
            response: 搜索响应
            max_results: 最大显示结果数
            
        Returns:
            格式化的搜索结果字符串
        """
        if not response.meals:
            return "未找到相关食谱"
        
        results = []
        for i, recipe in enumerate(response.meals[:max_results]):
            results.append(f"{i+1}. {format_recipe_summary(recipe)}")
        
        total_count = len(response.meals)
        if total_count > max_results:
            results.append(f"\n... 还有 {total_count - max_results} 个结果")
        
        return "\n\n".join(results)
    
    def format_list_results(self, response: RecipeListResponse, 
                           max_results: int = 10) -> str:
        """
        格式化列表结果
        
        Args:
            response: 列表响应
            max_results: 最大显示结果数
            
        Returns:
            格式化的列表结果字符串
        """
        if not response.meals:
            return "未找到相关食谱"
        
        results = []
        for i, recipe in enumerate(response.meals[:max_results]):
            results.append(f"{i+1}. {recipe.name} (ID: {recipe.id})")
        
        total_count = len(response.meals)
        if total_count > max_results:
            results.append(f"\n... 还有 {total_count - max_results} 个结果")
        
        return "\n".join(results)
    
    def comprehensive_search(self, query: str, max_results: int = 5) -> str:
        """
        综合搜索（按名称、成分、分类、地区）
        
        Args:
            query: 搜索关键词
            max_results: 每个类别的最大结果数
            
        Returns:
            综合搜索结果字符串
        """
        results = []
        
        # 按名称搜索
        name_results = self.search_by_name(query)
        if name_results and name_results.meals:
            results.append(f"按名称搜索 '{query}':")
            results.append(self.format_search_results(name_results, max_results))
        
        # 按成分搜索
        ingredient_results = self.search_by_ingredient(query)
        if ingredient_results and ingredient_results.meals:
            results.append(f"\n按成分搜索 '{query}':")
            results.append(self.format_list_results(ingredient_results, max_results))
        
        # 按分类搜索（如果匹配）
        query_title = query.title()
        if query_title in RECIPE_CATEGORIES:
            category_results = self.search_by_category(query_title)
            if category_results and category_results.meals:
                results.append(f"\n按分类搜索 '{query_title}':")
                results.append(self.format_list_results(category_results, max_results))
        
        # 按地区搜索（如果匹配）
        if query_title in RECIPE_AREAS:
            area_results = self.search_by_area(query_title)
            if area_results and area_results.meals:
                results.append(f"\n按地区搜索 '{query_title}':")
                results.append(self.format_list_results(area_results, max_results))
        
        return "\n\n".join(results) if results else f"未找到与 '{query}' 相关的食谱" 