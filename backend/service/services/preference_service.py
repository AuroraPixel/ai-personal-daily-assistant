"""
用户偏好设置服务

管理用户的偏好设置，包括保存、获取、更新等操作
"""

import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from core.database_core import DatabaseClient
from ..models.user_preference import UserPreference
from .user_service import UserService


class PreferenceService:
    """
    用户偏好设置服务类
    
    管理用户的偏好设置数据
    """
    
    def __init__(self, db_client: Optional[DatabaseClient] = None):
        """
        初始化偏好设置服务
        
        Args:
            db_client: 数据库客户端，如果未提供则创建新实例
        """
        self.db_client = db_client or DatabaseClient()
        self.user_service = UserService()
        
        # 确保数据库初始化
        if not self.db_client._initialized:
            self.db_client.initialize()
    
    def get_user_preferences(self, user_id: int, category: str = 'general') -> Optional[Dict[str, Any]]:
        """
        获取用户偏好设置
        
        Args:
            user_id: 用户ID
            category: 偏好设置类别
            
        Returns:
            偏好设置字典或None
        """
        try:
            # 验证用户是否存在
            if not self.user_service.validate_user_exists(user_id):
                return None
            
            with self.db_client.get_session() as session:
                preference = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category
                ).first()
                
                if preference:
                    return json.loads(preference.preferences)
                return None
                
        except Exception as e:
            print(f"获取用户偏好设置失败: {e}")
            return None
    
    def save_user_preferences(self, user_id: int, preferences: Dict[str, Any], 
                             category: str = 'general') -> bool:
        """
        保存用户偏好设置
        
        Args:
            user_id: 用户ID
            preferences: 偏好设置字典
            category: 偏好设置类别
            
        Returns:
            是否保存成功
        """
        try:
            # 验证用户是否存在
            if not self.user_service.validate_user_exists(user_id):
                print(f"用户 {user_id} 不存在")
                return False
            
            preferences_json = json.dumps(preferences, ensure_ascii=False)
            
            with self.db_client.get_session() as session:
                # 查找现有偏好设置
                existing_preference = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category
                ).first()
                
                if existing_preference:
                    # 更新现有设置
                    existing_preference.preferences = preferences_json
                    session.commit()
                else:
                    # 创建新设置
                    new_preference = UserPreference(
                        user_id=user_id,
                        preferences=preferences_json,
                        category=category
                    )
                    session.add(new_preference)
                    session.commit()
                
                return True
                
        except Exception as e:
            print(f"保存用户偏好设置失败: {e}")
            return False
    
    def update_user_preferences(self, user_id: int, preferences_update: Dict[str, Any], 
                               category: str = 'general') -> bool:
        """
        更新用户偏好设置（合并更新）
        
        Args:
            user_id: 用户ID
            preferences_update: 需要更新的偏好设置
            category: 偏好设置类别
            
        Returns:
            是否更新成功
        """
        try:
            # 获取现有设置
            existing_preferences = self.get_user_preferences(user_id, category) or {}
            
            # 合并设置
            existing_preferences.update(preferences_update)
            
            # 保存更新后的设置
            return self.save_user_preferences(user_id, existing_preferences, category)
            
        except Exception as e:
            print(f"更新用户偏好设置失败: {e}")
            return False
    
    def delete_user_preferences(self, user_id: int, category: str = 'general') -> bool:
        """
        删除用户偏好设置
        
        Args:
            user_id: 用户ID
            category: 偏好设置类别
            
        Returns:
            是否删除成功
        """
        try:
            with self.db_client.get_session() as session:
                preference = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category
                ).first()
                
                if preference:
                    session.delete(preference)
                    session.commit()
                    return True
                return False
                
        except Exception as e:
            print(f"删除用户偏好设置失败: {e}")
            return False
    
    def get_user_preference_value(self, user_id: int, key: str, 
                                 default_value: Any = None, category: str = 'general') -> Any:
        """
        获取用户偏好设置中的特定值
        
        Args:
            user_id: 用户ID
            key: 偏好设置键名
            default_value: 默认值
            category: 偏好设置类别
            
        Returns:
            偏好设置值
        """
        preferences = self.get_user_preferences(user_id, category)
        if preferences and key in preferences:
            return preferences[key]
        return default_value
    
    def set_user_preference_value(self, user_id: int, key: str, value: Any, 
                                 category: str = 'general') -> bool:
        """
        设置用户偏好设置中的特定值
        
        Args:
            user_id: 用户ID
            key: 偏好设置键名
            value: 偏好设置值
            category: 偏好设置类别
            
        Returns:
            是否设置成功
        """
        return self.update_user_preferences(user_id, {key: value}, category)
    
    def get_all_user_preferences(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        """
        获取用户所有类别的偏好设置
        
        Args:
            user_id: 用户ID
            
        Returns:
            所有偏好设置字典
        """
        try:
            with self.db_client.get_session() as session:
                preferences = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id
                ).all()
                
                result = {}
                for pref in preferences:
                    result[pref.category] = json.loads(pref.preferences)
                
                return result
                
        except Exception as e:
            print(f"获取用户所有偏好设置失败: {e}")
            return {}
    
    def get_preference_categories(self, user_id: int) -> list:
        """
        获取用户偏好设置的所有类别
        
        Args:
            user_id: 用户ID
            
        Returns:
            偏好设置类别列表
        """
        try:
            with self.db_client.get_session() as session:
                categories = session.query(UserPreference.category).filter(
                    UserPreference.user_id == user_id
                ).distinct().all()
                
                return [cat[0] for cat in categories]
                
        except Exception as e:
            print(f"获取用户偏好设置类别失败: {e}")
            return []
    
    def export_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        导出用户偏好设置
        
        Args:
            user_id: 用户ID
            
        Returns:
            导出的偏好设置字典
        """
        try:
            user_summary = self.user_service.get_user_summary(user_id)
            all_preferences = self.get_all_user_preferences(user_id)
            
            return {
                'user_info': user_summary,
                'preferences': all_preferences,
                'export_timestamp': json.dumps(str(self._get_current_timestamp()))
            }
            
        except Exception as e:
            print(f"导出用户偏好设置失败: {e}")
            return None
    
    def import_user_preferences(self, user_id: int, preferences_data: Dict[str, Any]) -> bool:
        """
        导入用户偏好设置
        
        Args:
            user_id: 用户ID
            preferences_data: 导入的偏好设置数据
            
        Returns:
            是否导入成功
        """
        try:
            if 'preferences' not in preferences_data:
                return False
            
            success = True
            for category, preferences in preferences_data['preferences'].items():
                if not self.save_user_preferences(user_id, preferences, category):
                    success = False
            
            return success
            
        except Exception as e:
            print(f"导入用户偏好设置失败: {e}")
            return False
    
    def _get_current_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now()
    
    def close(self):
        """关闭数据库连接"""
        if self.db_client:
            self.db_client.close() 