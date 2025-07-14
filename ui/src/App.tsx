import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ErrorBoundary from './components/ErrorBoundary';
import { setGlobalErrorHandler, setAuthFailureHandler } from './services/apiService';
import { useToast } from './components/ui/toast';
import { useAppDispatch } from './store/hooks';
import { logout } from './store/slices/authSlice';
import { useAuthInit, useAutoTokenRefresh } from './hooks/useAuthInit';
import { Loader2 } from 'lucide-react';

function App() {
  const { error: showError } = useToast();
  const dispatch = useAppDispatch();
  
  // 初始化认证状态
  const { isInitialized, isAuthenticated } = useAuthInit();
  
  // 自动token刷新
  useAutoTokenRefresh();

  useEffect(() => {
    // 设置全局API错误处理
    setGlobalErrorHandler((error: string, details?: any) => {
      showError(error, details?.message || '请稍后重试');
    });

    // 设置认证失败处理
    setAuthFailureHandler(() => {
      dispatch(logout());
    });
  }, [showError, dispatch]);

  // 认证初始化中，显示加载页面
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">初始化中...</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <Routes>
        {/* 公开路由 */}
        <Route 
          path="/login" 
          element={
            <ProtectedRoute requireAuth={false}>
              <Login />
            </ProtectedRoute>
          } 
        />
        
        {/* 受保护路由 */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute requireAuth={true}>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        
        {/* 默认重定向到主页 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ErrorBoundary>
  );
}

export default App;
