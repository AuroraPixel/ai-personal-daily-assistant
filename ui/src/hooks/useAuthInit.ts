import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { validateToken, restoreAuth } from '../store/slices/authSlice';
import { AuthManager } from '../lib/auth';

/**
 * 认证初始化Hook
 * 在应用启动时检查和恢复认证状态
 */
export const useAuthInit = () => {
  const dispatch = useAppDispatch();
  const { isAuthenticated, isLoading, token } = useAppSelector((state) => state.auth);

  useEffect(() => {
    console.log('🔐 开始认证初始化...');
    
    // 如果已经认证，不需要再次初始化
    if (isAuthenticated) {
      console.log('✅ 已认证，跳过初始化');
      return;
    }

    // 检查是否有本地存储的认证信息
    const hasValidAuth = AuthManager.hasValidAuth();
    
    if (hasValidAuth) {
      console.log('🔄 发现有效的本地认证信息，验证token...');
      
      // 验证token是否仍然有效
      dispatch(validateToken())
        .unwrap()
        .then((user) => {
          console.log('✅ Token验证成功，用户已登录:', user.username);
        })
        .catch((error) => {
          console.log('❌ Token验证失败:', error);
          console.log('🧹 清除无效的认证信息');
        });
    } else {
      console.log('ℹ️ 没有有效的本地认证信息');
    }
  }, [dispatch, isAuthenticated]);

  return {
    isInitialized: !isLoading,
    isAuthenticated,
  };
};

/**
 * 自动token刷新Hook
 * 监控token过期状态，自动刷新即将过期的token
 */
export const useAutoTokenRefresh = () => {
  const dispatch = useAppDispatch();
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  useEffect(() => {
    if (!isAuthenticated) return;

    const checkTokenExpiry = () => {
      if (AuthManager.isTokenExpiringSoon()) {
        console.log('⏰ Token即将过期，尝试刷新...');
        dispatch(validateToken())
          .unwrap()
          .then(() => {
            console.log('✅ Token刷新成功');
          })
          .catch((error) => {
            console.log('❌ Token刷新失败:', error);
          });
      }
    };

    // 每5分钟检查一次token状态
    const interval = setInterval(checkTokenExpiry, 5 * 60 * 1000);

    // 组件挂载时立即检查一次
    checkTokenExpiry();

    return () => clearInterval(interval);
  }, [dispatch, isAuthenticated]);
}; 