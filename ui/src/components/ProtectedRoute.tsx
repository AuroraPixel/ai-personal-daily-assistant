import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { getCurrentUser } from '../store/slices/authSlice';
import type { ProtectedRouteProps } from '../lib/types';
import { Loader2 } from 'lucide-react';

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireAuth = true 
}) => {
  const dispatch = useAppDispatch();
  const location = useLocation();
  const { isAuthenticated, isLoading, token, user } = useAppSelector((state) => state.auth);

  // 如果有token但没有用户信息，尝试获取用户信息
  // 注意：只有在需要认证的页面才进行此检查，避免在登录页面时触发
  useEffect(() => {
    if (requireAuth && token && !user && !isLoading && !isAuthenticated) {
      dispatch(getCurrentUser());
    }
  }, [requireAuth, token, user, isLoading, isAuthenticated, dispatch]);

  // 正在加载中
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">正在验证身份...</p>
        </div>
      </div>
    );
  }

  // 需要认证但未认证，重定向到登录页面
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 已认证但访问登录页面，重定向到主页
  if (!requireAuth && isAuthenticated && location.pathname === '/login') {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute; 